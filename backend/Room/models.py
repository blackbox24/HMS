from django.db import models
from Patient.models import Patient
from Staff.models import Staff

# Create your models here.
class Room(models.Model):
    room_num = models.BigIntegerField()
    patient_id = models.ForeignKey(Patient,on_delete=models.CASCADE)
    staff_id = models.ForeignKey(Staff,on_delete=models.CASCADE)
    admission_date = models.DateTimeField(auto_now=True)
    max_quantity = models.IntegerField()
    

    def __str__(self):
        return f"room_{self.room_num}"