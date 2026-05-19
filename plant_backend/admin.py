from django.contrib import admin
from .models import PlantInfo # ◄ Import your model

# Register your model here so it shows up in the dashboard
@admin.register(PlantInfo)
class PlantInfoAdmin(admin.ModelAdmin):
    list_display = ('folder_id', 'common_name', 'botanical_name', 'created_at')
    search_fields = ('common_name', 'botanical_name', 'folder_id')