from django.db import models
from Pharmacy.models import Pharmacy

# Create your models here.
class Patient(models.Model):
    pharmacy_id = models.ForeignKey(Pharmacy,on_delete=models.CASCADE)
    patient_fname = models.CharField(max_length=15)
    patient_lname = models.CharField(max_length=15)
    patient_phone = models.CharField(max_length=13,unique=True)

    def __str__(self):
        return f"{self.patient_fname} {self.patient_lname}"
