"""challenge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from challenge.views import AllEmployeesOfCompanyView, FriendsInCommonView, FavouriteFoodView

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('api/company_employees/<str:company_id>', AllEmployeesOfCompanyView.as_view(), name='company_employees'),
    path('api/common_friends/<path:person_ids>', FriendsInCommonView.as_view(), name='common_friends'),
    path('api/favourite_food/<str:person_id>',FavouriteFoodView.as_view(), name='favourite_food'),
]
