from datetime import date

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from authentication.models import CustomUser
from .models import Sawdust, CuttingRecord, WoodType, RawMaterial, ClientContact, WoodChip, RawMaterialBatch, Frame, \
    Board, ReceiptPhoto, CompletedAct
from .models import Order
from .widgets import DateInput


class ReceiptPhotoForm(forms.ModelForm):
    image = forms.ImageField(required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    class Meta:
        model = ReceiptPhoto
        fields = ['image']


class RawMaterialBatchForm(forms.ModelForm):

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data['delivery_date']
        return delivery_date.strftime('%Y-%m-%d')  # Convert to the format YYYY-MM-DD

    class Meta:
        model = RawMaterialBatch
        fields = ['sender', 'series', 'delivery_date', 'loading_point', 'quantity', 'volume', 'total_amount',
                  'not_declared', 'note']
        widgets = {
            'delivery_date': DateInput,  # Using DatePickerInput for the 'delivery_day' field
        }


class RawMaterialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        batch_series = kwargs.pop('batch_series', None)  # Change 'series' to 'batch_series'
        super(RawMaterialForm, self).__init__(*args, **kwargs)
        if batch_series:
            self.fields['batch'].initial = RawMaterialBatch.objects.get(series=batch_series)

        self.fields['batch'].widget = forms.HiddenInput()
        self.fields['is_cut'].widget = forms.HiddenInput()

    class Meta:
        model = RawMaterial
        fields = '__all__'


class WoodTypeForm(forms.ModelForm):
    class Meta:
        model = WoodType
        fields = '__all__'


class FrameForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['placeholder'] = 'Рама №1 - Дискова'

    class Meta:
        model = Frame
        fields = '__all__'


class CuttingRecordForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        show_all_raw_material = kwargs.pop('show_all_raw_material', False)
        super().__init__(*args, **kwargs)

        # Modify the queryset for the 'raw_material' field
        raw_material_queryset = RawMaterial.objects.filter(is_cut=False)
        if not show_all_raw_material:
            raw_material_queryset = raw_material_queryset.order_by('length', 'diameter', 'volume')
        self.fields['raw_material'].queryset = raw_material_queryset

        # Add placeholder to the 'volume' field
        self.fields['volume'].widget.attrs['placeholder'] = '55% від об\'єму сировини'

        # Add a hidden input field for 'frame'
        self.fields['frame'].widget = forms.HiddenInput()

        # Check if RawMaterial objects exist
        if not raw_material_queryset.exists():
            self.empty_raw_material_message = "Додайте сировину"

    def save(self, commit=True):
        cutting_record = super().save(commit=False)

        # Set the raw_material field to the selected raw material
        raw_material = self.cleaned_data['raw_material']
        cutting_record.raw_material = raw_material

        # If volume is not specified, calculate it as 55% of the raw_material volume
        if not cutting_record.volume:
            cutting_record.volume = round(raw_material.volume * 0.55, 2)

        # Call the parent class's save() method to save the record to the database
        if commit:
            cutting_record.save()

        return cutting_record

    class Meta:
        model = CuttingRecord
        fields = ['frame', 'created', 'raw_material', 'volume', 'note']
        widgets = {
            'created': DateInput(),
        }


class BoardCreationForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['length', 'width', 'height', 'quantity', 'wood_type']


class BoardEditForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['length', 'width', 'height', 'quantity', 'wood_type']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'  # Include all fields in the form


# class CuttingRecordForm(forms.ModelForm):
#     volume = forms.DecimalField(max_digits=5, decimal_places=2)
#     lengths = forms.CharField(max_length=100)
#
#     # Додайте поля для форми порізки
#     class Meta:
#         model = CuttingRecord
#         fields = '__all__'
#
#
# class SawdustForm(forms.ModelForm):
#     delivery_day = forms.DateField()
#     volume = forms.FloatField()
#     customer = forms.CharField(max_length=100)
#     price = forms.DecimalField(max_digits=8, decimal_places=2)
#
#     class Meta:
#         model = Sawdust
#         fields = '__all__'
#
#
# class GraftForm(forms.ModelForm):
#     delivery_day = forms.DateField()
#     volume = forms.FloatField()
#     customer = forms.CharField(max_length=100, )
#     price = forms.DecimalField(max_digits=8, decimal_places=2)
#
#     class Meta:
#         model = Graft
#         fields = '__all__'
#
#
# class PalletsForm(forms.ModelForm):
#     delivery_day = forms.DateField()
#     size = forms.CharField(max_length=50)
#     quantity = forms.IntegerField(min_value=1)
#     block_quantity = forms.IntegerField()
#
#     class Meta:
#         model = Pallets
#         fields = '__all__'

class ClientContactForm(forms.ModelForm):
    class Meta:
        model = ClientContact
        fields = "__all__"


# ----------------------------------------------------------------- CompletedActs
class CompletedActForm(forms.ModelForm):
    class Meta:
        model = CompletedAct
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))

        # Додайте віджет для вибору дати до полі transport_date
        self.fields['transport_date'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['driver'].queryset = CustomUser.objects.filter(role="DRIVER")
