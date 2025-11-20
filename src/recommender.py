import json
from typing import List, Dict, Tuple
from pathlib import Path
import numpy as np

class BookRecommender:
    """
    - method: content-based filtering
    - based on book's features (genre, length(number of pages), style, topic)
    - learn from user's rating
    - calculate similarity and suggest related books
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.ratings_file = self.data_dir/"user_ratings.json"
        self.profile_file = self.data_dir/"user_profile.json"

        # features' weights (sum=1)
        self.weights = {
            'genre': 0.4,
            'style': 0.3,
            'length': 0.2,
            'topic': 0.1
        }

    def load_ratings(self) -> Dict[str, float]:
        try:
            with open(self.ratings_file, 'r', encoding='utf-8') as f:
                ratings = json.load(f)
            return {int(k): float(v) for k, v in ratings.items()}
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Error {e} in load ratings")
            return {}

    def save_rating(self, book_id: int, rating: float) -> bool:
        if not 1 <= rating <= 5:
            print("rate must be between 1 and 5")
            return False

        ratings = self.load_ratings()
        ratings[book_id] = rating

        try:
            with open(self.ratings_file, 'w', encoding='utf-8') as f:
                json.dump(ratings, f, ensure_ascii=False, indent=2)

            self._update_profile()
            return True
        except Exception as e:
            print(f"Error {e} in saving rate!")
            return False

    def _update_profile(self):
        """
        update user profile based on ratings
        """
        from src.book_data import BookDataManager

        ratings = self.load_ratings()
        if not ratings:
            return

        book_manager = BookDataManager(self.data_dir)

        profile = {
            'genre_preferences': {},  # {genre: avg_rating}
            'length_preferences': {},  # {length: avg_rating}
            'style_preferences': {},  # {style: avg_rating}
            'topic_preferences': {},  # {topic: avg_rating}
            'total_ratings': len(ratings),
            'average_rating': sum(ratings.values()) / len(ratings)
        }

        # calculate average rate for each feature
        genre_ratings = {}
        length_ratings = {}
        style_ratings = {}
        topic_ratings = {}

        for book_id, rating in ratings.items():
            book = book_manager.get_book_by_id(book_id)
            if not book:
                continue

            genre = book['genre']
            if genre not in genre_ratings:
                genre_ratings[genre] = []
            genre_ratings[genre].append(rating)

            length = book['length_category']
            if length not in length_ratings:
                length_ratings[length] = []
            length_ratings[length].append(rating)

            style = book['style']
            if style not in style_ratings:
                style_ratings[style] = []
            style_ratings[style].append(rating)

            topic = book['topic']
            if topic not in topic_ratings:
                topic_ratings[topic] = []
            topic_ratings[topic].append(rating)


        # calculate averages

        # Bayesian Weighted Average (IMDB style)
        # weighted = (v / (v + m)) * R  +  (m / (v + m)) * C
        # R: average genre rate
        # v: number of books read in specific genre
        # c: total average of all rates
        # m: this number shows, how many data is needed to achieve a real rate

        C = sum(ratings.values()) / len(ratings)  # total average
        m = 5

        profile['genre_preferences'] = {
            g: (len(r) / (len(r) + m)) * np.mean(r) + (m / (len(r) + m)) * C
            for g, r in genre_ratings.items()
        }

        profile['length_preferences'] = {
            l: (len(r) / (len(r) + m)) * np.mean(r) + (m / (len(r) + m)) * C
            for l, r in length_ratings.items()
        }

        profile['style_preferences'] = {
            s: (len(r) / (len(r) + m)) * np.mean(r) + (m / (len(r) + m)) * C
            for s, r in style_ratings.items()
        }

        profile['topic_preferences'] = {
            t: (len(r) / (len(r) + m)) * np.mean(r) + (m / (len(r) + m)) * C
            for t, r in topic_ratings.items()
        }


        # ذخیره پروفایل
        try:
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error {e} in saving profile")


    def load_profile(self) -> Dict:
        try:
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            return profile
        except FileNotFoundError:
            return {
                'genre_preferences': {},
                'length_preferences': {},
                'style_preferences': {},
                'topic_preferences': {},
                'total_ratings': 0,
                'average_rating': 0
            }

    def calculate_similarity(self, book: Dict) -> float:
        """
        calculate the similarity between book and ratings

        Score = (Genre_Score × 0.4) + (Style_Score × 0.3) +
                (Length_Score × 0.2) + (Topic_Score × 0.1)

        each score is between 1 to 5
        """
        profile = self.load_profile()

        # if profile is empty return an average rate (3)
        if profile['total_ratings'] == 0:
            return 3.0

        genre_score = profile['genre_preferences'].get(
            book['genre'],
            profile['average_rating']  # if the genre is not read, use average
        )

        style_score = profile['style_preferences'].get(
            book['style'],
            profile['average_rating']
        )

        length_score = profile['length_preferences'].get(
            book['length_category'],
            profile['average_rating']
        )

        topic_score = profile['topic_preferences'].get(
            book['topic'],
            profile['average_rating']
        )

        final_score = (
                genre_score * self.weights['genre'] +
                style_score * self.weights['style'] +
                length_score * self.weights['length'] +
                topic_score * self.weights['topic']
        )

        return round(final_score, 2)


    def get_recommendations(self, books: List[Dict],
                            top_n: int = 5) -> List[Tuple[Dict, float]]:

        ratings = self.load_ratings()
        profile = self.load_profile()

        # recommend random books if there's no rate
        if profile['total_ratings'] == 0:
            import random
            unrated = [b for b in books if b['id'] not in ratings]
            random.shuffle(unrated)
            return [(b, 3.0) for b in unrated[:top_n]]

        recommendations = []

        # recommend those books that had not been read (we don't want to suggest read books)
        for book in books:
            if book['id'] not in ratings:
                score = self.calculate_similarity(book)
                recommendations.append((book, score))

        recommendations.sort(key=lambda x: x[1], reverse=True)

        return recommendations[:top_n]

    def explain_recommendation(self, book: Dict) -> str:
        profile = self.load_profile()

        if profile['total_ratings'] == 0:
            return "این کتاب به صورت تصادفی انتخاب شده (شما هنوز امتیازی نداده‌اید)"

        reasons = []

        # check genre
        genre = book['genre']
        if genre in profile['genre_preferences']:
            avg = profile['genre_preferences'][genre]
            if avg >= 4:
                reasons.append(f"شما به ژانر '{genre}' علاقه زیادی دارید (میانگین: {avg:.1f}⭐)")
            elif avg >= 3:
                reasons.append(f"ژانر '{genre}' برای شما جالب است (میانگین: {avg:.1f}⭐)")

        # check style
        style = book['style']
        if style in profile['style_preferences']:
            avg = profile['style_preferences'][style]
            if avg >= 4:
                reasons.append(f"سبک '{style}' مورد پسند شماست (میانگین: {avg:.1f}⭐)")

        # check length
        length = book['length_category']
        if length in profile['length_preferences']:
            avg = profile['length_preferences'][length]
            if avg >= 4:
                reasons.append(f"کتاب‌های '{length}' را ترجیح می‌دهید (میانگین: {avg:.1f}⭐)")

        if not reasons:
            return "این کتاب بر اساس ترجیحات کلی شما انتخاب شده است"

        return " • " + " • ".join(reasons)

    def get_rating_statistics(self) -> Dict:
        ratings = self.load_ratings()

        if not ratings:
            return {
                'total': 0,
                'average': 0,
                'distribution': {}
            }

        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in ratings.values():
            distribution[int(rating)] = distribution.get(int(rating), 0) + 1

        return {
            'total': len(ratings),
            'average': sum(ratings.values()) / len(ratings),
            'distribution': distribution,
            'min': min(ratings.values()),
            'max': max(ratings.values())
        }