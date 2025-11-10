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


* checks if docker is running

`sudo systemctl status docker`

  * if not

`sudo systemctl start docker`


### 2. Install ollama and llama3b-8:
* install ollama

`sudo docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama`


* run llama-3:8b on an image

`sudo docker exec ollama ollama run llama3:8b`


### 3. Download postgresql, create database and load ready-to-go sql dump
* Add postgresql's GPG key

`wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -`


* Adding its repository and updating packages

`sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'`

`sudo apt update`


* Creating database

`sudo -i -u postgres`

`createdb erste_2025`

`exit`


* Loading sql dump into a database

`psql -U postgres -d erste_2025 < injection.sql`



### 4. Create virtual python environment and install requirements
* create virtual env

`python3 -m venv env`


* load it

`source env/bin/activate`


* install all requirements

`pip install -r requirements.txt`

### 5. Add secret Django secret key to your project
* ask someone in charge for backend for this key

## And only after that you will be able to run backend successfully with command `python manage.py runserver 8000`
* FastAPI works on port 8001
