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


class SnippetListView(ListView):
    model = Snippet
    template_name = 'snippets/snippet_list.html'
    context_object_name = 'snippets'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        return context


class AddSnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ['title', 'code', 'description', 'language', 'tags']  # metti solo i campi utilizzati


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