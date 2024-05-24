from django.db import models
from Hospital.models import Hospital

# Create your models here.
class Department(models.Model):
    department_name = models.CharField(max_length=30)
    hospital_id = models.ForeignKey(Hospital,on_delete=models.CASCADE)

    def __str__(self):
        return self.department_name
