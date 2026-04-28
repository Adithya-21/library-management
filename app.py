import streamlit as st
import database
import pandas as pd
import os, base64, time, io
from datetime import datetime

# ------------------ 1. CONFIG & ADMIN SETUP ------------------
st.set_page_config(page_title="Apex Digital Library", layout="wide", page_icon="📖")
database.create_tables()

ADMIN_EMAIL = "adithya@example.com" 

# Folder setup
for folder in ["previews", "full_books"]:
    if not os.path.exists(folder): os.makedirs(folder)

# --- AUTO-STOCK ENGINE ---
if not database.get_all_books():
    books_to_add = [
        ["Microelectronic Circuits", "Adel Sedra", "B.Tech", 5, 0.0, "previews/micro_pre.pdf", "https://drive.google.com/uc?export=download&id=1dNx66_LSW3mojyvJUukP5BjdFI9IURLS"],
        ["Introduction to Python", "Guido van Rossum", "B.Tech", 3, 0.0, "previews/python_pre.pdf", "https://drive.google.com/uc?export=download&id=1AzZCmQV7l0_wLKJVXdRY-o3a9mDiEoXV"],
        ["Neethikathalu", "Traditional", "Telugu", 10, 0.0, "previews/neethi_pre.pdf", "https://drive.google.com/uc?export=download&id=1CJVvRcYpPhObo4Nog7sIBqqfHcg5FvWf"],
        ["Ramayan", "Valmiki", "Mythology", 2, 0.0, "previews/ramayan_pre.pdf", "https://drive.google.com/uc?export=download&id=1GHF1LNsDyHe8kzjBGQ0geCpVPJOJbR39"]
    ]
    for b in books_to_add:
        database.add_book(b[0], b[1], b[2], b[3], b[4], b[5], b[6])

# ------------------ 2. UI STYLING ------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .hero-bg {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 50px; border-radius: 25px; color: white;
        text-align: center; margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    .book-card {
        background: white; padding: 20px; border-radius: 18px;
        border: 1px solid #e2e8f0; transition: all 0.3s ease;
        margin-bottom: 15px; height: 180px;
        display: flex; flex-direction: column; justify-content: center;
        text-align: center;
    }
    .book-card:hover { transform: translateY(-5px); border-color: #3b82f6; box-shadow: 0 12px 24px rgba(0,0,0,0.1); }
    .book-title { color: #0f172a; font-weight: 800; font-size: 1.1rem; }
    .status-text { font-size: 0.85rem; color: #94a3b8; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# ------------------ 3. HELPERS ------------------
@st.cache_data
def get_pdf_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except: return None

def show_pdf(path):
    if os.path.exists(path):
        b64 = get_pdf_base64(path)
        if b64:
            pdf_display = f'''
                <object data="data:application/pdf;base64,{b64}" width="100%" height="800px" type="application/pdf" style="border-radius:20px; border:2px solid #3b82f6;">
                    <div style="padding:40px; text-align:center; background:#f1f5f9; border-radius:20px;">
                        <h4>Digital Viewer</h4>
                        <a href="data:application/pdf;base64,{b64}" download="preview.pdf" style="background-color:#3b82f6; color:white; padding:10px 20px; border-radius:8px; text-decoration:none;">📥 Download Preview</a>
                    </div>
                </object>'''
            st.markdown(pdf_display, unsafe_allow_html=True)
    else: st.error(f"Preview not found: {path}")

def payment_gateway(book_title, price, cat_key):
    st.markdown(f"<div style='background: white; padding: 30px; border-radius: 20px; border: 2px solid #3b82f6;'>", unsafe_allow_html=True)
    st.subheader("🔒 Secure Checkout")
    st.write(f"🛒 **Purchasing:** {book_title}")
    st.markdown(f"<h3 style='color:#2563eb;'>Total: ₹{price}</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    card = col1.text_input("Card Number", placeholder="XXXX XXXX XXXX XXXX", key=f"c_{cat_key}")
    cvv = col2.text_input("CVV", type="password", key=f"v_{cat_key}")
    if st.button("Authorize Payment", key=f"pay_btn_{cat_key}"):
        if len(card) >= 12:
            with st.spinner("Processing..."): time.sleep(2)
            st.balloons(); st.success("Transaction Complete!"); return True
        else: st.error("Invalid Details")
    st.markdown("</div>", unsafe_allow_html=True)
    return False

# ------------------ 4. AUTH & SESSION ------------------
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': None, 'email': None, 'active_book': None, 'active_mode': None, 'last_update': datetime.now().strftime("%d %b %Y, %I:%M %p")})

if not st.session_state['auth']:
    st.markdown("<div class='hero-bg'><h1>📖 Apex Digital Library</h1><p>Modern Learning • Engineering Excellence</p></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        t1, t2 = st.tabs(["🔑 Login", "📝 Register"])
        with t1:
            e_in = st.text_input("Email", key="l_email").lower().strip()
            p_in = st.text_input("Password", type="password", key="l_pass")
            if st.button("Enter Library", use_container_width=True):
                user = database.verify_login(e_in, p_in)
                if user:
                    st.session_state.update({'auth': True, 'user': user[0], 'email': e_in})
                    st.rerun()
                else: st.error("Verification failed.")
        with t2:
            n_reg = st.text_input("Full Name")
            e_reg = st.text_input("Email").lower().strip()
            p_reg = st.text_input("Password", type="password")
            if st.button("Create Account", use_container_width=True):
                database.add_user(n_reg, e_reg, p_reg); st.success("Account Created!")

# ------------------ 5. MAIN APP ------------------
else:
    current_email = str(st.session_state['email']).lower().strip()
    is_admin = (current_email == ADMIN_EMAIL or current_email == "adithya@example.com")
    
    st.sidebar.title(f"👋 Hi, {st.session_state['user']}")
    menu = ["📊 Dashboard", "📖 Explore Catalog"]
    if is_admin:
        menu.append("⚙️ Librarian Desk")
        st.sidebar.success("🛡️ Librarian Mode")
    
    choice = st.sidebar.selectbox("Navigation", menu)
    if st.sidebar.button("Logout"):
        st.session_state.update({'auth': False, 'active_book': None}); st.rerun()

    # A. DASHBOARD
    if choice == "📊 Dashboard":
        st.markdown("<div class='hero-bg'><h1>Library Metrics</h1></div>", unsafe_allow_html=True)
        books = database.get_all_books()
        c1, c2, c3 = st.columns(3)
        c1.metric("📚 Unique Titles", len(books))
        c2.metric("📦 Stock Available", sum([b[4] for b in books]) if books else 0)
        c3.metric("⚡ Status", "🟢 Online")
        
        # --- NEW: Last Update Timestamp ---
        st.markdown(f"<p class='status-text'>🕒 Last System Sync: {st.session_state['last_update']}</p>", unsafe_allow_html=True)
        
        if books:
            df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Category", "Stock", "Price", "URL", "Path"])
            st.dataframe(df[["Title", "Author", "Category", "Stock", "Price"]], use_container_width=True, hide_index=True)

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
                        st.markdown(f"<div class='book-card'><div class='book-title'>{b[1]}</div><div>{b[2]}</div><div style='font-size:0.8rem; color:#666;'>Copies: {b[4]}</div></div>", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        if c1.button("👁️ Preview", key=f"v_{cat}_{b[0]}"):
                            st.session_state.update({'active_book': b[0], 'active_mode': 'preview'})
                        if b[5] > 0:
                            if c2.button(f"₹{b[5]} Buy", key=f"b_{cat}_{b[0]}"):
                                st.session_state.update({'active_book': b[0], 'active_mode': 'pay'})
                        else:
                            if c2.button("📥 Get", key=f"d_{cat}_{b[0]}"):
                                st.session_state.update({'active_book': b[0], 'active_mode': 'download'})

                if st.session_state['active_book']:
                    active_b = next((x for x in data if x[0] == st.session_state['active_book']), None)
                    if active_b:
                        st.divider()
                        if st.button("❌ Close Viewer", key=f"close_{cat}"):
                            st.session_state['active_book'] = None; st.rerun()
                        mode = st.session_state['active_mode']
                        if mode == "preview":
                            show_pdf(active_b[6])
                        elif mode in ["pay", "download"]:
                            ok = payment_gateway(active_b[1], active_b[5], cat) if mode == "pay" else True
                            if ok:
                                f_path = active_b[7]
                                if str(f_path).startswith("http"):
                                    st.link_button("🚀 Download Full Book", f_path, use_container_width=True)
                                else:
                                    with open(f_path, "rb") as f:
                                        st.download_button("💾 Download Local PDF", f, file_name=f"{active_b[1]}.pdf", use_container_width=True)

    # C. LIBRARIAN DESK
    elif choice == "⚙️ Librarian Desk":
        st.title("🔐 Librarian Control Panel")
        
        # EXPORT SECTION
        if st.button("📥 Generate Audit Report (Excel)", use_container_width=True):
            conn = database.connect_db()
            df_books = pd.read_sql_query("SELECT * FROM books", conn)
            df_users = pd.read_sql_query("SELECT name, email FROM users", conn)
            conn.close()
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_books.to_excel(writer, sheet_name='Inventory', index=False)
                df_users.to_excel(writer, sheet_name='Users', index=False)
            st.download_button(label="📥 Download Report", data=buffer.getvalue(), 
                             file_name="Apex_Library_Report.xlsx", 
                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        st.divider()
        with st.form("add_book_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            t = col_a.text_input("Title")
            a = col_b.text_input("Author")
            cat = st.selectbox("Category", ["B.Tech", "Telugu", "Mythology"])
            col_q1, col_q2 = st.columns(2)
            stk = col_q1.number_input("Copies", min_value=1, value=1)
            pr = col_q2.number_input("Price", 0.0)
            is_link = st.checkbox("External Drive Link")
            pre_f = st.file_uploader("Preview PDF", type="pdf")
            if is_link: val = st.text_input("Drive Link")
            else: val = st.file_uploader("Full PDF", type="pdf")
            if st.form_submit_button("🚀 Commit Book", use_container_width=True):
                if t and a and pre_f and val:
                    ts = int(time.time())
                    pre_p = f"previews/{ts}_{pre_f.name}"
                    with open(pre_p, "wb") as f: f.write(pre_f.getbuffer())
                    if is_link: fin_p = val
                    else:
                        fin_p = f"full_books/{ts}_{val.name}"
                        with open(fin_p, "wb") as f: f.write(val.getbuffer())
                    database.add_book(t, a, cat, stk, pr, pre_p, fin_p)
                    
                    # --- UPDATE TIMESTAMP ON CHANGE ---
                    st.session_state['last_update'] = datetime.now().strftime("%d %b %Y, %I:%M %p")
                    st.success(f"Added {t}. Database sync complete."); st.rerun()
