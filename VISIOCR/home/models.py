from django.db import models

class VisitorPass(models.Model):
    visitor_pass_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=10)
    aadhaar_number = models.CharField(max_length=14)
    dob = models.DateField()
    date_of_visiting = models.DateField()
    duration_of_visiting = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.visitor_pass_id}"