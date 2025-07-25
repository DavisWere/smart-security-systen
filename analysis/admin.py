from django.contrib import admin
from .models import Neighborhood, SecurityDevice,\
     IncidentReport, Evidence, AIAnalysis, Alert, User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'role','username')
    search_fields = ('username', 'role')
    list_filter = ('created_at',)



@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created_at')
    search_fields = ('name', 'location')
    list_filter = ('created_at',)

@admin.register(SecurityDevice)
class SecurityDeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'get_device_type_display', 'neighborhood', 'location', 'is_active', 'last_ping')
    list_filter = ('device_type', 'is_active', 'neighborhood')
    search_fields = ('device_id', 'location')
    list_editable = ('is_active',)

@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_incident_type_display', 'device', 'timestamp', 'severity', 'is_verified')
    list_filter = ('incident_type', 'timestamp', 'is_verified')
    search_fields = ('description',)
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_evidence_type_display', 'incident', 'created_at')
    list_filter = ('evidence_type', 'created_at')
    search_fields = ('incident__description',)
    raw_id_fields = ('incident',)

@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_analysis_type_display', 'evidence', 'confidence', 'created_at')
    list_filter = ('analysis_type', 'created_at')
    search_fields = ('evidence__incident__description',)
    raw_id_fields = ('evidence',)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_alert_level_display', 'incident', 'is_resolved', 'created_at')
    list_filter = ('alert_level', 'is_resolved', 'created_at')
    search_fields = ('message',)
    list_editable = ('is_resolved',)
    raw_id_fields = ('incident',)