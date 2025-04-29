from django.db import models
import uuid 
def get_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f'analysis_images/{filename}'

class AnalysisResult(models.Model):
    SOURCE_TYPE_CHOICES = [
        ('F', 'Dosya'),
        ('U', 'URL'),
    ]
    source_type = models.CharField(max_length=1, choices=SOURCE_TYPE_CHOICES)
    source_input = models.TextField() 
    image_file = models.ImageField(upload_to=get_image_upload_path, null=True, blank=True)
    object_name = models.CharField(max_length=200)
    keywords = models.JSONField() 
    summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.object_name} ({self.get_source_type_display()}: {self.source_input[:50]})"