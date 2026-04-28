import streamlit as st
import database
import pandas as pd
import os, base64, time, io
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# ------------------ 1. CONFIG & ADMIN SETUP ------------------
st.set_page_config(page_title="Apex Digital Library", layout="wide", page_icon="📖")
database.create_tables()

ADMIN_EMAIL = "adithya@example.com" 
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

# Ensure storage folders exist - Strictly 'preview' (no 's')
for f in ["preview", "full_books"]:
    os.makedirs(os.path.join(BASE_DIR, f), exist_ok=True)

# --- AUTO-STOCK ENGINE: Path updated to 'preview/' ---
def refresh_library_data():
    books_to_add = [
        ["Microelectronic Circuits", "Adel Sedra", "B.Tech", 5, 0.0, "preview/micro_pre.pdf", "https://drive.google.com/uc?export=download&id=1dNx66_LSW3mojyvJUukP5BjdFI9IURLS"],
        ["Introduction to Python", "Guido van Rossum", "B.Tech", 3, 100.0, "preview/python_pre.pdf", "https://drive.google.com/uc?export=download&id=1AzZCmQV7l0_wLKJVXdRY-o3a9mDiEoXV"],
        ["Neethikathalu", "Traditional", "Telugu", 10, 0.0, "preview/neethi_pre.pdf", "https://drive.google.com/uc?export=download&id=1CJVvRcYpPhObo4Nog7sIBqqfHcg5FvWf"],
        ["Ramayan", "Valmiki", "Mythology", 2, 200.0, "preview/ramayan_pre.pdf", "https://drive.google.com/uc?export=download&id=1GHF1LNsDyHe8kzjBGQ0geCpVPJOJbR39"]
    ]
    for b in books_to_add:
        database.add_book(b[0], b[1], b[2], b[3], b[4], b[5], b[6])

if not database.get_all_books():
    refresh_library_data()

# ------------------ 2. THE ABSOLUTE PDF LOADER ------------------
def get_pdf_base64(full_path):
    try:
        with open(full_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except: return None

def show_pdf(relative_path):
    # Construct absolute path using current BASE_DIR
    abs_path = os.path.join(BASE_DIR, relative_path)
    
    if os.path.exists(abs_path):
        b64 = get_pdf_base64(abs_path)
        if b64:
            pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="800px" style="border:2px solid #3b82f6; border-radius:15px;"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error("Error reading file.")
    else:
        st.error(f"📂 Path Error: The server cannot find {abs_path}")
        st.info("💡 Tip: Go to Librarian Desk and click '🔄 Reset & Refresh Database' to fix old paths.")

def draw_clock():
    clock_html = """
    <div id="clock" style="font-family:sans-serif; color:#3b82f6; font-size:22px; font-weight:800; text-align:center; padding:10px; background:#0f172a; border-radius:10px; border:1px solid #1e293b;">00:00:00</div>
    <script>
    function updateClock() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        document.getElementById('clock').innerText = `${hours}:${minutes}:${seconds}`;
    }
    setInterval(updateClock, 1000); updateClock();
    </script>"""
    components.html(clock_html, height=70)

# ------------------ 3. UI STYLING ------------------
st.markdown("""<style>
    .hero-bg { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 20px; }
    .book-card { background: white; padding: 15px; border-radius: 15px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 10px; height: 160px; }
    .book-title { color: #0f172a; font-weight: 800; font-size: 1rem; }
    </style>""", unsafe_allow_html=True)

# ------------------ 4. AUTH & MAIN ------------------
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': None, 'email': None, 'celebrate': False, 'active_book': None, 'active_mode': None})

if not st.session_state['auth']:
    st.markdown("<div class='hero-bg'><h1>📖 Apex Digital Library</h1></div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])
    with t1:
        e = st.text_input("Email", key="l_e").lower().strip()
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Enter Library", use_container_width=True):
            user = database.verify_login(e, p)
            if user: st.session_state.update({'auth': True, 'user': user[0], 'email': e, 'celebrate': True}); st.rerun()
    with t2:
        n_reg = st.text_input("Full Name")
        e_reg = st.text_input("Email").lower().strip()
        p_reg = st.text_input("Password", type="password")
        if st.button("Create Account", use_container_width=True):
            if n_reg and e_reg and p_reg:
                database.add_user(n_reg, e_reg, p_reg); st.success("🎉 Hurrah! Welcome to the family. Login now!")

else:
    if st.session_state['celebrate']:
        st.balloons(); st.toast(f"Welcome, {st.session_state['user']}! 🥳")
        st.session_state['celebrate'] = False

    # Sidebar
    st.sidebar.markdown("### 🕒 System Time")
    draw_clock()
    
    # IST CORRECTED GREETING
    ist_now = datetime.now() + timedelta(hours=5, minutes=30)
    hour = ist_now.hour
    greet = "🌅 Good Morning" if hour < 12 else "☀️ Good Afternoon" if hour < 17 else "🌙 Good Evening"
    
    st.sidebar.subheader(f"{greet},")
    st.sidebar.title(f"{st.session_state['user']}!")

    current_email = str(st.session_state['email']).lower().strip()
    is_admin = (current_email == ADMIN_EMAIL or current_email == "adithya@example.com")
    
    menu = ["📊 Dashboard", "📖 Explore Catalog"]
    if is_admin: menu.append("⚙️ Librarian Desk")
    
    choice = st.sidebar.selectbox("Navigation", menu)
    if st.sidebar.button("Logout", use_container_width=True): st.session_state.update({'auth': False}); st.rerun()

    # A. DASHBOARD
    if choice == "📊 Dashboard":
        st.markdown("<div class='hero-bg'><h1>Library Metrics</h1></div>", unsafe_allow_html=True)
        books = database.get_all_books()
        c1, c2 = st.columns(2)
        c1.metric("📚 Titles", len(books)); c2.metric("📦 Status", "🟢 Online")
        if books:
            df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Cat", "Stock", "Price", "URL", "Path"])
            st.dataframe(df[["Title", "Author", "Cat", "Price"]], use_container_width=True, hide_index=True)

    # B. EXPLORE CATALOG
    elif choice == "📖 Explore Catalog":
        st.title("Digital Archive")
        tabs = st.tabs(["🎓 B.Tech", "📜 Telugu", "🕉️ Mythology"])
        genres = ["B.Tech", "Telugu", "Mythology"]
        for i, cat in enumerate(genres):
            with tabs[i]:
                data = database.get_books_by_category(cat)
                cols = st.columns(3)
                for idx, b in enumerate(data):
                    with cols[idx % 3]:
                        st.markdown(f"<div class='book-card'><div class='book-title'>{b[1]}</div><div>{b[2]}</div></div>", unsafe_allow_html=True)
                        if st.button("👁️ Preview", key=f"v_{cat}_{b[0]}"):
                            st.session_state.update({'active_book': b[0], 'active_mode': 'preview'})
                        if b[5] > 0:
                            if st.button(f"₹{int(b[5])} Buy", key=f"b_{cat}_{b[0]}"):
                                st.session_state.update({'active_book': b[0], 'active_mode': 'pay'})
                        else:
                            if st.button("📥 Get", key=f"d_{cat}_{b[0]}"):
                                st.session_state.update({'active_book': b[0], 'active_mode': 'download'})

                if st.session_state['active_book']:
                    active_b = next((x for x in data if x[0] == st.session_state['active_book']), None)
                    if active_b:
                        st.divider()
                        if st.button("❌ Close Viewer", key=f"close_{cat}", use_container_width=True):
                            st.session_state['active_book'] = None; st.rerun()
                        if st.session_state['active_mode'] == 'preview':
                            show_pdf(active_b[6])
                        else:
                            if active_b[7].startswith("http"): st.link_button("🚀 Access", active_b[7], use_container_width=True)

    # C. LIBRARIAN DESK
    elif choice == "⚙️ Librarian Desk":
        st.title("🔐 Librarian Control Panel")
        col_r1, col_r2 = st.columns(2)
        if col_r1.button("🔄 Reset & Refresh Database", use_container_width=True):
            conn = database.connect_db(); cursor = conn.cursor()
            cursor.execute("DELETE FROM books") # WIPES THE OLD PATHS
            conn.commit(); conn.close()
            refresh_library_data() # RE-ADDS WITH THE NEW 'preview/' PATH
            st.success("Database synced with 'preview/' folder!"); time.sleep(1); st.rerun()
            
        if col_r2.button("📥 Export Audit Report (Excel)", use_container_width=True):
            conn = database.connect_db(); df_b = pd.read_sql_query("SELECT * FROM books", conn); df_u = pd.read_sql_query("SELECT name, email FROM users", conn); conn.close()
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_b.to_excel(writer, sheet_name='Inventory', index=False); df_u.to_excel(writer, sheet_name='Users', index=False)
            st.download_button(label="📥 Download Excel", data=buffer.getvalue(), file_name="Apex_Report.xlsx")

        st.divider(); st.subheader("➕ Add New Resource")
        with st.form("add_book_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            t = col_a.text_input("Title"); a = col_b.text_input("Author"); cat = st.selectbox("Category", ["B.Tech", "Telugu", "Mythology"])
            stk = st.number_input("Stock", min_value=1, value=1); pr = st.number_input("Price (₹)", 0.0)
            is_link = st.checkbox("External Link"); pre_f = st.file_uploader("Preview PDF", type="pdf")
            val = st.text_input("URL") if is_link else st.file_uploader("Full PDF", type="pdf")
            if st.form_submit_button("🚀 Commit to Database", use_container_width=True):
                if t and a and pre_f and val:
                    ts = int(time.time()); pre_p = f"preview/{ts}_{pre_f.name}"
                    with open(os.path.join(BASE_DIR, pre_p), "wb") as f: f.write(pre_f.getbuffer())
                    if is_link: fin_p = val
                    else:
                        fin_p = f"full_books/{ts}_{val.name}"
                        with open(os.path.join(BASE_DIR, fin_p), "wb") as f: f.write(val.getbuffer())
                    database.add_book(t, a, cat, stk, pr, pre_p, fin_p); st.success(f"Added '{t}'!"); time.sleep(1); st.rerun()
