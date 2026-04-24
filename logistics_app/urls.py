from django.urls import path
from .views import *

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    path('', BookingListView.as_view(), name='booking_list'),
    path('booking/<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path('booking/create/', BookingCreateView.as_view(), name='booking_create'),
    path('booking/<int:pk>/edit/', BookingUpdateView.as_view(), name='booking_update'),

    path('booking/<int:booking_pk>/containers/create/', ContainerCreateView.as_view(), name='container_create'),
    path('container/<int:pk>/edit/', ContainerUpdateView.as_view(), name='container_update'),
    path('location/<int:pk>/', LocationDetailView.as_view(), name='location_detail'),

    path('container/<int:container_pk>/damage-photo/add/', ContainerDamagePhotoCreateView.as_view(), name='container_damage_photo_create'),

    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]