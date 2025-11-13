from django.shortcuts import render

from django.shortcuts import  redirect
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm  #
from django.utils import timezone
def index_view(request):
    """
    זוהי דלת הכניסה הראשית לאתר (כתובת "/")
    היא בודקת אם המשתמש מחובר.
    """
    if request.user.is_authenticated:
        # אם כן - שלח אותו ישר לעמוד האישי (dashboard)
        return redirect('dashboard')

    # אם לא - הצג לו את עמוד הבית הציבורי
    return render(request, 'tasks/home.html')
@login_required 
def dashboard_view(request):
    """
    מציג את הדשבורד עם רשימות המשימות וסיכום חודשי הכולל 4 גרפים.
    """

    # --- 1. לוגיקה של רשימות משימות (לעמודות) ---
    base_tasks = Task.objects.filter(user=request.user, parent=None)

    new_tasks_list = base_tasks.filter(status='new').order_by('due_date')
    in_progress_tasks_list = base_tasks.filter(status='in_progress').order_by('due_date')
    done_tasks_list = base_tasks.filter(status='done').order_by('-updated_at')

    # --- 2. לוגיקה חדשה: מוניטור חודשי (4 גרפים) ---
    today = timezone.now()

    # מצא את כל המשימות עם תאריך יעד בחודש ובשנה הנוכחיים
    tasks_this_month = Task.objects.filter(
        user=request.user,
        due_date__year=today.year,
        due_date__month=today.month
    )

    # ספירת המספרים עבור 3 הגרפים הנפרדים (פריטים 1, 2, 3)
    new_tasks_count = tasks_this_month.filter(status='new').count()
    progress_tasks_count = tasks_this_month.filter(status='in_progress').count()
    done_tasks_count = tasks_this_month.filter(status='done').count()

    # סה"כ משימות לגרף המשולב (פריט 4)
    total_tasks_count = new_tasks_count + progress_tasks_count + done_tasks_count

    # חישוב אחוזים לגרף המשולב
    new_percent = 0
    progress_percent = 0
    in_progress_end_percent = 0 # נקודת הסיום של הכחול

    if total_tasks_count > 0:
        new_percent = int((new_tasks_count / total_tasks_count) * 100)
        progress_percent = int((progress_tasks_count / total_tasks_count) * 100)
        in_progress_end_percent = new_percent + progress_percent
    # --- סוף לוגיקה חדשה ---

    # 3. עדכון ה-context עם כל המידע
    context = {
        # רשימות לעמודות
        'new_tasks': new_tasks_list,
        'in_progress_tasks': in_progress_tasks_list,
        'done_tasks': done_tasks_list,

        # מידע למוניטור החודשי (4 הגרפים)
        'today': today,
        'new_tasks_count': new_tasks_count,
        'progress_tasks_count': progress_tasks_count,
        'done_tasks_count': done_tasks_count,
        'total_tasks_count': total_tasks_count,
        'new_percent': new_percent,
        'in_progress_end_percent': in_progress_end_percent,
    }

    return render(request, 'tasks/dashboard.html', context)
@login_required
def add_task_view(request):
    """
    מציג ומטפל בטופס הוספת משימה חדשה.
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.user = request.user  # שייך אוטומטית למשתמש המחובר
            new_task.save()
            form.save_m2m() # חובה לשמור קשרי תגיות (many-to-many)
            return redirect('dashboard') # חזור לדשבורד אחרי הצלחה
    else:
        form = TaskForm() # הצג טופס ריק

    context = {
        'form': form
    }
    return render(request, 'tasks/add_task.html', context)