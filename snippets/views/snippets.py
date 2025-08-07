from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from snippets.models import Snippet
from snippets.forms.search_input_forms import SnippetSearchForm
from snippets.utils.recommendations import get_user_recommendations, get_similar_snippets


class SnippetListView(ListView):
    model = Snippet
    template_name = 'snippets/snippet_list.html'
    context_object_name = 'snippets'
    paginate_by = 20

    # Store recommended snippets in an instance variable
    recommended_snippets = None

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q', '').strip()

        # Get recommendations first if the user is authenticated
        user = self.request.user
        if user.is_authenticated:
            # We'll call the recommendation function here
            # and store the result for use in get_context_data
            self.recommended_snippets = get_user_recommendations(user, top_n=5)
            # Exclude the recommended snippets from the main queryset before pagination
            if self.recommended_snippets:
                recommended_ids = [s.pk for s in self.recommended_snippets]
                queryset = queryset.exclude(pk__in=recommended_ids)

        if query:
            queryset = queryset.filter(title__icontains=query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add the pre-fetched recommended snippets to the context
        if self.recommended_snippets:
            context['recommended_snippets'] = self.recommended_snippets

        context['search_form'] = SnippetSearchForm(self.request.GET)

        return context


class SnippetDetailView(DetailView):
    model = Snippet
    template_name = 'snippets/snippet_detail.html'
    context_object_name = 'snippet'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        snippet = self.get_object()
        user = self.request.user
        context['user'] = user
        context['bookmarked'] = user.is_authenticated and user.bookmarks.filter(snippet=snippet).exists()

        # Use the user-aware version of get_similar_snippets
        context['recommended_snippets'] = get_similar_snippets(snippet, user=user)
        return context


class AddSnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ['title', 'code', 'description', 'language', 'tags']


class AddSnippetView(LoginRequiredMixin, CreateView):
    model = Snippet
    form_class = AddSnippetForm
    template_name = 'snippets/add_snippet.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Snippet created successfully.')
        return response

    def get_success_url(self):
        return self.object.get_absolute_url()


@login_required
@require_POST
def snippet_remove_view(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    if request.user == snippet.author or request.user.groups.filter(name='Moderator').exists():
        snippet.delete()
        messages.success(request, 'Snippet deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this snippet.')
    return redirect('profile')


@login_required
def edit_snippet_view(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    if not (request.user == snippet.author or request.user.groups.filter(name='Moderator').exists()):
        messages.error(request, 'You do not have permission to edit this snippet.')
        return redirect(snippet.get_absolute_url())

    if request.method == 'POST':
        form = AddSnippetForm(request.POST, instance=snippet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Snippet modified successfully.')
            return redirect(snippet)
        else:
            messages.error(request, 'Please fill all required fields correctly.')
    else:
        form = AddSnippetForm(instance=snippet)

    return render(request, 'snippets/edit_snippet.html', {'form': form})