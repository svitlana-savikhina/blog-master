from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "is_staff")
        read_only = ("id", "is_staff")
        extra_kwargs = {"password": {"write_only": True},
                        "min_length": 8}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='profile.username', read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username')


# class ProfileSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Profile
#        fields = ('user', 'username', 'avatar')
#        read_only_fields = ('user',)


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='profile.username')
    avatar = serializers.ImageField(source='profile.avatar', allow_null=True, required=False)

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'avatar')

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        email = validated_data.get('email', instance.email)

        # Update user fields
        instance.email = email
        instance.save()

        # Update profile fields
        profile = instance.profile
        profile.username = profile_data.get('username', profile.username)
        profile.avatar = profile_data.get('avatar', profile.avatar)
        profile.save()

        return instance
