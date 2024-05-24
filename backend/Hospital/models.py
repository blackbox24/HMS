from django.db import models

# Create your models here.
class Hospital(models.Model):
    h_name = models.CharField(max_length=15)
    h_address = models.CharField(max_length=15)
    h_phone = models.CharField(max_length=13)

    def __str__(self):
        return self.h_name