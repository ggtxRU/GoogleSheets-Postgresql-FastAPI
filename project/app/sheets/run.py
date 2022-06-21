"""
All the work of the server with Google Sheets takes place here.
"""
import asyncio
import os
from datetime import datetime

import googleapiclient.discovery
import httplib2
import httpx
from bs4 import BeautifulSoup as bsp
from loguru import logger
from oauth2client.service_account import ServiceAccountCredentials

from ..logs.loguru_config import init_logging
from ..models.tortoise import Orders


async def get_data_from_google_sheets() -> list:
    """
    Here, we check our Google Sheets for changes and updates.

    """
    logger.info("Sending request to Google Sheets ... ")
    # key, from Google Developer Console
    CREDENTIALS_FILE = "creds.json"
    # ID Google Sheets
    spreadsheet_id = "14h001HdvIbWxzuzNPUOBjGRpRzPOOK7-eZkGI0n7TDk"
    # We specify the services that we will work with
    # In our case, these are spreadsheets and Google Drive
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    # Сreating an authentication object
    httpAuth = credentials.authorize(httplib2.Http())
    # Get instance of API, with whom we will work
    service = googleapiclient.discovery.build("sheets", "v4", http=httpAuth)
    # Read file
    r = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range="A:D", majorDimension="ROWS")
        .execute()["values"][1::]
    )
    return r


async def get_dollar_quote() -> float:
    """

    Here we send a request to the Central Bank of the Russian Federation,
    and get a quote of the USD, which translate into the ruble finally.

    """
    with httpx.Client() as client:
        r = client.get(f"https://www.cbr.ru/scripts/XML_daily.asp")
        if r.status_code == 200:
            quote_usd = round(
                float(
                    (
                        (bsp(r.content, features="xml"))
                        .find(ID="R01235")
                        .find("Value")
                        .text
                    ).replace(",", ".")
                ),
                2,
            )
        else:
            logger.info("Can't request to USD quote..")
            try:
                await get_dollar_quote()
            except:
                asyncio.sleep(10)
                await get_dollar_quote()
    return quote_usd


async def run_cycle() -> asyncio:
    """
    Here, we starting a new iteration, where we get a table from Google Sheets and the dollar exchange rate.

    """
    dict_data = await get_data_from_google_sheets()  # get Google Sheets table
    quote_usd = await get_dollar_quote()  # get dollar exchange rate
    """
    Next, we make a query to the database for each order from Google Sheets table. 
    If order exists in DB, we will check all the columns and update the ones that are needed based on the relevant Google-table, 
    if not, the order will be created in the database.
    """
    update_count = create_count = delete_count = 0
    for data in dict_data:
        # query to update
        ord_id = await Orders.filter(id=int(data[0])).first().values()
        if ord_id:
            # here, if order exist in DB, we check all columns, if there are changes in the original document, we will transfer them to DB
            if ord_id["order_number"] != int(data[1]):  # check order number column
                update_count += 1
                old_order_number = ord_id["order_number"]
                update_order_number = await Orders.filter(id=int(data[0])).update(
                    order_number=int(data[1])
                )
                logger.info(
                    f"[NEW UPDATING]\nOrder id: {data[0]}\nUpdated |Order number| from {old_order_number} to {data[1]}\n[UPDATE COMPLETE]"
                )
            if ord_id["price_usd"] != int(data[2]):  # check order price columns
                update_count += 2
                old_order_price_usd = ord_id["price_usd"]
                old_order_price_rub = ord_id["price_rub"]
                new_price_rub = float(data[2]) * float(quote_usd)
                update_order_price = await Orders.filter(id=int(data[0])).update(
                    price_usd=float(data[2]), price_rub=new_price_rub
                )
                if update_order_price:
                    logger.info(
                        f"[NEW UPDATING]\nOrder id: {data[0]}\nUpdated |Price in USD| from {old_order_price_usd} to {data[2]}\nUpdated |Price in RUB| from {old_order_price_rub} to {new_price_rub}\n[UPDATE COMPLETE]"
                    )

            if ord_id["delivery_date"] != data[3]:  # check delivery date column
                update_count += 1
                old_order_delivery_date = ord_id["delivery_date"]
                update_order_delivery_date = await Orders.filter(
                    id=int(data[0])
                ).update(
                    delivery_date=datetime.strptime(str(data[3]), "%d.%m.%Y").strftime(
                        "%d.%m.%Y"
                    )
                )
                logger.info(
                    f"[NEW UPDATING]\nOrder id: {data[0]}\nUpdated |Delivery date| from {old_order_delivery_date} to {data[3]}\n[UPDATE COMPLETE]"
                )
        if not ord_id:
            # create order in db, if not exist
            create_count += 1
            order = Orders(
                id=int(data[0]),
                order_number=int(data[1]),
                price_usd=float(data[2]),
                price_rub=round((float(data[2]) * float(quote_usd)), 2),
                delivery_date=(datetime.strptime(str(data[3]), "%d.%m.%Y")).strftime(
                    "%d.%m.%Y"
                ),
            )
            await order.save()

    logger.info(f"\nCREATED: {create_count}\nUPDATED: {update_count}")
    all_orders_in_db_count = await Orders.all().count()
    if (
        len(dict_data) < all_orders_in_db_count
    ):  # check len of our Google table, and postgres table
        await delete_data_from_db(dict_data)

    await asyncio.sleep(int(os.environ.get("TIME_INTERVAL_GOOGLE_SHEETS_REQUEST")))
    return asyncio.create_task(run_cycle())


async def delete_data_from_db(dict_data: list) -> None:
    """Here, we check our DB with Google Sheets table for looking columns what we need to delete from db."""
    delete_count = 0
    all_orders_in_db = await Orders.all().values()  # check db
    for j in all_orders_in_db:
        j = list(j.values())
        price_rub_pop = j.pop(3)
        j = [str(i) for i in j]
        if (
            j not in dict_data
        ):  # looking for order, what which is no longer in google table, but is still in our database
            values_from_db = j
            await Orders.filter(
                id=values_from_db[0],
                order_number=values_from_db[1],
                price_usd=values_from_db[2],
                price_rub=price_rub_pop,
                delivery_date=values_from_db[3],
            ).delete()
            delete_count += 1

    logger.info(f"DELETED: {delete_count}")


async def activate_checking() -> None:
    """
    Start the cycle of getting data from Google Sheets.

    Getting data from Google Sheets table, getting a dollar quote, and subsequent work with data.

    """
    init_logging()
    await asyncio.sleep(5)
    asyncio.create_task(run_cycle())
