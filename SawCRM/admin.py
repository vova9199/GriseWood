from django.contrib import admin

# Register your models here.
from .models import Staff, Order, RawMaterialBatch, RawMaterial, CuttingRecord, Frame, ReceiptPhoto

admin.site.register(Staff)
admin.site.register(RawMaterialBatch)
admin.site.register(Frame)
admin.site.register(Order)
admin.site.register(RawMaterial)
admin.site.register(CuttingRecord)


class ReceiptPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch', 'image', 'image_preview',)
    search_fields = ('batch__series',)  # Додаємо можливість пошуку за серією партії

    def image_preview(self, obj):
        # Виводимо зображення прев'ю в адмінці
        return obj.image.url if obj.image else ''

    image_preview.allow_tags = True
    image_preview.short_description = 'Прев\'ю зображення'


admin.site.register(ReceiptPhoto, ReceiptPhotoAdmin)
