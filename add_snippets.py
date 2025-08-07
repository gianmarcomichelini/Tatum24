#  python manage.py shell < add_snippets.py
from django.contrib.auth.models import User
from django.db import connection
from snippets.models import Language, Snippet
from ratings.models import Rating
from snippets.utils.recommendations import get_similar_snippets, get_user_recommendations

# 1. Define and get users and languages
try:
    gim = User.objects.get(username='gim')
    franco = User.objects.get(username='franco')
    dc = User.objects.get(username='dc')
    users = [gim, franco, dc]
    print("✅ Found existing users: gim, franco, dc")
except User.DoesNotExist:
    raise Exception("Please create users 'gim', 'franco', and 'dc' before running this script.")

python, _ = Language.objects.get_or_create(slug='python', defaults={'name': 'Python', 'language_code': 'python'})
javascript, _ = Language.objects.get_or_create(slug='javascript',
                                               defaults={'name': 'JavaScript', 'language_code': 'javascript'})
go, _ = Language.objects.get_or_create(slug='go', defaults={'name': 'Go', 'language_code': 'go'})
java, _ = Language.objects.get_or_create(slug='java', defaults={'name': 'Java', 'language_code': 'java'})
ruby, _ = Language.objects.get_or_create(slug='ruby', defaults={'name': 'Ruby', 'language_code': 'ruby'})
rust, _ = Language.objects.get_or_create(slug='rust', defaults={'name': 'Rust', 'language_code': 'rust'})
languages = [python, javascript, go, java, ruby, rust]
print("✅ Found or created languages: Python, JavaScript, Go, Java, Ruby, Rust")

# 2. Clean slate
Snippet.objects.all().delete()
Rating.objects.all().delete()
with connection.cursor() as cursor:
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='snippets_snippet';")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='ratings_rating';")
print("✅ Cleaned database.")

# 3. Create diverse snippets
snippets_data = [
    # Python Snippets (by gim)
    {'title': 'Python Loop', 'language': python, 'author': gim, 'tags': 'python,loops,beginner',
     'code': 'for i in range(5): pass'},
    {'title': 'Python Decorator', 'language': python, 'author': gim, 'tags': 'python,decorators,advanced',
     'code': 'def decorator(func): return func'},
    # JavaScript Snippets (by franco)
    {'title': 'JS Arrow Function', 'language': javascript, 'author': franco, 'tags': 'javascript,es6,functions',
     'code': 'const add = (a, b) => a + b;'},
    {'title': 'JS Async/Await', 'language': javascript, 'author': franco, 'tags': 'javascript,async,promises',
     'code': 'async function fetchData() {}'},
    # Go Snippets (by dc)
    {'title': 'Go HTTP Server', 'language': go, 'author': dc, 'tags': 'go,http,server',
     'code': 'http.HandleFunc("/hello", func) ...'},
    # Java Snippets (by franco)
    {'title': 'Java For Loop', 'language': java, 'author': franco, 'tags': 'java,loops,collections',
     'code': 'for (String s : list) {}'},
    # Ruby Snippets (by gim)
    {'title': 'Ruby Blocks', 'language': ruby, 'author': gim, 'tags': 'ruby,blocks,iterators',
     'code': '[1, 2, 3].each { |n| puts n }'},
    # Rust Snippets (by dc)
    {'title': 'Rust Ownership', 'language': rust, 'author': dc, 'tags': 'rust,ownership,memory-management',
     'code': 'fn main() { let s1 = String::from("hello"); let s2 = s1; }'},
    # Mix of languages and tags to test similarity
    {'title': 'Go Goroutines', 'language': go, 'author': franco, 'tags': 'go,concurrency,async',
     'code': 'go func() {}()'},
    {'title': 'Python Generators', 'language': python, 'author': dc, 'tags': 'python,generators,iterators,advanced',
     'code': 'def gen(): yield 1'},
    {'title': 'JS Array Map', 'language': javascript, 'author': gim,
     'tags': 'javascript,arrays,es6,functional-programming', 'code': 'arr.map(x => x * 2);'},
    {'title': 'Java Streams', 'language': java, 'author': dc, 'tags': 'java,streams,functional-programming',
     'code': 'list.stream().filter(x -> x > 5).collect(Collectors.toList());'},
    {'title': 'Ruby Rails Helper', 'language': ruby, 'author': franco, 'tags': 'ruby,rails,helpers',
     'code': 'def my_helper; "hello"; end'},
    {'title': 'Rust Traits', 'language': rust, 'author': gim, 'tags': 'rust,traits,generics',
     'code': 'trait MyTrait { fn my_func(); }'},
]

created_snippets = []
for data in snippets_data:
    snippet = Snippet.objects.create(**data)
    created_snippets.append(snippet)
    print(f'✅ Created snippet: {data["title"]} by {data["author"].username}')

# 4. Create sample ratings to influence recommendations
Rating.objects.create(user=gim, snippet=created_snippets[1], rating=Rating.LIKE)  # gim likes 'Python Decorator'
Rating.objects.create(user=gim, snippet=created_snippets[2], rating=Rating.LIKE)  # gim likes 'JS Arrow Function'
Rating.objects.create(user=franco, snippet=created_snippets[0], rating=Rating.LIKE)  # franco likes 'Python Loop'
Rating.objects.create(user=franco, snippet=created_snippets[6], rating=Rating.LIKE)  # franco likes 'Python Generators'
Rating.objects.create(user=dc, snippet=created_snippets[2], rating=Rating.LIKE)  # dc likes 'JS Arrow Function'
Rating.objects.create(user=dc, snippet=created_snippets[5], rating=Rating.DISLIKE)  # dc dislikes 'Go Goroutines'
print("✅ Created sample ratings.")

# 5. Test recommendations
print("\n🔍 Testing RECOMMENDATIONS\n" + "-" * 50)

# --- Test get_similar_snippets (Content-based on a single snippet) ---
print("\n--- Testing `get_similar_snippets` (content-based) ---")

# Test recommendations for user 'gim'
print("\n--- Snippet-based Recommendations for GIM ---")
current_snippet_gim = created_snippets[0]  # The 'Python Loop' snippet
print(f"Base Snippet: {current_snippet_gim.title} by {current_snippet_gim.author.username}")
recommendations_gim = get_similar_snippets(current_snippet_gim, user=gim, top_n=3)
for rec in recommendations_gim:
    print(f'  → {rec.title} (tags: {rec.tags}, author: {rec.author.username})')

# Test recommendations for user 'franco'
print("\n--- Snippet-based Recommendations for FRANCO ---")
current_snippet_franco = created_snippets[3]  # The 'JS Async/Await' snippet
print(f"Base Snippet: {current_snippet_franco.title} by {current_snippet_franco.author.username}")
recommendations_franco = get_similar_snippets(current_snippet_franco, user=franco, top_n=3)
for rec in recommendations_franco:
    print(f'  → {rec.title} (tags: {rec.tags}, author: {rec.author.username})')

# Test recommendations for user 'dc'
print("\n--- Snippet-based Recommendations for DC ---")
current_snippet_dc = created_snippets[4]  # The 'Go HTTP Server' snippet
print(f"Base Snippet: {current_snippet_dc.title} by {current_snippet_dc.author.username}")
recommendations_dc = get_similar_snippets(current_snippet_dc, user=dc, top_n=3)
for rec in recommendations_dc:
    print(f'  → {rec.title} (tags: {rec.tags}, author: {rec.author.username})')

# --- Test get_user_recommendations (User-based on entire history) ---
print("\n--- Testing `get_user_recommendations` (user-based) ---")

# Test user-based recommendations for 'gim'
print("\n--- User-based Recommendations for GIM ---")
print(f"Gim has liked: {created_snippets[1].title} (python) and {created_snippets[2].title} (javascript)")
user_recommendations_gim = get_user_recommendations(gim, top_n=3)
for rec in user_recommendations_gim:
    print(f'  → {rec.title} (tags: {rec.tags}, author: {rec.author.username})')

# Test user-based recommendations for 'franco'
print("\n--- User-based Recommendations for FRANCO ---")
print(f"Franco has liked: {created_snippets[0].title} (python) and {created_snippets[6].title} (ruby)")
user_recommendations_franco = get_user_recommendations(franco, top_n=3)
for rec in user_recommendations_franco:
    print(f'  → {rec.title} (tags: {rec.tags}, author: {rec.author.username})')

# Test user-based recommendations for 'dc'
print("\n--- User-based Recommendations for DC ---")
print(f"DC has liked: {created_snippets[2].title} (javascript) and disliked: {created_snippets[5].title} (java)")
user_recommendations_dc = get_user_recommendations(dc, top_n=3)
for rec in user_recommendations_dc:
    print(f'  → {rec.title} (tags: {rec.tags}, author: {rec.author.username})')