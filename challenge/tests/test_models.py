"""
Unit test for challenge.models
"""

from unittest import TestCase

from challenge import models
from dateutil import parser

DEF_PERSON_ID = 999
DEF_PERSON_NAME = 'Barrett Lambert'
DEF_PERSON_MONGODB_ID = '595eeb9c99c4894033d5d53b'
DEF_PERSON_GUID = '53e2b104-869c-44c2-b200-7f14b403bd89'
DEF_PERSON_ALIVE = True
DEF_PERSON_PICTURE_URL = 'http://placehold.it/32x32'
DEF_PERSON_AGE = 28
DEF_PERSON_EYE_COLOUR = models.EYE_COLOUR_BROWN
DEF_PERSON_GENDER = models.GENDER_MALE
DEF_PERSON_EMAIL = 'barrettlambert@earthmark.com'
DEF_PERSON_PHONE = '+1 (810) 488-2604'
DEF_PERSON_ADDRESS = '618 Sumner Place, Sperryville, Minnesota, 4964'
DEF_PERSON_REG_DATE = '2015-05-02T03:11:16 -10:00'
DEF_PERSON_ABOUT = '''Ut laboris et aliqua est laboris tempor. Non qui ipsum consectetur ex aliquip deserunt 
                            velit consectetur cupidatat consectetur nulla magna. Occaecat duis aliquip consectetur 
                            amet enim cillum enim laboris commodo culpa Lorem elit. Aliquip est qui aliquip laborum 
                            incididunt eu. Nostrud occaecat ad qui ea reprehenderit aute eu exercitation. 
                            Exercitation non pariatur ex sint voluptate deserunt.\r\n'''


class TestCompany(TestCase):
    def setUp(self):
        models.Company.objects.all().delete()

    @staticmethod
    def createCompany(name='moiler'):
        return models.Company.objects.create(name=name)

    def test_createCompany(self):
        company = TestCompany.createCompany()

        self.assertTrue(isinstance(company, models.Company))
        self.assertEqual('moiler', company.name)
        self.assertTrue(company.id > 0)


class TestFood(TestCase):
    def setUp(self):
        models.Food.objects.all().delete()

    @staticmethod
    def createFood(name='radish', food_type=models.FOOD_TYPE_VEGETABLE):
        return models.Food.objects.create(name=name, type=food_type)

    def test_createFood(self):
        food = TestFood.createFood()

        self.assertTrue(isinstance(food, models.Food))
        self.assertEqual('radish', food.name)
        self.assertEqual(models.FOOD_TYPE_VEGETABLE, food.type)
        self.assertTrue(food.id > 0)


class TestPerson(TestCase):
    def setUp(self):
        models.Person.objects.all().delete()
        models.PersonTag.objects.all().delete()

    @staticmethod
    def createPerson(person_id=DEF_PERSON_ID,
                     mongodb_id=DEF_PERSON_MONGODB_ID,
                     guid=DEF_PERSON_GUID, alive=DEF_PERSON_ALIVE,
                     picture_url=DEF_PERSON_PICTURE_URL,
                     age=DEF_PERSON_AGE,
                     eye_colour=DEF_PERSON_EYE_COLOUR,
                     name=DEF_PERSON_NAME,
                     gender=DEF_PERSON_GENDER,
                     employer=None,
                     email=DEF_PERSON_EMAIL,
                     phone=DEF_PERSON_PHONE,
                     address=DEF_PERSON_ADDRESS,
                     about=DEF_PERSON_ABOUT,
                     registration_date=DEF_PERSON_REG_DATE):
        return models.Person.objects.create(id=person_id, mongodb_id=mongodb_id, guid=guid,
                                            name=name, age=age, eye_colour=eye_colour,
                                            is_alive=alive, gender=gender, address=address,
                                            email=email, phone=phone, employer=employer,
                                            about=about, picture_url=picture_url,
                                            registration_date=parser.parse(registration_date))

    def test_createPerson(self):
        person = TestPerson.createPerson()
        self.assertTrue(isinstance(person, models.Person))
        self.assertEqual(DEF_PERSON_ID, person.id)
        self.assertEqual(DEF_PERSON_MONGODB_ID, person.mongodb_id)
        self.assertEqual(DEF_PERSON_GUID, person.guid)
        self.assertEqual(DEF_PERSON_ALIVE, person.is_alive)
        self.assertEqual(DEF_PERSON_PICTURE_URL, person.picture_url)
        self.assertEqual(DEF_PERSON_AGE, person.age)
        self.assertEqual(DEF_PERSON_EYE_COLOUR, person.eye_colour)
        self.assertEqual(DEF_PERSON_NAME, person.name)
        self.assertEqual(DEF_PERSON_GENDER, person.gender)
        self.assertIsNone(person.employer)
        self.assertEqual(DEF_PERSON_EMAIL, person.email)
        self.assertEqual(DEF_PERSON_PHONE, person.phone)
        self.assertEqual(DEF_PERSON_ADDRESS, person.address)
        self.assertEqual(DEF_PERSON_ABOUT, person.about)
        self.assertEqual(parser.parse(DEF_PERSON_REG_DATE), person.registration_date)

    def test_friendRelationship(self):
        person1 = TestPerson.createPerson(person_id=10)
        person2 = TestPerson.createPerson(person_id=20)
        person3 = TestPerson.createPerson(person_id=30)

        person1.friends.add(person2)

        self.assertTrue(person2 in person1.friends.all())
        self.assertFalse(person1 in person1.friends.all())
        self.assertFalse(person3 in person1.friends.all())
        # Relationship should not be symmetrical (according to data file):
        self.assertFalse(person1 in person2.friends.all())

    def test_foodRelationship(self):
        apple = TestFood.createFood(name='Apple', food_type=models.FOOD_TYPE_FRUIT)
        banana = TestFood.createFood(name='Banana', food_type=models.FOOD_TYPE_FRUIT)
        lettuce = TestFood.createFood(name='Lettuce', food_type=models.FOOD_TYPE_VEGETABLE)

        person1 = TestPerson.createPerson(person_id=1)
        person1.favourite_food.add(apple)
        person1.favourite_food.add(banana)
        person2 = TestPerson.createPerson(person_id=2)
        person2.favourite_food.add(apple)
        person2.favourite_food.add(lettuce)

        self.assertEqual({apple, banana}, set(person1.favourite_food.all()))
        self.assertEqual({apple, lettuce}, set(person2.favourite_food.all()))
        self.assertEqual({person1, person2}, set(apple.people.all()))
        self.assertEqual({person1}, set(banana.people.all()))
        self.assertEqual({person2}, set(lettuce.people.all()))

    def test_companyRelationship(self):
        person = TestPerson.createPerson(person_id=4)
        company = TestCompany.createCompany()
        company.employees.add(person)
        self.assertEqual(company, person.employer)

    def test_tagRelationship(self):
        person1 = TestPerson.createPerson(person_id=5)
        person2 = TestPerson.createPerson(person_id=6)
        tag1 = models.PersonTag.objects.create(name='skiing')
        tag2 = models.PersonTag.objects.create(name='gigs')
        tag3 = models.PersonTag.objects.create(name='skiing')

        person1.tags.add(tag1)
        person1.tags.add(tag2)
        person2.tags.add(tag3)

        self.assertEqual([tag1, tag2], list(person1.tags.all()))
        self.assertEqual([tag3], list(person2.tags.all()))
        self.assertEqual({tag1, tag2, tag3}, set(models.PersonTag.objects.all()))
