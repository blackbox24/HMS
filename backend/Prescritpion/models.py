from django.db import models
from Patient.models import Patient 

# Create your models here.
class Prescription(models.Model):
    patient_id = models.ForeignKey(Patient,on_delete=models.CASCADE)
    medication = models.CharField(max_length=15,unique=True)
    expiry_date = models.DateTimeField(null=False)
    cost = models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medication}"
