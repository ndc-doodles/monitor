from django.db import models

# Create your models here.


class AdminLogin(models.Model):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)  # hashed

    def __str__(self):
        return self.username


class Register(models.Model):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)  # hashed

    def __str__(self):
        return self.username
    
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(Register, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
class DailyPlan(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='plans')  # ✅ Add this
    date = models.DateField()
    session = models.CharField(max_length=10, choices=[("Morning", "Morning"), ("Afternoon", "Afternoon")])
    point_text = models.TextField()
    status = models.CharField(max_length=50, choices=[("Pending", "Pending"), ("In Progress", "In Progress"), ("Done", "Done")])

    def __str__(self):
        return f"{self.date} - {self.session} - {self.point_text[:30]}"    

    
