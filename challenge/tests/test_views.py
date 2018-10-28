"""
Unit test for challenge.views
"""

from unittest import TestCase
from django.test import Client
from django import urls
import json
from challenge import models

from challenge.dataconversion import json_converter
from challenge.tests import test_data


class _BaseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        models.Company.objects.all().delete()
        models.PersonTag.objects.all().delete()
        models.Food.objects.all().delete()
        models.Person.objects.all().delete()


class TestAllEmployeesOfCompanyView(_BaseViewTest):
    def setUp(self):
        _BaseViewTest.setUp(self)
        person_obj = json_converter.create_person(test_data.TEST_PERSON_RECORD1)
        json_converter.create_company(test_data.TEST_COMPANY_RECORD)
        json_converter.associate_person_and_company(person_obj, test_data.TEST_PERSON_RECORD1)

    def test_get_happy_path_by_id(self):
        response = self.client.get(urls.reverse('company_employees', args=(4,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual({"errorMsg": "", "results": [{"id": 364, "name": "Eaton Schneider"}]},
                         json.loads(response.content.decode("utf-8")))

    def test_get_happy_path_by_name(self):
        response = self.client.get(urls.reverse('company_employees', args=('BUGSALL',)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual({"errorMsg": "", "results": [{"id": 364, "name": "Eaton Schneider"}]},
                         json.loads(response.content.decode("utf-8")))

    def test_get_unrecognised_company(self):
        response = self.client.get(urls.reverse('company_employees', args=('MOILER',)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'errorMsg': 'Unable to find a Company with ID or name of MOILER',
                          'results': []}, json.loads(response.content.decode("utf-8")))


class TestFriendsInCommonView(_BaseViewTest):
    def setUp(self):
        _BaseViewTest.setUp(self)
        person1_obj = json_converter.create_person(test_data.TEST_PERSON_RECORD1)
        person2_obj = json_converter.create_person(test_data.TEST_PERSON_RECORD2)
        _person3_obj = json_converter.create_person(test_data.TEST_PERSON_RECORD3)
        json_converter.associate_person_with_friends(person1_obj, test_data.TEST_PERSON_RECORD1)
        json_converter.associate_person_with_friends(person2_obj, test_data.TEST_PERSON_RECORD2)

    def test_get_happy_path_by_person_ids(self):
        response = self.client.get(urls.reverse('common_friends', args=('364/0',)), {'eye_colour': 'BR',
                                                                                     'is_alive': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual({"errorMsg": "",
                          "results": {"friends": [{"id": 1, "name": "Decker Mckenzie"}],
                                      "people": [{"phone": "+1 (946) 403-2062",
                                                  "address": "195 Hazel Court, Goldfield, Kentucky, 8502",
                                                  "age": 54, "name": "Eaton Schneider"},
                                                 {"phone": "+1 (910) 567-3630",
                                                  "address": "628 Sumner Place, Sperryville, American Samoa, 9819",
                                                  "age": 61, "name": "Carmella Lambert"}]}},
                         json.loads(response.content.decode("utf-8")))




    def test_get_happy_path_by_person_name(self):
        response = self.client.get(urls.reverse('common_friends', args=('Eaton Schneider/0',)), {'eye_colour': 'BR',
                                                                                                   'is_alive': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual({"errorMsg": "",
                          "results": {"friends": [{"id": 1, "name": "Decker Mckenzie"}],
                                      "people": [{"phone": "+1 (946) 403-2062",
                                                  "address": "195 Hazel Court, Goldfield, Kentucky, 8502",
                                                  "age": 54, "name": "Eaton Schneider"},
                                                 {"phone": "+1 (910) 567-3630",
                                                  "address": "628 Sumner Place, Sperryville, American Samoa, 9819",
                                                  "age": 61, "name": "Carmella Lambert"}]}},
                         json.loads(response.content.decode("utf-8")))

    def test_get_unrecognised_person(self):
        response = self.client.get(urls.reverse('common_friends', args=('Cheggars/0',)), {'eye_colour': 'BR',
                                                                                                   'is_alive': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'errorMsg': 'Unable to find a Person with ID or name of Cheggars',
                          'results': {'friends': [], 'people': []}},
                         json.loads(response.content.decode("utf-8")))

    def test_get_unrecognised_query_param(self):
        response = self.client.get(urls.reverse('common_friends', args=('364/0',)), {'eye_colour': 'BR',
                                                                                     'ethical_person': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'errorMsg': 'Invalid query, please check query parameters',
                          'results': {'friends': [], 'people': []}},
                         json.loads(response.content.decode("utf-8")))


class TestFavouriteFoodView(_BaseViewTest):
    def setUp(self):
        _BaseViewTest.setUp(self)
        person1_obj = json_converter.create_person(test_data.TEST_PERSON_RECORD1)
        json_converter.associate_person_and_food(person1_obj, test_data.TEST_PERSON_RECORD1)

    def test_get_happy_path_by_person_id(self):
        response = self.client.get(urls.reverse('favourite_food', args=(364, )))
        self.assertEqual(response.status_code, 200)
        resulting_json = json.loads(response.content.decode("utf-8"))
        # Check fruit and veg individually as order cannot be guaranteed
        self.assertEqual({'apple', 'banana'}, set(resulting_json.pop('fruits')))
        self.assertEqual({'celery', 'cucumber'}, set(resulting_json.pop('vegetables')))
        # Now check the rest
        self.assertEqual({'age': 54,'username': 'eatonschneider@earthmark.com'}, resulting_json)

    def test_get_happy_path_by_person_name(self):
        response = self.client.get(urls.reverse('favourite_food', args=('Eaton Schneider', )))
        self.assertEqual(response.status_code, 200)
        resulting_json = json.loads(response.content.decode("utf-8"))
        # Check fruit and veg individually as order cannot be guaranteed
        self.assertEqual({'apple', 'banana'}, set(resulting_json.pop('fruits')))
        self.assertEqual({'celery', 'cucumber'}, set(resulting_json.pop('vegetables')))
        # Now check the rest
        self.assertEqual({'age': 54,'username': 'eatonschneider@earthmark.com'}, resulting_json)

    def test_get_unrecognised_person(self):
        response = self.client.get(urls.reverse('favourite_food', args=('Boycee', )))
        self.assertEqual(response.status_code, 200)
        self.assertEqual({}, json.loads(response.content.decode("utf-8")))
