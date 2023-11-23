from django.conf.urls.static import static
from django.urls import path

from GriseWood import settings
from SawCRM import views
from SawCRM.views import RawMaterialBatchDetailView, BatchPhotoView, PhotoDeleteView

urlpatterns = [

    # path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    # path('buh/', views.buh_page, name='buh_page'),
    # path('inzh/', views.inzh_page, name='inzh_page'),
    # path('director/', views.director_page, name='director_page'),

    path('logout/', views.logout_user, name='logout'),


    # path('media/photos/<int:pk>/', views.view_batch_photo, name='view_batch_photo'),
    path('raw_material_batch_list/', views.raw_material_batch_list, name='raw_material_batch_list'),
    path('raw_material_batch/create/', views.create_raw_material_batch, name='create_raw_material_batch'),
    path('raw_material_batch/edit/<int:pk>/', views.RawMaterialBatchDetailView.as_view(), name='edit_delete_batch'),
    path('raw_material_batch/delete/<int:pk>/', views.raw_material_batch_delete, name='delete_raw_material_batch'),
    # path('raw_material_batch/delete/<int:pk>', views.RawMaterialBatchDeleteView.as_view(), name='delete_raw_material_batch'),
    # path('raw_material_batch/batch_photo/<int:pk>/', views.view_batch_photo, name='view_batch_photo'),
    # path('rawmaterialbatch/<int:pk>/add_receipt_photo/', views.add_receipt_photo, name='add_receipt_photo'),
    # path('rawmaterialbatch/<int:pk>/delete_receipt_photo/', views.delete_receipt_photo, name='delete_receipt_photo'),
    # path('raw_material/create/without_series/', views.create_raw_material, name='create_raw_material'),
    path('raw_material/create/<int:pk>/', views.create_raw_material, name='create_raw_material'),
    # path('raw_material_batch/create/', views.create_raw_material_batch, name='create_raw_material_batch'),
    # path('raw_material/batch/<int:batch_id>/', views.create_raw_material_with_batch, name='create_raw_material_with_batch'),
    # path('raw_material/create/', views.create_raw_material, name='create_raw_material'),
    # path('raw_material/create/<int:series>/', views.create_raw_material, name='create_raw_material_with_batch'),
    # path('raw_material_batch/<int:pk>/view_batch_photos/', RawMaterialBatchDetailView.as_view(), name='view_batch_photos'),
    # path('raw_material_batch/<int:batch_id>/add_receipt_photo/', views.add_receipt_photo, name='add_receipt_photo'),
    # path('raw_material_batch/<int:batch_id>/delete_receipt_photo/<int:photo_id>/', views.delete_receipt_photo, name='delete_receipt_photo'),
    path('raw_material_batch/<int:batch_id>/view_batch_photos/', BatchPhotoView.as_view(), name='view_batch_photos'),
    path('raw_material_batch/<int:batch_id>/delete_receipt_photo/<int:photo_id>/', PhotoDeleteView.as_view(),
         name='delete_receipt_photo'),

    path('frames/', views.frames_list, name='frames_list'),
    path('frames/create/', views.create_frame, name='create_frame'),
    path('frames/<int:frame_pk>/create_cutting_record/', views.create_cutting_record, name='create_cutting_record'),
    path('frames/<int:frame_pk>/edit_delete_cutting_record/', views.edit_delete_cutting_record, name='edit_delete_cutting_record'),
    path('frames/<int:frame_pk>/edit_delete_cutting_record/<int:record_pk>/', views.edit_delete_cutting_record, name='edit_delete_cutting_record'),

    path('boards/', views.board_list, name='board_list'),
    path('boards/create/', views.create_board, name='create_board'),
    path('boards/edit/<int:board_id>/', views.edit_board, name='edit_board'),
    path('boards/delete/<int:board_id>/', views.delete_board, name='delete_board'),

    path('order_list/', views.order_list, name='order_list'),
    path('order/create', views.create_order, name='create_order'),
    path('order/<int:pk>/edit_delete_order/', views.edit_delete_order, name='edit_delete_order'),
    path('order/<int:pk>/delete_order/', views.delete_order, name='delete_order'),

    path('accounting/', views.accounting, name='accounting'),

    path('raw_material/edit/<int:pk>/', views.edit_raw_material, name='edit_raw_material'),
    path('raw_material/delete/<int:pk>/', views.delete_raw_material, name='delete_raw_material'),
    path('wood_type/create/', views.create_wood_type, name='create_wood_type'),

    path('clients/', views.client_list, name='clients'),
    path('clients/create/', views.add_client, name='add_client'),

    path('salary_list/', views.salary_list, name='salary_list')

]

