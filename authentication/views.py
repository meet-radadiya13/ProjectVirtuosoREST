# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from authentication.models import User
from authentication.serializers import UserCreationSerializer, \
    UserDetailSerializer


class UserViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company']

    def get_serializer_class(self):
        if self.action == 'create' or \
                self.action == 'partial_update':
            return UserCreationSerializer
        elif self.action == 'list' or self.action == 'retrieve':
            return UserDetailSerializer
        else:
            return UserDetailSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        if self.request.user.is_owner:
            queryset = queryset.filter(company=self.request.user.company)
        else:
            queryset = queryset.none()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = UserCreationSerializer(
            data=request.data, context={'user': request.user}
        )
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserDetailSerializer(
                    user, context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def list(self, request, *args, **kwargs):
    #     queryset = User.objects.all()
    #     serializer = UserDetailSerializer(queryset, many=True)
    #     data = serializer.data
    #     return Response(data)
    #
    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = UserDetailSerializer(instance)
    #     return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserCreationSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserCreationSerializer(
            instance, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
