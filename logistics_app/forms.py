from django import forms
from .models import Booking, Container, Location, ContainerDamagePhoto
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class BookingCreateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'booking_number',
            'vessel_name',
            'voyage',
            'pol',
            'pod',
            'etd',
            'eta',
            'free_time_until',
            'forwarder',
            'cargo_description',
            'remarks',
        ]
        widgets = {
            'etd': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'eta': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'booking_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vessel_name': forms.TextInput(attrs={'class': 'form-control'}),
            'voyage': forms.TextInput(attrs={'class': 'form-control'}),
            'pol': forms.TextInput(attrs={'class': 'form-control'}),
            'pod': forms.TextInput(attrs={'class': 'form-control'}),
            'free_time_until': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'forwarder': forms.Select(attrs={'class': 'form-control'}),
            'cargo_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['forwarder'].queryset = User.objects.filter(is_staff=False).order_by('username')


class BookingUpdateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['shipper', 'consignee', 'notify_party', 'cargo_description', 'remarks']
        widgets = {
            'shipper': forms.TextInput(attrs={'class': 'form-control'}),
            'consignee': forms.TextInput(attrs={'class': 'form-control'}),
            'notify_party': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ContainerCreateForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ['container_number', 'container_type', 'status', 'current_location', 'payload', 'remarks',]
        widgets = {
            'container_number': forms.TextInput(attrs={'class': 'form-control'}),
            'container_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'current_location': forms.Select(attrs={'class': 'form-control'}),
            'payload': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ContainerUpdateForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ['cargo_weight', 'tare_weight', 'status', 'remarks']
        widgets = {
            'cargo_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tare_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        cargo_weight = cleaned_data.get('cargo_weight')
        payload = self.instance.payload

        if cargo_weight is not None and payload is not None and cargo_weight > payload:
            self.add_error(
                'cargo_weight',
                f'Вага вантажу: ({cargo_weight}) не може бути більше, ніж Payload: ({payload})!'
            )

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ContainerDamagePhotoForm(forms.ModelForm):
    class Meta:
        model = ContainerDamagePhoto
        fields = ['image', 'description']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }