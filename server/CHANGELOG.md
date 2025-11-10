## 6 nov. 13:49
changed connecting info to DB in file settings.py

deployed docker image (used commands below (you have to be in directory in which exists Dockerfile !!! AND .env file !!!))

`docker build -t django-service .`

`docker run -d -p 8001:8001 --env-file ./.env --name django django-service`

and you will be able to test it on url `localhost:8001`

to enter into a docker image use this command

`docker exec -it django /bin/bash`


## 6 nov. 14:25
added api on a django side

## 6 nov. 23:15
rewriting db.models for a new database

## 6 nov. 23:31
rewriting embedding for a new database
