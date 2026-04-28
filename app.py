import streamlit as st
import database
import pandas as pd
import os, base64, time

# ------------------ 1. CONFIG & ADMIN SETUP ------------------
st.set_page_config(page_title="Lumina Pro | Library", layout="wide", page_icon="✨")
database.create_tables()

ADMIN_EMAIL = "adithya@example.com" 

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

# ------------------ 2. HELPERS ------------------
@st.cache_data
def get_pdf_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except: return None

def show_pdf(path):
    if os.path.exists(path):
        b64 = get_pdf_base64(path)
        st.markdown(f'<object data="data:application/pdf;base64,{b64}" width="100%" height="750px" type="application/pdf" style="border-radius:15px; border:2px solid #3b82f6;"></object>', unsafe_allow_html=True)
    else: st.error(f"Preview not found: {path}")

# ------------------ 3. SESSION STATE ------------------
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user_name': None, 'user_email': None})

# ------------------ 4. AUTH GATE ------------------
if not st.session_state['auth']:
    st.title("🏛️ Lumina Library")
    t1, t2 = st.tabs(["Login", "Register"])
    
    with t1:
        # Added unique keys to prevent the DuplicateElementId error
        e_login = st.text_input("Email", key="login_email_input").lower().strip()
        p_login = st.text_input("Password", type="password", key="login_pass_input")
        if st.button("Login", key="login_submit_btn"):
            user = database.verify_login(e_login, p_login)
            if user:
                # user[0] is Name, user[1] is Email in your SQLite setup
                st.session_state.update({'auth': True, 'user_name': user[0], 'user_email': user[1]})
                st.rerun()
            else: st.error("Invalid credentials.")

    with t2:
        n_reg = st.text_input("Full Name", key="reg_name_input")
        e_reg = st.text_input("Email", key="reg_email_input").lower().strip()
        p_reg = st.text_input("Password", type="password", key="reg_pass_input")
        if st.button("Register Account", key="reg_submit_btn"):
            database.add_user(n_reg, e_reg, p_reg)
            st.success("Success! Please switch to the Login tab.")

# ------------------ 5. MAIN APP ------------------
else:
    # CLEAN ADMIN CHECK
    current_user = str(st.session_state['user_email']).lower().strip()
    is_admin = (current_user == ADMIN_EMAIL or current_user == "adithya@example.com")

    st.sidebar.title(f"👋 Hi, {st.session_state['user_name']}")
    
    menu = ["📊 Dashboard", "📖 Explore Catalog"]
    if is_admin:
        menu.append("⚙️ Librarian Desk")
        st.sidebar.success("🛡️ Admin Access")

    choice = st.sidebar.selectbox("Navigation", menu)
    
    if st.sidebar.button("Logout"):
        st.session_state.update({'auth': False, 'user_email': None})
        st.rerun()

    # --- ROUTES ---
    if choice == "📊 Dashboard":
        st.header("Library Dashboard")
        books = database.get_all_books()
        st.metric("Total Books", len(books))
        if books:
            df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Category", "Stock", "Price", "URL", "Path"])
            st.dataframe(df[["Title", "Author", "Category", "Price"]], use_container_width=True, hide_index=True)

    elif choice == "📖 Explore Catalog":
        st.title("Resource Gallery")
        cat = st.radio("Select Genre", ["B.Tech", "Telugu", "Mythology"], horizontal=True)
        data = database.get_books_by_category(cat)
        
        if not data:
            st.info("No books here yet.")
        else:
            cols = st.columns(3)
            for idx, b in enumerate(data):
                with cols[idx % 3]:
                    st.info(f"**{b[1]}**\n\n{b[2]}")
                    c1, c2 = st.columns(2)
                    if c1.button("👁️ View", key=f"v_{b[0]}"):
                        show_pdf(b[6])
                    
                    full_p = b[7]
                    if full_p.startswith("http"):
                        c2.link_button("📥 Get", full_p)
                    else:
                        c2.warning("Local Link")

    elif choice == "⚙️ Librarian Desk":
        st.title("Librarian Control Panel")
        with st.form("add_book_form"):
            t = st.text_input("Title")
            a = st.text_input("Author")
            c = st.selectbox("Category", ["B.Tech", "Telugu", "Mythology"])
            p = st.number_input("Price", 0.0)
            is_link = st.checkbox("External Link (Drive)")
            pre_f = st.file_uploader("Preview PDF", type="pdf")
            if is_link:
                val = st.text_input("Direct Link")
            else:
                val = st.file_uploader("Full PDF", type="pdf")
            
            if st.form_submit_button("Add Book"):
                if t and a and pre_f and val:
                    ts = int(time.time())
                    pre_path = f"previews/{ts}_{pre_f.name}"
                    with open(pre_path, "wb") as f: f.write(pre_f.getbuffer())
                    
                    if is_link:
                        final_path = val
                    else:
                        final_path = f"full_books/{ts}_{val.name}"
                        with open(final_path, "wb") as f: f.write(val.getbuffer())
                    
                    database.add_book(t, a, c, 1, p, pre_path, final_path)
                    st.success("Book Added!")
                    st.rerun()
