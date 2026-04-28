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

# ------------------ 2. HELPERS & STYLING ------------------
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
    else: st.error(f"File not found: {path}")

# ------------------ 3. SESSION STATE ------------------
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user_info': None})

# ------------------ 4. AUTH GATE ------------------
if not st.session_state['auth']:
    st.title("🏛️ Lumina Library")
    t1, t2 = st.tabs(["Login", "Register"])
    with t1:
        e = st.text_input("Email").lower().strip()
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            user = database.verify_login(e, p)
            if user:
                # We save the WHOLE user tuple to avoid index errors
                st.session_state.update({'auth': True, 'user_info': user})
                st.rerun()
            else: st.error("Login Failed")
    with t2:
        n_reg = st.text_input("Name")
        e_reg = st.text_input("Email (Use: adithya@example.com)").lower().strip()
        p_reg = st.text_input("Password", type="password")
        if st.button("Register"):
            database.add_user(n_reg, e_reg, p_reg); st.success("Created!")

# ------------------ 5. MAIN APP ------------------
else:
    # DIAGNOSTIC: See what is inside your user profile
    user_data_string = str(st.session_state['user_info']).lower()
    
    # Check if the admin email exists ANYWHERE in your user data
    is_admin = "adithya@example.com" in user_data_string
    
    st.sidebar.title("Navigation")
    # Show diagnostic info if admin fails
    if not is_admin:
        st.sidebar.warning(f"Debug: {user_data_string}")
    else:
        st.sidebar.success("🛡️ Admin Authenticated")

    menu = ["📊 Dashboard", "📖 Explore Catalog"]
    if is_admin:
        menu.append("⚙️ Librarian Desk")
    
    choice = st.sidebar.selectbox("Menu", menu)
    if st.sidebar.button("Logout"):
        st.session_state.update({'auth': False, 'user_info': None}); st.rerun()

    # --- ROUTES ---
    if choice == "📊 Dashboard":
        st.header("Analytics")
        books = database.get_all_books()
        st.metric("Total Books", len(books))
        if books:
            df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Category", "Stock", "Price", "URL", "Path"])
            st.dataframe(df[["Title", "Author", "Category", "Price"]], use_container_width=True)

    elif choice == "📖 Explore Catalog":
        st.title("Digital Library")
        cat = st.radio("Category", ["B.Tech", "Telugu", "Mythology"], horizontal=True)
        data = database.get_books_by_category(cat)
        cols = st.columns(3)
        for idx, b in enumerate(data):
            with cols[idx % 3]:
                st.info(f"**{b[1]}**\n\n{b[2]}")
                if st.button("👁️ Preview", key=f"v_{b[0]}"):
                    show_pdf(b[6])
                full_p = b[7]
                if full_p.startswith("http"):
                    st.link_button("📥 Download", full_p)
                else:
                    st.warning("Local file download pending.")

    elif choice == "⚙️ Librarian Desk":
        st.title("Admin Desk")
        st.write("Welcome, Adithya. You can now add books.")
        # (Your book adding form goes here)
