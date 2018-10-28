"""
Management command to load company and person data sets from supplied json
files into the system database
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import challenge.dataconversion.json_converter as json_converter
import json
import logging

from challenge import models

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    For loading json from the file we will use the standard json library.

    This is fine for the current dataset but in order to scale to a larger
    dataset we would need to read the file in a streamed fashion one
    record at a time.  E.g. using a library such as ijson
    """

    RESOURCE_DIR = os.path.join(settings.BASE_DIR, 'resources')
    COMPANIES_FILE = os.path.join(RESOURCE_DIR, 'companies.json')
    PEOPLE_FILE = os.path.join(RESOURCE_DIR, 'people.json')

    def handle(self, *args, **options):
        """
        Command entry point
        :param args:
        :param options:
        :return:
        """
        self._clean_existing_data()

        LOGGER.info('IMPORTING company data')
        with open(Command.COMPANIES_FILE) as companies_file:
            self._process_companies(json.load(companies_file))
        LOGGER.info('COMPLETED company import')

        LOGGER.info('IMPORTING people data')
        with open(Command.PEOPLE_FILE) as people_file:
            # NOTE: Not scalable - a large json file could exhaust available memory:
            self._process_people(json.load(people_file))

        LOGGER.info('COMPLETED people import')

    @staticmethod
    def _clean_existing_data():
        LOGGER.info('CLEANING existing data before import')
        models.PersonTag.objects.all().delete()
        models.Food.objects.all().delete()
        models.Company.objects.all().delete()
        models.Person.objects.all().delete()
        LOGGER.info('CLEANING completed')

    @staticmethod
    def _process_companies(companies_json):
        for company_json in companies_json:
            json_converter.create_company(company_json)

    @staticmethod
    def _process_people(people_json):
        for person_json in people_json:
            obj = json_converter.create_person(person_json)
            json_converter.associate_person_and_company(obj, person_json)
            json_converter.associate_person_and_tags(obj, person_json)
            json_converter.associate_person_and_food(obj, person_json)
            obj.save()

        # Second loop to associate people with friends once
        # objects are written
        for person_json in people_json:
            obj = json_converter.get_person(person_json)
            json_converter.associate_person_with_friends(obj, person_json)
