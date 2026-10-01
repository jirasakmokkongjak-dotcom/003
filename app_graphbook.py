import streamlit as st
import pandas as pd
from datetime import date

from neo4j_service import (
    ping,
    seed_demo_data,
    get_students,
    get_dashboard_metrics,
    get_profile,
    recommend_books,
    search_books,
    list_categories,
    record_borrow,
    graph_neighborhood,
)

st.set_page_config(
    page_title="GraphBook Recommendation System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
.stApp {
    background: #f6f7fb;
}

section[data-testid="stSidebar"] {
    background: #111827;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.hero {
    padding: 34px;
    border-radius: 24px;
    background: linear-gradient(135deg, #111827, #374151);
    color: white;
    margin-bottom: 24px;
}

.hero h1 {
    margin: 0;
    font-size: 38px;
    font-weight: 800;
}

.hero p {
    margin-top: 10px;
    color: #d1d5db;
    font-size: 16px;
}

.page-title {
    font-size: 30px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 3px;
}

.page-subtitle {
    color: #667085;
    margin-bottom: 22px;
}

.info-card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}

.book-card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    margin-bottom: 12px;
}

.book-title {
    font-size: 19px;
    font-weight: 750;
    color: #111827;
}

.tag {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: #eef2ff;
    color: #4338ca;
    font-size: 13px;
    margin-right: 5px;
}

.score {
    display: inline-block;
    padding: 6px 11px;
    border-radius: 20px;
    background: #ecfdf3;
    color: #027a48;
    font-weight: 700;
    font-size: 13px;
}

.small {
    color: #667085;
    font-size: 14px;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# CONNECTION
# =========================================================
@st.cache_data(ttl=30)
def connection_status():
    try:
        return ping()
    except Exception:
        return False


if "seeded" not in st.session_state:
    st.session_state.seeded = False


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## 📚 GraphBook")
st.sidebar.caption("Book Recommendation System")

page = st.sidebar.radio(
    "เมนูหลัก",
    [
        "🏠 Dashboard",
        "👤 Students",
        "📚 Books",
        "🔎 Search Books",
        "⭐ Recommendations",
        "🕸️ Graph Explorer",
        "➕ Borrow Book",
    ],
)

st.sidebar.divider()
st.sidebar.markdown("### 🗄️ Neo4j Aura")

connected = connection_status()

if connected:
    st.sidebar.success("● Connected")
else:
    st.sidebar.error("● Disconnected")

if st.sidebar.button("🔄 ตรวจสอบการเชื่อมต่อ", use_container_width=True):
    connection_status.clear()
    st.rerun()

if st.sidebar.button("🌱 Load Demo Data", use_container_width=True):
    try:
        seed_demo_data()
        st.session_state.seeded = True
        connection_status.clear()
        st.sidebar.success("เพิ่มข้อมูลตัวอย่างแล้ว")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"เกิดข้อผิดพลาด: {e}")

st.sidebar.divider()
st.sidebar.caption("Python • Streamlit • Neo4j Aura • Cypher")


# =========================================================
# DASHBOARD
# =========================================================
if page == "🏠 Dashboard":

    st.markdown("""
    <div class="hero">
        <h1>📚 GraphBook Recommendation System</h1>
        <p>
            ระบบแนะนำหนังสือด้วย Graph Database
            วิเคราะห์ความสัมพันธ์ระหว่างนักศึกษา หนังสือ
            ผู้เขียน หมวดหมู่ และประวัติการยืม
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">ภาพรวมข้อมูลจาก Neo4j Graph Database</div>',
        unsafe_allow_html=True,
    )

    if not connected:
        st.warning(
            "ยังไม่สามารถเชื่อมต่อ Neo4j ได้ กรุณาตรวจสอบค่าใน "
            "Streamlit Secrets"
        )
    else:
        try:
            metrics = get_dashboard_metrics()

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric("👤 Students", metrics["students"])

            with c2:
                st.metric("📚 Books", metrics["books"])

            with c3:
                st.metric("📖 Borrows", metrics["borrows"])

            with c4:
                st.metric("🤝 Friendships", metrics["friendships"])

        except Exception as e:
            st.error(f"ไม่สามารถโหลด Dashboard: {e}")

    st.markdown("### 🔗 โครงสร้าง Graph")

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        ("👤", "Student", "ข้อมูลนักศึกษา"),
        ("📚", "Book", "ข้อมูลหนังสือ"),
        ("✍️", "Author", "ข้อมูลผู้เขียน"),
        ("🏷️", "Category", "หมวดหมู่หนังสือ"),
    ]

    for col, (icon, title, desc) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(
                f"""
                <div class="info-card">
                    <h3>{icon} {title}</h3>
                    <div class="small">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### 🧠 หลักการแนะนำ")

    st.markdown("""
    <div class="info-card">
        ระบบพิจารณาหลายปัจจัยร่วมกัน ได้แก่
        <b>หนังสือที่เพื่อนยืม</b>,
        <b>ความสนใจของนักศึกษา</b>,
        <b>ความนิยมของหนังสือ</b>
        และ <b>คะแนนรีวิว</b>
        แล้วนำมาคำนวณเป็นคะแนน Recommendation
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# STUDENTS
# =========================================================
elif page == "👤 Students":

    st.markdown('<div class="page-title">👤 Students</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">ข้อมูลนักศึกษาจาก Neo4j</div>',
        unsafe_allow_html=True,
    )

    if not connected:
        st.warning("กรุณาเชื่อมต่อ Neo4j ก่อน")
    else:
        try:
            students = get_students()

            if students:
                df = pd.DataFrame(students)
                df.columns = [
                    "รหัสนักศึกษา",
                    "ชื่อ",
                    "สาขา",
                    "ชั้นปี",
                ]
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("ยังไม่มีข้อมูล Student")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")


# =========================================================
# BOOKS
# =========================================================
elif page == "📚 Books":

    st.markdown('<div class="page-title">📚 Books</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">รายการหนังสือใน Graph Database</div>',
        unsafe_allow_html=True,
    )

    if not connected:
        st.warning("กรุณาเชื่อมต่อ Neo4j ก่อน")
    else:
        try:
            books = search_books()

            if books:
                for book in books:
                    authors = ", ".join(book["authors"]) if book["authors"] else "-"
                    categories = ", ".join(book["categories"]) if book["categories"] else "-"

                    st.markdown(
                        f"""
                        <div class="book-card">
                            <div class="book-title">📖 {book['title']}</div>
                            <div class="small">ID: {book['book_id']} · ปี {book['year']}</div>
                            <br>
                            <b>ผู้เขียน:</b> {authors}<br>
                            <b>หมวดหมู่:</b> {categories}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("ยังไม่มีข้อมูล Book")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")


# =========================================================
# SEARCH
# =========================================================
elif page == "🔎 Search Books":

    st.markdown('<div class="page-title">🔎 Search Books</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">ค้นหาหนังสือจากชื่อ ผู้เขียน หรือหมวดหมู่</div>',
        unsafe_allow_html=True,
    )

    if not connected:
        st.warning("กรุณาเชื่อมต่อ Neo4j ก่อน")
    else:
        try:
            categories = ["ทุกหมวดหมู่"] + list_categories()

            c1, c2 = st.columns([2, 1])

            with c1:
                keyword = st.text_input(
                    "ค้นหาหนังสือ",
                    placeholder="เช่น Python, Database, AI...",
                )

            with c2:
                selected_category = st.selectbox(
                    "หมวดหมู่",
                    categories,
                )

            category = (
                None
                if selected_category == "ทุกหมวดหมู่"
                else selected_category
            )

            results = search_books(keyword, category)

            st.write(f"พบ {len(results)} รายการ")

            for book in results:
                authors = ", ".join(book["authors"]) or "-"
                categories_text = ", ".join(book["categories"]) or "-"

                st.markdown(
                    f"""
                    <div class="book-card">
                        <div class="book-title">📖 {book['title']}</div>
                        <div class="small">
                            {book['book_id']} · ปี {book['year']}
                        </div>
                        <p>✍️ {authors}</p>
                        <span class="tag">{categories_text}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        except Exception as e:
            st.error(f"ค้นหาไม่สำเร็จ: {e}")


# =========================================================
# RECOMMENDATIONS
# =========================================================
elif page == "⭐ Recommendations":

    st.markdown(
        '<div class="page-title">⭐ Book Recommendations</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-subtitle">'
        'แนะนำหนังสือจากความสัมพันธ์ใน Graph Database'
        '</div>',
        unsafe_allow_html=True,
    )

    if not connected:
        st.warning("กรุณาเชื่อมต่อ Neo4j ก่อน")
    else:
        try:
            students = get_students()

            if not students:
                st.info("ยังไม่มีข้อมูล Student")
            else:
                student_map = {
                    f"{s['name']} ({s['student_id']})": s["student_id"]
                    for s in students
                }

                selected = st.selectbox(
                    "เลือกนักศึกษา",
                    list(student_map.keys()),
                )

                student_id = student_map[selected]

                limit = st.slider(
                    "จำนวนหนังสือที่ต้องการแนะนำ",
                    min_value=3,
                    max_value=15,
                    value=8,
                )

                if st.button(
                    "✨ สร้างคำแนะนำ",
                    type="primary",
                    use_container_width=True,
                ):
                    results = recommend_books(student_id, limit)

                    if not results:
                        st.info(
                            "ยังไม่มีหนังสือที่สามารถแนะนำให้ผู้ใช้นี้ได้"
                        )
                    else:
                        st.success(
                            f"พบหนังสือที่แนะนำ {len(results)} รายการ"
                        )

                        for i, book in enumerate(results, 1):
                            authors = ", ".join(book["authors"]) or "-"
                            categories = ", ".join(book["categories"]) or "-"

                            friends = ", ".join(book["friend_names"]) or "-"
                            matched = ", ".join(
                                book["matched_categories"]
                            ) or "-"

                            st.markdown(
                                f"""
                                <div class="book-card">
                                    <div class="book-title">
                                        #{i} 📚 {book['title']}
                                    </div>

                                    <div class="small">
                                        {book['book_id']} · ปี {book['year']}
                                    </div>

                                    <br>
                                    <b>✍️ ผู้เขียน:</b> {authors}<br>
                                    <b>🏷️ หมวดหมู่:</b> {categories}<br>
                                    <b>👥 เพื่อนที่เกี่ยวข้อง:</b> {friends}<br>
                                    <b>💡 หมวดที่ตรงความสนใจ:</b> {matched}

                                    <br><br>

                                    <span class="score">
                                        ⭐ Score {book['score']}
                                    </span>
                                    &nbsp;
                                    <span class="tag">
                                        👥 เพื่อน {book['friend_count']}
                                    </span>
                                    &nbsp;
                                    <span class="tag">
                                        🔥 Popularity {book['popularity']}
                                    </span>
                                    &nbsp;
                                    <span class="tag">
                                        ⭐ Rating {book['avg_rating']}
                                    </span>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

        except Exception as e:
            st.error(f"สร้างคำแนะนำไม่สำเร็จ: {e}")


# =========================================================
# GRAPH EXPLORER
# =========================================================
elif page == "🕸️ Graph Explorer":

    st.markdown(
        '<div class="page-title">🕸️ Graph Explorer</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-subtitle">'
        'ดูความสัมพันธ์ของนักศึกษาใน Graph Database'
        '</div>',
        unsafe_allow_html=True,
    )

    if not connected:
        st.warning("กรุณาเชื่อมต่อ Neo4j ก่อน")
    else:
        try:
            students = get_students()

            student_map = {
                f"{s['name']} ({s['student_id']})": s["student_id"]
                for s in students
            }

            selected = st.selectbox(
                "เลือกนักศึกษา",
                list(student_map.keys()),
            )

            student_id = student_map[selected]

            graph = graph_neighborhood(student_id)

            if graph:
                df = pd.DataFrame(graph)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )

                st.markdown("### 🔗 ความสัมพันธ์ที่พบ")

                relation_counts = (
                    df["relationship"]
                    .value_counts()
                    .reset_index()
                )
                relation_counts.columns = [
                    "Relationship",
                    "Count",
                ]

                st.bar_chart(
                    relation_counts.set_index("Relationship")
                )

            else:
                st.info("ไม่พบความสัมพันธ์")

        except Exception as e:
            st.error(f"โหลด Graph ไม่สำเร็จ: {e}")


# =========================================================
# BORROW
# =========================================================
elif page == "➕ Borrow Book":

    st.markdown(
        '<div class="page-title">➕ Borrow Book</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-subtitle">'
        'บันทึกประวัติการยืมหนังสือและคะแนนรีวิว'
        '</div>',
        unsafe_allow_html=True,
    )

    if not connected:
        st.warning("กรุณาเชื่อมต่อ Neo4j ก่อน")
    else:
        try:
            students = get_students()
            books = search_books()

            student_map = {
                f"{s['name']} ({s['student_id']})": s["student_id"]
                for s in students
            }

            book_map = {
                f"{b['title']} ({b['book_id']})": b["book_id"]
                for b in books
            }

            with st.form("borrow_form"):

                student = st.selectbox(
                    "นักศึกษา",
                    list(student_map.keys()),
                )

                book = st.selectbox(
                    "หนังสือ",
                    list(book_map.keys()),
                )

                borrow_date = st.date_input(
                    "วันที่ยืม",
                    value=date.today(),
                )

                rating = st.slider(
                    "คะแนนหนังสือ",
                    min_value=0.0,
                    max_value=5.0,
                    value=5.0,
                    step=0.5,
                )

                submit = st.form_submit_button(
                    "💾 บันทึกข้อมูล",
                    use_container_width=True,
                )

            if submit:
                record_borrow(
                    student_map[student],
                    book_map[book],
                    borrow_date.isoformat(),
                    rating,
                )

                st.success("บันทึกการยืมหนังสือเรียบร้อยแล้ว")
                connection_status.clear()

        except Exception as e:
            st.error(f"บันทึกข้อมูลไม่สำเร็จ: {e}")


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(
    "GraphBook Recommendation System • "
    "Streamlit + Neo4j Aura + Cypher"
)
