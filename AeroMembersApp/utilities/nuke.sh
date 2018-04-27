#!/bin/bash 

mv ../migrations/loadItems.py .
rm ../migrations/0*
mysql -u plumber -pplumberpass -e 'drop database aeromembersdb'
mysql -u plumber -pplumberpass -e 'create database aeromembersdb'
python ../../manage.py makemigrations
mv loadItems.py ../migrations/
python ../../manage.py migrate