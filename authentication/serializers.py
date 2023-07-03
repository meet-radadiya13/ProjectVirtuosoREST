import base64
import binascii
import datetime
import imghdr
import os

import six
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from authentication.models import Company, User
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
        max_length=20, allow_null=True,
        allow_blank=True
    )
    email = serializers.EmailField(
        max_length=20, allow_null=True,
        allow_blank=True
    )
    firstname = serializers.CharField(
        max_length=20, allow_null=True,
        allow_blank=True
    )
    lastname = serializers.CharField(
        max_length=20, allow_null=True,
        allow_blank=True
    )
    about = serializers.CharField(
        max_length=20, allow_null=True,
        allow_blank=True
    )
    contact_no = serializers.CharField(
        max_length=20, allow_null=True,
        allow_blank=True
    )
    image = Base64ImageField(allow_null=True, )

    class Meta:
        model = User
        fields = ('username', 'email', 'firstname', 'lastname',
                  'about', 'contact_no', 'image')

    def to_internal_value(self, data):
        if 'email' in data:
            data['email'] = data['email'].lower()
        return super().to_internal_value(data)

    def create(self, validated_data):
        password = User.objects.make_random_password()
        validated_data['password'] = password
        user = User.objects.filter(email=validated_data['email']).first()
        if user and user.is_active:
            raise ValidationError(
                {'detail': 'User with this email already exists.'}
            )
        elif user and not user.is_active:
            user.is_active = True
            user.has_changed_password = False
            user.date_joined = datetime.datetime.now()
            send_registration_mail(user.email, password, )
        else:
            validated_data['username'] = validated_data['email'].split('@')[0]
            user = User.objects.create_user(**validated_data)
            send_registration_mail(user.email, password, )
        if 'company_id' in self.context:
            company = Company.objects.get(id=self.context['company_id'])
            user.company = company
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'firstname', 'lastname',
                  'about', 'contact_no', 'image', 'is_active', 'is_staff',
                  'is_superuser', 'date_joined', 'last_login', 'company',
                  'is_owner', 'has_changed_password', 'stripe_customer_id',
                  'stripe_subscription_id')
