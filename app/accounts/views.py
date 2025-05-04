# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('login')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # 回傳欄位錯誤訊息，Status 400
                return JsonResponse(form.errors, status=400)
    else:
        form = SignUpForm()
    return render(request, 'auth.html', {'form': form})

# views.py
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.contrib.auth import login as auth_login

class LoginView(auth_views.LoginView):
    template_name = 'auth.html'   # 同一份 template 下面掛 Vue
    def post(self, request, *args, **kwargs):
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        form = self.get_form()
        if form.is_valid():
            # 正常登入
            user = form.get_user()
            auth_login(request, user)
            return JsonResponse({'success': True}) if is_ajax else super().form_valid(form)
        else:
            errors = form.errors.get_json_data()
            if is_ajax:
                # 轉成簡單的 field: [msg, ...] 格式
                clean = {f: [d['message'] for d in v] for f, v in errors.items()}
                return JsonResponse(clean, status=400)
            return super().form_invalid(form)

class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('login')

from django.contrib.auth.decorators import login_required

def current_user(request):
    if request.user.is_authenticated:
        u = request.user
        return JsonResponse({
            "id": u.id,
            "username": u.username,
            "email": u.email,
        })
    # not logged in → just return null
    return JsonResponse(None, safe=False, status=200)

from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

@require_GET
@login_required
def fetch_messages(request):
    # Just return an empty list for now
    return JsonResponse([], safe=False)
