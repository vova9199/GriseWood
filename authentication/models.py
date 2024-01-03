import datetime
import os


from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth import get_user_model

from GriseWood import settings

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GriseWood.settings')
# application = get_wsgi_application()
#

EMPLOYEE = 'EMPLOYEE'
DRIVER = 'DRIVER'
TRUCK_DRIVER = 'TRUCK DRIVER'
ENGINEER = 'ENGINEER'
MANAGER = 'MANAGER'
COUNTER = 'COUNTER'
DIRECTOR = 'DIRECTOR'

ROLE_CHOICES = [
    (EMPLOYEE, 'Працівник'),
    (DRIVER, 'Водій'),
    (TRUCK_DRIVER, 'Далекобійник'),
    (ENGINEER, 'Інженер'),
    (MANAGER, 'Менеджер'),
    (COUNTER, 'Бухгалтер'),
    (DIRECTOR, 'Директор')
]


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not username:
            raise ValueError('The USERNAME must be set')

        user = self.model(email=self.normalize_email(email),
                          username=username,
                          first_name=extra_fields.get('first_name', None),
                          last_name=extra_fields.get('last_name', None),
                          )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and return a superuser with an email, username, and password.
        """
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=extra_fields.get('first_name', ''),
            last_name=extra_fields.get('last_name', ''),
        )

        user.role = DIRECTOR
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        user.save()
        return user


class CustomUser(AbstractBaseUser):

    first_name = models.CharField(max_length=20, default=None, verbose_name='Ім`я')
    patronymic = models.CharField(max_length=20, blank=True, null=True, default=None, verbose_name='По батькові')
    last_name = models.CharField(max_length=20, default=None, verbose_name='Прізвище')
    username = models.CharField(max_length=30, unique=True, verbose_name='Логін')
    email = models.CharField(max_length=100, blank=True, null=True, default=None, unique=True, verbose_name='Пошта')
    password = models.CharField(default=None, blank=True, null=True, max_length=255, verbose_name='Пароль')
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Номер телефону')
    created_at = models.DateTimeField(editable=False, auto_now=True, verbose_name='Дата сворення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default=EMPLOYEE, verbose_name='Роль')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='user_set',
        related_query_name='user',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='user_set',
        related_query_name='user',
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"'id': {self.id}, 'first_name': '{self.first_name}', 'patronymic': '{self.patronymic}', 'last_name': '{self.last_name}', 'email': '{self.email}', 'created_at': {int(self.created_at.timestamp())}, 'updated_at': {int(self.updated_at.timestamp())}, 'role': {self.role}, 'is_active': {self.is_active}"  # 'password': '{self.password}', \

    def __repr__(self):
        return f"{CustomUser.__name__}(id={self.id})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    @staticmethod
    def get_by_id(user_id):
        custom_user = CustomUser.objects.filter(id=user_id).first()
        return custom_user if custom_user else None

    @staticmethod
    def get_by_email(email):
        custom_user = CustomUser.objects.filter(email=email).first()
        return custom_user if custom_user else None

    @staticmethod
    def delete_by_id(user_id):
        user_to_delete = CustomUser.objects.filter(id=user_id).first()
        if user_to_delete:
            CustomUser.objects.filter(id=user_id).delete()
            return True
        return False

    @staticmethod
    def create(email, password, first_name=None, patronymic=None, last_name=None):
        if len(first_name) <= 20 and len(patronymic) <= 20 and len(last_name) <= 20 and len(email) <= 100 and len(
                email.split('@')) == 2 and len(CustomUser.objects.filter(email=email)) == 0:
            custom_user = CustomUser(email=email, password=password, first_name=first_name, patronymic=patronymic,
                                     last_name=last_name)
            custom_user.save()
            return custom_user
        return None

    def to_dict(self):
        return {'id': self.id,
                'first_name': f'{self.first_name}',
                'patronymic': f'{self.patronymic}',
                'last_name': f'{self.last_name}',
                'email': f'{self.email}',
                'created_at': int(self.created_at.timestamp()),
                'updated_at': int(self.updated_at.timestamp()),
                'role': self.role,
                'is_active': self.is_active}

    def update(self,
               first_name=None,
               last_name=None,
               patronymic=None,
               password=None,
               role=None,
               is_active=None,
               phone=None):  # Added phone parameter

        user_to_update = CustomUser.objects.filter(email=self.email).first()
        if first_name is not None and len(first_name) <= 20:
            user_to_update.first_name = first_name
        if last_name is not None and len(last_name) <= 20:
            user_to_update.last_name = last_name
        if patronymic is not None and len(patronymic) <= 20:
            user_to_update.patronymic = patronymic
        if password is not None:
            user_to_update.password = password
        if role is not None:
            user_to_update.role = role
        if is_active is not None:
            user_to_update.is_active = is_active
        if phone is not None:
            user_to_update.phone = phone  # Added line to update phone
        user_to_update.save()

    @staticmethod
    def get_all():
        """
        returns data for json request with QuerySet of all users
        """
        return CustomUser.objects.all()

    def get_role_name(self):
        """
        returns str role name
        """
        return self.role

from django.contrib.auth.backends import ModelBackend

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Спробуйте знайти користувача за `username` або `email`
        user = get_user_model().objects.filter(models.Q(username=username) | models.Q(email=username)).first()

        # Перевірте пароль, якщо користувача знайдено
        if user and user.check_password(password):
            return user

        return None
