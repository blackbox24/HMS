from django.db import models
from Patient.models import Patient
from Doctor.models import Doctor
# Create your models here.
class Appointment(models.Model):
    patient_id = models.ForeignKey(Patient,on_delete=models.CASCADE)
    doctor_id = models.ForeignKey(Doctor,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"appointment_{self.id}"
