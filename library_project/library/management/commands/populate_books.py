from django.core.management.base import BaseCommand
from library.models import Book, Author, Category
from django.conf import settings
import requests
import pprint

class Command(BaseCommand):
    help = 'Populate the database with random books by a specific author from the Google Books API'

    def add_arguments(self, parser):
        parser.add_argument('author_name', type=str, help='Name of the author to fetch books for')
        parser.add_argument('--num_books', type=int, default=40, help='Number of books to fetch per API call (default: 40)')
        parser.add_argument('--total_books', type=int, default=100, help='Total number of books to fetch (default: 100)')

    def is_english(self, book_data):
        # Check if the language is English (adjust the language code as needed)
        return book_data['volumeInfo'].get('language', '').lower() == 'en'

    def handle(self, *args, **kwargs):
        author_name = kwargs['author_name']
        num_books_to_fetch = kwargs['num_books']
        total_books_to_fetch = kwargs['total_books']
        api_key = settings.GOOGLE_BOOKS_API_KEY

        start_index = 0  # Initialize the start index for pagination
        books_fetched = 0  # Initialize a counter for the total number of books fetched

        while start_index < total_books_to_fetch:
            # Create an API query to fetch books by the author with pagination
            api_url = 'https://www.googleapis.com/books/v1/volumes?q=inauthor:"{}"&maxResults={}&startIndex={}'.format(
                author_name, num_books_to_fetch, start_index
            )

            try:
                response = requests.get(api_url, params={'key': api_key})
                data = response.json()

                if 'items' in data:
                    for book_data in data['items']:
                        if self.is_english(book_data):
                            title = book_data['volumeInfo'].get('title', 'N/A')

                            # Check if the book already exists in the database
                            book_exists = Book.objects.filter(title=title).exists()

                            if not book_exists:
                                description = book_data['volumeInfo'].get('description', None)
                                published_date_str = book_data['volumeInfo'].get('publishedDate', 'N/A')

                                # Create or update authors
                                authors_data = book_data['volumeInfo'].get('authors', [])
                                authors = [Author.objects.get_or_create(name=author)[0] for author in authors_data]

                                # Create or update categories
                                categories_data = book_data['volumeInfo'].get('categories', [])
                                categories = [Category.objects.get_or_create(name=category)[0] for category in categories_data]

                                # Create the book
                                book = Book(
                                    title=title,
                                    description=description,
                                    publication_date_str=published_date_str,
                                    # Set other fields here
                                )
                                book.save()

                                book.authors.set(authors)
                                book.genre.set(categories)
                                # Update other fields as needed

                                self.stdout.write(self.style.SUCCESS('Successfully added book: {}'.format(title)))
                                books_fetched += 1

                        else:
                            # The book is not in English, skip it
                            self.stdout.write(self.style.WARNING('Skipping non-English book: {}'.format(title)))

                        # Check if the desired number of books has been fetched
                        if books_fetched >= total_books_to_fetch:
                            break

                else:
                    self.stdout.write(self.style.ERROR('No books found in the API response.'))

                # Increment the start index for the next API call
                start_index += num_books_to_fetch

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR('Error fetching data from the Google Books API: {}'.format(e)))

            # Check if the desired number of books has been fetched
            if books_fetched >= total_books_to_fetch:
                break

        self.stdout.write(self.style.SUCCESS('Database population complete.'))
