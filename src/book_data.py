import json
import os
from typing import List, Dict, Optional
from pathlib import Path

class BookDataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.books_file = self.data_dir/"books.json"
        self.ratings_file = self.data_dir/"user_ratings.json"
        self.profile_file = self.data_dir/"user_profile.json"

        self.data_dir.mkdir(exist_ok=True)

        self._initialize_files()

    def _initialize_files(self):
        if not self.ratings_file.exists():
            with open(self.ratings_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

        # user_profile file
        if not self.profile_file.exists():
            initial_profile = {
                "genre_preferences": {},
                "length_preferences": {},
                "style_preferences": {},
                "topic_preferences": {},
                "total_ratings": 0,
                "average_rating": 0
            }
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(initial_profile, f, ensure_ascii=False, indent=2)

    def load_books(self) -> List[Dict]:
        try:
            with open(self.books_file, 'r', encoding='utf-8') as f:
                books = json.load(f)
            return books
        except FileNotFoundError:
            print(f"File {self.books_file} not found!")
            return []
        except json.JSONDecodeError as e:
            print(f"Error {e} while reading json file!")
            return []

    def save_books(self, books: List[Dict]) -> bool:
        try:
            with open(self.books_file, 'w', encoding='utf-8') as f:
                json.dump(books, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error {e} while saving book!")
            return False

    def get_book_by_id(self, book_id: int) -> Optional[Dict]:
        books = self.load_books()
        for book in books:
            if book['id'] == book_id:
                return book
        return None

    def add_book(self, book_data: Dict) -> bool:
        books = self.load_books()

        # generate new id
        if books:
            new_id = max(book['id'] for book in books) + 1
        else:
            new_id = 1

        book_data['id'] = new_id

        if not self._validate_book(book_data):
            return False

        books.append(book_data)
        return self.save_books(books)

    def _validate_book(self, book: Dict) -> bool:
        required_fields = [
            'title', 'author', 'genre', 'pages',
            'length_category', 'style', 'topic', 'year'
        ]

        for field in required_fields:
            if field not in book:
                print(f"Field {field} does not exist!")
                return False

        if not isinstance(book['pages'], int) or book['pages'] <= 0:
            print("The number of pages must be a positive integer!")
            return False

        if not isinstance(book['year'], int):
            print("the year value must be an integer number!")
            return False

        valid_lengths = ['کوتاه', 'متوسط', 'بلند']
        if book['length_category'] not in valid_lengths:
            print(f"the length of the book must be one of {valid_lengths}")
            return False

        valid_styles = ['ساده', 'آکادمیک', 'شاعرانه']
        if book['style'] not in valid_styles:
            print(f"the style of the book must be one of {valid_styles}")
            return False

        return True

    def get_all_genres(self) -> List[str]:
        books = self.load_books()
        genres = list(set(book['genre'] for book in books))
        return sorted(genres)


    def search_books(self, query: str) -> List[Dict]:
        books = self.load_books()
        query = query.lower()

        results = []
        for book in books:
            if (query in book['title'].lower() or
                    query in book['author'].lower() or
                    query in book['genre'].lower() or
                    query in book['topic'].lower()):
                results.append(book)

        return results

    def get_statistics(self) -> Dict:
        books = self.load_books()

        if not books:
            return {}

        genres = {}
        styles = {}
        lengths = {}

        for book in books:
            genres[book['genre']] = genres.get(book['genre'], 0) + 1
            styles[book['style']] = styles.get(book['style'], 0) + 1
            lengths[book['length_category']] = lengths.get(book['length_category'], 0) + 1

        return {
            'total_books': len(books),
            'genres': genres,
            'styles': styles,
            'lengths': lengths,
            'avg_pages': sum(b['pages'] for b in books) / len(books) if books else 0
        }