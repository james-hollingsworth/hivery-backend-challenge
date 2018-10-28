"""
This module contains all functions required to translate
model data into the output format that will be returned
over the REST API

"""
from abc import ABCMeta, abstractmethod
from challenge import models


class BaseSerializer(object):
    """
    Base serialiser to generate the json returned by features 1 and 2 of the challenge.

    Uses an abstract method to force child classes to implement the code to generate
    JSON specific to that child class.
    """
    __metaclass__ = ABCMeta

    KEY_RESULTS = 'results'
    KEY_ERROR_MSG = 'errorMsg'

    def __init__(self, error_msg):
        self.error_msg = error_msg

    @abstractmethod
    def _serialize_results(self):
        pass

    def to_json(self):
        """
        Generates the JSON to return as a response over the API
        :return:
        """
        return {BaseSerializer.KEY_RESULTS: self._serialize_results(),
                BaseSerializer.KEY_ERROR_MSG: self.error_msg}


class SummaryPeopleSerializer(BaseSerializer):
    """
    Generates JSON representing the bare minimum of data about a Person
    """

    KEY_ID = 'id'
    KEY_NAME = 'name'

    def __init__(self, people_result_set, error_msg):
        BaseSerializer.__init__(self, error_msg)
        self.people_result_set = people_result_set

    def _serialize_results(self, data=None):
        data = self.people_result_set if data is None else data
        return [{SummaryPeopleSerializer.KEY_ID: person.id,
                 SummaryPeopleSerializer.KEY_NAME: person.name} for person in data]


class FriendsInCommonSerializer(SummaryPeopleSerializer):
    """
    Generates JSON representing the supplied People objects and
    the supplied friends of those people (also People objects)
    """

    KEY_PEOPLE = 'people'
    KEY_FRIENDS = 'friends'

    KEY_ID = 'id'
    KEY_NAME = 'name'
    KEY_AGE = 'age'
    KEY_ADDRESS = 'address'
    KEY_PHONE = 'phone'

    def __init__(self, people_result_set, friends_result_set, error_msg):
        SummaryPeopleSerializer.__init__(self, people_result_set, error_msg)
        self.friends_result_set = friends_result_set

    def _serialize_results(self, data=None):
        return {FriendsInCommonSerializer.KEY_PEOPLE:
                    [{FriendsInCommonSerializer.KEY_NAME: person.name,
                      FriendsInCommonSerializer.KEY_AGE: person.age,
                      FriendsInCommonSerializer.KEY_ADDRESS: person.address,
                      FriendsInCommonSerializer.KEY_PHONE: person.phone} for person in self.people_result_set],
                FriendsInCommonSerializer.KEY_FRIENDS:
                    SummaryPeopleSerializer._serialize_results(self, data=self.friends_result_set)}


class FavouriteFruitSerializer(object):
    """
    Generates the JSON to describe the favourite fruits and veg of an individual
    """

    KEY_USERNAME = 'username'
    KEY_AGE = 'age'
    KEY_FRUITS = 'fruits'
    KEY_VEGETABLES = 'vegetables'

    def __init__(self, person_obj):
        self.person_obj = person_obj

    def to_json(self):
        if self.person_obj:
            return {FavouriteFruitSerializer.KEY_USERNAME: self.person_obj.email,
                    FavouriteFruitSerializer.KEY_AGE: self.person_obj.age,
                    FavouriteFruitSerializer.KEY_FRUITS: [f.name for f in
                                                          self.person_obj.favourite_food.all().filter(
                                                              type=models.FOOD_TYPE_FRUIT)],
                    FavouriteFruitSerializer.KEY_VEGETABLES: [f.name for f in
                                                              self.person_obj.favourite_food.all().filter(
                                                                  type=models.FOOD_TYPE_VEGETABLE)]}
        else:
            return {}
