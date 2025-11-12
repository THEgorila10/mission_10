from django.db import models
from django.contrib.auth.models import User # ייבוא מערכת המשתמשים של ג'אנגו

class Tag(models.Model):
    """ מודל עבור תגיות (למשל: #עבודה, #פרטי) """
    name = models.CharField(max_length=100, unique=True, verbose_name="שם תגית")

    def __str__(self):
        return self.name

class Task(models.Model):
    """ מודל המשימה הראשי """

    # --- הגדרות בחירה (Choices) ---
    PRIORITY_CHOICES = [
        ('H', 'גבוהה'),
        ('M', 'בינונית'),
        ('L', 'נמוכה'),
    ]
    STATUS_CHOICES = [
        ('new', 'חדשה'),
        ('in_progress', 'בתהליך'),
        ('done', 'הושלמה'),
    ]

    # --- שדות בסיסיים ---
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="משתמש")
    title = models.CharField(max_length=255, verbose_name="כותרת")
    description = models.TextField(blank=True, null=True, verbose_name="תיאור")
    due_date = models.DateTimeField(verbose_name="תאריך יעד", null=True, blank=True)
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M', verbose_name="עדיפות")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="סטטוס")

    # --- מימוש רעיונות מתקדמים ---
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='sub_tasks',
        verbose_name="משימת אב"
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="תגיות")

    # --- שדות אוטומטיים ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['due_date', 'priority'] # סדר מיון ברירת מחדל