from django.db import models
from Patient.models import Patient
from staff.models import Staff

# Create your models here.
class Room(models.Model):
    room_num = models.BigIntegerField(max_length=100)
    patient_id = models.ForeignKey(Patient,on_delete=models.CASCADE)
    staff_id = models.ForeignKey(Staff,on_delete=models.CASCADE)
    admission_date = models.DateTimeField(auto_now=True)
    max_quantity = models.IntegerField(max_length=10)
    

    def __str__(self):
        return f"room_{self.room_num}"