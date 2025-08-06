from django import forms
from django.contrib.auth.models import User
from users.models import Profile


class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email")
    image = forms.ImageField(widget=forms.FileInput, required=False)

    class Meta:
        model = Profile
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email

        # You can add the form-control class here to be sure it's applied
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance and self.instance.user:
            if User.objects.exclude(pk=self.instance.user.pk).filter(email=email).exists():
                raise forms.ValidationError("This email is already in use. Please choose another.")
        return email

    def save(self, commit=True):
        profile = super(UserProfileForm, self).save(commit=False)
        if self.instance and self.instance.user:
            user = self.instance.user
            user.email = self.cleaned_data['email']
            user.save()
        if commit:
            profile.save()
        return profile