# Book Recommender System 📚

A personalized, offline book recommendation web app built with **Streamlit**.

Rate the books you've read → Get smart, tailored book suggestions → Track your reading habits → Add new books to your library.

Everything runs locally on your machine — no accounts, no internet required.

---

### Features

| Page              | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| **Home**          | Personalized recommendations, quick search, reading stats overview         |
| **Rate Books**    | Rate or update ratings for any book (with filters for genre, length, style)|
| **My Profile**    | Reading statistics, favorite genres & styles, rating distribution chart    |
| **Add Book**      | Full form to add new books to your personal library                         |
| **Statistics**    | System-wide stats: genre distribution, writing style breakdown, etc.       |

---

### Requirements

- Python 3.9+
- pip

### Installation & Running

```bash
# 1. Clone or download the project
git clone https://github.com/yourusername/book-recommender.git
cd book-recommender

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
streamlit run app.py
```

The app will open automatically at http://localhost:8501

## Project Structure

```bash
.
├── app.py                  # Main Streamlit application
├── style.css               # Custom styling (optional)
├── requirements.txt        # Python dependencies
├── data/                   # Automatically created on first run
│   ├── books.json          # Book catalog
│   ├── user_ratings.json   # Your ratings (created automatically)
│   └── user_profile.json   # Cached user preferences
├── src/
│   ├── book_data.py        # Book data loading & management
│   ├── recommender.py      # Recommendation engine
│   └── utils.py            # Helper functions (emojis, reading time, etc.)
└── README.md


```


## Adding Initial Books (Optional)
```json
[
  {
    "id": 1,
    "title": "The Alchemist",
    "author": "Paulo Coelho",
    "genre": "Fiction",
    "style": "Poetic",
    "pages": 198,
    "length_category": "Short",
    "topic": "Self-discovery",
    "year": 1988,
    "description": "A magical story about following your dreams..."
  }
]
```
## Customize Appearance

Edit style.css in the project root to change colors, fonts, spacing, etc.

