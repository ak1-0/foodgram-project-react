#  Foodgram - сеть для обмена рецептами

Добро пожаловать в проект Foodgram! Здесь можно размещать свои рецепты, просматривать, подписываться и добавлять в избранное рецепты других пользователей.  
Так же можно добавить понравившийся рецепт в список покупок и скачать файл "Что купить" с просуммированными наименованиями продуктов в текстовом формате.   

## Данные для входа в админку
Username: admin  
Password: admin  
email: a@a.ru  

Проект доступен по адресу:  
- https://myfood.sytes.net/recipes 
- https://myfood.sytes.net/admin/  

## Технологии, которые потребуются для разворачивания проекта:
-Docker,  
-Postgres,  
-Python,  
-Gunicorn,  
-Linux,    
-Ubuntu.  

## Как развернуть проект на своем сервере
Зайдите на свой удаленный сервер, перейдите в домашнюю директорию, установите Docker и Docker Compose.   
Создайте папку для проекта 'foodram',  
в ней создайте файлы docker-compose.production.yml и .env  
``` 
mkdir foodram  
cd foodram
```
Скопируйте содержимое docker-compose.production.yml и .env из этого проекта и вставьте код ваши файлы. Предварительно в файл .env укажите свои данные.
```
sudo nano docker-compose.production.yml  
sudo nano .env  
```

Запустите Docker Compose в режиме демона:  
```
sudo docker compose -f docker-compose.production.yml up -d  
```
Выполните миграции, соберите статику бэкенда  
(если работаете из VSCode и будут появляться ошибки, откройте PowerShell и попробуйте выполнить неудавшееся действие через него)  
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate  
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic  
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/  
```
Проект должен стать доступным по вашему доменному имени или локально:  
https://доменное_имя  

http://127.0.0.1:8000  


## Переменные проекта  
Вставьте свои данные:  
```
POSTGRES_USER=foodram_user  
POSTGRES_PASSWORD=foodram_password  
POSTGRES_DB=foodram  
DB_HOST=db  
DB_PORT=1234  
SECRET_KEY=django_secret_key_example  
DEBUG=False  
```

## Остановка контейнеров
Ctrl+С   
или в новом терминале выполните команду  
```
sudo docker compose -f docker-compose.yml down  
```