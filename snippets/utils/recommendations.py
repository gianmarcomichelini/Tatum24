from collections import defaultdict
from django.db.models import Q

from ratings.models import Rating
from snippets.models import Snippet


def get_similar_snippets(current_snippet, user=None, top_n=5):
    """
    Computes a weighted similarity score based on tags, language, and ratings.
    """
    current_tags = current_snippet.get_normalized_tags()
    if not current_tags:
        return Snippet.objects.none()

    # Heuristic filtering: find snippets that share at least one tag or the same language
    # Also, exclude snippets by the current user
    candidate_snippets = Snippet.objects.exclude(pk=current_snippet.pk)
    if user and user.is_authenticated:
        candidate_snippets = candidate_snippets.exclude(author=user)

    candidate_snippets = candidate_snippets.filter(
        Q(language=current_snippet.language) |
        Q(tags__icontains=list(current_tags)[0])
    )

    scored_snippets = defaultdict(float)

    # 1. Tag and Language Scoring
    for snippet in candidate_snippets:
        score = 0

        # Tag overlap: count shared tags
        other_tags = snippet.get_normalized_tags()
        shared_tags_count = len(current_tags & other_tags)

        if shared_tags_count > 0:
            score += shared_tags_count * 1.5  # Weight tag similarity heavily

        # Language match: boost if it's the same language
        if snippet.language == current_snippet.language:
            score += 3.0  # Give a significant boost for language match

        scored_snippets[snippet] += score

    # 2. Add Social Proof (Ratings)
    for snippet, score in list(scored_snippets.items()):  # use list() to iterate over a copy
        weighted_rating = snippet.get_weighted_score() * 2.0
        scored_snippets[snippet] += weighted_rating

    # 3. Add Personalized Scoring for the user
    if user and user.is_authenticated:
        # Find authors of snippets the user has liked
        liked_authors_ids = user.ratings.filter(rating='like').values_list('snippet__author_id', flat=True)

        for snippet, score in list(scored_snippets.items()):
            if snippet.author_id in liked_authors_ids:
                scored_snippets[snippet] += 1.0  # Boost if the author is one the user has liked before

    # Sort and return the top N
    sorted_scored = sorted(scored_snippets.items(), key=lambda item: item[1], reverse=True)
    return [snippet for snippet, score in sorted_scored[:top_n]]


# New function for user-based recommendations on the list page
def get_user_recommendations(user, top_n=5):
    """
    Generates recommendations for a user based on their past likes and dislikes.
    This is a simple content-based approach.
    """
    # Get all snippets the user has liked
    liked_snippets = Snippet.objects.filter(ratings__user=user, ratings__rating=Rating.LIKE)

    # If the user has not liked anything, return popular snippets
    if not liked_snippets:
        return Snippet.objects.order_by('-ratings__rating')[:top_n]

    # Aggregate tags from liked snippets
    user_tags = set()
    for snippet in liked_snippets:
        user_tags.update(snippet.get_normalized_tags())

    if not user_tags:
        return Snippet.objects.none()

    # Find snippets that match the user's preferred tags
    # Start with a simple OR filter on all tags
    query = Q()
    for tag in user_tags:
        query |= Q(tags__icontains=tag)

    # Exclude snippets the user has already interacted with AND snippets written by the user
    rated_snippet_ids = user.ratings.values_list('snippet_id', flat=True)

    candidate_snippets = Snippet.objects.exclude(pk__in=rated_snippet_ids).exclude(author=user).filter(query)

    # Score the candidates based on tag overlap and other factors
    scored_snippets = defaultdict(float)
    for snippet in candidate_snippets:
        score = 0
        other_tags = snippet.get_normalized_tags()
        shared_tags_count = len(user_tags & other_tags)

        if shared_tags_count > 0:
            score += shared_tags_count * 2.0  # Heavier weight for shared tags

        # You can add other factors here, like popularity, recency, etc.
        scored_snippets[snippet] += score

    # Sort and return the top N
    sorted_scored = sorted(scored_snippets.items(), key=lambda item: item[1], reverse=True)
    return [snippet for snippet, score in sorted_scored[:top_n]]