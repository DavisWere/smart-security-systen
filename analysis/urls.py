from rest_framework.routers import DefaultRouter
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    NeighborhoodViewSet,
    SecurityDeviceViewSet,
    IncidentReportViewSet,
    EvidenceViewSet,
    AIAnalysisViewSet,
    AlertViewSet,
    UserViewSet,CustomObtainTokenPairView
)

router = DefaultRouter()
router.register(r'neighborhoods', NeighborhoodViewSet)
router.register(r'devices', SecurityDeviceViewSet)
router.register(r'incidents', IncidentReportViewSet)
router.register(r'evidences', EvidenceViewSet)
router.register(r'analyses', AIAnalysisViewSet)
router.register(r'alerts', AlertViewSet)
router.register(r'users', UserViewSet,)




urlpatterns = [
    path("token/request/", CustomObtainTokenPairView.as_view(), name="token_request"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"), 
]

urlpatterns += router.urls