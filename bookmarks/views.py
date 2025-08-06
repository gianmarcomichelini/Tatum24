from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib import messages

from snippets.models import Snippet
from bookmarks.models import Bookmark


@login_required
def AddBookmarkView(request, snippet_id):
    snippet = get_object_or_404(Snippet, pk=snippet_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, snippet=snippet)
    if created:
        messages.success(request, 'Snippet bookmarked successfully.')
    else:
        messages.info(request, 'Snippet was already bookmarked.')
    return HttpResponseRedirect(snippet.get_absolute_url())


@login_required
def DeleteBookmarkView(request, snippet_id):
    snippet = get_object_or_404(Snippet, pk=snippet_id)
    if request.method == "POST":
        if snippet.bookmarks.filter(user=request.user).exists():
            Bookmark.objects.filter(user=request.user, snippet=snippet).delete()
            messages.success(request, 'Snippet removed from bookmarks successfully.')
        else:
            messages.info(request, 'Snippet was not bookmarked.')
    return redirect('/bookmarks/user-bookmarks/')

class UserBookmarksListView(ListView):
    model = Bookmark
    template_name = 'bookmarks/templates/bookmark/user_bookmarks.html'
    context_object_name = 'bookmarks'
    paginate_by = 10

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class MostBookmarkedView(ListView):
    model = Snippet
    template_name = 'bookmarks/templates/bookmark/most_bookmarked.html'
    context_object_name = 'most_bookmarked_list'
    paginate_by = 10

    def get_queryset(self):
        return Snippet.objects.annotate(
            bookmark_count=Count('bookmarks')
        ).order_by('-bookmark_count')[:3]