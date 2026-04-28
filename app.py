import streamlit as st
import database
import pandas as pd
import os, base64, time

# ------------------ 1. SETUP ------------------
st.set_page_config(page_title="Lumina Pro | Library", layout="wide", page_icon="✨")
database.create_tables()

# THE ADMIN EMAIL
ADMIN_EMAIL = "adithya@example.com" 

for folder in ["previews", "full_books"]:
    if not os.path.exists(folder): os.makedirs(folder)

# AUTO-STOCK (Ensures your 4 books exist in the DB)
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
def get_pdf_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except: return None

def show_pdf(path):
    if os.path.exists(path):
        b64 = get_pdf_base64(path)
        if b64:
            # Using <iframe> for cleaner preview
            pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="700px" style="border-radius:15px; border:2px solid #3b82f6;"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else: st.error("Failed to load PDF data.")
    else: st.error(f"File not found on GitHub: {path}")

# ------------------ 3. AUTH ------------------
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'u_name': None, 'u_email': None, 'active_book': None, 'active_mode': None})

if not st.session_state['auth']:
    st.title("🏛️ Lumina Library")
    t1, t2 = st.tabs(["Login", "Register"])
    with t1:
        e = st.text_input("Email", key="l_e").lower().strip()
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Access Library", key="l_btn"):
            user = database.verify_login(e, p)
            if user:
                st.session_state.update({'auth': True, 'u_name': user[0], 'u_email': user[1]})
                st.rerun()
            else: st.error("Login Failed.")
    with t2:
        n_reg = st.text_input("Name", key="r_n")
        e_reg = st.text_input("Email", key="r_e").lower().strip()
        p_reg = st.text_input("Password", type="password", key="r_p")
        if st.button("Register", key="r_btn"):
            database.add_user(n_reg, e_reg, p_reg); st.success("Created! Switch to Login.")

# ------------------ 4. MAIN APP ------------------
else:
    # --- ADMIN CHECK LOGIC ---
    current_email = str(st.session_state['u_email']).lower().strip()
    is_admin = (current_email == ADMIN_EMAIL or current_email == "adithya@example.com")

    st.sidebar.title(f"👋 Hi, {st.session_state['u_name']}")
    menu = ["📊 Dashboard", "📖 Explore Catalog"]
    if is_admin: 
        menu.append("⚙️ Librarian Desk")
        st.sidebar.success("🛡️ Admin Mode")

    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "📊 Dashboard":
        st.header("Library Analytics")
        books = database.get_all_books()
        st.metric("Total Books", len(books))
        if books:
            df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Category", "Stock", "Price", "Preview", "Full"])
            st.dataframe(df.drop(columns=["Preview", "Full"]), use_container_width=True)

    elif choice == "📖 Explore Catalog":
        st.title("Resource Gallery")
        genres = ["B.Tech", "Telugu", "Mythology"]
        tabs = st.tabs(genres)
        for i, g in enumerate(genres):
            with tabs[i]:
                data = database.get_books_by_category(g)
                cols = st.columns(3)
                for idx, b in enumerate(data):
                    with cols[idx % 3]:
                        st.info(f"**{b[1]}**\n\n{b[2]}")
                        c1, c2 = st.columns(2)
                        if c1.button("👁️ Preview", key=f"v_{b[0]}_{g}"):
                            st.session_state.update({'active_book': b[0], 'active_mode': 'preview'})
                        if c2.button("📥 Get", key=f"g_{b[0]}_{g}"):
                            st.session_state.update({'active_book': b[0], 'active_mode': 'download'})

                # VIEWER LOGIC
                if st.session_state['active_book']:
                    active_b = next((x for x in data if x[0] == st.session_state['active_book']), None)
                    if active_b:
                        st.divider()
                        if st.button("❌ Close", key=f"cls_{g}"): 
                            st.session_state['active_book'] = None; st.rerun()
                        
                        if st.session_state['active_mode'] == 'preview':
                            show_pdf(active_b[6])
                        else:
                            f_path = active_b[7]
                            if str(f_path).startswith("http"):
                                st.link_button("🚀 Download from Cloud", f_path, use_container_width=True)
                            else:
                                with open(f_path, "rb") as f:
                                    st.download_button("💾 Download Local", f, file_name=f"{active_b[1]}.pdf")

    elif choice == "⚙️ Librarian Desk":
        st.title("Admin Desk")
        st.write("Add new books to the library.")
        # (Librarian form logic)
