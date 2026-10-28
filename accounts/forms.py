
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user

from django import forms
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=False,
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
    )

    email = forms.EmailField(
        required=False,
    )

    class Meta:
        model = UserProfile
        fields = [
            "profile_picture",
            "bio",
            "date_of_birth",
            "location",
        ]

        widgets = {
            "bio": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Tell us a little about yourself",
            }),
            "date_of_birth": forms.DateInput(attrs={
                "type": "date",
            }),
            "location": forms.TextInput(attrs={
                "placeholder": "Your city or country",
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user

        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email

        self.fields["profile_picture"].required = False

    def save(self, commit=True):
        profile = super().save(commit=False)

        if commit:
            profile.save()

        if self.user:
            self.user.first_name = self.cleaned_data["first_name"]
            self.user.last_name = self.cleaned_data["last_name"]
            self.user.email = self.cleaned_data["email"]

            self.user.save(
                update_fields=[
                    "first_name",
                    "last_name",
                    "email",
                ]
            )

        return profile
