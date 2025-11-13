# tasks/forms.py
from django import forms
from .models import Task

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