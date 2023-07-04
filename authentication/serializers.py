import base64
import binascii
import imghdr
import os

import six
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from authentication.models import User
from authentication.utils import send_registration_mail


class Base64ImageField(serializers.ImageField):
    """
    Decode Base64 to Image.
    """

    def to_internal_value(self, data):
        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')
                try:
                    decoded_file = base64.b64decode(data)
                except Exception as e:
                    print("exception", e)
                    self.fail('invalid_image')
                if decoded_file:
                    file_name = str(binascii.hexlify(os.urandom(6)).decode())
                    file_extension = self.get_file_extension(
                        file_name, decoded_file
                    )
                    if file_extension.lower() not in ['png', 'jpg', 'jpeg',
                                                      'gif']:
                        raise ValidationError(
                            {'detail': 'please upload valid image.'}
                        )
                    complete_file_name = "%s.%s" % (file_name, file_extension,)
                    data = ContentFile(decoded_file, name=complete_file_name)
                    if data.size > 5242880:
                        raise ValidationError(
                            {'detail': 'please upload image '
                                       'with less then 5MB size.'}
                        )
                    else:
                        pass
        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension


class UserCreationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=20, allow_null=False,
        allow_blank=False,
    )
    email = serializers.EmailField(
        max_length=40, allow_null=False,
        allow_blank=False,
    )
    firstname = serializers.CharField(
        max_length=20, allow_null=False,
        allow_blank=False,
    )
    lastname = serializers.CharField(
        max_length=20, allow_null=False,
        allow_blank=False,
    )
    about = serializers.CharField(
        max_length=20, allow_null=False,
        allow_blank=False,
    )
    contact_no = serializers.RegexField(
        regex=r'^(\+\d{1,3})?,?\s?\d{8,13}',
        required=True
    )
    image = Base64ImageField(allow_null=True, )

    class Meta:
        model = User
        fields = ('username', 'email', 'firstname', 'lastname',
                  'about', 'contact_no', 'image')

    def validate(self, attrs):
        current_user = self.context['user']
        attrs['email'] = attrs['email'].lower()
        attrs['password'] = User.objects.make_random_password()
        user = User.objects.filter(email=attrs['email']).first()
        if user:
            if user.is_active:
                raise ValidationError(
                    {'detail': 'User with this email already exists.'}
                )
            else:
                attrs['is_active'] = True
                attrs['has_changed_password'] = False
        if current_user.company.is_deleted:
            raise ValidationError(
                {'detail': 'Company does not exists.'}
            )
        attrs['company'] = current_user.company
        return attrs

    def create(self, validated_data):
        password = validated_data['password']
        validated_data['password'] = make_password(password)
        user = super(UserCreationSerializer, self).create(validated_data)
        send_registration_mail(user.email, password)
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'firstname', 'lastname',
                  'about', 'contact_no', 'image', 'is_active', 'is_staff',
                  'is_superuser', 'date_joined', 'last_login', 'company',
                  'is_owner', 'has_changed_password', 'stripe_customer_id',
                  'stripe_subscription_id')

    def get_image(self, obj):
        return self.context['request'].build_absolute_uri(obj.image.url)
