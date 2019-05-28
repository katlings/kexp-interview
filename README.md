# kexp-interview

A webapp to display the tracks played on KEXP in the last hour, and allow
comments to be added, edited, and stored.

## Postgres Database Setup

Comments are stored in a Postgres database; the credentials are set to the
default `postgres` database (under user `postgres`) running on `localhost` and
can be edited in [settings.py](../blob/master/playlist/settings.py). Database
setup is as follows:

1. Create the database. If using the default `postgres` database, this will be
   done when installing postgres.

2. Run Django migrations; this will create the table setup. From the
   [playlist](../blob/master/playlist/) folder, run

   ```
   python manage.py migrate
   ```

## Webapp

Once the database is set up, the Django webapp can be run locally with

```
python manage.py runserver
```

By default, it will run on localhost at port 8000. The playlist comment
feature is mapped to `http://localhost:8000/playlist/`.

