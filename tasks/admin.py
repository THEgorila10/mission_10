from django.contrib import admin
from .models import Task, Tag

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'due_date', 'priority', 'status', 'parent')
    list_filter = ('status', 'priority', 'due_date', 'user')
    search_fields = ('title', 'description')
    # שורה זו מאפשרת חיפוש נוח של תגיות, משימות אב ומשתמשים
    autocomplete_fields = ('tags', 'parent', 'user') 
def get_changeform_initial_data(self, request):
        """
        קובע ערך ברירת מחדל עבור שדה המשתמש 
        כאשר יוצרים משימה חדשה באדמין.
        """
        return {'user': request.user.pk}
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',) # מאפשר חיפוש תגיות