from django.db import models

class Dataset(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, unique=True)
    file = models.FileField(upload_to='datasets/')

    def __str__(self):
        return self.name

    @property
    def file_path(self):
        return self.file.path
