from rest_framework import serializers
from django.contrib.auth import authenticate
from eduAPI.models import User
from django.contrib.auth.password_validation import validate_password


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm', 'role']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': True},
            'email': {
                'required': True,
                'error_messages': {
                    'unique': 'This email is already used.'
                }
            }
        }
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        username = validated_data['email'].split('@')[0]
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role']
        )
        return user


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid login credentials")
        if not user.is_email_verified:
            raise serializers.ValidationError("Email is not verified")
        return data


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'role', 
            'is_email_verified', 'phone_number', 'specialization',
            'academic_degree', 'country', 'state', 'profile_image', 'cover_image',
            'birthdate', 'grade_level'
        ]
        read_only_fields = ['id', 'email', 'is_email_verified', 'full_name']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'specialization',
            'academic_degree', 'country', 'state', 'profile_image', 'cover_image',
            'birthdate', 'grade_level'
        ]
    
    def validate(self, data):
        # Add any specific validation logic for profile updates here
        return data 


class StudentProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    grade_level_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'birthdate', 'grade_level', 'grade_level_display',
            'country', 'state', 'profile_image', 'cover_image',
            'profile_image_url', 'cover_image_url'
        ]
        read_only_fields = ['email']
        
    def get_full_name(self, obj):
        return obj.full_name
    
    def get_profile_image_url(self, obj):
        if obj.profile_image:
            return self.context['request'].build_absolute_uri(obj.profile_image.url)
        return None
        
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return self.context['request'].build_absolute_uri(obj.cover_image.url)
        return None
        
    def get_grade_level_display(self, obj):
        if obj.grade_level:
            return dict(User.GRADE_CHOICES).get(obj.grade_level)
        return None


class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=False)  # Make username optional

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'password', 'password_confirm', 'username']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {
                'required': True,
                'error_messages': {
                    'unique': 'This email is already used.'
                }
            }
        }

    def validate(self, attrs):
        print(f"Validating registration data: {attrs}")
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        
        # Auto-generate username from email if not provided
        if not attrs.get('username'):
            attrs['username'] = attrs['email'].split('@')[0]
            print(f"Generated username: {attrs['username']}")

        return attrs

    def create(self, validated_data):
        print(f"Creating user with data: {validated_data}")
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                role=validated_data['role'],
                password=validated_data['password']
            )
            print(f"User created successfully: {user}")
            return user
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            raise serializers.ValidationError(f"Failed to create user: {str(e)}")


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    verification_code = serializers.CharField(required=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True, min_length=8, write_only=True)


class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class TeacherProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'specialization', 'academic_degree', 'years_of_experience',
            'birthdate', 'country', 'state', 'profile_image', 'cover_image',
            'profile_image_url', 'cover_image_url'
        ]
        read_only_fields = ['email']
        
    def get_full_name(self, obj):
        return obj.full_name
    
    def get_profile_image_url(self, obj):
        if obj.profile_image:
            return self.context['request'].build_absolute_uri(obj.profile_image.url)
        return None
        
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return self.context['request'].build_absolute_uri(obj.cover_image.url)
        return None


class AdvisorProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'birthdate', 'country', 'state', 
            'profile_image', 'cover_image', 'profile_image_url', 'cover_image_url'
        ]
        read_only_fields = ['email']
        
    def get_full_name(self, obj):
        return obj.full_name
    
    def get_profile_image_url(self, obj):
        if obj.profile_image:
            return self.context['request'].build_absolute_uri(obj.profile_image.url)
        return None
        
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return self.context['request'].build_absolute_uri(obj.cover_image.url)
        return None 