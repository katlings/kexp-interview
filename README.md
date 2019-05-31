# kexp-interview

A webapp to display the tracks played on KEXP in the last hour, and allow
comments to be added, edited, and stored.

## Requirements

Tested with:
```
Ubuntu 16.04, 18.04
Postgres 9.5, 10.8
Python 3.6.8
Django 1.11
```

## Postgres Database Setup

Comments are stored in a Postgres database; the credentials are set to the
default `postgres` database (under user `postgres`) running on `localhost` and
can be edited in [settings.py](../master/playlist/playlist/settings.py). Database
setup is as follows:

1. Create the database. If using the default `postgres` database, this will be
   done when installing postgres. On Ubuntu, install with
   ```
   sudo apt install postgresql postgresql-server-dev-all
   ```
   To use TCP authentication instead of messing around with Unix users, the
   default uname on Postgres needs a password.
   ```
   $ sudo -u postgres psql
   postgres=# ALTER USER postgres PASSWORD 'pgres';
   ALTER ROLE
   postgres=# \q
   ```

2. Install Python dependencies with
   ```
   pip install -r requirements.txt
   ```
   A [virtualenv](https://virtualenv.pypa.io/en/latest/) is handy.

3. Run Django migrations; this will create the table setup. From the
   [playlist](../master/playlist/) folder, run
   ```
   python manage.py migrate
   ```

## Webapp

Once the database is set up, the Django webapp can be run locally with
```
python manage.py runserver
```
from the [playlist](../master/playlist/) folder. By default, it will
run on `localhost` on port `8000`. The playlist comment feature is mapped to
`http://localhost:8000/playlist/`.

## Testing

Again, once the database is set up, tests can be run with
```
python manage.py test
```
from the [playlist](../master/playlist/) folder.
