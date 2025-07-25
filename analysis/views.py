from rest_framework import viewsets, permissions
from django.utils import timezone
from django.contrib.auth.decorators import login_required

import time
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Neighborhood, SecurityDevice, \
    Incident, Evidence, AIAnalysis, Alert,User, ChatMessage
from .serializers import (
    NeighborhoodSerializer,UserSerializer,
    SecurityDeviceSerializer,
    IncidentSerializer,ChatMessageSerializer,
    EvidenceSerializer,
    AIAnalysisSerializer,
    AlertSerializer, CustomTokenObtainPairSerializer
)
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from django.http import JsonResponse
import requests
import os
from django.shortcuts import render

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
    


# class StartDetectionView(APIView):
#     def post(self, request):
#         cache.set('detection_status', 'start', timeout=60 * 60)  # 1 hour
#         return Response({"message": "Detection started remotely."}, status=status.HTTP_200_OK)

# class StopDetectionView(APIView):
#     def post(self, request):
#         cache.set('detection_status', 'stop', timeout=60 * 60)
#         return Response({"message": "Detection stopped remotely."}, status=status.HTTP_200_OK)

# class DetectionStatusView(APIView):
#     def get(self, request):
#         status_value = cache.get('detection_status', 'stop')  # default to 'stop'
#         return Response({"status": status_value}, status=status.HTTP_200_OK)

@csrf_exempt
def safehaven_analysis_view(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', None)
        user = request.user if request.user.is_authenticated else None

        if not user:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        # If no prompt is provided, auto-analyze incidents
        if not prompt:
            recent_incidents = Incident.objects.filter(ai_analysis__isnull=True).order_by('-timestamp')[:10]

            if not recent_incidents.exists():
                return JsonResponse({'message': 'No new incidents found for analysis'}, status=200)

            incident_text = "\n".join([
                f"Time: {incident.created_at}, Type: {incident.incident_type}, "
                f"Description: {incident.description or 'N/A'}, "
                f"Evidence: {request.build_absolute_uri(incident.evidence_file.url) if incident.evidence_file else 'None'}"
                for incident in recent_incidents
            ])
            prompt = (
                "Analyze the following recent security incidents. "
                "Summarize the key issues, categorize them by type, and recommend actions if needed:\n\n"
                + incident_text
            )
        else:
            recent_incidents = None  # For manual analysis

        # Setup Mistral API call
        api_key = os.getenv("API_KEY")
        model = "mistral-small-latest"

        system_message = (
            "You are an AI analyst for SafeHaven Security System. Analyze incidents, identify patterns, and recommend actions. "
            "Be brief and precise, highlighting any critical threats or repeated behaviors."
        )

        history_messages = [{"role": "system", "content": system_message}]
        history_messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": history_messages
        }

        response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            time.sleep(retry_after)
            response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload)

        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]

        # Save to chat history
        ChatMessage.objects.create(
            user=user,
            conversation=[{"user": prompt}, {"mistral": reply}],
            updated_at=timezone.now()
        )

        # Update analyzed incidents with AI feedback
        if recent_incidents:
            for incident in recent_incidents:
                incident.ai_analysis = reply
                incident.save(update_fields=['ai_analysis'])

        return JsonResponse({
            "response": reply,
            "status": "success"
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
class ChatHistoryViewSet(viewsets.ModelViewSet):
    permission_classes =[permissions.IsAuthenticated]
    serializer_class = ChatMessageSerializer
    queryset = ChatMessage.objects.all()



@login_required
def safehaven_analysis_page(request):
    """
    Render the SafeHaven analysis page with chat history
    """
    # Get recent chat history for the current user
    chat_history = ChatMessage.objects.filter(
        user=request.user
    ).order_by('-updated_at')[:10]
    
    context = {
        'chat_history': chat_history,
        'user': request.user,
    }
    
    return render(request, 'dashboard.html', context)