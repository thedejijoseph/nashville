
"""
Data Writer

Simple script to write fetched data into a database (postgres)

Project Nashville is setup to answer one question with the help of interactive
data visualisation: what are the most expensive areas to live in Lagos?
"""

import json

from peewee import Model, PostgresqlDatabase
from peewee import AutoField, IntegerField, TextField, ForeignKeyField
from peewee import chunked

from environs import Env

env = Env()
env.read_env()


DATABASE_NAME = env('DB_NAME')
USER = env('DB_USER')
PASSWORD = env('DB_PASSWORD')
HOST = env('DB_HOST')
PORT = env('DB_PORT')

# connect to the database
db = PostgresqlDatabase(
    database=DATABASE_NAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    # sslmode='require'
)

class ApartmentModel(Model):
    serial_id = AutoField(primary_key=True)

    slug = TextField(unique=True)

    property_size = IntegerField(null=True)
    property_size_unit = TextField(null=True)
    furnished = TextField(null=True)
    bedrooms = IntegerField(null=True)
    bathrooms = IntegerField(null=True)
    price = IntegerField(null=True)
    period_raw = TextField(null=True)
    period = TextField(null=True)
    region_text = TextField(null=True)
    region = TextField(null=True)
    region_parent = TextField(null=True)
    state = TextField(null=True)
    description = TextField(null=True)
    title = TextField(null=True)
    url = TextField(null=True)
    status = TextField(null=True)
    category = TextField(null=True)

    class Meta:
        database = db
        db_table = 'apartments'

class ImageModel(Model):
    serial_id = AutoField(primary_key=True)

    apartment_id = ForeignKeyField(ApartmentModel, backref='images')
    url = TextField(null=True)

    class Meta:
        database = db
        db_table = 'images'


# connect to the database and create the table (if not exists)
# db.connect()
ApartmentModel.create_table(fail_silently=True)
ImageModel.create_table(fail_silently=True)


def insert_apartment(apartment):
    # insert a single apartment
    with db.atomic():
        new_apartment = ApartmentModel.insert(**apartment).execute()
    return new_apartment

def insert_many_apartments(apartments):
    # insert manay apartments at once
    with db.atomic():
        many_apartments = ApartmentModel.insert_many(apartments).execute()
    return many_apartments

def insert_all_apartments(all_apartments):
    # insert all apartments
    with db.atomic():
        for batch in chunked(all_apartments, 100):
            ApartmentModel.insert_many(batch).execute()
    return



def close_db():
    # close the database connection
    db.close()

