from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Neighborhood, SecurityDevice, \
    Incident, Evidence, AIAnalysis, Alert,User
from .serializers import (
    NeighborhoodSerializer,UserSerializer,
    SecurityDeviceSerializer,
    IncidentSerializer,
    EvidenceSerializer,
    AIAnalysisSerializer,
    AlertSerializer, CustomTokenObtainPairSerializer
)
 

class CustomObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_superuser:
            user = User.objects.filter(id=user.id)
        else:
            user = User.objects.all()
        return user


class NeighborhoodViewSet(viewsets.ModelViewSet):
    queryset = Neighborhood.objects.all()
    serializer_class = NeighborhoodSerializer
    authentication_classes = []  # No authentication required
    permission_classes = []  # No permissions required

class SecurityDeviceViewSet(viewsets.ModelViewSet):
    queryset = SecurityDevice.objects.all()
    serializer_class = SecurityDeviceSerializer
    authentication_classes = []
    permission_classes = []

class IncidentReportViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all().order_by('-timestamp')
    serializer_class = IncidentSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()
        # Example filter - you can add more as needed
        incident_type = self.request.query_params.get('type')
        if incident_type:
            queryset = queryset.filter(incident_type=incident_type.upper())
        return queryset

class EvidenceViewSet(viewsets.ModelViewSet):
    queryset = Evidence.objects.all().order_by('-created_at')
    serializer_class = EvidenceSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()
        incident_id = self.request.query_params.get('incident_id')
        if incident_id:
            queryset = queryset.filter(incident_id=incident_id)
        return queryset

class AIAnalysisViewSet(viewsets.ModelViewSet):
    queryset = AIAnalysis.objects.all().order_by('-created_at')
    serializer_class = AIAnalysisSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()
        evidence_id = self.request.query_params.get('evidence_id')
        if evidence_id:
            queryset = queryset.filter(evidence_id=evidence_id)
        return queryset

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all().order_by('-created_at')
    serializer_class = AlertSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()
        # Example filters
        resolved = self.request.query_params.get('resolved')
        if resolved:
            queryset = queryset.filter(is_resolved=resolved.lower() == 'true')
        
        incident_id = self.request.query_params.get('incident_id')
        if incident_id:
            queryset = queryset.filter(incident_id=incident_id)
            
        return queryset


