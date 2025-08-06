from django.contrib.auth.models import User
from snippets.models import Language, Snippet
from django.db import connection

# Get or create language Python
language, _ = Language.objects.get_or_create(
    slug='python',
    defaults={'name': 'Python', 'language_code': 'python'}
)

author = User.objects.first()
if not author:
    raise Exception("Create at least one user before running this script")

snippets_data = [
    {
        'title': 'Hello World in Python',
        'description': 'A simple hello world program',
        'code': 'print("Hello, World!")',
        'tags': 'python,beginner,syntax,print'
    },
    {
        'title': 'List Comprehension',
        'description': 'Create a list with squares using list comprehension',
        'code': '[x**2 for x in range(10)]',
        'tags': 'python,list-comprehension,loops,functional-programming'
    },
    {
        'title': 'Read File in Python',
        'description': 'Open and read a file safely with context manager',
        'code': 'with open("file.txt") as f:\n    content = f.read()',
        'tags': 'python,file-io,context-manager,best-practices'
    },
    {
        'title': 'Lambda Function',
        'description': 'Example of anonymous lambda function',
        'code': 'add = lambda x, y: x + y\nprint(add(2, 3))',
        'tags': 'python,lambda,functional-programming,anonymous-function'
    },
    {
        'title': 'Dictionary Comprehension',
        'description': 'Create a dictionary from two lists using comprehension',
        'code': '{k: v for k, v in zip(keys, values)}',
        'tags': 'python,dictionary,comprehension,data-structures'
    },
    {
        'title': 'Exception Handling',
        'description': 'Basic try-except block example',
        'code': 'try:\n    1/0\nexcept ZeroDivisionError:\n    print("Cannot divide by zero")',
        'tags': 'python,exceptions,error-handling,try-except'
    },
    {
        'title': 'Class Definition',
        'description': 'Basic Python class with constructor and method',
        'code': 'class Person:\n    def __init__(self, name):\n        self.name = name\n    def greet(self):\n        print(f"Hello, {self.name}")',
        'tags': 'python,oop,class,methods,constructors'
    },
    {
        'title': 'Decorators',
        'description': 'Simple decorator example to log function calls',
        'code': 'def log(func):\n    def wrapper(*args, **kwargs):\n        print(f"Calling {func.__name__}")\n        return func(*args, **kwargs)\n    return wrapper',
        'tags': 'python,decorators,functions,meta-programming'
    },
    {
        'title': 'Using Generators',
        'description': 'Generator function example with yield keyword',
        'code': 'def countdown(n):\n    while n > 0:\n        yield n\n        n -= 1',
        'tags': 'python,generators,yield,iterators,memory-efficiency'
    },
    {
        'title': 'Multithreading Example',
        'description': 'Basic multithreading using threading.Thread',
        'code': 'import threading\n\ndef worker():\n    print("Worker thread")\n\nthread = threading.Thread(target=worker)\nthread.start()\nthread.join()',
        'tags': 'python,multithreading,concurrency,threading,parallelism'
    }
]

# Delete existing snippets for this language and author
Snippet.objects.filter(language=language, author=author).delete()

# Reset SQLite auto-increment primary key counter
with connection.cursor() as cursor:
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='snippets_snippet';")

# Insert new snippets
for data in snippets_data:
    snippet = Snippet.objects.create(
        title=data['title'],
        language=language,
        author=author,
        description=data['description'],
        code=data['code'],
        tags=data['tags'],
    )
    print(f'Created snippet: {data["title"]}')