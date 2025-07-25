from rest_framework.routers import DefaultRouter
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    NeighborhoodViewSet,
    SecurityDeviceViewSet,
    IncidentReportViewSet,
    EvidenceViewSet,
    AIAnalysisViewSet,safehaven_analysis_page,
    AlertViewSet,safehaven_analysis_view,
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
    # path('detection-status/', DetectionStatusView.as_view(), name='detection-status'),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"), 
    path("api/analysis/", safehaven_analysis_view, name="safehaven_analysis"),
    path('dashboard/', safehaven_analysis_page, name='dashboard'),
    # path('start-detection/', StartDetectionView.as_view(), name='start-detection'),
    # path('stop-detection/', StopDetectionView.as_view(), name='stop-detection'),
]

urlpatterns += router.urls