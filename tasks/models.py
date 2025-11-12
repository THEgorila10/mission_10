from django.db import models

# Create your models here.
class Task(models.Model):
    
    # הגדרת בחירות קבועות עבור עדיפות
    PRIORITY_CHOICES = [
        ('L', 'Low'),       # נמוכה
        ('M', 'Medium'),    # בינונית
        ('H', 'High'),      # גבוהה
    ]

    # הגדרת בחירות קבועות עבור סטטוס
    STATUS_CHOICES = [
        ('T', 'To Do'),         # לביצוע
        ('I', 'In Progress'),   # בתהליך
        ('D', 'Done'),          # בוצע
    ]

    # שדות המודל (העמודות בטבלה)
    title = models.CharField(max_length=200)
    due_date = models.DateTimeField(null=True, blank=True) # מאפשר ערך ריק
    priority = models.CharField(
        max_length=1, 
        choices=PRIORITY_CHOICES, 
        default='M' # עדיפות ברירת מחדל
    )
    status = models.CharField(
        max_length=1, 
        choices=STATUS_CHOICES, 
        default='T' # סטטוס ברירת מחדל
    )
    created_at = models.DateTimeField(auto_now_add=True) # תאריך יצירה אוטומטי

    # פונקציה שקובעת איך המשימה תופיע באדמין
    def __str__(self):
        return self.title