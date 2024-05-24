from django.db import models
from Department.models import Department
# Create your models here.
class Staff(models.Model):
    department_id = models.ForeignKey(Department,on_delete=models.CASCADE)
    staff_fname = models.CharField(max_length=15)
    staff_lname = models.CharField(max_length=15)
    staff_address = models.CharField(max_length=15)
    staff_phone = models.CharField(max_length=13)

    def __str__(self):
        return f"{self.staff_fname} {self.staff_lname}";
