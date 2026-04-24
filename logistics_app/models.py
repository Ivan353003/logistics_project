from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    working_hours = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    booking_number = models.CharField(max_length=20, unique=True)
    shipper = models.CharField(max_length=150)
    consignee = models.CharField(max_length=150)
    notify_party = models.CharField(max_length=150)

    vessel_name = models.CharField(max_length=100, blank=True, null=True)
    voyage = models.CharField(max_length=10, blank=True, null=True)
    pol = models.CharField(max_length=100, verbose_name='Port of Loading')
    pod = models.CharField(max_length=100, verbose_name='Port of Discharge')
    etd = models.DateField(blank=True, null=True)
    eta = models.DateField(blank=True, null=True)

    free_time_until = models.DateField(blank=True, null=True)

    cargo_description = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_bookings')
    forwarder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_bookings')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.booking_number


class Container(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('issued', 'Issued'),
        ('picked_up', 'Picked Up'),
        ('loaded', 'Loaded Full'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered Full'),
        ('empty_returned', 'Empty Returned'),
    ]

    TYPE_CHOICES = [
        ('20DV', '20DV'),
        ('40DV', '40DV'),
        ('40HC', '40HC'),
        ('40HR', '40HR'),
    ]

    container_number = models.CharField(max_length=15, unique=True)
    container_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='containers')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    current_location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True, related_name='containers')

    cargo_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tare_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payload = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.container_number

    @property
    def gross_weight(self):
        cargo = self.cargo_weight or 0
        tare = self.tare_weight or 0
        return cargo + tare

    @property
    def is_overdue(self):
        if self.booking.free_time_until:
            return self.booking.free_time_until < timezone.localdate()
        return False


class ContainerDamagePhoto(models.Model):
    container = models.ForeignKey(Container, on_delete=models.CASCADE, related_name='damage_photos')
    image = models.ImageField(upload_to='damage_photos/')
    description = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Damage photo for {self.container.container_number}'