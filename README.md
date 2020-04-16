#  jupy
## платформа прототипирования и расчетов на базе Jupyther Notebook (Python3)

(by) Dmitry Ponyatov <<dponyatov@gmail.com>> 2020

git server: http://192.168.12.34/ponyatov/jupy

- система коллективного сетевого доступа (веб-клиент, без установки ПО на рабочих станциях)
- сервер БД Postgres/PostGis
- интеграция с интранет-сервисами УГМС

service: http://127.0.0.1:8000/

## meteo.kit

github (public EDS only): https://github.com/ponyatov/jupy/tree/public/nb

* @ref frame
* @ref eds
* @ref core

## Install

* https://jupyter.org/hub
* https://jupyterhub.readthedocs.io/en/stable/installation-guide-hard.html

```
$ curl -sL https://deb.nodesource.com/setup_13.x | sudo bash -
$ make install
```
```
$ cd /etc/systemd/system
$ sudo ln -s /home/ponyatov/jupy/etc/systemd/jupyterhub.service jupyterhub.service
$ sudo systemctl daemon-reload
$ sudo systemctl enable jupyterhub.service
$ sudo systemctl start jupyterhub.service
$ sudo systemctl status jupyterhub.service
```

### Postgresql

* https://computingforgeeks.com/install-postgresql-11-on-debian-10-buster/

```
$ wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
# Debian 10 buster
$ echo "deb http://apt.postgresql.org/pub/repos/apt/ buster"-pgdg main | sudo tee /etc/apt/sources.list.d/postgres.list
```
```
$ sudo su - postgres
$ psql -c "alter user postgres with password 'StrongDBPassword'"
```
```
$ sudo su - postgres
$ createuser --pwprompt jupy
$ createdb -O jupy jupy
$ psql -WU postgres -h 127.0.0.1 -d jupy -c "create extension postgis"
$ psql -WU postgres -h 127.0.0.1 -d jupy -c "create extension plpython3u"
```
