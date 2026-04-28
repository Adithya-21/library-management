import streamlit as st
import database
import pandas as pd
import os, base64, time

# ------------------ 1. CONFIG & ADMIN SETUP ------------------
st.set_page_config(page_title="Lumina Pro | Library", layout="wide", page_icon="✨")
database.create_tables()

# The Official Admin Email
ADMIN_EMAIL = "adithya@example.com" 

# Ensure folders exist on the server
for folder in ["previews", "full_books"]:
    if not os.path.exists(folder): os.makedirs(folder)

# --- AUTO-STOCK ENGINE ---
if not database.get_all_books():
    books_to_add = [
        ["Microelectronic Circuits", "Adel Sedra", "B.Tech", 1, 0.0, "previews/micro_pre.pdf", "https://drive.google.com/uc?export=download&id=1dNx66_LSW3mojyvJUukP5BjdFI9IURLS"],
        ["Introduction to Python", "Guido van Rossum", "B.Tech", 1, 0.0, "previews/python_pre.pdf", "https://drive.google.com/uc?export=download&id=1AzZCmQV7l0_wLKJVXdRY-o3a9mDiEoXV"],
        ["Neethikathalu", "Traditional", "Telugu", 1, 0.0, "previews/neethi_pre.pdf", "https://drive.google.com/uc?export=download&id=1CJVvRcYpPhObo4Nog7sIBqqfHcg5FvWf"],
        ["Ramayan", "Valmiki", "Mythology", 1, 0.0, "previews/ramayan_pre.pdf", "https://drive.google.com/uc?export=download&id=1GHF1LNsDyHe8kzjBGQ0geCpVPJOJbR39"]
    ]
    for b in books_to_add:
        database.add_book(b[0], b[1], b[2], b[3], b[4], b[5], b[6])

# ------------------ 2. UI STYLING ------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #fdfdfd; }
    .hero-bg {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 30px;
    }
    .book-card {
        background: white; padding: 20px; border-radius: 18px; border: 1px solid #e5e7eb;
        transition: all 0.3s ease; text-align: center; height: 160px;
        display: flex; flex-direction: column; justify-content: center;
    }
    .book-card:hover { transform: translateY(-5px); border-color: #3b82f6; box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
    .book-title { color: #1f2937; font-weight: 800; font-size: 1.1rem; }
    .payment-box { background: white; padding: 30px; border-radius: 20px; border: 2px solid #3b82f6; }
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
        pdf_display = f'<object data="data:application/pdf;base64,{b64}" width="100%" height="750px" type="application/pdf" style="border-radius:15px; border:2px solid #3b82f6;"></object>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        st.info("💡 Pro-Tip: If preview is blank, use the 'Download' button below to view the full file.")
    else: st.error(f"File not found: {path}")

# ------------------ 4. AUTHENTICATION ------------------
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': None, 'email': None, 'active_book': None, 'active_mode': None})

if not st.session_state['auth']:
    st.markdown("<div class='hero-bg'><h1>🏛️ Lumina Library</h1><p>Digital Archive</p></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        tab1, tab2 = st.tabs(["🔒 Login", "📝 Register"])
        with tab1:
            e_in = st.text_input("Email", key="login_email").lower().strip()
            p_in = st.text_input("Password", type="password", key="login_pass")
            if st.button("Enter Library"):
                user = database.verify_login(e_in, p_in)
                if user:
                    st.session_state.update({'auth': True, 'user': user[0], 'email': user[1]})
                    st.rerun()
                else: st.error("User not found or password incorrect.")
        with tab2:
            n_reg = st.text_input("Name")
            e_reg = st.text_input("Email (Admin: adithya@example.com)").lower().strip()
            p_reg = st.text_input("Password", type="password")
            if st.button("Create Account"):
                database.add_user(n_reg, e_reg, p_reg); st.success("Account Created! Now Login.")

# ------------------ 5. MAIN APP ------------------
else:
    # --- THE MASTER KEY CHECK ---
    user_email = str(st.session_state['email']).lower().strip()
    
    st.sidebar.title(f"👋 Hi, {st.session_state['user']}")
    
    menu = ["📊 Dashboard", "📖 Explore Catalog"]
    
    # HARD-CODED CHECK: This ignores all bugs and checks the string directly
    if user_email == "adithya@example.com" or user_email == ADMIN_EMAIL:
        menu.append("⚙️ Librarian Desk")
        st.sidebar.success("🛡️ Admin Mode Active")
    
    choice = st.sidebar.selectbox("Menu", menu)
    if st.sidebar.button("Logout"):
        st.session_state.update({'auth': False, 'active_book': None}); st.rerun()

    # A. DASHBOARD
    if choice == "📊 Dashboard":
        st.header("Library Analytics")
        books = database.get_all_books()
        c1, c2 = st.columns(2)
        c1.metric("Available Titles", len(books))
        c2.metric("System Status", "Ready")
        if books:
            df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Category", "Stock", "Price", "URL", "Path"])
            st.table(df[["Title", "Author", "Category", "Price"]])

    # B. EXPLORE CATALOG
    elif choice == "📖 Explore Catalog":
        st.title("Resource Gallery")
        cat_tabs = st.tabs(["B.Tech", "Telugu", "Mythology"])
        genres = ["B.Tech", "Telugu", "Mythology"]
        
        for i, g in enumerate(genres):
            with cat_tabs[i]:
                data = database.get_books_by_category(g)
                if not data: st.info("This shelf is empty.")
                cols = st.columns(3)
                for idx, b in enumerate(data):
                    with cols[idx % 3]:
                        st.markdown(f"<div class='book-card'><div class='book-title'>{b[1]}</div><div>{b[2]}</div></div>", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        if c1.button("👁️ Preview", key=f"v_{b[0]}"):
                            st.session_state.update({'active_book': b[0], 'active_mode': 'preview'})
                        if c2.button("📥 Get", key=f"g_{b[0]}"):
                            st.session_state.update({'active_book': b[0], 'active_mode': 'download'})

                # Viewer Section
                if st.session_state['active_book']:
                    active_b = next((x for x in data if x[0] == st.session_state['active_book']), None)
                    if active_b:
                        st.divider()
                        if st.button("❌ Close"): st.session_state['active_book'] = None; st.rerun()
                        if st.session_state['active_mode'] == 'preview':
                            show_pdf(active_b[6])
                        else:
                            f_path = active_b[7]
                            if f_path.startswith("http"):
                                st.link_button("🚀 Download from Cloud Storage", f_path, use_container_width=True)
                            else:
                                try:
                                    with open(f_path, "rb") as f:
                                        st.download_button("💾 Download Local Copy", f, file_name=f"{active_b[1]}.pdf")
                                except: st.error("Local file missing on GitHub.")

    # C. LIBRARIAN DESK
    elif choice == "⚙️ Librarian Desk":
        st.title("Librarian Control Desk")
        if st.button("Force Clear Cache"): st.cache_data.clear(); st.rerun()
        
        with st.form("new_book"):
            t = st.text_input("Book Title")
            a = st.text_input("Author")
            c = st.selectbox("Genre", ["B.Tech", "Telugu", "Mythology"])
            p = st.number_input("Price", 0.0)
            is_link = st.checkbox("Using External Link (Drive/Cloud)")
            pre_f = st.file_uploader("Preview PDF", type="pdf")
            if is_link:
                full_val = st.text_input("Paste Direct Link Here")
            else:
                full_val = st.file_uploader("Full PDF (GitHub)", type="pdf")
            
            if st.form_submit_button("Add to Library"):
                if t and a and pre_f and full_val:
                    ts = int(time.time())
                    pre_p = f"previews/{ts}_{pre_f.name}"
                    with open(pre_p, "wb") as f: f.write(pre_f.getbuffer())
                    
                    if is_link: final_f = full_val
                    else:
                        final_f = f"full_books/{ts}_{full_val.name}"
                        with open(final_f, "wb") as f: f.write(full_val.getbuffer())
                    
                    database.add_book(t, a, c, 1, p, pre_p, final_f)
                    st.success("Library updated!")
