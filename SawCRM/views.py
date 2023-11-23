from django.contrib import messages
from django.db.models import Sum, F
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
# from .forms import RawMaterialForm, CuttingRecordForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
# from .models import CustomUser

from django.shortcuts import render, redirect, get_object_or_404
# from .forms import ClientContactForm
# from .models import ClientContact, RawMaterial, CuttingRecord, Sawdust, Pallets, Graft
from django.template.defaultfilters import floatformat
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import UpdateView, DeleteView, DetailView

from .models import RawMaterial, CuttingRecord, Sawdust, WoodChip, Pallet, WoodType, RawMaterialBatch, Frame, Order, \
    Board, ReceiptPhoto


def index(request):
    return redirect('home')


def home(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Перенаправлення на головну сторінку після успішного входу
        else:
            error_message = "Неправильне ім'я користувача або пароль."
            return render(request, 'home.html', {'error_message': error_message})
    else:
        return render(request, 'home.html')


def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('home')



# ------------------------------------------- Director ------------------------------------------------


@login_required
@user_passes_test(lambda user: user.groups.filter(name='Director').exists())
def create_client(request):
    pass
    # Логіка створення клієнта


# ------------------------------------------- Engineer ------------------------------------------------
# @login_required
# @user_passes_test(lambda user: user.groups.filter(name='Engineer').exists())
# def raw_material_batch_list(request):
#     rawmaterials = RawMaterial.objects.all()  # Отримання дереве
#     cutmaterials = CuttingRecord.objects.all()  # Отримання сировини
#     sawdust = Sawdust.objects.all()  # Отримання тирси
#     graft = Graft.objects.all()  # Отримання щепи
#     pallets = Pallets.objects.all()  # Отримання палетів
#     return render(request, 'raw_material_batch_list.html', {'rawmaterials': rawmaterials,
#                                               'cutmaterials': cutmaterials,
#                                               'sawdust': sawdust,
#                                               'graft': graft,
#                                               'pallets': pallets})


def get_color_styles(total_quantity, total_volume, batch):
    total_quantity_style = 'color: green;' if total_quantity == batch.quantity else 'color: red;'

    if total_volume is not None and batch.volume is not None:
        total_volume_diff = total_volume - batch.volume
        total_volume_style = 'color: green;' if abs(total_volume_diff) <= 0.05 else 'color: red;'
    else:
        total_volume_style = 'color: red;'

    return total_quantity_style, total_volume_style


# def rawmaterialbatch_detail(request, pk):
#     raw_material_batch = get_object_or_404(RawMaterialBatch, pk=pk)
#
#     if request.method == 'POST':
#         # Логіка для завантаження фото
#         form = ReceiptPhotoForm(request.POST, request.FILES, instance=raw_material_batch)
#         if form.is_valid():
#             form.save()
#     else:
#         form = ReceiptPhotoForm(instance=raw_material_batch)
#
#     return render(request, 'your_template.html', {'raw_material_batch': raw_material_batch, 'form': form})
# def add_receipt_photo(request, batch_id):
#
#     if request.method == 'POST':
#         batch = get_object_or_404(RawMaterialBatch, id=batch_id)
#         form = ReceiptPhotoForm(request.POST, request.FILES)
#         if form.is_valid():
#             photo = form.save(commit=False)
#             photo.batch = batch
#             photo.save()
#             return redirect('edit_delete_batch', pk=batch_id)
#     else:
#         form = ReceiptPhotoForm()
#
#     return render(request, 'raw_material_batch/add_receipt_photo.html', {'form': form, 'batch_id': batch_id})
#
#
# def delete_receipt_photo(request, batch_id, photo_id):
#     batch = get_object_or_404(RawMaterialBatch, id=batch_id)
#     photo = get_object_or_404(ReceiptPhoto, id=photo_id, batch=batch)
#
#     if request.method == 'POST':
#         photo.image.delete()
#         photo.delete()
#         return redirect('edit_delete_batch', pk=batch_id)
#
#     return render(request, 'raw_material_batch/delete_receipt_photo.html', {'batch': batch, 'photo': photo})

from django.http import JsonResponse

def simple_view_photo(request):
    pass

class BatchPhotoView(View):
    template_name = 'raw_material_batch/view_batch_photos.html'

    def get(self, request, *args, **kwargs):
        batch_id = kwargs.get('batch_id')
        batch = RawMaterialBatch.objects.get(id=batch_id)
        photos = ReceiptPhoto.objects.filter(batch__id=batch_id)
        form_photo = ReceiptPhotoForm()
        context = {'batch': batch, 'photos': photos, 'form_photo': form_photo}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        batch_id = kwargs.get('batch_id')
        form = ReceiptPhotoForm(request.POST, request.FILES)

        if form.is_valid():
            batch_photo = form.save(commit=False)
            batch_photo.batch_id = batch_id
            batch_photo.save()
            messages.success(request, 'Фото успішно додано.')
        else:
            messages.error(request, 'Помилка при додаванні фото.')

        return redirect('view_batch_photos', batch_id=batch_id)


class PhotoDeleteView(View):
    def post(self, request, *args, **kwargs):
        photo_id = kwargs.get('photo_id')
        try:
            photo = ReceiptPhoto.objects.get(id=photo_id)
            photo.delete_photo()
            messages.success(request, 'Фото успішно видалено.')
        except ReceiptPhoto.DoesNotExist:
            messages.error(request, 'Помилка при видаленні фото.')

        return redirect(photo.get_absolute_url())

@login_required
# @user_passes_test(lambda user: user.groups.filter(name='Engineer').exists())
def raw_material_batch_list(request):
    batches = RawMaterialBatch.objects.all()  # Отримання партій
    raw_materials = RawMaterial.objects.all().order_by('length', 'diameter', 'volume')  # Отримання дереве
    cuttingrecords = CuttingRecord.objects.all()  # Отримання сировини
    sawdust = Sawdust.objects.all()  # Отримання тирси
    woodchip = WoodChip.objects.all()  # Отримання щепи
    pallets = Pallet.objects.all()  # Отримання палетів

    # Calculate total quantities in footer
    total_batches = batches.count() if batches else 0
    total_batch_quantity = batches.aggregate(Sum('quantity'))['quantity__sum'] if batches else 0
    total_batches_volume = batches.aggregate(Sum('volume'))['volume__sum'] if batches else 0
    total_raw_material_volume = sum(batch.get_total_volume_fact() for batch in batches)
    total_batches_total_amount = batches.aggregate(Sum('total_amount'))['total_amount__sum'] if batches else 0
    # total_raw_material_volume = raw_materials.aggregate(Sum('volume'))['volume__sum'] if raw_materials else 0
    total_raw_material_quantity = raw_materials.aggregate(total_quantity=Sum('is_cut'))[
        'total_quantity'] if raw_materials else 0

    # Format total values with 2 decimal places
    total_batches_volume = floatformat(total_batches_volume, 2)
    total_batches_total_amount = floatformat(total_batches_total_amount, 2)
    total_raw_material_volume = floatformat(total_raw_material_volume, 2)

    return render(request, 'raw_material_batch/raw_material_batch_list.html', {'batches': batches,
                                              'raw_materials': raw_materials,
                                              'total_batches': total_batches,
                                              'total_batch_quantity': total_batch_quantity,
                                              'total_batches_volume': total_batches_volume,
                                              'total_batches_total_amount': total_batches_total_amount,
                                              'total_raw_material_volume': total_raw_material_volume,
                                              'total_raw_material_quantity': total_raw_material_quantity,
                                              'cutting_records': cuttingrecords,
                                              'sawdust': sawdust,
                                              'woodchip': woodchip,
                                                                               'pallets': pallets})


def create_raw_material_batch(request):
    if request.method == 'POST':
        form = RawMaterialBatchForm(request.POST, request.FILES)
        photo_form = ReceiptPhotoForm(request.POST, request.FILES)

        if 'submit_action' in request.POST:
            submit_action = request.POST['submit_action']

            if submit_action == 'add_without_batch':
                return redirect('create_raw_material')

            elif submit_action == 'add_batch':
                if form.is_valid() and photo_form.is_valid():
                    series = form.cleaned_data['series']
                    existing_batch = RawMaterialBatch.objects.filter(series=series).first()

                    if existing_batch:
                        # Якщо партія вже існує, ви можете повернутися з повідомленням
                        messages.error(request,
                                       f'Партія з серією ЮІГ №{series} вже існує! Ось детальна інформація про цю партію:')
                        return render(request, 'raw_material_batch/create_raw_material_batch.html',
                                      {'form': form, 'existing_batch': existing_batch})
                    else:
                        # Збереження Batch
                        batch = form.save()

                        # Додавання фото до Batch
                        photo = photo_form.save(commit=False)
                        photo.save()
                        batch.receipt_photos.add(photo)

                        return redirect('create_raw_material', pk=batch.pk)
    else:
        form = RawMaterialBatchForm()
        photo_form = ReceiptPhotoForm()

    context = {'form': form, 'photo_form': photo_form}
    return render(request, 'raw_material_batch/create_raw_material_batch.html', context)


class RawMaterialBatchDetailView(DetailView):
    model = RawMaterialBatch
    template_name = 'raw_material_batch/edit_delete_batch.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_form'] = RawMaterialBatchForm(instance=self.object)

        # Додайте обчислення total_quantity та total_vol
        raw_materials_of_batch = RawMaterial.objects.filter(batch=self.object)
        context['total_quantity'] = raw_materials_of_batch.count()
        context['total_vol'] = raw_materials_of_batch.aggregate(total_volume=Sum('volume'))['total_volume']

        # Додайте розрахунок стилів для total_quantity та total_vol
        if context['total_quantity'] == self.object.quantity:
            context['total_quantity_style'] = 'color: green;'
        else:
            context['total_quantity_style'] = 'color: red;'

        total_vol_float = float(context['total_vol'] or 0)
        batch_vol_float = float(self.object.volume or 0)

        if abs(total_vol_float - batch_vol_float) <= 0.05:
            context['total_volume_style'] = 'color: green;'
        else:
            context['total_volume_style'] = 'color: red;'

        context['photos'] = self.object.get_all_photos()
        context['form_photo'] = ReceiptPhotoForm()

        return context

    def post(self, request, *args, **kwargs):
        batch = self.get_object()
        form = ReceiptPhotoForm(request.POST, request.FILES)

        if form.is_valid():
            batch.add_photo(form.cleaned_data['image'])
            messages.success(request, 'Фото успішно додано.')
        else:
            messages.error(request, 'Помилка при додаванні фото.')

        return redirect('view_batch_photos', pk=batch.pk)


def raw_material_batch_delete(request, pk):
    batch = RawMaterialBatch.objects.get(pk=pk)
    series = batch.series
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST['action']
        if action == 'confirm_delete':
            batch.delete()
            messages.success(request, f'Запис видалено! (Серія ЮІГ: {series})')
            return redirect('inventory')  # Replace 'raw_material_batch_list' with the URL name of your raw_material_batch_list page
    return redirect('edit_delete_batch',
                    pk=pk)  # Replace 'edit_delete_batch' with the URL name of your RawMaterialBatchDetailView


def create_raw_material(request, pk=None):
    batch = get_object_or_404(RawMaterialBatch, pk=pk) if pk is not None else None

    if request.method == 'POST':
        form = RawMaterialForm(request.POST)
        if form.is_valid():
            length = form.cleaned_data['length']
            diameter = form.cleaned_data['diameter']
            wood_type = form.cleaned_data['wood_type']

            # # Check if a record with the same length, diameter, and wood type exists for this batch
            # existing_raw_material = RawMaterial.objects.filter(batch=batch, length=length, diameter=diameter, wood_type=wood_type).first()
            # if existing_raw_material:
            #     existing_raw_material.quantity = F('quantity') + form.cleaned_data['quantity']
            #     existing_raw_material.save()
            # else:
            #     raw_material = form.save(commit=False)
            #     raw_material.batch = batch
            #     raw_material.save()

            # Зберегти сировину без додавання кількості якщо є вже з такими замірами
            raw_material = form.save(commit=False)
            raw_material.batch = batch
            raw_material.save()

            if 'submit_action' in request.POST:
                submit_action = request.POST['submit_action']
                if submit_action == 'save_and_add_more':
                    messages.success(request, 'Запис добавлено успішно.')
                    return redirect('create_raw_material', pk=pk)
                elif submit_action == 'save_and_exit':
                    return redirect('inventory')
    else:
        initial_data = {'batch': batch} if batch else None
        form = RawMaterialForm(initial=initial_data)

    raw_materials_of_batch = RawMaterial.objects.filter(batch=batch).order_by('length', 'diameter', 'volume') if batch else []
    total_quantity = raw_materials_of_batch.count()
    total_volume = raw_materials_of_batch.aggregate(total_volume=Sum('volume'))['total_volume']

    total_quantity_style, total_volume_style = get_color_styles(total_quantity, total_volume, batch)

    context = {
        'form': form,
        'batch': batch,
        'raw_material_of_batch': raw_materials_of_batch,
        'total_quantity': total_quantity if total_quantity is not None else 0,
        'total_volume': total_volume,
        'total_quantity_style': total_quantity_style,
        'total_volume_style': total_volume_style,
    }

    return render(request, 'raw_material/create_raw_material.html', context)




# def create_raw_material(request, series=None):
#     if request.method == 'POST':
#         form = RawMaterialForm(request.POST, batch_series=series)
#         if form.is_valid():
#             length = form.cleaned_data['length']
#             diameter = form.cleaned_data['diameter']
#
#             # Check if a record with the same length and diameter exists for this batch
#             if series:
#                 try:
#                     raw_material = RawMaterial.objects.get(batch__series=series, length=length, diameter=diameter)
#                     raw_material.quantity += form.cleaned_data['quantity']
#                 except RawMaterial.DoesNotExist:
#                     raw_material = form.save(commit=False)
#                     batch = RawMaterialBatch.objects.get(series=series)
#                     raw_material.batch = batch
#             else:
#                 raw_material = form.save(commit=False)
#                 raw_material.batch = None  # Set batch to None for records without a batch
#
#             raw_material.save()
#             if 'submit_action' in request.POST:
#                 submit_action = request.POST['submit_action']
#                 if submit_action == 'save_and_add_more':
#                     return redirect(f'../../../raw_material/create/series={series}')
#                 elif submit_action == 'save_and_exit':
#                     return redirect('raw_material_batch_list')
#     else:
#         initial_data = {'batch': series} if series else None
#         form = RawMaterialForm(initial=initial_data)
#
#     if series:
#         batch = RawMaterialBatch.objects.get(series=series)
#         raw_material_of_batch = RawMaterial.objects.filter(batch=batch)
#         total_quantity = raw_material_of_batch.aggregate(total_quantity=Sum('quantity'))['total_quantity']
#     else:
#         batch = None
#         raw_material_of_batch = []
#         total_quantity = None
#
#     context = {
#         'form': form,
#         'batch': batch,
#         'raw_material_of_batch': raw_material_of_batch,
#         'series': series,
#         'total_quantity': total_quantity,
#     }
#     return render(request, 'create_raw_material.html', context)


def edit_raw_material(request, pk):
    raw_material = get_object_or_404(RawMaterial, pk=pk)
    batch_id = raw_material.batch.id
    form = RawMaterialForm(request.POST or None, instance=raw_material)
    if form.is_valid():
        form.save()
        return redirect('create_raw_material', pk=batch_id)
    return render(request, 'raw_material/edit_raw_material.html', {'form': form})


def delete_raw_material(request, pk):
    raw_material = get_object_or_404(RawMaterial, pk=pk)
    batch_id = raw_material.batch.id
    if request.method == 'POST':
        raw_material.delete()
        return redirect('create_raw_material', pk=batch_id)
    return render(request, 'raw_material/delete_raw_material.html', {'raw_material': raw_material})


def create_wood_type(request):
    wood_types = WoodType.objects.all()
    if request.method == 'POST':
        form = WoodTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Інформація добавлена успішно!")
            return redirect('create_wood_type')
    else:
        form = WoodTypeForm()

    return render(request, 'woodtype/create_wood_type.html', {'form': form, 'wood_types': wood_types})


def frames_list(request):
    frames = Frame.objects.all()
    return render(request, 'frame/frames_list.html', {'frames': frames})


def create_frame(request):
    frames = Frame.objects.all()

    if request.method == 'POST':
        form = FrameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('frames_list')
    else:
        form = FrameForm()
    return render(request, 'frame/create_frame.html', {'form': form,
                                                 'frames': frames,
                                                       })


# def create_cutting_record(request):
#     if request.method == 'POST':
#         form = CuttingRecordForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Порізка добавлена успішно!")
#             return redirect('create_cutting_record')
#     else:
#         # messages.error(request, 'Сталася помилка при вводі сировини!')
#         form = CuttingRecordForm()
#
#     return render(request, 'create_cutting_record.html', {'form': form})

def create_cutting_record(request, frame_pk):
    frame = get_object_or_404(Frame, pk=frame_pk)
    cutting_records = CuttingRecord.objects.filter(frame=frame)

    # Check if RawMaterial table is empty
    if not RawMaterial.objects.exists():
        messages.error(request, 'В базі немає записів про сировину! \nСпочатку додайте записи, щоб порізати!')
        return redirect('frames_list')

    if request.method == 'POST':
        form = CuttingRecordForm(request.POST)
        if form.is_valid():
            form.instance.frame = frame
            form.save()
            if 'submit_action' in request.POST:
                submit_action = request.POST['submit_action']
                if submit_action == 'save_and_add_more':
                    messages.success(request, 'Запис добавлено успішно.')
                    return redirect('create_cutting_record', frame_pk=frame.pk)
                elif submit_action == 'save_and_exit':
                    return redirect('frames_list')
    else:
        form = CuttingRecordForm(initial={'frame': frame})  # No need to specify show_all_raw_material here

    return render(request, 'cuttingrecord/create_cutting_record.html', {'form': form, 'frame': frame, 'cutting_records': cutting_records})

def edit_delete_cutting_record(request, frame_pk, record_pk=None):
    frame = get_object_or_404(Frame, pk=frame_pk)
    record = None

    if record_pk:
        record = get_object_or_404(CuttingRecord, pk=record_pk)

    if request.method == 'POST':
        if 'edit' in request.POST:
            form = CuttingRecordForm(request.POST, instance=record, show_all_raw_material=True)
            if form.is_valid():
                form.save()
                return redirect('edit_delete_cutting_record', frame_pk=frame.pk)
        elif 'delete' in request.POST:
            if record:
                record.delete()
                if record.raw_material:
                    record.raw_material.quantity += 1
                    record.raw_material.save()
            return redirect('edit_delete_cutting_record', frame_pk=frame.pk)
    else:
        form = CuttingRecordForm(show_all_raw_material=True, instance=record)  # Show all records regardless of quantity

    cutting_records = CuttingRecord.objects.filter(frame=frame)

    return render(request, 'cuttingrecord/edit_delete_cutting_record.html', {'form': form, 'frame': frame, 'cutting_records': cutting_records})



# ------------------------------------------- Board

def board_list(request):
    boards = Board.objects.all()
    return render(request, 'board/board_list.html', {'boards': boards})

def create_board(request):
    if request.method == 'POST':
        form = BoardCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('board_list')  # Перенаправте користувача на сторінку зі списком дошок (змініть 'boards' на свій шлях)
    else:
        form = BoardCreationForm()

    return render(request, 'board/create_board.html', {'form': form})


def edit_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    if request.method == 'POST':
        form = BoardEditForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            return redirect('board_list')

    else:
        form = BoardEditForm(instance=board)

    return render(request, 'board/edit_board.html', {'form': form, 'board': board})


def delete_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    if request.method == 'POST':
        board.delete()
        return redirect('board_list')

    return render(request, 'delete_board.html', {'board': board})



# ------------------------------------------- ORDER

def order_list(request):
    orders = Order.objects.all()
    return render(request, 'order/order_list.html', {'orders': orders})

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            return redirect('order_details', pk=order.pk)
    else:
        form = OrderForm()

    return render(request, 'order/create_order.html', {'form': form})


def order_details(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'order_details.html', {'order': order})


def edit_delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_details', pk=pk)
    else:
        form = OrderForm(instance=order)

    return render(request, 'order/edit_delete_order.html', {'form': form, 'order': order})


def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('inventory')
    return render(request, 'order/delete_order.html', {'order': order})

# def create_cutting_record(request, frame_pk):
#     frame = get_object_or_404(Frame, pk=frame_pk)
#
#     if request.method == 'POST':
#         form = CuttingRecordForm(request.POST)
#         if form.is_valid():
#             # Set the frame based on the URL parameter
#             form.instance.frame = frame
#             form.save()
#             # ... (your existing success logic)
#             if 'submit_action' in request.POST:
#                 submit_action = request.POST['submit_action']
#                 if submit_action == 'save_and_add_more':
#                     messages.success(request, 'Запис добавлено успішно.')
#                     return redirect('create_cutting_record', frame_pk=frame.pk)
#                 elif submit_action == 'save_and_exit':
#                     return redirect('frames_list')
#     else:
#         form = CuttingRecordForm(initial={'frame': frame})  # Pass the frame to the form's initial data
#
#     # Retrieve CuttingRecord objects with the specified frame
#     cutting_records = CuttingRecord.objects.filter(frame=frame)
#
#     return render(request, 'create_cutting_record.html', {'form': form, 'frame': frame, 'cutting_records': cutting_records})
#
# def edit_delete_cutting_record(request, frame_pk, record_pk=None):
#     frame = get_object_or_404(Frame, pk=frame_pk)
#     record = None
#
#     if record_pk:
#         record = get_object_or_404(CuttingRecord, pk=record_pk)
#
#     if request.method == 'POST':
#         if 'edit' in request.POST:
#             form = CuttingRecordForm(request.POST, instance=record)
#             if form.is_valid():
#                 form.save()
#                 return redirect('create_cutting_record', frame_pk=frame.pk)
#         elif 'delete' in request.POST:
#             # Check if the record was deleted
#             if record:
#                 record.delete()
#                 # Increase the quantity of the corresponding RawMaterial
#                 if record.raw_material:
#                     record.raw_material.quantity += 1
#                     record.raw_material.save()
#             return redirect('create_cutting_record', frame_pk=frame.pk)
#     else:
#         form = CuttingRecordForm(instance=record)
#
#     cutting_records = CuttingRecord.objects.filter(frame=frame)
#
#     return render(request, 'edit_delete_cutting_record.html', {'form': form, 'frame': frame, 'cutting_records': cutting_records})

# ------------------------------------------- Manager ------------------------------------------------
from django.shortcuts import render, redirect
from .forms import ClientContactForm, RawMaterialForm, CuttingRecordForm, WoodTypeForm, RawMaterialBatchForm, FrameForm, \
    OrderForm, BoardCreationForm, BoardEditForm, ReceiptPhotoForm
from .models import ClientContact, CuttingRecord


def client_list(request):
    clients = ClientContact.objects.all()
    return render(request, 'client/clients_list.html', {'clients': clients})


def add_client(request):
    if request.method == 'POST':
        form = ClientContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientContactForm()

    return render(request, 'add_client.html', {'form': form})


def edit_client(request, client_id):
    client = get_object_or_404(ClientContact, id=client_id)

    if request.method == 'POST':
        form = ClientContactForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client_details', client_id=client_id)
    else:
        form = ClientContactForm(instance=client)

    return render(request, 'client/edit_client.html', {'form': form, 'client_id': client_id})

# @login_required
# @user_passes_test(lambda u: u.position == CustomUser.BUH)
# def buh_page(request):
#     return render(request, 'buh_page.html')
#
# @login_required
# @user_passes_test(lambda u: u.position == CustomUser.INZH)
# def inzh_page(request):
#     return render(request, 'inzh_page.html')
#
# @login_required
# @user_passes_test(lambda u: u.position == CustomUser.DIRECTOR)
# def director_page(request):
#     return render(request, 'director_page.html')


# ------------------------------------------- Counter ------------------------------------------------

def accounting(request):
    batches = RawMaterialBatch.objects.filter(not_declared=0)  # Get batches that are not declared

    # Calculate total quantities
    total_batches = batches.count()
    total_batches_quantity = batches.aggregate(Sum('quantity'))['quantity__sum']
    total_batches_volume = batches.aggregate(Sum('volume'))['volume__sum']
    total_batches_total_amount = batches.aggregate(Sum('total_amount'))['total_amount__sum']

    return render(request, 'accounting/accounting.html', {
        'batches': batches,
        'total_batches': total_batches,
        'total_batches_quantity': total_batches_quantity,
        'total_batches_volume': total_batches_volume,
        'total_batches_total_amount': total_batches_total_amount,
    })


def salary_list(request):
    return None


