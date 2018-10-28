"""
Data model for the application
"""

import django.db.models as models


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)


FOOD_TYPE_FRUIT = 'F'
FOOD_TYPE_VEGETABLE = 'V'
FOOD_TYPE_OTHER = 'O'
FOOD_TYPE = (
    (FOOD_TYPE_FRUIT,     'Fruit'),
    (FOOD_TYPE_VEGETABLE, 'Vegetable'),
    (FOOD_TYPE_OTHER,     'Other'),
)


class Food(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=1, choices=FOOD_TYPE)


EYE_COLOUR_BROWN = 'BR'
EYE_COLOUR_BLUE = 'BL'
EYE_COLOUR_GREEN = 'GR'
EYE_COLOUR_GREY = 'GY'
EYE_COLOUR_ALBINO = 'AL'
EYE_COLOUR_OTHER = 'OT'
EYE_TYPE = (
    (EYE_COLOUR_BROWN,  'Brown'),
    (EYE_COLOUR_BLUE,   'Blue'),
    (EYE_COLOUR_GREEN,  'Green'),
    (EYE_COLOUR_GREY,   'Grey'),
    (EYE_COLOUR_ALBINO, 'Albino'),
    (EYE_COLOUR_OTHER,  'Other'),

)


class PersonTag(models.Model):
    name = models.CharField(max_length=30, unique=True)


GENDER_MALE = 'M'
GENDER_FEMALE = 'F'
GENDER_OTHER = 'O'
GENDER_TYPE = (
    (GENDER_MALE,   'Male'),
    (GENDER_FEMALE, 'Female'),
    (GENDER_OTHER,  'Other')
)


class Person(models.Model):
    """
    Holds the main fields associated with an individual which were
    imported from the people.json data file

    Certain fields in this file are not considered to 'belong'
    to the individual and have been excluded such as:
        greeting - seems related to a messaging application
        balanceInDollars - perhaps better placed in an Accounts class at a later date

    """
    # MongoDB ID is stored for possible future use
    mongodb_id = models.CharField(max_length=24)

    # guid is stored for possible future use
    guid = models.CharField(max_length=68)

    name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    is_alive = models.BooleanField()
    gender = models.CharField(max_length=1, choices=GENDER_TYPE)
    eye_colour = models.CharField(max_length=2, choices=EYE_TYPE)

    address = models.CharField(max_length=255)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=30, null=True)

    employer = models.ForeignKey(Company, related_name='employees', on_delete=models.SET_NULL, null=True)

    about = models.CharField(max_length=1024)
    picture_url = models.URLField()

    tags = models.ManyToManyField(PersonTag, related_name='people')
    friends = models.ManyToManyField('self', symmetrical=False, related_name='followers')
    favourite_food = models.ManyToManyField(Food, related_name='people')

    registration_date = models.DateTimeField()


class ModelHelperMixin(object):
    @staticmethod
    def get_entity_by_id_or_name(model_class, obj_id):
        error_msg = ''
        obj = None
        try:
            if obj_id.isdigit():
                obj = model_class.objects.get(pk=obj_id)
            else:
                # Assume lookup by name has been requested instead
                obj = model_class.objects.get(name=obj_id)
        except model_class.DoesNotExist:
            error_msg = 'Unable to find a {0} with ID or name of {1}'.format(model_class.__name__, obj_id)
        return obj, error_msg
