from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy

from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import BookingCreateForm, BookingUpdateForm, ContainerCreateForm, ContainerUpdateForm, LoginForm, RegisterForm, ContainerDamagePhotoForm
from .models import Booking, Container, Location, ContainerDamagePhoto
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone
from django.db.models import Count

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'logistics_app/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all().select_related('forwarder', 'created_by')
        return Booking.objects.filter(forwarder=self.request.user).select_related('forwarder', 'created_by')


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'logistics_app/booking_detail.html'
    context_object_name = 'booking'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        queryset = Booking.objects.select_related('forwarder', 'created_by').prefetch_related('containers')
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(forwarder=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['containers'] = self.object.containers.select_related('current_location').prefetch_related('damage_photos')
        return context


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingCreateForm
    template_name = 'logistics_app/booking_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.created_by = self.request.user
        booking.save()
        self.object = booking
        return redirect('booking_detail', pk=booking.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Booking'
        return context


class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    template_name = 'logistics_app/booking_form.html'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(forwarder=self.request.user)

    def get_form_class(self):
        if self.request.user.is_staff:
            return BookingCreateForm
        return BookingUpdateForm

    def get_success_url(self):
        return reverse_lazy('booking_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Booking'
        context['booking'] = self.object
        return context


class ContainerCreateView(LoginRequiredMixin, CreateView):
    model = Container
    form_class = ContainerCreateForm
    template_name = 'logistics_app/container_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        self.booking = get_object_or_404(Booking, pk=self.kwargs['booking_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        container = form.save(commit=False)
        container.booking = self.booking
        container.save()
        self.object = container
        return redirect('booking_detail', pk=self.booking.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Add Container to {self.booking.booking_number}'
        context['booking'] = self.booking
        return context


class ContainerUpdateView(LoginRequiredMixin, UpdateView):
    model = Container
    template_name = 'logistics_app/container_form.html'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        queryset = Container.objects.select_related('booking', 'current_location')
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(booking__forwarder=self.request.user)

    def get_form_class(self):
        if self.request.user.is_staff:
            return ContainerCreateForm
        return ContainerUpdateForm

    def get_success_url(self):
        return reverse_lazy('booking_detail', kwargs={'pk': self.object.booking.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Container {self.object.container_number}'
        context['container'] = self.object
        return context


class LocationDetailView(LoginRequiredMixin, DetailView):
    model = Location
    template_name = 'logistics_app/location_detail.html'
    context_object_name = 'location'

    def get_queryset(self):
        return Location.objects.all().order_by('name')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'logistics_app/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_staff:
            containers = Container.objects.select_related('booking', 'current_location').all()
        else:
            containers = Container.objects.select_related('booking', 'current_location').filter(
                booking__forwarder=self.request.user
            )

        total_containers = containers.count()

        overdue_containers = containers.filter(booking__free_time_until__lt=timezone.localdate()).count()

        containers_by_status = (
            containers.values('status')
            .annotate(total=Count('id'))
            .order_by('status')
        )

        containers_by_location = (
            containers.values('current_location__name')
            .annotate(total=Count('id'))
            .order_by('current_location__name')
        )

        context.update({
            'total_containers': total_containers,
            'overdue_containers': overdue_containers,
            'containers_by_status': containers_by_status,
            'containers_by_location': containers_by_location,
        })

        return context


class ContainerDamagePhotoCreateView(LoginRequiredMixin, CreateView):
    model = ContainerDamagePhoto
    form_class = ContainerDamagePhotoForm
    template_name = 'logistics_app/container_damage_photo_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.container = get_object_or_404(Container.objects.select_related('booking'), pk=self.kwargs['container_pk'])

        if not request.user.is_staff and self.container.booking.forwarder != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        photo = form.save(commit=False)
        photo.container = self.container
        photo.save()
        self.object = photo
        messages.success(self.request, 'Damage photo uploaded successfully.')
        return redirect('booking_detail', pk=self.container.booking.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Add damage photo for {self.container.container_number}'
        context['container'] = self.container
        return context


def login_view(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'registration/login.html', {'form': form})

    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Вітаємо, {username}')
                return redirect('booking_list')
            else:
                form.add_error(None, 'Невірний логін або пароль')
    return render(request, 'registration/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('booking_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            forwarders_group, created = Group.objects.get_or_create(name='Forwarders')
            user.groups.add(forwarders_group)

            login(request, user)
            messages.success(request, 'Реєстрація успішна. Ви увійшли як експедитор.')
            return redirect('booking_list')

    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Ви вийшли з системи')
    return redirect('login')