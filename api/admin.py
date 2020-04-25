from django.contrib import admin

from api.models import DataSpecification, DataValues

admin.register(DataSpecification, DataValues)