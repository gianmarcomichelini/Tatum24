import os
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.staticfiles import finders
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import logging

from snippets.models import Snippet

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_static_content(path):
    """
    Helper function to get the content of a static file.
    It uses Django's staticfiles finders to work in both dev and production.
    """
    try:
        # The finders.find() function will return the absolute path to the file.
        static_file_path = finders.find(path)
        if static_file_path:
            with open(static_file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        logger.error(f"Error loading static file '{path}': {e}")
    return ""


def render_to_pdf(template_src, context_dict={}):
    """
    A helper function to render a Django template to a PDF file.
    This encapsulates the pisa logic, making the view cleaner.
    """
    template = render_to_string(template_src, context_dict)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(template, dest=response)
    if pisa_status.err:
        return None, pisa_status.err
    return response, None


@login_required
def download_pdf_view(request, snippet_id):
    """
    A view to generate and download a PDF of a code snippet.
    """
    snippet = get_object_or_404(Snippet, pk=snippet_id)

    # Use the pre-highlighted code directly from the model, avoiding redundant work.
    # Get the CSS content from your static file to be inlined.
    pygments_css = get_static_content('css/pygments.css')

    if not pygments_css:
        messages.error(request, "Pygments CSS file could not be found.")
        return redirect('snippet_detail', pk=snippet_id)

    context = {
        'snippet': snippet,
        'pygments_css': pygments_css,  # Pass the CSS content to the template
    }

    pdf_response, err = render_to_pdf('snippets/snippet_pdf.html', context)

    if err:
        # Log the error for debugging purposes
        logger.error(f"PDF generation error for snippet {snippet_id}: {err}")

        # Provide a friendly error message to the user and redirect
        messages.error(request, "Sorry, we couldn't generate the PDF. Please try again later.")
        return redirect('snippet_detail', pk=snippet_id)

    # Set the filename for the downloaded PDF
    pdf_response['Content-Disposition'] = f'attachment; filename="{snippet.title}.pdf"'

    return pdf_response