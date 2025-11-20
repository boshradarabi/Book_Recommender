import streamlit as st
import sys
from pathlib import Path
from src.book_data import BookDataManager
from src.recommender import BookRecommender
from src.utils import *

sys.path.append(str(Path(__file__).parent))


def load_css(file_path: str):
    """بارگذاری فایل CSS در Streamlit"""
    if Path(file_path).exists():
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"فایل CSS پیدا نشد: {file_path}")

load_css("style.css")

@st.cache_resource
def init_system():
    """مقداردهی سیستم"""
    book_manager = BookDataManager()
    recommender = BookRecommender()
    return book_manager, recommender

book_manager, recommender = init_system()


st.set_page_config(
    page_title="سامانه پیشنهاد کتاب",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def home_page():
    st.markdown("""
            <h1 style=
            # 'text-align: center;
            direction: rtl;
            '>🏠خانه</h1>
        """, unsafe_allow_html=True)

    st.markdown("""
        <h2 style=
        'text-align: center;
        direction: rtl;
        '>📚نمایش پیشنهادات</h2>
    """, unsafe_allow_html=True)
    st.markdown("---")


    # بارگذاری داده‌ها
    books = book_manager.load_books()
    ratings = recommender.load_ratings()
    profile = recommender.load_profile()

    # نمایش وضعیت
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📚 کتاب‌های موجود", value=len(books))
    with col2:
        st.metric(label="⭐ امتیازهای شما", value=profile['total_ratings'])
    with col3:
        if profile['total_ratings'] > 0:
            avg = profile['average_rating']
            st.metric(label="📊 میانگین امتیاز", value=f"{avg:.1f} {get_star_display(avg)}")
        else:
            st.metric(label="📊 میانگین امتیاز", value="بدون امتیاز")

    st.markdown("---")

    # 🔍 جستجوی کتاب
    search_query = st.text_input("🔎 جستجوی ژانر، کتاب، موضوع یا نویسنده:")
    if search_query:
        search_results = book_manager.search_books(search_query)
        if search_results:
            st.subheader(f"نتایج جستجو برای '{search_query}':")
            for book in search_results:
                st.markdown(f"**{book['title']}** — {book['author']} | {book['genre']} | {book['topic']}")
        else:
            st.warning(f"هیچ کتابی با '{search_query}' پیدا نشد!")

    st.markdown("---")

    # پیشنهادات ویژه
    st.subheader("💡 پیشنهادات ویژه برای شما")
    if profile['total_ratings'] == 0:
        st.info("👋 برای دریافت پیشنهادات شخصی‌سازی شده، لطفاً به چند کتاب امتیاز دهید!")
        st.markdown("👈 از منوی سمت راست به بخش **'امتیازدهی'** بروید")




    col = st.columns([0.2, 1])[0]  # ستون باریک برای selectbox

    with col:
        num_recommendations = st.selectbox(
            "تعداد پیشنهادات:",
            options=list(range(3, 11)),
            index=1
        )

    recommendations = recommender.get_recommendations(books, top_n=num_recommendations)

    if not recommendations:
        st.warning("همه کتاب‌ها را امتیاز داده‌اید! 🎉")
        st.info("کتاب جدید اضافه کنید تا پیشنهادات جدید دریافت کنید.")
    else:
        for i, (book, score) in enumerate(recommendations, 1):
            with st.container():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"### {i}. {get_genre_emoji(book['genre'])} {book['title']}")
                    st.markdown(f"**نویسنده:** {book['author']}")
                    st.markdown(f"**ژانر:** {book['genre']} | **سبک:** {book['style']}")
                    st.markdown(f"**صفحات:** {book['pages']} ({book['length_category']})")
                    st.markdown(f"**موضوع:** {book['topic']}")
                    if 'description' in book:
                        st.markdown(f"*{book['description']}*")
                    explanation = recommender.explain_recommendation(book)
                    st.info(f"💭 **چرا این کتاب؟** {explanation}")
                with col2:
                    st.metric(label="امتیاز پیشبینی", value=f"{score:.1f}", delta=get_star_display(score))
                    st.markdown(f"**زمان مطالعه:**")
                    st.markdown(calculate_reading_time(book['pages']))
                    with st.expander("⭐ امتیاز سریع"):
                        rating = st.slider("امتیاز:", 1.0, 5.0, 3.0, 0.5, key=f"quick_rate_{book['id']}")
                        if st.button("ثبت امتیاز", key=f"submit_{book['id']}"):
                            if recommender.save_rating(book['id'], rating):
                                st.success("✅ امتیاز ثبت شد!")
                                st.rerun()

            st.markdown("---")

def rating_page():
    """صفحه امتیازدهی به کتاب‌ها"""
    st.title("⭐ امتیازدهی به کتاب‌ها")
    st.markdown("---")

    books = book_manager.load_books()
    ratings = recommender.load_ratings()

    selected_book_id = st.session_state.get('selected_book_id', None)

    if selected_book_id:
        filtered_books = [b for b in books if b['id'] == selected_book_id]
    else:
        filtered_books = books  # همه کتاب‌ها

    if selected_book_id:
        del st.session_state['selected_book_id']

    # تب‌ها
    tab1, tab2 = st.tabs(["📚 همه کتاب‌ها", "✅ امتیاز داده‌شده"])

    with tab1:
        st.subheader("لیست کتاب‌ها")

        # فیلترها
        col1, col2, col3 = st.columns(3)

        with col1:
            genres = ["همه"] + book_manager.get_all_genres()
            selected_genre = st.selectbox("ژانر:", genres)

        with col2:
            lengths = ["همه", "کوتاه", "متوسط", "بلند"]
            selected_length = st.selectbox("طول:", lengths)

        with col3:
            styles = ["همه", "ساده", "آکادمیک", "شاعرانه"]
            selected_style = st.selectbox("سبک:", styles)

        # فیلتر کردن
        filtered_books = books
        if selected_genre != "همه":
            filtered_books = [b for b in filtered_books if b['genre'] == selected_genre]
        if selected_length != "همه":
            filtered_books = [b for b in filtered_books if b['length_category'] == selected_length]
        if selected_style != "همه":
            filtered_books = [b for b in filtered_books if b['style'] == selected_style]

        st.info(f"📊 {len(filtered_books)} کتاب یافت شد")

        # نمایش کتاب‌ها
        for book in filtered_books:
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"### {get_genre_emoji(book['genre'])} {book['title']}")
                    st.markdown(f"**{book['author']}** | {book['genre']} | {book['pages']} صفحه")
                    if 'description' in book:
                        st.markdown(f"*{book['description']}*")

                with col2:
                    current_rating = ratings.get(book['id'], None)

                    if current_rating:
                        st.success(f"امتیاز فعلی: {current_rating} {get_star_display(current_rating)}")

                    new_rating = st.slider(
                        "امتیاز:",
                        1.0, 5.0,
                        current_rating if current_rating else 3.0,
                        0.5,
                        key=f"rate_{book['id']}"
                    )

                    if st.button("ثبت/ویرایش", key=f"btn_{book['id']}"):
                        if recommender.save_rating(book['id'], new_rating):
                            st.success("✅ ثبت شد!")
                            st.rerun()

                st.markdown("---")

    with tab2:
        st.subheader("کتاب‌های امتیازدهی شده")

        if not ratings:
            st.info("هنوز به هیچ کتابی امتیاز نداده‌اید!")
        else:
            rated_books = [book_manager.get_book_by_id(bid) for bid in ratings.keys()]
            rated_books = [b for b in rated_books if b]  # حذف None

            # مرتب‌سازی
            sort_order = st.radio(
                "مرتب‌سازی:",
                ["بالاترین امتیاز", "پایین‌ترین امتیاز", "جدیدترین"]
            )

            if sort_order == "بالاترین امتیاز":
                rated_books.sort(key=lambda b: ratings[b['id']], reverse=True)
            elif sort_order == "پایین‌ترین امتیاز":
                rated_books.sort(key=lambda b: ratings[b['id']])

            for book in rated_books:
                rating = ratings[book['id']]

                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"### {book['title']}")
                    st.markdown(f"{book['author']} | {book['genre']}")

                with col2:
                    st.metric(
                        "امتیاز شما",
                        f"{rating} ⭐"
                    )
                    if st.button("حذف", key=f"del_{book['id']}"):
                        # حذف امتیاز
                        del ratings[book['id']]
                        import json
                        with open("data/user_ratings.json", 'w', encoding='utf-8') as f:
                            json.dump(ratings, f)
                        recommender._update_profile()
                        st.rerun()

                st.markdown("---")


def profile_page():
    """صفحه پروفایل کاربر"""
    st.title("👤 پروفایل من")
    st.markdown("---")

    profile = recommender.load_profile()
    ratings = recommender.load_ratings()
    books = book_manager.load_books()

    if profile['total_ratings'] == 0:
        st.info("هنوز پروفایلی ایجاد نشده! لطفاً به کتاب‌ها امتیاز دهید.")
        return

    # آمار کلی
    st.subheader("📊 آمار کلی")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("کتاب‌های خوانده شده", profile['total_ratings'])

    with col2:
        st.metric("میانگین امتیاز", f"{profile['average_rating']:.2f} ⭐")

    # گزارش مطالعه
    report = generate_reading_report(ratings, books)

    with col3:
        st.metric("صفحات خوانده شده", report['total_pages'])

    with col4:
        st.metric("زمان مطالعه", report['estimated_reading_time'])

    st.markdown("---")

    # ترجیحات
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏷️ ژانرهای مورد علاقه")
        if profile['genre_preferences']:
            import pandas as pd
            genre_df = pd.DataFrame([
                {"ژانر": k, "امتیاز میانگین": v}
                for k, v in sorted(
                    profile['genre_preferences'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            ])
            st.dataframe(genre_df, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("✨ سبک‌های مورد علاقه")
        if profile['style_preferences']:
            import pandas as pd
            style_df = pd.DataFrame([
                {"سبک": k, "امتیاز میانگین": v}
                for k, v in sorted(
                    profile['style_preferences'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            ])
            st.dataframe(style_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # نمودار
    st.subheader("📈 توزیع امتیازات")

    stats = recommender.get_rating_statistics()
    if stats['total'] > 0:
        import plotly.graph_objects as go

        fig = go.Figure(data=[
            go.Bar(
                x=list(stats['distribution'].keys()),
                y=list(stats['distribution'].values()),
                marker_color='#667eea'
            )
        ])

        fig.update_layout(
            title="تعداد کتاب‌ها به تفکیک امتیاز",
            xaxis_title="امتیاز",
            yaxis_title="تعداد",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)


# ================== صفحه اضافه کردن کتاب ==================
def add_book_page():
    """صفحه اضافه کردن کتاب جدید"""
    st.title("➕ اضافه کردن کتاب جدید")
    st.markdown("---")

    with st.form("add_book_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("عنوان کتاب *")
            author = st.text_input("نویسنده *")
            pages = st.number_input("تعداد صفحات *", min_value=1, value=200)
            year = st.number_input("سال انتشار *", min_value=-1000, max_value=2025, value=2020)

        with col2:
            genres = book_manager.get_all_genres()
            genre = st.selectbox("ژانر *", genres + ["سایر"])
            if genre == "سایر":
                genre = st.text_input("ژانر جدید:")

            style = st.selectbox("سبک نگارش *", ["ساده", "آکادمیک", "شاعرانه"])
            length = categorize_page_count(pages)
            # st.markdown(f"**طول کتاب:** {length}")  # نمایش طول محاسبه شده
            topic = st.text_input("موضوع اصلی *")

        description = st.text_area("توضیحات (اختیاری)")

        submitted = st.form_submit_button("➕ اضافه کردن")

        if submitted:
            # اعتبارسنجی
            if not all([title, author, genre, topic]):
                st.error("لطفاً تمام فیلدهای الزامی (*) را پر کنید!")
            else:
                new_book = {
                    'title': title,
                    'author': author,
                    'genre': genre,
                    'pages': pages,
                    'length_category': length,
                    'style': style,
                    'topic': topic,
                    'year': year
                }

                if description:
                    new_book['description'] = description

                if book_manager.add_book(new_book):
                    st.success(f"✅ کتاب '{title}' با موفقیت اضافه شد!")
                else:
                    st.error("❌ خطا در اضافه کردن کتاب!")


# ================== صفحه آمار ==================
def statistics_page():
    """صفحه آمار سیستم"""
    st.title("📊 آمار سیستم")
    st.markdown("---")

    stats = book_manager.get_statistics()

    if not stats:
        st.warning("هیچ داده‌ای موجود نیست!")
        return

    # آمار کلی
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("تعداد کل کتاب‌ها", stats['total_books'])

    with col2:
        st.metric("میانگین صفحات", f"{stats['avg_pages']:.0f}")

    with col3:
        st.metric("تعداد ژانرها", len(stats['genres']))

    st.markdown("---")

    # نمودارها
    import plotly.graph_objects as go

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("توزیع ژانرها")
        fig1 = go.Figure(data=[
            go.Pie(
                labels=list(stats['genres'].keys()),
                values=list(stats['genres'].values()),
                hole=0.3
            )
        ])
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("توزیع سبک‌ها")
        fig2 = go.Figure(data=[
            go.Bar(
                x=list(stats['styles'].keys()),
                y=list(stats['styles'].values()),
                marker_color='#764ba2'
            )
        ])
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)


def main():
    st.sidebar.title("📚منوی اصلی")
    st.sidebar.markdown("---")

    st.sidebar.markdown("### انتخاب کنید:")
    menu = st.sidebar.radio(
        "",
        ["🏠 خانه", "⭐ امتیازدهی", "👤 پروفایل من", "➕ اضافه کردن کتاب", "📊 آمار"]
    )

    st.sidebar.markdown("---")
    st.sidebar.info("""
    **راهنما:**

    1️⃣ به کتاب‌ها امتیاز دهید

    2️⃣ پیشنهادات شخصی دریافت کنید

    3️⃣ کتاب جدید اضافه کنید
    """)

    # نمایش صفحه مربوطه
    if menu == "🏠 خانه":
        home_page()
    elif menu == "⭐ امتیازدهی":
        rating_page()
    elif menu == "👤 پروفایل من":
        profile_page()
    elif menu == "➕ اضافه کردن کتاب":
        add_book_page()
    elif menu == "📊 آمار":
        statistics_page()


if __name__ == "__main__":
    main()