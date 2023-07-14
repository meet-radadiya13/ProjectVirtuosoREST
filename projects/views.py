from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from projects.filters import ProjectFilter
from projects.models import AuditHistory, Project
from projects.permissions import IsProjectOwner
from projects.serializers import AuditHistorySerializer, \
    ProjectCreationSerializer, \
    ProjectDetailSerializer, ProjectUpdateSerializer

offset = openapi.Parameter(
    'offset', openapi.IN_QUERY,
    description="enter offset you want to pass",
    type=openapi.TYPE_STRING
    )
# Create your views here.
class ProjectViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', ]
    permission_classes = (IsAuthenticated, IsProjectOwner)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'tags']
    filterset_class = ProjectFilter
    search_fields = ['name']

    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreationSerializer
        elif self.action == 'partial_update':
            return ProjectUpdateSerializer
        elif self.action == 'list' or self.action == 'retrieve':
            return ProjectDetailSerializer
        else:
            return ProjectDetailSerializer

    def get_queryset(self):
        queryset = Project.objects.filter(
            created_by__company=self.request.user.company
        ).exclude(is_deleted=True)
        if not self.request.user.is_owner:
            queryset = queryset.filter(
                Q(created_by=self.request.user) | Q(
                    assign=self.request.user
                )
            )
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'user': request.user}
        )
        if serializer.is_valid():
            project = serializer.save()
            return Response(
                ProjectDetailSerializer(project).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(manual_parameters=[offset])
    def list(self, request, *args, **kwargs):
        offset = request.query_params.get('offset')
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={'offset': offset}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data,
            partial=True
        )
        if serializer.is_valid():
            project = serializer.save()
            return Response(
                ProjectDetailSerializer(project).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def count_projects(self, request, *args, **kwargs):
        return Response({'count': Project.objects.count()})


class AuditHistoryViewSet(mixins.ListModelMixin, GenericViewSet):
    http_method_names = ['get', ]
    permission_classes = (IsAuthenticated,)
    serializer_class = AuditHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task', ]

    def get_queryset(self):
        queryset = AuditHistory.objects.filter(
            project__created_by__company=self.request.user.company
        ).exclude(is_deleted=True)
        if not self.request.user.is_owner:
            queryset = queryset.filter(
                Q(project__created_by=self.request.user) | Q(
                    project__assign=self.request.user
                )
            )
        return queryset

    @swagger_auto_schema(manual_parameters=[offset])
    def list(self, request, *args, **kwargs):
        time_offset = request.query_params.get('offset')
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={'offset': time_offset}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
