from django.shortcuts import redirect, render
from django.urls import resolve
from django.http import Http404

from django.shortcuts import redirect

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            # Якщо шлях починається з /admin/, не застосовуємо middleware
            return self.get_response(request)

        if not request.user.is_authenticated:
            # Якщо користувач не залогінений, перенаправляємо його на сторінку логіна
            return redirect('login')

        # Додайте умову, щоб не переадресовувати, якщо користувач вже аутентифікований
        if request.user.is_authenticated and request.path == '/login/':
            return redirect('home')

        response = self.get_response(request)
        return response
