from django.db import models
from Patient.models import Patient

# Create your models here.
class Invoice(models.Model):
    patient_id =  models.ForeignKey(Patient,on_delete=models.CASCADE)
    service = models.CharField(max_length=30,unique=True)
    cost = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.service}"
    
