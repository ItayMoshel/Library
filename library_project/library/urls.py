from django.urls import path
from .views import BookList, UserRegistrationView

urlpatterns = [
    path('api/books/', BookList.as_view(), name='book-list-api'),
    path('api/register/', UserRegistrationView.as_view(), name='user-registration'),
]
