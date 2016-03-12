# -*- coding: utf-8 -*-

import re

from dateutil.parser import parse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from accidents.items import Accident, AircraftType, Airline, Airfield, \
    EngineType, Aircraft, Weather


class GetAccidentSpider(CrawlSpider):
    name = 'get_accident'
    allowed_domains = ['aviation-safety.net']
    start_urls = ['https://aviation-safety.net/database/']

    rules = (
        Rule(LinkExtractor(allow=r'dblist\.php\?Year='), follow=True),
        Rule(LinkExtractor(allow=r'database\/types\/.+\/index'), follow=True),
        Rule(LinkExtractor(allow=r'database\/types\/.+\/specs'),
             callback='parse_aircraft', follow=False),
        Rule(LinkExtractor(allow=r'record\.php\?id='),
             callback='parse_accident', follow=True),
        Rule(LinkExtractor(allow=r'operator\/airline.php\?var='),
             callback='parse_airline', follow=False),
        Rule(LinkExtractor(allow=r'airport\/airport\.php\?id='),
             callback='parse_airfield', follow=False),
        Rule(LinkExtractor(allow=r'\/engine'), callback='parse_engine',
             follow=False),
    )

    def parse_accident(self, response):
        i = Accident()

        i.asn_id = re.split(r'record.php\?id=', response.url)[-1]
        date_text = response.xpath(
            "//tr[td='Date:']/td[2]/text()").extract()[0]
        if (date_text.strip() == 'date unk.'):
            return
        i.date = parse(date_text)
        i.time = response.xpath('//input[@id="sid"]/@value').extract()

        # extract aircraft
        aircraft = Aircraft()
        i.registration = response.xpath('//input[@id="sid"]/@value').extract()
        i.model_serial_number = response.xpath(
            '//input[@id="sid"]/@value').extract()
        i.asn_aircraft_type = response.xpath(
            '//input[@id="sid"]/@value').extract()
        i.first_flight_date = response.xpath(
            '//input[@id="sid"]/@value').extract()
        i.engines_number = response.xpath('//input[@id="sid"]/@value').extract()
        i.asn_engine_type = response.xpath(
            '//input[@id="sid"]/@value').extract()

        i.aircraft = aircraft
        i.damage_type = response.xpath('//input[@id="sid"]/@value').extract()
        i.lat = response.xpath('//input[@id="sid"]/@value').extract()
        i.long = response.xpath('//input[@id="sid"]/@value').extract()
        i.flight_phase = response.xpath('//input[@id="sid"]/@value').extract()
        i.asn_dep_airfield = response.xpath(
            '//input[@id="sid"]/@value').extract()

        dep_weather = Weather()
        i.wind_speed_ff_ms = response.xpath(
            '//input[@id="sid"]/@value').extract()
        i.wind_direction_ddd = response.xpath(
            '//input[@id="sid"]/@value').extract()
        i.vi.i.y_VVVV = response.xpath('//input[@id="sid"]/@value').extract()
        i.VPP_vi.i.y_VrVrVrVr = response.xpath(
            '//input[@id="sid"]/@value').extract()
        i.weather = response.xpath('//input[@id="sid"]/@value').extract()
        i.cloudy = response.xpath('//input[@id="sid"]/@value').extract()
        i.temperature_cs = response.xpath('//input[@id="sid"]/@value').extract()
        i.dewpoint = response.xpath('//input[@id="sid"]/@value').extract()
        i.VPP = response.xpath('//input[@id="sid"]/@value').extract()
        i.dep_weather = dep_weather

        dest_weather = Weather()
        i.wind_speed_ff_ms = response.xpath(
            '//input[@id="sid"]/@value').extract()
        i.wind_direction_ddd = response.xpath(
            '//input[@id="sid"]/@value').extract()
        i.vi.i.y_VVVV = response.xpath('//input[@id="sid"]/@value').extract()
        i.VPP_vi.i.y_VrVrVrVr = response.xpath(
            '//input[@id="sid"]/@value').extract()
        i.weather = response.xpath('//input[@id="sid"]/@value').extract()
        i.cloudy = response.xpath('//input[@id="sid"]/@value').extract()
        i.temperature_cs = response.xpath('//input[@id="sid"]/@value').extract()
        i.dewpoint = response.xpath('//input[@id="sid"]/@value').extract()
        i.VPP = response.xpath('//input[@id="sid"]/@value').extract()

        i.asn_dest_airfield = response.xpath(
            '//input[@id="sid"]/@value').extract()
        i.dest_weather = dest_weather

        i.save()
        return i

    def parse_aircraft_type(self, response):
        i = AircraftType()
        i.asn_id = response.xpath('//input[@id="sid"]/@value').extract()
        i.ICAO = response.xpath('//input[@id="sid"]/@value').extract()
        i.first_flight_date = response.xpath(
            '//input[@id="sid"]/@value').extract()
        i.production_total = response.xpath(
            '//input[@id="sid"]/@value').extract()
        i.ICAO_mass_group = response.xpath(
            '//input[@id="sid"]/@value').extract()

        return i

    def parse_airline(self, response):
        i = Airline()
        i.isn_id = response.xpath('//input[@id="sid"]/@value').extract()
        i.name = response.xpath('//input[@id="sid"]/@value').extract()
        i.country = response.xpath('//input[@id="sid"]/@value').extract()
        i.ICAO = response.xpath('//input[@id="sid"]/@value').extract()
        i.IATA = response.xpath('//input[@id="sid"]/@value').extract()
        i.founded = response.xpath('//input[@id="sid"]/@value').extract()
        i.ended = response.xpath('//input[@id="sid"]/@value').extract()
        return i

    def parse_airfield(self, response):
        i = Airfield()
        i.isn_id = response.xpath('//input[@id="sid"]/@value').extract()
        i.name = response.xpath('//input[@id="sid"]/@value').extract()
        i.ICAO = response.xpath('//input[@id="sid"]/@value').extract()
        i.IATA = response.xpath('//input[@id="sid"]/@value').extract()
        i.lat = response.xpath('//input[@id="sid"]/@value').extract()
        i.long = response.xpath('//input[@id="sid"]/@value').extract()
        return i

    def parse_engine(self, response):
        i = EngineType()
        i.model_name = response.xpath('//input[@id="sid"]/@value').extract()
        i.country = response.xpath('//input[@id="sid"]/@value').extract()
        i.developed = response.xpath('//input[@id="sid"]/@value').extract()
        i.type = response.xpath('//input[@id="sid"]/@value').extract()
