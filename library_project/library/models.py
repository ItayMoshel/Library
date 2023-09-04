from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(blank=True)

    groups = models.ManyToManyField(Group, verbose_name=_("groups"), blank=True, related_name="custom_users")
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        related_name="custom_users",
    )

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    authors = models.ManyToManyField(Author)
    genre = models.ManyToManyField(Category)
    publication_date = models.DateField(blank=True, null=True)
    publication_date_str = models.CharField(max_length=20, blank=True,
                                            null=True)
    isbn = models.CharField(max_length=13)
    cover_image_url = models.URLField()
    external_link = models.URLField()
    users_own = models.ManyToManyField(CustomUser, related_name='owned_books', blank=True)
    users_want_to_buy = models.ManyToManyField(CustomUser, related_name='books_wanted_to_buy', blank=True)
    language = models.CharField(max_length=50)
    page_count = models.PositiveIntegerField(null=True, default=None)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    publisher = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    authors = models.ManyToManyField(Author)
    content = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.book.title}"
