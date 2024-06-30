from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseBadRequest

from ratings.models import Rating
from snippets.models import Snippet


@login_required
def RateSnippetView(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)
    user = request.user

    if request.method == 'POST':
        rating_value = request.POST.get('rating')

        # Check if the rating value is valid
        if rating_value not in [Rating.LIKE, Rating.DISLIKE]:
            return HttpResponseBadRequest("Invalid rating value")

        # Check if the user has already rated this snippet
        if snippet.has_user_rated(user):
            # Update existing rating if user has already rated
            rating = snippet.ratings.get(user=user)
            rating.rating = rating_value
            rating.save()
        else:
            # Create new rating if user has not rated before
            rating = Rating.objects.create(snippet=snippet, user=user, rating=rating_value)

        # Redirect to the snippet detail page after rating
        return redirect('snippet_detail', pk=pk)
    else:
        return HttpResponseBadRequest("Only POST method is allowed for rating snippets")


def TopRatedSnippetsView(request):
    # Annotate each Snippet with counts of likes and dislikes
    top_snippets = Snippet.objects.annotate(
        total_likes=Count('ratings', filter=Q(ratings__rating='like')),
        total_dislikes=Count('ratings', filter=Q(ratings__rating='dislike'))
    ).annotate(
        # Calculate popularity_score as the difference between total_likes and total_dislikes
        popularity_score=F('total_likes') - F('total_dislikes')
    ).order_by('-popularity_score')[:10]  # Retrieve the top 10 snippets based on popularity_score

    popularity_score_arr = []

    for snippet in top_snippets:
        popularity_score = snippet.popularity_score
        if snippet.popularity_score <= 0:
            continue
        popularity_score_arr.append({  # Constructs a dictionary and appends it to "popularity_score_arr"
            'snippet': snippet,
            'popularity_score': popularity_score
        })

    context = {
        'top_snippets': popularity_score_arr  # Uses the correct array with best snippets
    }
    return render(request, 'ratings/templates/top_rated_snippets.html', context)
