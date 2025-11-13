from django.shortcuts import render
from django.contrib.auth.models import User

from django.shortcuts import  redirect
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm  #
from django.utils import timezone
from django.contrib.auth import login
from .forms import TaskForm, RegisterForm
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.template.loader import render_to_string
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
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 1. צור את המשתמש אבל אל תשמור עדיין
            user = form.save(commit=False)
            # 2. סמן אותו כלא פעיל עד לאישור אימייל
            user.is_active = False 
            user.save() # שמור את המשתמש הלא פעיל

            # 3. --- בניית קישור ההפעלה ---
            current_site = get_current_site(request).domain
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activate_url = reverse('activate', kwargs={'uidb64': uid, 'token': token})

            # 4. יצירת גוף ההודעה מתוך קובץ טקסט
            mail_subject = f"הפעל את החשבון שלך, {user.username}!"
            message = render_to_string('registration/account_activation_email.txt', {
                'user': user,
                'domain': current_site,
                'activate_url': activate_url,
            })

            # 5. שליחת האימייל
            send_mail(
                subject=mail_subject,
                message=message,
                from_email="admin@taskmanager.com",
                recipient_list=[user.email],
                fail_silently=False,
            )

            # 6. שלח את המשתמש לעמוד "בדוק אימייל"
            return render(request, 'registration/check_email.html')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})
def activate_view(request, uidb64, token):
    try:
        # נסה לפענח את המזהה ולקבל את המשתמש
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # בדוק אם המשתמש קיים והטוקן תקין
    if user is not None and default_token_generator.check_token(user, token):
        # הפעל את החשבון
        user.is_active = True
        user.save()
        # בצע לוג-אין ושלח לדשבורד
        login(request, user)
        return redirect('dashboard')
    else:
        # אם הקישור שגוי או פג תוקף
        return render(request, 'registration/activation_failed.html')