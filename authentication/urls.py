from django.urls import path
import authentication.views as views


urlpatterns = [
    path("register/", views.register, name="register"),
    path('login/', views.user_login, name='login'),
    path("logout/", views.user_logout, name="logout"),

    path("all_users/", views.all_users, name="all_users"),
    path("update/<int:id>/", views.register, name="update"),
    path("edit/<int:id>/", views.edit_user_info, name="edit_user_info"),
    path("delete/<int:id>/", views.delete_user, name="delete_user"),
    path("info/<int:id>/", views.user_info, name="user_info"),
]
