from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models

from authentication.models import CommonModel

from django.conf import settings


class Project(CommonModel):
    name = models.CharField(max_length=100, blank=True, null=True)
    acronym = models.CharField(max_length=3, blank=True, null=True)
    assign = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    is_completed = models.BooleanField(default=False)
    dead_line = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=200), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="project_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="project_updated_by",
    )
