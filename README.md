# The Budget

The budget is built using Python + Django, Postgres, Docker Compose.

## Get started

In order to get started, you need to have Docker installed in you dev box.

```
cd django_project
```

From the _django_project_ directory, run the following commands to build the docker image.

```
docker build .
```

After building the image, run the container by using docker-compose

```
docker-compose up
```

You can also switch off the environment by running docker-compose down

```
docker-compose down
```

And you can rebuild after some modification using the command below

```
docker-compose up -d --build
```


Now, in order to run the app it's necessary to run the migrations first so it applies the database schema updates where necessary

Do so by running the command _migrate_

```
docker-compose exec web python manage.py migrate
```

To enable the superuser, then, run the following

```
docker-compose exec web python manage.py createsuperuser
```

### Specifics

In order to update the schema of a specific app inside the project
```
sudo docker-compose exec web python manage.py makemigrations <project_name>
```
Remember to apply this migration in the database after running command. To do so run the _migrate_ command mentioned above.

source ./the_budget_venv/bin/activate
source the_budget_venv/bin/activate