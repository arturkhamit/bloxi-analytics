# HOW TO RUN BACKEND


## before executing server you have to:


### 1. Install docker:
* Add Docker's official GPG key

`sudo apt-get update`

`sudo apt-get install ca-certificates curl`

`sudo install -m 0755 -d /etc/apt/keyrings`

`sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc`

`sudo chmod a+r /etc/apt/keyrings/docker.asc`


* Add the repository to Apt sources

`echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null`

`sudo apt-get update`


* check if docker is running

`sudo systemctl status docker`

  * if not

`sudo systemctl start docker`


### 2. Download postgresql and create database
* Add postgresql's GPG key

`wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -`


* Adding its repository and updating packages

`sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'`

`sudo apt update`


* Ask repository creator for a DB


### 3. Create virtual python environment and install requirements
* create virtual env

`python3 -m venv env`


* load it

`source env/bin/activate`


* install all requirements

`pip install -r requirements.txt`

### 4. Add secret Django secret key to your project
* ask someone in charge for backend for this key

## Only after that you will be able to run backend successfully with command (you have to be in server/src_django directory)
`python manage.py runserver`

## running FastAPI (you have to be in server/ directory):
`uvicorn main:app --reload --host 0.0.0.0 --port 8001`



# HOW TO RUN AI
## TODO
