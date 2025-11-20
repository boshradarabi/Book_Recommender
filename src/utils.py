import json
from typing import Dict, List
from datetime import datetime

def format_book_card(book: Dict) -> str:
    card = f"""
📖 **{book['title']}**
✍️ نویسنده: {book['author']}
🏷️ ژانر: {book['genre']}
📄 صفحات: {book['pages']} ({book['length_category']})
✨ سبک: {book['style']}
💭 موضوع: {book['topic']}
📅 سال: {book['year']}
"""

    if 'description' in book:
        card += f"📝 {book['description']}\n"

    return card.strip()

def categorize_page_count(pages: int) -> str:
    if pages < 200:
        return "کوتاه"
    elif pages < 500:
        return "متوسط"
    else:
        return "بلند"


def get_star_display(rating: float) -> str:
    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    return "⭐" * full_stars + "✨" * half_star + "☆" * empty_stars

def calculate_reading_time(pages: int, pages_per_hour: int = 50) -> str:
    hours = pages / pages_per_hour

    if hours < 1:
        minutes = int(hours * 60)
        return f"حدود {minutes} دقیقه"
    elif hours < 24:
        return f"حدود {hours:.1f} ساعت"
    else:
        days = hours / 24
        return f"حدود {days:.1f} روز"

def get_genre_emoji(genre: str) -> str:
    """
    ایموجی مناسب برای ژانر

    Args:
        genre: نام ژانر

    Returns:
        ایموجی
    """
    emoji_map = {
        'داستانی': '📚',
        'علمی': '🔬',
        'روانشناسی': '🧠',
        'فلسفی': '💭',
        'تاریخی': '📜',
        'هنری': '🎨',
        'خودیاری': '💪',
        'آموزشی': '📖'
    }

    return emoji_map.get(genre, '📕')

def generate_reading_report(ratings: Dict[int, float], books: List[Dict]) -> Dict:
    if not ratings:
        return {
            'total_books_read': 0,
            'total_pages': 0,
            'favorite_genre': None,
            'average_rating': 0
        }

    # کتاب‌های خوانده شده
    books_dict = {b['id']: b for b in books}
    read_books = [books_dict[bid] for bid in ratings.keys() if bid in books_dict]

    # محاسبه آمار
    total_pages = sum(b['pages'] for b in read_books)

    # ژانر محبوب
    genre_ratings = {}
    for book in read_books:
        genre = book['genre']
        if genre not in genre_ratings:
            genre_ratings[genre] = []
        genre_ratings[genre].append(ratings[book['id']])

    favorite_genre = None
    if genre_ratings:
        favorite_genre = max(
            genre_ratings.items(),
            key=lambda x: (len(x[1]), sum(x[1]) / len(x[1]))
        )[0]

    return {
        'total_books_read': len(read_books),
        'total_pages': total_pages,
        'favorite_genre': favorite_genre,
        'average_rating': sum(ratings.values()) / len(ratings),
        'estimated_reading_time': calculate_reading_time(total_pages)
    }