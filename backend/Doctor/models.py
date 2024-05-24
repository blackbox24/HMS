from django.db import models
from Department.models import Department

# Create your models here.
class Doctor(models.Model):
    department_id = models.ForeignKey(Department,on_delete=models.CASCADE)
    doctor_fname = models.CharField(max_length=15)
    doctor_lname = models.CharField(max_length=15)
    doctor_phone = models.CharField(max_length=13)

    def __str__(self):
        return f"{self.doctor_fname} {self.doctor_lname}";
    