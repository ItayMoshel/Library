from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from .models import Book, CustomUser
from .serializers import BookSerializer, UserLoginSerializer, CustomUserSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status


class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if 'profile_picture' in serializer.validated_data and not serializer.validated_data['profile_picture']:
            del serializer.validated_data['profile_picture']

        user = CustomUser(**serializer.validated_data)
        user.set_password(serializer.validated_data['password'])
        print("User Data:", user.__dict__)

        user.save()
        print("User Data After Save:", user.__dict__)

        token, created = Token.objects.get_or_create(user=user)
        response_data = serializer.data
        response_data['token'] = token.key
        headers = self.get_success_headers(response_data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class BookList(APIView):
    def get(self, request):
        author_name = request.query_params.get('author_name')  # Get the author's name from query parameter
        if author_name:
            books = Book.objects.filter(authors__name=author_name).order_by('title')  # Sort by title
        else:
            books = Book.objects.all().order_by('title')  # Sort by title
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
