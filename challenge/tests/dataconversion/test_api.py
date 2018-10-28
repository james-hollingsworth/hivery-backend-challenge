"""
Unit test for challenge.dataconversion.api
"""

from unittest import TestCase

import challenge.dataconversion.json_converter as json_converter
from challenge import models
from challenge.dataconversion import api
from challenge.tests import test_data


class TestApi(TestCase):
    def setUp(self):
        models.Company.objects.all().delete()
        models.PersonTag.objects.all().delete()
        models.Food.objects.all().delete()
        models.Person.objects.all().delete()
        self.company_obj1 = json_converter.create_company(test_data.TEST_COMPANY_RECORD)
        self.person_obj1 = json_converter.create_person(test_data.TEST_PERSON_RECORD1)
        self.person_obj2 = json_converter.create_person(test_data.TEST_PERSON_RECORD2)
        json_converter.associate_person_and_food(self.person_obj1, test_data.TEST_PERSON_RECORD1)
        json_converter.associate_person_and_food(self.person_obj2, test_data.TEST_PERSON_RECORD2)

    def test_base_serializer(self):
        class MockSerializer(api.BaseSerializer):
            def _serialize_results(self):
                return {'test'}

        ms = MockSerializer('error!')
        self.assertEqual({'results': {'test'}, 'errorMsg': 'error!'}, ms.to_json())

    def test_summary_people_serializer(self):
        serializer = api.SummaryPeopleSerializer([self.person_obj1], 'no error')
        self.assertEqual({'results': [{'id': 364, 'name': 'Eaton Schneider'}], 'errorMsg': 'no error'},
                         serializer.to_json())

    def test_friends_in_common_serializer(self):
        serializer = api.FriendsInCommonSerializer([self.person_obj1], [self.person_obj2], 'all good')
        self.assertEqual({'results': {'friends': [{'id': 0, 'name': 'Carmella Lambert'}],
                                      'people': [{'address': '195 Hazel Court, Goldfield, Kentucky, 8502',
                                                  'age': 54, 'name': 'Eaton Schneider','phone': '+1 (946) 403-2062'}]},
                                      'errorMsg': 'all good'},  serializer.to_json())

    def test_favourite_fruit_serializer(self):
        serializer = api.FavouriteFruitSerializer(self.person_obj1)
        resulting_json = serializer.to_json()
        # Check fruit and veg individually as order cannot be guaranteed
        self.assertEqual({'apple', 'banana'}, set(resulting_json.pop('fruits')))
        self.assertEqual({'celery', 'cucumber'}, set(resulting_json.pop('vegetables')))
        # Now check the rest
        self.assertEqual({'age': 54,'username': 'eatonschneider@earthmark.com'}, resulting_json)




