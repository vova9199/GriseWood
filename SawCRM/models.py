import csv
import os
import shutil
import uuid
from datetime import datetime, date
from django.conf import settings

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import User
from django.db.models import F, Sum
from django.db.models.functions import TruncMonth
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.db import models
from authentication.models import CustomUser
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

# class WorkingHours(models.Model):
#     employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Працівник')
#     hours = models.IntegerField(verbose_name='Години')
#     hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Ставка')
#     created = models.DateField(auto_now=True, verbose_name='Дата створення/оновлення')


class Expense(models.Model):
    # Додайте поля для витрат на техніку, паливо, запчастини тощо.

    pass


class Equipment(models.Model):
    CAR = 'CAR'
    TRUCK = 'TRUCK'
    SPECIAL = 'SPECIAL'
    AGRICULTURAL = 'AGRICULTURAL'

    EQUIPMENT_TYPES = [
        (CAR, 'Легкова'),
        (TRUCK, 'Фура'),
        (SPECIAL, 'Спецтехніка'),
        (AGRICULTURAL, 'Сільгосптехніка'),
    ]

    number = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=12, choices=EQUIPMENT_TYPES)

    # Додаткові поля та методи моделі

    def __str__(self):
        return self.name


class EquipmentTrip(models.Model):
    # Додайте поля для рейсів техніки.
    pass


class WorkPerformed(models.Model):
    # Додайте поля для актів виконаних робіт на техніку.
    pass


class ClientContact(models.Model):
    name = models.CharField(max_length=100, verbose_name='ПІБ клієнта або організація')
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефону', blank=True, null=True)
    address = models.CharField(max_length=255, verbose_name='Адреса', blank=True, null=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.address} - {self.phone_number}'


class WoodType(models.Model):
    name = models.CharField(max_length=100, verbose_name='Тип дерева')

    def __str__(self):
        return f'{self.name}'


class RawMaterialBatch(models.Model):
    sender = models.CharField(max_length=300, verbose_name='Вантажовідправник')
    series = models.CharField(max_length=50, verbose_name='Серія ЮІГ')
    delivery_date = models.DateField(verbose_name='Дата', default=date.today)
    created = models.DateField(auto_now=False, auto_now_add=True, verbose_name='Дата створення запису')
    loading_point = models.CharField(max_length=100, verbose_name='Пункт завантаження')
    quantity = models.IntegerField(verbose_name='Кількість дерева', help_text='шт. в партії', default=0)
    volume = models.FloatField(verbose_name='Об\'єм по ТТН', help_text='(м³)')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Загальна сума', help_text='(грн)')
    not_declared = models.BooleanField(default=False, verbose_name='Не декларувати')
    note = models.TextField(null=True, blank=True, verbose_name='Примітка')

    # receipt_photo = models.ImageField(upload_to=batch_upload_to, null=True, blank=True, verbose_name='Фото квитанції')
    # receipt_photos = models.ManyToManyField(ReceiptPhoto, blank=True, related_name='batch_photos')
    # def get_total_volume_fact(self):
    #     # Отримати суму об'ємів усіх сировинних матеріалів, які належать даній партії
    #     total_volume = self.rawmaterial_set.aggregate(Sum('volume'))['volume__sum']
    #     return total_volume if total_volume is not None else 0.0

    def get_total_volume_fact(self):
        return sum(raw_material.volume for raw_material in self.rawmaterial_set.all())

    def get_total_quantity_fact(self):
        # сума всіх записів RawMaterial для даної партії
        return self.rawmaterial_set.all().count() or 0

    def get_price_per_cubic_meter(self):
        # обрахунок ціни за 1 м³ (власний розрахунок, який потрібно додати)
        return float(self.total_amount) / float(self.volume) if self.volume else 0

    def __str__(self):
        formatted_date = self.delivery_date.strftime('%d.%m.%Y')
        if_declared = 'Не декларовано' if self.not_declared == 1 else ''
        return f'№{self.series} - {formatted_date} - {self.loading_point} - {self.quantity} шт. - {self.volume} м³ - {self.total_amount} грн - Примітка: {self.note} | {if_declared}'
        # return f'{self.series}'

    def add_photo(self, photo):
        receipt_photo = ReceiptPhoto.objects.create(batch=self, image=photo)
        return receipt_photo

    def delete_photo(self, photo_id):
        photo = ReceiptPhoto.objects.get(id=photo_id)
        if photo:
            photo.image.delete()
            photo.delete()

    def get_all_photos(self):
        return self.receipt_photos.all()

    class Meta:
        ordering = ['-created', 'volume', 'total_amount']


def batch_upload_to(instance, filename):
    # Отримуємо значення поля 'delivery_date' та 'series' для поточного екземпляру
    batch_id = instance.batch.id
    series = instance.batch.series
    # Генеруємо унікальний ідентифікатор (uuid)
    # unique_id = str(uuid.uuid4().hex)
    # new_filename = f"{batch_id}_{series}_{unique_id}.{filename.split('.')[-1]}"

    new_filename = f"{batch_id}_{series}.{filename.split('.')[-1]}"

    # Повертаємо шлях для збереження файлу
    return os.path.join('BatchPhotos', new_filename)


class ReceiptPhoto(models.Model):
    image = models.ImageField(upload_to=batch_upload_to, null=True, blank=True, help_text="Завантажте зображення")
    batch = models.ForeignKey(RawMaterialBatch, on_delete=models.CASCADE, related_name='receipt_photos')

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    def delete_photo(self):
        # Метод для видалення фото
        self.image.delete()
        self.delete()

    def get_absolute_url(self):
        # URL для повернення після видалення
        return reverse('view_batch_photos', kwargs={'batch_id': self.batch_id})


# TODO: is_cut
class RawMaterial(models.Model):
    # order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=False, null=True, verbose_name='Замовлення')
    batch = models.ForeignKey(RawMaterialBatch, on_delete=models.CASCADE, verbose_name='Партія', blank=True, null=True,
                              default=None)
    # delivery_day = models.DateField(verbose_name='Дата', default=delivery_day.today, help_text='Формат: dd.mm.yyyy')
    created = models.DateField(auto_now=False, auto_now_add=True, verbose_name='Дата створення запису')

    # quantity = models.IntegerField(verbose_name='Кількість', default=1, help_text='штук такого діаметру')
    is_cut = models.BooleanField(default=False, verbose_name='Порізаний')
    length = models.FloatField(verbose_name='Довжина',
                               # validators=[MinValueValidator(4.0), MaxValueValidator(7.0)],
                               help_text='(м). Від 4 до 7')
    diameter = models.FloatField(verbose_name='Діаметр', help_text='(см)')
    volume = models.FloatField(verbose_name='Об\'єм', null=True, blank=True,
                               help_text='(м3) Пропустіть, щоб використати константи')
    wood_type = models.ForeignKey(WoodType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Тип')

    def save(self, *args, **kwargs):
        if not self.volume:
            # Розрахунок об'єму на основі формулі або таблиці
            self.volume = calculate_raw_material_volume(self.diameter, self.length)

        super().save(*args, **kwargs)

    # Змінюємо статус на "Поразіний"
    def change_status(self, new_status=True):
        self.is_cut = new_status

    def get_total_quantity(self):
        return sum(batch.quantity for batch in self.batches.all())

    def get_total_price(self):
        return sum(batch.price for batch in self.batches.all())

    # def __str__(self):
    #     return f'Прихід: {self.delivery_day} - Кількість: {self.get_total_quantity()} - Ціна: {self.get_total_price()}'

    def __str__(self):
        return f'{self.length} м - {self.diameter} см - {self.volume} м³ - {self.wood_type}'

    class Meta:
        verbose_name_plural = 'Raw Materials'
        ordering = ['length', 'diameter', 'volume', 'wood_type']


class Frame(models.Model):
    name = models.CharField(max_length=100, verbose_name='Назва рами')

    def __str__(self):
        return f'{self.name}'


class Board(models.Model):
    length = models.FloatField(verbose_name='Довжина', help_text='(м)')
    width = models.PositiveIntegerField(verbose_name='Ширина', help_text='(мм)')
    height = models.PositiveIntegerField(verbose_name='Висота', help_text='(мм)')
    quantity = models.PositiveIntegerField(verbose_name='К-ість', default=0, help_text='(шт.)')
    volume = models.FloatField(verbose_name='Об\'єм', help_text='(м³)')
    wood_type = models.ForeignKey(WoodType, verbose_name='Тип дерева', on_delete=models.SET_NULL, null=True,
                                  help_text='Тип дерева')

    class Meta:
        verbose_name_plural = 'Raw Materials'
        ordering = ['length', 'width', 'height', 'quantity', 'volume']

    def save(self, *args, **kwargs):
        # Розраховуємо об'єм при збереженні запису
        self.volume = (self.length * self.width / 100 * self.height / 100 * self.quantity)
        super().save(*args, **kwargs)

    def create(length, width, height, quantity):
        # Перевірка наявності запису з такими параметрами
        existing_board = Board.objects.filter(
            length=length, width=width, height=height
        ).first()

        if existing_board:
            # Якщо запис існує, оновити кількість
            existing_board.quantity = F('quantity') + quantity
            existing_board.save()
        else:
            # Якщо запис не існує, створити новий запис та розрахувати об'єм
            volume = (length * width * height * quantity) / 1000000000.0
            Board.objects.create(length=length, width=width, height=height, quantity=quantity, volume=volume)

    @classmethod
    def add_to_quantity(cls, board_id, additional_quantity):
        try:
            board = cls.objects.get(pk=board_id)
            board.quantity += additional_quantity
            board.save()
            return True
        except cls.DoesNotExist:
            return False

    @classmethod
    def subtract_from_quantity(cls, board_id, subtracted_quantity):
        try:
            board = cls.objects.get(pk=board_id)
            if board.quantity >= subtracted_quantity:
                board.quantity -= subtracted_quantity
                board.save()
                return True
            return False
        except cls.DoesNotExist:
            return False

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    def __str__(self):
        return f'{self.length}m x {self.width}mm x {self.height}mm - {self.quantity} шт. ({self.wood_type})'


# TODO: можливо видалити цю модель, бо
class CuttingRecord(models.Model):
    # order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True,
    #                           verbose_name='Замовлення', help_text='(не обов\'язково)')
    frame = models.ForeignKey(Frame, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Рама')
    created = models.DateField(verbose_name='Дата порізки', default=date.today)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE,
                                     verbose_name='Сировина')  # Додали поле для сировини
    # width = models.FloatField()
    # height = models.FloatField()
    volume = models.FloatField(null=True, blank=True, help_text='(не обов\'язково) буде вираховуватись ',
                               verbose_name='Об\'єм')
    note = models.TextField(null=True, blank=True, verbose_name='Примітка')

    def save(self, *args, **kwargs):
        # If volume is not specified, calculate it as 55% of the raw_material volume
        if not self.volume:
            self.volume = self.raw_material.volume * 0.55

        # # Decrease the quantity of the raw_material after saving the cutting record
        # if self.raw_material and self.raw_material.quantity >= 1:
        #     self.raw_material.quantity -= 1
        #     self.raw_material.save()

        # mark as is_cut = True
        if self.raw_material.is_cut == False:
            self.raw_material.is_cut = True
            self.raw_material.save()

        # Call the parent class's save() method to save the record to the database
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Отримуємо пов'язаний запис RawMaterial
        raw_material = self.raw_material
        if raw_material:
            # При видаленні CuttingRecord встановлюємо is_cut на False
            raw_material.is_cut = False
            raw_material.save()

        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['frame', '-created', 'raw_material', 'volume']


class Sawdust(models.Model):
    # order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Замовлення', blank=True, null=True,
    #                           default=None, help_text='(не обов\'язково)')
    volume = models.FloatField()


class WoodChip(models.Model):
    # BOARD = 'BOARD'
    # CHIP = 'CHIP'
    #
    # STATUS_CHOICES = [
    #     (BOARD, 'Дошка'),
    #     (CHIP, 'Щепа'),
    # ]
    # order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Замовлення', blank=True, null=True,
    #                           default=None, help_text='(не обов\'язково)')
    # status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=BOARD)
    volume = models.FloatField()

    def __str__(self):
        return f'{self.get_status_display()} - {self.board_volume}м3'


class Pallet(models.Model):
    # order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Замовлення', blank=True, null=True,
    #                           default=None, help_text='(не обов\'язково)')
    note = models.TextField(null=True, blank=True, verbose_name='Примітка')
    quantity_of_blocks = models.IntegerField()


class DailyBusinessReport(models.Model):
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2)

    def calculate_profit(self):
        # Метод для розрахунку прибутку на основі витрат та заробітку.
        pass


from django.db import models
from django.contrib.auth.models import User

class CompletedActManager(models.Manager):
    def get_monthly_statistics(self):
        monthly_stats = (
            self
            .annotate(month=TruncMonth('transport_date', field_name='month', output_field=models.DateField()))
            .values('month')
            .annotate(total_distance=Sum('distance'))
            .annotate(total_volume=Sum('volume'))
            .order_by('-month')
        )

        return monthly_stats

class CompletedAct(models.Model):
    transport_date = models.DateField(
        verbose_name='Дата перевезення',
        help_text='Дата, коли була виконано перевезення.',
        blank=True,
        null=True
    )
    waybill_number = models.CharField(
        max_length=255,
        verbose_name='ТТН',
        help_text='Номер транспортно-товарної накладної.',
        blank = True,
        null = True
    )

    driver = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        verbose_name='Водій',
        help_text='Водій, який виконав роботу.',
        null=True
    )

    volume = models.FloatField(
        verbose_name='Об\'єм',
        help_text='Об\'єм перевезення.',
        blank=True,
        null=True
    )
    distance = models.FloatField(
        verbose_name='Дистація',
        help_text='Кількість кілометрів, пройдених транспортом.',
        blank=True,
        null=True
    )
    loading_point = models.CharField(
        max_length=255,
        verbose_name='Пункт завантаження',
        help_text='Місце, де відбулося завантаження товарів.',
        blank=True,
        null=True
    )
    delivery_point = models.CharField(
        max_length=255,
        verbose_name='Пункт доставки',
        help_text='Місце, куди було доставлено вантаж.',
        blank=True,
        null=True
    )
    note = models.TextField(
        verbose_name='Примітка',
        help_text='Додаткова інформація чи коментарі.',
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення',
        help_text='Дата і час створення запису.'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата оновлення',
        help_text='Дата і час останнього оновлення запису.'
    )

    objects = CompletedActManager()

    def __str__(self):
        return f"Робота #{self.id}: {self.waybill_number} {self.driver.first_name} {self.driver.last_name} " \
               f"{self.loading_point} - {self.delivery_point} ({self.distance} м) [{self.transport_date} | {self.volume} м³])"


        # # Отримання статистики для конкретного водія
        # driver = User.objects.get(username='your_driver_username')
        # monthly_statistics = CompletedAct.objects.filter(driver=driver).get_monthly_statistics()

    class Meta:
        verbose_name = 'Completed Act'
        verbose_name_plural = 'Completed Acts'
        ordering = ['-transport_date', 'loading_point', 'delivery_point', '-created_at', 'driver']

class Transfer(models.Model):
    # Додайте поля для перевезень (дальнобій)
    # driver = models.ForeignKey(
    #     CustomUser,
    #     on_delete=models.SET_NULL,
    #     verbose_name='Водій',
    #     help_text='Водій, який виконав роботу.',
    #     blank=True,
    #     null=True,
    # )
    pass


class Order(models.Model):
    STATUS_CHOICES = [
        ('inactive', 'Неактивне'),
        ('in_progress', 'В процесі'),
        ('ready', 'Готове до відправки'),
        ('closed', 'Закрите'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive', verbose_name='Статус')
    client = models.ManyToManyField(ClientContact, verbose_name='Клієнт')
    boards = models.ManyToManyField(Board, verbose_name='Дошка')
    sawdust = models.ManyToManyField(Sawdust, verbose_name='Тирса')
    woodchip = models.ManyToManyField(WoodChip, verbose_name='Щепа')
    pallets = models.ManyToManyField(Pallet, verbose_name='Палети')
    created_date = models.DateField(auto_now_add=True, verbose_name='Дата створення')
    closed_date = models.DateField(verbose_name='Дата відправки', blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ціна замовлення', blank=True,
                                      null=True)

    def __str__(self):
        return f'Замовлення від {self.client} ({self.created_date})'

    # # Fields for sales of products
    # sawdust = models.ForeignKey(Sawdust, on_delete=models.SET_NULL, null=True, blank=True)
    # woodchip = models.ForeignKey(WoodChip, on_delete=models.SET_NULL, null=True, blank=True)
    # pallets = models.ForeignKey(Pallet, on_delete=models.SET_NULL, null=True, blank=True)



def calculate_raw_material_volume(diameter, length):
    # Розрахунок об'єму на основі формул або таблиці
    if diameter and length:
        static_file_path = os.path.join(settings.BASE_DIR, 'staticfiles/csv/volumes.csv')
        with open(static_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                d = int(row['d'])
                l = int(row['l'])
                volume = float(row['V'])

                if diameter == d and length == l:
                    return volume



    # # Модель RawMaterial буде представляти сировину на складі
# class RawMaterial(models.Model):
#     delivery_day = models.DateField(verbose_name='Дата', auto_now=True)
#     length = models.PositiveIntegerField(verbose_name='Довжина')
#     diameters = models.CharField(max_length=255, verbose_name='Діаметри')
#     type = models.CharField(max_length=100, verbose_name='Тип')
#
#     def __str__(self):
#         return f'{self.type} - {self.length}м - {self.diameters} м3'
#
#
# # Модель CuttingRecord буде представляти запис про порізку сировини.
# class CuttingRecord(models.Model):
#     delivery_day = models.DateField(verbose_name='Дата')
#     raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, verbose_name='Сировина')
#     quantity = models.PositiveIntegerField(verbose_name='К-сть')

#
#     def __str__(self):
#         return f'Порізка {self.raw_material.type} - {self.quantity}м3'
#
# class Sawdust(models.Model):
#     delivery_day = models.DateField(verbose_name='Дата')
#     volume = models.FloatField(verbose_name='Об\'єм')
#     customer = models.CharField(max_length=100, verbose_name='Замовник')
#     price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Ціна')
#
#     def __str__(self):
#         return f'Тирса {self.volume}м3'
#
# class Graft(models.Model):
#     delivery_day = models.DateField(verbose_name='Дата')
#     volume = models.FloatField(verbose_name='Об\'єм')
#     customer = models.CharField(max_length=100, verbose_name='Замовник')
#     price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Ціна')
#
# class Pallets(models.Model):
#     delivery_day = models.DateField(verbose_name='Дата')
#     size = models.CharField(max_length=50, verbose_name='Розмір')
#     quantity = models.IntegerField(verbose_name='К-сть')
#     block_quantity = models.IntegerField(verbose_name='К-сть блоків')
#


# Group.objects.get_or_create(name='Director')
# Group.objects.get_or_create(name='Engineer')
# Group.objects.get_or_create(name='Manager')
# Group.objects.get_or_create(name='Accountant')
