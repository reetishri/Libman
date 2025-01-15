from django.db import models

class Student(models.Model):
    
    roll_no = models.CharField(max_length=20, primary_key=True)
    student_name = models.CharField(max_length=255)
    department = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='profilepic/', null=True, blank=True)

class Staff(models.Model):
    
    staff_id = models.CharField(max_length=255, primary_key=True)
    staff_name = models.CharField(max_length=255)

class Book(models.Model):
    book_id = models.CharField(max_length=255, primary_key=True)
    book_name = models.CharField(max_length=255)
    book_cover = models.ImageField(upload_to='covers/', null=True, blank=True) # For image uploads
    genre = models.CharField(max_length=255)

class IssueBooks(models.Model):
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, primary_key=True)
    roll_no = models.ForeignKey(Student, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    
    

    