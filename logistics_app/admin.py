from django.contrib import admin
from .models import Booking, Container, Location, ContainerDamagePhoto


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'working_hours')
    search_fields = ('name', 'address', 'contact_person')
    list_filter = ('name',)


class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_number', 'forwarder', 'created_by', 'vessel_name', 'voyage', 'pol', 'pod', 'free_time_until')
    search_fields = ('booking_number', 'shipper', 'consignee', 'notify_party')
    list_filter = ('forwarder', 'created_by', 'pol', 'pod')


class ContainerAdmin(admin.ModelAdmin):
    list_display = ('container_number', 'container_type', 'booking', 'status', 'current_location', 'cargo_weight', 'tare_weight', 'payload')
    search_fields = ('container_number',)
    list_filter = ('container_type', 'status', 'current_location')


class ContainerDamagePhotoAdmin(admin.ModelAdmin):
    list_display = ('container', 'description', 'uploaded_at')
    search_fields = ('container__container_number', 'description')


admin.site.register(Location, LocationAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Container, ContainerAdmin)
admin.site.register(ContainerDamagePhoto, ContainerDamagePhotoAdmin)