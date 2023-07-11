import django_filters
from django.contrib.postgres.fields import ArrayField
from django_filters import rest_framework as filters

from projects.models import Project


class ProjectFilter(filters.FilterSet):
    tags = filters.CharFilter(method='filter_tags')

    def filter_tags(self, queryset, name, value):
        tags = value.split(',')
        return queryset.filter(tags__contains=tags)

    class Meta:
        model = Project
        fields = ['name', 'tags']
        filter_overrides = {
            ArrayField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }
