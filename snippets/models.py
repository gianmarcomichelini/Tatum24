from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from markdown import markdown
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from pygments.lexers import get_lexer_by_name

from ratings.models import Rating


class Language(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    language_code = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('language_detail', kwargs={'slug': self.slug})

    def get_lexer(self):
        return get_lexer_by_name(self.language_code)


class Snippet(models.Model):
    title = models.CharField(max_length=255)
    language = models.ForeignKey(Language, related_name='snippets', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='snippets', on_delete=models.CASCADE)
    description = models.TextField()
    description_html = models.TextField(editable=False)
    code = models.TextField()
    highlighted_code = models.TextField(editable=False)
    pub_date = models.DateTimeField(default=timezone.now, editable=False)
    update_date = models.DateTimeField(default=timezone.now, editable=False)
    tags = models.CharField(max_length=255, default='')

    class Meta:
        ordering = ['-update_date', '-pub_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pub_date = timezone.now()
        self.update_date = timezone.now()
        self.description_html = markdown(self.description)
        self.highlighted_code = self.highlight()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('snippet_detail', kwargs={'pk': self.pk})

    def highlight(self):
        return highlight(self.code, self.language.get_lexer(), HtmlFormatter(linenos=False))

    def get_likes(self):
        return self.ratings.filter(rating=Rating.LIKE).count()

    def get_dislikes(self):
        return self.ratings.filter(rating=Rating.DISLIKE).count()

    def has_user_rated(self, user):
        return self.ratings.filter(user=user).exists()

    def get_comments(self):
        return self.comments.all()


class Comment(models.Model):
    snippet = models.ForeignKey(Snippet, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    pub_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.snippet.title}'

    def get_absolute_url(self):
        return self.snippet.get_absolute_url()