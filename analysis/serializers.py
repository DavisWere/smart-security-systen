from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from analysis.models import User
from django.contrib.auth.hashers import make_password
from . models import *



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['is_superuser'] = user.is_superuser
        token['username'] = user.username
        token['email'] = user.email

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        """Get user info"""
        user_data = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "is_superuser": self.user.is_superuser,
            'role':self.user.role
        }

        data.update({"user": user_data})

        return data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'department', 'role',
                  'email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)
        return data

    def create(self, validated_data):
        password = validated_data.get('password')
        if password:
            validated_data['password'] = make_password(password)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            """Hash the new password"""
            instance.set_password(password)

        return super().update(instance, validated_data)


class IncidentReportSerializer(serializers.ModelSerializer):
    incident_type = serializers.CharField(max_length=100)  # Override to allow any value
    
    class Meta:
        model = IncidentReport
        fields = '__all__'
    
    def validate_incident_type(self, value):
        """
        Validate incident_type but allow any value (not just the choices)
        """
        # You can add any custom validation here if needed
        return value.strip().upper()  # Convert to uppercase for consistency
    
    def to_representation(self, instance):
        """
        Custom representation to show both the stored value and display value
        """
        representation = super().to_representation(instance)
        # Get the display value for known types
        if instance.incident_type in dict(IncidentReport.INCIDENT_TYPES):
            representation['incident_type_display'] = dict(IncidentReport.INCIDENT_TYPES).get(
                instance.incident_type, instance.incident_type
            )
        else:
            representation['incident_type_display'] = instance.incident_type
        return representation
    
class NeighborhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model= Neighborhood
        fields = '__all__'

class SecurityDeviceSerializer(serializers.ModelSerializer):
   neighborhood = NeighborhoodSerializer(read_only=True)
   class Meta:
       model= SecurityDevice
       fields = '__all__'

class IncidentReportSerializer(serializers.ModelSerializer):
    device = SecurityDeviceSerializer(read_only=True)
    evidences = serializers.SerializerMethodField()
    
    class Meta:
        model = IncidentReport
        fields = '__all__'
        read_only_fields = ['timestamp']
    
    def get_evidences(self, obj):
        return EvidenceSerializer(obj.evidences.all(), many=True, context=self.context).data

class EvidenceSerializer(serializers.ModelSerializer):
    incident = serializers.PrimaryKeyRelatedField(queryset=IncidentReport.objects.all())
    ai_analyses = serializers.SerializerMethodField()
    
    class Meta:
        model = Evidence
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_ai_analyses(self, obj):
        return AIAnalysisSerializer(obj.aianalysis_set.all(), many=True, context=self.context).data

class AIAnalysisSerializer(serializers.ModelSerializer):
    evidence = serializers.PrimaryKeyRelatedField(queryset=Evidence.objects.all())
    confidence_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = AIAnalysis
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_confidence_percentage(self, obj):
        return f"{obj.confidence:.0%}"

class AlertSerializer(serializers.ModelSerializer):
    incident = serializers.PrimaryKeyRelatedField(queryset=IncidentReport.objects.all())
    alert_level_display = serializers.CharField(source='get_alert_level_display', read_only=True)
    
    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ['created_at']



   