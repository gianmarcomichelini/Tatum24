from snippets.models import Snippet
from users.forms.modify_profile_form import UserProfileForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from users.models import Profile


@login_required
def profile_view(request):
    """
    Renders the user's profile page.
    Moderators see all snippets, normal users see only their own.
    """
    user = request.user

    # Determine the template and snippets based on user group
    if user.groups.filter(name='Moderator').exists():
        template_name = 'users/templates/profile/moderator_profile.html'
        # Optimize query for moderators
        snippets = Snippet.objects.select_related('author').order_by('author__username')
    else:
        template_name = 'users/templates/profile/normal_profile.html'
        snippets = Snippet.objects.filter(author=user)

    context = {
        'user': user,
        'snippets': snippets,
    }
    return render(request, template_name, context)


@login_required
def profile_update_view(request):
    """
    Handles the profile update form for a user.
    """
    # Use request.user.profile to get the profile. Django's OneToOneField
    # will create it on first access if it doesn't exist, preventing a
    # DoesNotExist error. If you're not using OneToOne, your get_or_create is fine.
    user_profile = request.user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            # The form is invalid, so let the template render the specific errors.
            # No need for a generic error message here.
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        'form': form,
    }
    return render(request, 'users/templates/profile/profile_update.html', context)