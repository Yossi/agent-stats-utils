Agent-stats Utils
=================

## Features

## How to use

## Setting up
###Reqirements
python3+
mysql server

clone this repo.
get phantomjs http://phantomjs.org/releases.html
throw it in the same dir as the other checked out files, or change the code in util.py that looks like this
     driver = webdriver.PhantomJS('phantomjs', service_args=['--cookies-file=cookies.txt'])
to point to the path where you installed phantomjs.
create database from schema.sql (this is destructive to existing tables. do not run on an existing setup with data you dont want to lose)
copy secrets.py.example to secrets.py and change the settings and credentials in there to real values.
virtualenv -p /usr/bin/python3 venv
pip install -r requirements.txt