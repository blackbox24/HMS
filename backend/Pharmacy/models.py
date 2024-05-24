from django.db import models

# Create your models here.
class Pharmacy(models.Model):
    pharmacy_name = models.CharField(max_length=15)
    pharmacy_address = models.CharField(max_length=15)
    pharmacy_phone = models.CharField(max_length=13)

    def __str__(self):
        return f"{self.pharmacy_name}"
