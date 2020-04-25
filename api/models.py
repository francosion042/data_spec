from django.db import models
from django.contrib.postgres.fields import JSONField


class DataSpecification(models.Model):
    providerId = models.IntegerField()
    fields = JSONField(db_index=True, default=list)


class DataValues(models.Model):
    providerId = models.IntegerField()
    data = JSONField(db_index=True, default=list)