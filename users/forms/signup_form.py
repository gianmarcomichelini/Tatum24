from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError

class SignupForm(UserCreationForm):
    # UserCreationForm already includes username, password1, and password2.
    # We just need to add the email field.
    email = forms.EmailField(
        required=True,
        label="Email address",
        help_text="A valid email is required for account recovery."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use. Please choose another.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
        return user