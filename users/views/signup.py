from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import FormView

from users.models import Profile
from users.forms.signup_form import SignupForm
from django.urls import reverse_lazy

class SignupView(FormView):
    template_name = 'users/templates/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Create the user from the form data
        user = form.save()

        # Manually authenticate and log in the new user
        login(self.request, user)

        # Create a profile for the new user
        Profile.objects.get_or_create(user=user)

        messages.success(self.request, 'Signup successful. Welcome to our community!')
        return super().form_valid(form)

    def form_invalid(self, form):
        # Consistent with the profile_update_view's implicit best practice,
        # we will rely on the form's field-specific errors instead of a
        # redundant generic error message.
        # messages.error(self.request, 'There was an error with your submission. Please correct the fields below.')

        # Re-render the form with the specific field errors.
        return super().form_invalid(form)