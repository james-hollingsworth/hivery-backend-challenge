"""
Views representing each of the api functions implemented by this application
"""


from django.core.exceptions import ValidationError, FieldError
from django.http import JsonResponse
from django.views import View

from challenge import models
from challenge.dataconversion.api import SummaryPeopleSerializer, FriendsInCommonSerializer, FavouriteFruitSerializer


class AllEmployeesOfCompanyView(View, models.ModelHelperMixin):
    """
    This view is the implementation of the requirement:
        * Given a company, the API needs to return all their employees.
          Provide the appropriate solution if the company does not have any employees.

    The company_id can either be the numeric ID (index) of the company or its name (case sensitive)

    If an invalid company ID is used, a meaningful error message will be returned
    """
    def get(self, _request, company_id):
        results = []

        company, error_msg = self.get_entity_by_id_or_name(models.Company, company_id)
        if not error_msg:
            results = company.employees.all()
        return JsonResponse(SummaryPeopleSerializer(results, error_msg).to_json())


class FriendsInCommonView(View, models.ModelHelperMixin):
    """
    This view is the implementation of the requirement:
        * Given 2 people, provide their information (Name, Age, Address, phone) and the list of their friends in common
          which have brown eyes and are still alive.

    This view actually supports any number of people (their identifiers separated by '/'s) and any combination of
    fields on the model can be queried.

    In addition the identifier used to identify a person can either be their ID (index) or their name (case sensitive)

    If an invalid person ID is used or invalid fields specified, a meaningful error message will be returned
    """

    def get(self, request, person_ids):
        try:
            error_msg = ''
            friend_attributes = dict(request.GET.items())

            person_ids = person_ids.split('/')
            person_tuples = [self.get_entity_by_id_or_name(models.Person, person_id) for person_id in person_ids]
            person_objs, error_msgs = zip(*person_tuples)
            if any(error_msgs):
                error_msg = ', '.join([msg for msg in error_msgs if msg])
                return JsonResponse(FriendsInCommonSerializer([], [], error_msg).to_json())
            else:
                friends_in_common = set.intersection(*[set(person_obj.friends.all()) for person_obj in person_objs])

                # Now filter the friends by the supplied attributes
                friends_in_common = models.Person.objects.filter(pk__in=[f.id for f in friends_in_common])
                friends_in_common = friends_in_common.filter(**friend_attributes)

                return JsonResponse(FriendsInCommonSerializer(person_objs, friends_in_common, error_msg).to_json())
        except (ValidationError, FieldError):
            return JsonResponse(FriendsInCommonSerializer([], [], 'Invalid query, please check query parameters').to_json())


class FavouriteFoodView(View, models.ModelHelperMixin):
    """
    This view is the implementation of the requirement:
        * Given 1 people, provide a list of fruits and vegetables they like.
          This endpoint must respect this interface for the output:
          {"username": "Ahi", "age": "30", "fruits": ["banana", "apple"], "vegetables": ["beetroot", "lettuce"]}

    The identifier used to identify the person can either be their ID (index) or their name (case sensitive)

    If an invalid ID is used, an empty result set will be returned rather than an error as the requirement specified
    an API.
    """
    def get(self, _request, person_id):
        person, _ = self.get_entity_by_id_or_name(models.Person, person_id)
        return JsonResponse(FavouriteFruitSerializer(person).to_json())


