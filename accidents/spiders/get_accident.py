# -*- coding: utf-8 -*-

import re

from datetime import datetime
from urlparse import urlparse, urljoin, urlunparse

import scrapy
from dateutil.parser import parse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from accidents.items import Accident, AircraftType, Airline, Airfield, \
    EngineType, Aircraft, Weather, db


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
        print 'url ==== {}'.format(response.url)
        asn_id = re.split(r'record.php\?id=', response.url)[-1]
        with db.transaction():
            accident = Accident.get_or_create(asn_id=asn_id)
            accident.main_url = response.url
            accident.date = self.extract_date(response)
            accident.time = self.extract_typical(response, "Time:",
                                                 datetime.time)

            accident.aircraft = self.extract_aircraft(response)

            url = self.extract_url('Type:', response)
            request = scrapy.Request(url, callback=self.parse_aircraft_type)
            request.meta['item'] = accident
            yield request

            xpath_result = response.xpath("//script[text()[contains(.,'map')]]")
            if (xpath_result):
                request = scrapy.Request("accident geo",
                                         callback=self.parse_accident_geo)
                request['meta'] = accident
                yield request

            accident.damage_type = self.extract_typical(response,
                                                        "Airplane damage:")
            accident.flight_phase = self.extract_typical(response, "Phase:")
            accident.flight_nature = self.extract_typical(response, "Nature:")

            accident.asn_dep_airfield = self.extract_typical(response,
                                                             "Registration:")
            accident.asn_dest_airfield = self.extract_typical(response,
                                                              "Registration:")

            # dep_metar_string = self.extract_typical(response, "Registration:")
            # accident.dep_weather = self.extract_weather(dep_metar_string)
            #
            # dest_metar_string = self.extract_typical(response, "Registration:")
            # accident.dest_weather = self.extract_weather(dest_metar_string)

            # accident.save()

    def extract_url(self, parsed_row_name, response):
        try:
            parsed_url = urlparse(response.url)
            aircraft_type_url = self.extract_typical(response, parsed_row_name,
                                                     lambda x:
                                                     re.findall(r'href="(.+?)"',
                                                                x[0])[0])
            url = urlunparse((parsed_url.scheme, parsed_url.netloc,
                              aircraft_type_url, '', '', None))
            return url
        except:
            return ''

    def extract_date(self, response):
        date_text = response.xpath(
            "//tr[td='Date:']/td[2]/text()").extract()[0].strip(' x')
        if (date_text.strip() == 'date unk.'):
            typical = None
        else:
            typical = self.extract_typical(response, "Date:",
                                           lambda x: parse(x[0].strip(' x')))
        return typical

    def extract_aircraft(self, response):
        aircraft = Aircraft()
        aircraft.registration = self.extract_typical(response, "Registration:")
        aircraft.model_serial_number = self.extract_typical(
            response, "C/n / msn:")
        aircraft.asn_aircraft_type = self.extract_typical(
            response, "Type:",
            lambda x: re.findall(r'types\/(.+?)\/index"', x)[-1])
        aircraft.first_flight_date = self.extract_typical(
            response, "First flight:", lambda x: parse((x[0].split()[0])))

        number_string = self.extract_typical(response, "Engines:")
        aircraft.engines_number = int(number_string) if number_string else None

        aircraft.asn_engine_type = self.extract_typical(
            response, "Engines:",
            lambda x: re.findall(r'engine\/(.+?)\"', x[-1])[0])
        return aircraft

    def parse_accident_geo(selfself, response):
        id = re.split(r'php\?id=', response.url)[-1]
        dep = Airfield.get_or_create(asn_id=id)
        parameter = 'Departure airport'
        xpath_result = response.xpath(
            "//Placemark[name='%s']/Lookat/node()" % parameter).extract()
        dep = Airfield.get_or_create()

        i = Accident.get_or_create(id=id)
        # i.lat = self.extract_typical(response, "Registration:")
        #i.long = self.extract_typical(response, "Registration:")


        return None

    def extract_weather(self, response):
        dep_weather = Weather()
        dep_weather.wind_speed_ff_ms = self.extract_typical(response,
                                                            "Registration:")
        dep_weather.wind_direction_ddd = self.extract_typical(response,
                                                              "Registration:")
        dep_weather.vi.i.y_VVVV = self.extract_typical(response,
                                                       "Registration:")
        dep_weather.VPP_vi.i.y_VrVrVrVr = self.extract_typical(response,
                                                               "Registration:")
        dep_weather.weather = self.extract_typical(response, "Registration:")
        dep_weather.cloudy = self.extract_typical(response, "Registration:")
        dep_weather.temperature_cs = self.extract_typical(response,
                                                          "Registration:")
        dep_weather.dewpoint = self.extract_typical(response, "Registration:")
        dep_weather.VPP = self.extract_typical(response, "Registration:")
        return dep_weather

    def extract_typical(self, response, parameter, proceed=lambda x: x[0]):
        try:
            xpath_result = response.xpath(
                "//tr[td='%s']/td[2]/node()" % parameter).extract()
            return None if not xpath_result else self.method_name(proceed,
                                                                  xpath_result)
        except Exception as ex:
            print ex
            return None

    def method_name(self, proceed, xpath_result):
        proceed1 = proceed(xpath_result)
        strip = proceed1
        return strip

    def parse_aircraft_type(self, response):
        i = AircraftType()
        try:
            i.asn_id = response.xpath('//input[@id="sid"]/@value').extract()
            i.ICAO = response.xpath('//input[@id="sid"]/@value').extract()
            i.first_flight_date = response.xpath(
                '//input[@id="sid"]/@value').extract()
            i.production_total = response.xpath(
                '//input[@id="sid"]/@value').extract()
            i.ICAO_mass_group = response.xpath(
                '//input[@id="sid"]/@value').extract()
        finally:
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
