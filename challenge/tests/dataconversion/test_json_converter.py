"""
Unit test for challenge.dataconversion.json_converter
"""

from unittest import TestCase
from dateutil import parser

from challenge import models
import challenge.dataconversion.json_converter as json_converter
from challenge.tests import test_data


class TestConversion(TestCase):
    def setUp(self):
        models.Company.objects.all().delete()
        models.PersonTag.objects.all().delete()
        models.Food.objects.all().delete()
        models.Person.objects.all().delete()

    def test_create_company(self):
        obj = json_converter.create_company(test_data.TEST_COMPANY_RECORD)

        saved_obj = models.Company.objects.get(pk=4)

        self.assertIsInstance(obj, models.Company)
        self.assertEqual(4, obj.id)
        self.assertEqual('BUGSALL', obj.name)
        self.assertEqual(obj, saved_obj)

    def test_create_person(self):
        obj = json_converter.create_person(test_data.TEST_PERSON_RECORD1)

        saved_obj = models.Person.objects.get(pk=364)

        self.assertIsInstance(obj, models.Person)
        self.assertEqual(364, obj.id)
        self.assertEqual('595eeb9cdc0ce518cab8cbcf', obj.mongodb_id)
        self.assertEqual('c38970e7-343f-4389-bc51-819092ae09b4', obj.guid)

        self.assertEqual('Eaton Schneider', obj.name)
        self.assertEqual(54, obj.age)
        self.assertTrue(obj.is_alive)
        self.assertEqual(models.GENDER_MALE, obj.gender)
        self.assertEqual(models.EYE_COLOUR_BROWN, obj.eye_colour)

        self.assertEqual('195 Hazel Court, Goldfield, Kentucky, 8502', obj.address)
        self.assertEqual('eatonschneider@earthmark.com', obj.email)
        self.assertEqual('+1 (946) 403-2062', obj.phone)

        self.assertEqual("Sit labore ad et tempor labore anim officia pariatur eiusmod ullamco reprehenderit. Nisi excepteur dolore officia quis eiusmod irure id non. Aliqua et excepteur eiusmod nostrud laboris et. Elit in elit magna qui. Reprehenderit culpa enim cillum cupidatat excepteur laboris excepteur ullamco et ad. Ipsum laboris voluptate cupidatat sunt nulla dolor.\r\n",
                         obj.about)
        self.assertEqual('http://placehold.it/32x32', obj.picture_url)

        self.assertEqual(parser.parse('2015-07-14T07:39:45 -10:00'), obj.registration_date)

    def test_associate_person_and_company(self):
        person_obj = json_converter.create_person(test_data.TEST_PERSON_RECORD1)
        company_obj = json_converter.create_company(test_data.TEST_COMPANY_RECORD)

        # Sanity checks
        self.assertIsNone(person_obj.employer)
        self.assertEqual([], list(company_obj.employees.all()))

        json_converter.associate_person_and_company(person_obj, test_data.TEST_PERSON_RECORD1)

        self.assertEqual(company_obj, person_obj.employer)
        self.assertEqual({person_obj}, set(company_obj.employees.all()))

    def test_associate_person_and_company_which_deosnt_exist(self):
        person_record_copy = test_data.TEST_PERSON_RECORD1.copy()
        person_record_copy[json_converter.FIELD_PERSON_ID] = '9999999'
        person_record_copy[json_converter.FIELD_PERSON_COMPANY] ='9999999'

        person_obj = json_converter.create_person(person_record_copy)

        json_converter.associate_person_and_company(person_obj, person_record_copy)

        self.assertIsNone(person_obj.employer)

    def test_associate_person_with_friends(self):
        person_obj1 = json_converter.create_person(test_data.TEST_PERSON_RECORD1)
        person_obj2 = json_converter.create_person(test_data.TEST_PERSON_RECORD2)
        person_obj3 = json_converter.create_person(test_data.TEST_PERSON_RECORD3)

        json_converter.associate_person_with_friends(person_obj1, test_data.TEST_PERSON_RECORD1)
        json_converter.associate_person_with_friends(person_obj2, test_data.TEST_PERSON_RECORD2)
        json_converter.associate_person_with_friends(person_obj3, test_data.TEST_PERSON_RECORD3)

        self.assertEqual({person_obj2, person_obj3}, set(person_obj1.friends.all()))
        self.assertEqual({person_obj3}, set(person_obj2.friends.all()))
        self.assertEqual(set(), set(person_obj3.friends.all()))

    def test_associate_person_and_tags(self):
        person_obj = json_converter.create_person(test_data.TEST_PERSON_RECORD1)
        json_converter.associate_person_and_tags(person_obj, test_data.TEST_PERSON_RECORD1)

        self.assertEqual({"pariatur", "proident", "culpa", "ex", "proident", "in", "sint"},
                         set([tag.name for tag in person_obj.tags.all()]))

    def test_associate_person_and_food(self):
        person_obj = json_converter.create_person(test_data.TEST_PERSON_RECORD1)
        json_converter.associate_person_and_food(person_obj, test_data.TEST_PERSON_RECORD1)

        self.assertEqual({"cucumber", "banana", "apple", "celery"},
                         set([food.name for food in person_obj.favourite_food.all()]))
