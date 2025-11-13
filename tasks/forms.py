# tasks/forms.py
from django import forms
from .models import Task
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        # אלו השדות שיופיעו בטופס
        # שים לב ש-user לא כאן!
        fields = ['title', 'description', 'due_date', 'priority', 'status', 'parent', 'tags']
        
        # הגדרת סוגי הקלט (כדי לקבל בורר תאריכים יפה)
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # טריק להפוך שדות ללא חובה, בהתאם למודל
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['due_date'].required = False
        self.fields['priority'].required = False
        self.fields['status'].required = False
        self.fields['parent'].required = False
        self.fields['tags'].required = False
class RegisterForm(UserCreationForm):
    # הוספת שדה אימייל כשדה חובה
    email = forms.EmailField(required=True, label="כתובת אימייל")

    class Meta:
        model = User
        # הגדרת השדות שיופיעו בטופס
        fields = ("username", "email") 

    def save(self, commit=True):
        # דרסנו את פונקציית השמירה
        user = super(RegisterForm, self).save(commit=False)
        # שמירת האימייל שהוזן בטופס
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user