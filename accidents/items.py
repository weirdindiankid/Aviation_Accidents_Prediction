# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from peewee import Model, CharField, DateField, TimeField, ForeignKeyField, \
    DecimalField, IntegerField, PostgresqlDatabase

COORDINATES_LENGTH = 9
COORDINATES_DECIMAL = 6

db = PostgresqlDatabase('accidents',  # Required by Peewee.
                        user='bars_web_bb',
                        # Will be passed directly to psycopg2.
                        password='bars_web_bb',
                        host='localhost', )


class Airfield(Model):
    asn_id = CharField(20)
    name = CharField(100)
    ICAO = CharField(6)
    IATA = CharField(6)
    lat = DecimalField(max_digits=COORDINATES_LENGTH,
                       decimal_places=COORDINATES_DECIMAL)
    long = DecimalField(max_digits=COORDINATES_LENGTH,
                        decimal_places=COORDINATES_DECIMAL)

    class Meta:
        database = db


class Airline(Model):
    asn_id = CharField(20)
    name = CharField(100)
    country = CharField(30)
    ICAO = CharField(6)
    IATA = CharField(6)
    founded = DateField()
    ended = DateField()

    class Meta:
        database = db


class Weather(Model):
    wind_speed_ff_ms = IntegerField()
    wind_direction_ddd = DecimalField(max_digits=3, decimal_places=0)
    visibility_VVVV = IntegerField()
    VPP_visibility_VrVrVrVr = IntegerField()
    weather = CharField(20)
    cloudy = CharField(20)
    temperature_cs = IntegerField()
    dewpoint = IntegerField()
    VPP = CharField(20)

    class Meta:
        database = db


class EngineType(Model):
    model_name = CharField(100)
    country = CharField(30)
    developed = DateField()
    type = CharField(30)

    class Meta:
        database = db


class AircraftType(Model):
    asn_id = CharField(20)
    ICAO = CharField(20)
    first_flight_date = DateField()
    production_total = IntegerField()
    ICAO_mass_group = CharField(5)

    class Meta:
        database = db


class Aircraft(Model):
    registration = CharField(20)
    model_serial_number = CharField(20)
    aircraft_type = ForeignKeyField(AircraftType, related_name='aircrafts',
                                    null=True)
    asn_aircraft_type = CharField(20)
    first_flight_date = DateField()
    total_airframe_hours = IntegerField()
    engines_number = IntegerField()
    engine_type = ForeignKeyField(EngineType, related_name='aircrafts',
                                  null=True)
    asn_engine_type = CharField(20)

    class Meta:
        database = db


class Accident(Model):
    asn_id = CharField(20)
    date = DateField()
    time = TimeField()
    aircraft = ForeignKeyField(Aircraft, related_name='accidents')
    damage_type = CharField(max_length=100)
    lat = DecimalField(max_digits=COORDINATES_LENGTH,
                       decimal_places=COORDINATES_DECIMAL)
    long = DecimalField(max_digits=COORDINATES_LENGTH,
                        decimal_places=COORDINATES_DECIMAL)
    flight_phase = CharField()
    dep_airfield = ForeignKeyField(Airfield, related_name='dep_accidents')
    asn_dep_airfield = CharField(20)
    dep_weather = ForeignKeyField(Weather, related_name='department_accident')
    dest_airfield = ForeignKeyField(Airfield, related_name='dest_accidents')
    asn_dest_airfield = CharField(20)
    dest_weather = ForeignKeyField(Weather, related_name='destination_accident')

    class Meta:
        database = db


db.connect()

Airfield.create_table(True)
EngineType.create_table(True)
Weather.create_table(True)
AircraftType.create_table(True)
Airline.create_table(True)
Aircraft.create_table(True)
Accident.create_table(True)
