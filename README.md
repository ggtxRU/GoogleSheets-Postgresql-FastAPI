<h1 align="center">
  Тестовое задание
</h1>
<br>
<h3>
  Получение данных с документа при помощи Google API, сделанного в Google Sheets + Telegram оповещения
</h3>
<hr data-sourcepos="22:1-23:0">
<p>
  <i>Запускается бесконечный цикл получения данных с заданной периодичностью, данные заносятся в БД Postgres с добавлением колонки «стоимость в руб». Данные для перевода $ в рубли берутся по курсу ЦБ РФ. </i>
</p>
<p>
  <i>Проверяется соблюдение «срока поставки» из таблицы.  В случае, если срок прошел, будет отправлено уведомление в Telegram.</i>
</p>
  <br>
  
 <h2>Инструкция по запуску</h2><br>
<li>
  <strong>Клонировать репозиторий</strong>
</li>
<br>
<ul><code>$ git clone git@github.com:ggtxRU/GoogleSheets-Postgresql-FastAPI.git</code></ul><br>
<li>
  <strong>Перейти в директорию с проектом</strong>
</li>
<br>
<ul><code>$ cd GoogleSheets-Postgresql-FastAPI/</code></ul><br>
<li>
  <strong>Проставить переменные окружения в docker-comopse.yml</strong>
</li>
<ul><code>CHAT_ID=<чат, куда бот будет присылать оповещения><br></code></ul>
<ul><code>TIME_INTERVAL_TG_BOT=<временной интервал работы бота (раз в N секунд будут проверяться все сроки поставок из БД, если будет найдена просроченная дата, бот отправит уведомление></code></ul>
<ul><code>TIME_INTERVAL_GOOGLE_SHEETS_REQUEST=<временной интервал запросов к Google-таблице (в секундах)><br></code></ul>
 <br>
  <li>
  <strong>Запуск</strong>
</li> 
  <ul><code>docker-compose up --build<br></code></ul><br>
  
  <li>
  <strong>REST API</strong>
</li> 
<ul><code>http://localhost:8004/docs ---> реализовано одно REST API получения ордера из БД<br></code></ul><br>
