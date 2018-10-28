"""
Converts an input data source in json format
to internal data model
"""

import functools
import logging
from dateutil import parser

import challenge.models as models

LOGGER = logging.getLogger(__name__)

# Define field names as they appear in the input data source
FIELD_COMPANY_ID = 'index'
FIELD_COMPANY_NAME = 'company'
FIELD_PERSON_MONGODB_ID = '_id'
FIELD_PERSON_ID = 'index'
FIELD_PERSON_GUID = 'guid'
FIELD_PERSON_HAS_DIED = 'has_died'
FIELD_PERSON_BALANCe = 'balance'
FIELD_PERSON_PICTURE = 'picture'
FIELD_PERSON_AGE = 'age'
FIELD_PERSON_EYE_COLOUR = 'eyeColor'
FIELD_PERSON_NAME = 'name'
FIELD_PERSON_GENDER = 'gender'
FIELD_PERSON_COMPANY = 'company_id'
FIELD_PERSON_EMAIL = 'email'
FIELD_PERSON_PHONE = 'phone'
FIELD_PERSON_ADDRESS = 'address'
FIELD_PERSON_ABOUT = 'about'
FIELD_PERSON_REGISTERED = 'registered'
FIELD_PERSON_TAGS = 'tags'
FIELD_PERSON_FRIENDS = 'friends'
FIELD_PERSON_FOOD = 'favouriteFood'

GENDER_LOOKUP = {
    'male': models.GENDER_MALE,
    'female': models.GENDER_FEMALE
}

EYE_COLOUR_LOOKUP = {
    'brown': models.EYE_COLOUR_BROWN,
    'blue': models.EYE_COLOUR_BLUE,
    'green': models.EYE_COLOUR_GREEN,
    'grey': models.EYE_COLOUR_GREY,
    'albino': models.EYE_COLOUR_ALBINO
}

ALL_KNOWN_FRUIT = {'apple', 'strawberry', 'orange', 'banana'}

ALL_KNOWN_VEGETABLES = {'celery', 'beetroot', 'carrot', 'cucumber'}


def create_company(company_json):
    """
    Does what it says on the tin..
    :param company_json: A single company json record previously read from input data source
    :return: Created Company object
    """
    LOGGER.info('CREATING company with id={0}'.format(company_json[FIELD_COMPANY_ID]))
    company = models.Company(id=company_json[FIELD_COMPANY_ID], name=company_json[FIELD_COMPANY_NAME])
    company.save()
    return company


def create_person(person_json):
    """
    Does what it says on the tin..
    :param person_json: A single person json record  previously read from input data source
    :return: Created Person object
    """
    LOGGER.info('CREATING person with id={0}'.format(person_json[FIELD_PERSON_ID]))
    person = models.Person()

    person.id = person_json[FIELD_PERSON_ID]
    person.mongodb_id = person_json[FIELD_PERSON_MONGODB_ID]
    person.guid = person_json[FIELD_PERSON_GUID]

    person.name = person_json[FIELD_PERSON_NAME]
    person.age = person_json[FIELD_PERSON_AGE]
    person.is_alive = not person_json[FIELD_PERSON_HAS_DIED]
    person.gender = GENDER_LOOKUP.get(person_json[FIELD_PERSON_GENDER].lower(), models.GENDER_OTHER)
    person.eye_colour = EYE_COLOUR_LOOKUP.get(person_json[FIELD_PERSON_EYE_COLOUR].lower(), models.EYE_COLOUR_OTHER)

    person.address = person_json[FIELD_PERSON_ADDRESS]
    person.email = person_json.get(FIELD_PERSON_EMAIL)
    person.phone = person_json.get(FIELD_PERSON_PHONE)

    person.about = person_json[FIELD_PERSON_ABOUT]
    person.picture_url = person_json[FIELD_PERSON_PICTURE]

    person.registration_date = parser.parse(person_json[FIELD_PERSON_REGISTERED])

    person.save()
    return person


def associate_person_and_company(person_obj, person_json):
    """
    Does what it says on the tin..
    :param person_obj:  A previously created person object
    :param person_json: A single person json record  previously read from input data source
    :return:
    """
    LOGGER.info('ASSOCIATING company of person id {0}'.format(person_obj.id))
    company_id = person_json.get(FIELD_PERSON_COMPANY)
    if company_id:
        try:
            company_obj = models.Company.objects.get(pk=company_id)
            company_obj.employees.add(person_obj)
            company_obj.save()
            LOGGER.debug('ASSOCIATED person id {0} with company id {1}'.format(person_obj.id, company_id))
        except models.Company.DoesNotExist:
            LOGGER.error('Person with id={0} references non-existent company with id={1}'.format(person_obj.id,
                                                                                                 company_id))


def associate_person_with_friends(person_obj, person_json):
    """
    Does what it says on the tin..
    :param person_obj:  A previously created person object
    :param person_json: A single person json record  previously read from input data source
    :return:
    """
    # Some data indicates a person is friends with themselves, remove circular references:
    LOGGER.info('ASSOCIATING friends of person id {0}'.format(person_obj.id))
    friend_dicts = [f for f in person_json.get(FIELD_PERSON_FRIENDS, []) if f != person_obj.id]
    for friend_dict in friend_dicts:
        try:
            friend_id = friend_dict[FIELD_PERSON_ID]
            friend_obj = _get_person(friend_id)
            person_obj.friends.add(friend_obj)
            person_obj.save()
            LOGGER.debug('ASSOCIATED person id {0} with friend id {1}'.format(person_obj.id, friend_id))
        except models.Person.DoesNotExist:
            LOGGER.error('Person with id={0} references non-existent friend with id={1}'.format(person_obj.id,
                                                                                                friend_id))


def associate_person_and_tags(person_obj, person_json):
    """
    Does what it says on the tin..
    :param person_obj:  A previously created person object
    :param person_json: A single person json record  previously read from input data source
    :return:
    """
    LOGGER.info('ASSOCIATING tags of person id {0}'.format(person_obj.id))
    for tag_name in set(person_json.get(FIELD_PERSON_TAGS, [])):
        tag_obj, created  = models.PersonTag.objects.get_or_create(
            name=tag_name,
            defaults={'name': tag_name})
        if created:
            tag_obj.save()
        person_obj.tags.add(tag_obj)
        LOGGER.debug('ASSOCIATED person id {0} with tag name {1}'.format(person_obj.id, tag_name))


def associate_person_and_food(person_obj, person_json):
    """
    Does what it says on the tin..
    :param person_obj:  A previously created person object
    :param person_json: A single person json record  previously read from input data source
    :return:
    """
    LOGGER.info('ASSOCIATING food of person id {0}'.format(person_obj.id))
    for food_name in set(person_json.get(FIELD_PERSON_FOOD, [])):
        if food_name in ALL_KNOWN_FRUIT:
            food_type = models.FOOD_TYPE_FRUIT
        elif food_name in ALL_KNOWN_VEGETABLES:
            food_type = models.FOOD_TYPE_VEGETABLE
        else:
            food_type = models.FOOD_TYPE_OTHER
        food_obj, created = models.Food.objects.get_or_create(
            name=food_name,
            defaults={'name': food_name, 'type': food_type})
        if created:
            food_obj.save()
        person_obj.favourite_food.add(food_obj)
        LOGGER.debug('ASSOCIATED person id {0} with food name {1}'.format(person_obj.id, food_name))


# TODO - Configure cache via settings instead...
@functools.lru_cache(maxsize=128)
def _get_person(person_id):
    """
    Retrieve a person object by ID.  Use an LRU cache so we benefit from
    a level of record caching without exhausting available memory
    :param person_id:
    :return:
    """
    return models.Person.objects.get(pk=person_id)


def get_person(person_json):
    return _get_person(person_json[FIELD_PERSON_ID])
