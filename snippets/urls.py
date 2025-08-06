from django.urls import path

from snippets.views.comments import add_comment_view, delete_comment_view
from snippets.views.download_pdf import download_pdf_view
from snippets.views.languages import LanguageListView, LanguageDetailView
from snippets.views.popular import TopAuthorsView, TopLanguagesView
from snippets.views.snippets import (
    SnippetListView,
    SnippetDetailView,
    AddSnippetView,
    snippet_remove_view,
    edit_snippet_view,
)

urlpatterns = [
    path('', SnippetListView.as_view(), name='snippet_list'),
]

# Snippets

urlpatterns += [
    path('<int:pk>/', SnippetDetailView.as_view(), name='snippet_detail'),
    path('add_snippet/', AddSnippetView.as_view(), name='add_snippet'),
    path('<int:pk>/remove/', snippet_remove_view, name='snippet_remove'),
    path('<int:pk>/edit/', edit_snippet_view, name='edit_snippet'),

    path('top-authors/', TopAuthorsView.as_view(), name='tatum24_top_authors'),
]

# Languages

urlpatterns += [
    path('languages/<slug:slug>/', LanguageDetailView.as_view(), name='language_detail'),
    path('language_list', LanguageListView.as_view(), name='language_list'),
    path('top-languages/', TopLanguagesView.as_view(), name='tatum24_top_languages'),
]

# Comments

urlpatterns += [
    path('<int:snippet_id>/add_comment/', add_comment_view, name='add_comment'),
    path('<int:comment_id>/delete-comment/', delete_comment_view, name='delete_comment'),

]

# Download pdf

urlpatterns += [
    path('snippet/<int:snippet_id>/download_pdf/', download_pdf_view, name='download_pdf'),
]
