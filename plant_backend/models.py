from django.db import models

class PlantInfo(models.Model):
    folder_id = models.CharField(max_length=255, unique=True, db_index=True)
    common_name = models.CharField(max_length=255)
    botanical_name = models.CharField(max_length=255)
    medicinal_benefits = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.common_name} ({self.botanical_name})"