# kexp-interview

A webapp to display the tracks played on KEXP in the last hour, and allow
comments to be added, edited, and stored.

## Postgres Database Setup

Comments are stored in a Postgres database; the credentials are set to the
default `postgres` database (under user `postgres`) running on `localhost` and
can be edited in [settings.py](../master/playlist/playlist/settings.py). Database
setup is as follows:

1. Create the database. If using the default `postgres` database, this will be
   done when installing postgres.

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
