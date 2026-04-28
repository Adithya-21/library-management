import streamlit as st
import database
import pandas as pd
import os, base64, time

# ------------------ 1. CONFIG & ADMIN SETUP ------------------
st.set_page_config(page_title="Lumina Pro | Library", layout="wide", page_icon="✨")
database.create_tables()

# !!! SECURITY: Ensure this matches your login email exactly !!!
ADMIN_EMAIL = "adithya@example.com" 

# --- AUTO-STOCK: This adds your 4 books automatically if the library is empty ---
if not database.get_all_books():
    books_to_add = [
        ["Microelectronic Circuits", "Adel Sedra", "B.Tech", 1, 0.0, "previews/micro_pre.pdf", "https://drive.google.com/uc?export=download&id=1dNx66_LSW3mojyvJUukP5BjdFI9IURLS"],
        ["Introduction to Python", "Guido van Rossum", "B.Tech", 1, 0.0, "previews/python_pre.pdf", "https://drive.google.com/uc?export=download&id=1AzZCmQV7l0_wLKJVXdRY-o3a9mDiEoXV"],
        ["Neethikathalu", "Traditional", "Telugu", 1, 0.0, "previews/neethi_pre.pdf", "https://drive.google.com/uc?export=download&id=1CJVvRcYpPhObo4Nog7sIBqqfHcg5FvWf"],
        ["Ramayan", "Valmiki", "Mythology", 1, 0.0, "previews/ramayan_pre.pdf", "https://drive.google.com/uc?export=download&id=1GHF1LNsDyHe8kzjBGQ0geCpVPJOJbR39"]
    ]
    for b in books_to_add:
        database.add_book(b[0], b[1], b[2], b[3], b[4], b[5], b[6])

# Folder setup
for folder in ["previews", "full_books"]:
    if not os.path.exists(folder): os.makedirs(folder)

# ------------------ 2. ADVANCED UI STYLING ------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #fdfdfd; }
    
    .hero-bg {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 50px; border-radius: 20px; color: white;
        text-align: center; margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
    }
    
    .book-card {
        background: white; padding: 20px; border-radius: 18px;
        border: 1px solid #e5e7eb; transition: all 0.3s ease;
        margin-bottom: 15px; height: 160px;
        display: flex; flex-direction: column; justify-content: center;
        text-align: center;
    }
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }
    .book-title { color: #1f2937; font-weight: 800; font-size: 1.1rem; }
    .book-author { color: #6b7280; font-size: 0.85rem; margin-top: 5px; }
    
    .payment-box {
        background: #ffffff; padding: 30px; border-radius: 20px;
        border: 2px solid #3b82f6; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------ 3. PERFORMANCE HELPERS ------------------
@st.cache_data
def get_pdf_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except:
        return None

def show_pdf(path):
    if os.path.exists(path):
        b64 = get_pdf_base64(path)
        if b64:
            # Added unique style to prevent layout shifts
            st.markdown(f'<div style="border-radius:15px; overflow:hidden; border:2px solid #3b82f6;"><iframe src="data:application/pdf;base64,{b64}" width="100%" height="700px" style="border:none;"></iframe></div>', unsafe_allow_html=True)
        else:
            st.error("Could not process PDF preview.")
    else:
        st.error(f"Preview file not found: {path}")

def payment_gateway(book_title, price, cat_key):
    st.markdown(f"<div class='payment-box'>", unsafe_allow_html=True)
    st.subheader("🔒 Secure Checkout")
    st.write(f"🛒 **Purchasing:** {book_title}")
    st.markdown(f"<p style='color:#1a73e8; font-weight:bold; font-size:22px;'>Total: ₹{price}</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    card = col1.text_input("Card Number", placeholder="XXXX XXXX XXXX XXXX", key=f"card_{cat_key}")
    cvv = col2.text_input("CVV", type="password", key=f"cvv_{cat_key}")
    if st.button("Unlock Full Book", key=f"final_pay_btn_{cat_key}"):
        if len(card) >= 12:
            with st.spinner("Processing..."): time.sleep(3)
            st.balloons(); st.success("Success!"); return True
        else: st.error("Invalid Details")
    st.markdown("</div>", unsafe_allow_html=True)
    return False

# ------------------ 4. SESSION STATE ------------------
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': None, 'email': None, 'active_book': None, 'active_mode': None})

# ------------------ 5. AUTH GATE ------------------
if not st.session_state['auth']:
    st.markdown("<div class='hero-bg'><h1>🏛️ Lumina Library</h1><p>Premium Resources for Engineering & Culture</p></div>", unsafe_allow_html=True)
    c_a, c_b, c_c = st.columns([1, 2, 1])
    with c_b:
        t_auth1, t_auth2 = st.tabs(["🔒 Login", "📝 Register"])
        with t_auth1:
            e_login = st.text_input("Email", key="l_email").lower().strip()
            p_login = st.text_input("Password", type="password", key="l_pass")
            if st.button("Access Library", key="l_btn"):
                user = database.verify_login(e_login, p_login)
                if user:
                    st.session_state.update({'auth': True, 'user': user[0], 'email': user[1]})
                    st.rerun()
                else: st.error("Login Failed")
        with t_auth2:
            n_reg = st.text_input("Full Name", key="r_name")
            e_reg = st.text_input("Email", key="r_email").lower().strip()
            p_reg = st.text_input("Password", type="password", key="r_pass")
            if st.button("Create My Account", key="r_btn"):
                database.add_user(n_reg, e_reg, p_reg); st.success("Registered!")

# ------------------ 6. MAIN APP (Logged In) ------------------
else:
    st.sidebar.title(f"👋 Hi, {st.session_state['user']}")
    menu = ["📊 Dashboard", "📖 Explore Catalog"]
    
    # Clean check for Admin Desk
    user_email = str(st.session_state['email']).lower().strip()
    if user_email == ADMIN_EMAIL.lower().strip() or user_email == "adithya@example.com":
        menu.append("⚙️ Librarian Desk")
    
    choice = st.sidebar.selectbox("Navigation", menu)
    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.update({'auth': False, 'active_book': None}); st.rerun()

    # A. DASHBOARD
    if choice == "📊 Dashboard":
        st.markdown("<div class='hero-bg'><h1>Library Inventory</h1></div>", unsafe_allow_html=True)
        books = database.get_all_books()
        c1, c2, c3 = st.columns(3)
        c1.metric("Titles", len(books))
        c2.metric("Stock", sum([b[4] for b in books]) if books else 0)
        c3.metric("Status", "Online")
        if books:
            df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Category", "Stock", "Price", "URL", "Path"])
            st.dataframe(df.drop(columns=["URL", "Path"]), use_container_width=True, hide_index=True)

    # B. EXPLORE CATALOG
    elif choice == "📖 Explore Catalog":
        st.title("Digital Shelves")
        genres = ["B.Tech", "Telugu", "Mythology"]
        tabs = st.tabs(genres)
        
        for i, cat in enumerate(genres):
            with tabs[i]:
                data = database.get_books_by_category(cat)
                if not data: st.info(f"No books in {cat} yet.")
                
                cols = st.columns(3)
                for idx, b in enumerate(data):
                    with cols[idx % 3]:
                        st.markdown(f"""<div class='book-card'><div class='book-title'>{b[1]}</div><div class='book-author'>{b[2]}</div></div>""", unsafe_allow_html=True)
                        btn_c1, btn_c2 = st.columns(2)
                        
                        if btn_c1.button("👁️ Preview", key=f"v_{cat}_{b[0]}"):
                            st.session_state['active_book'], st.session_state['active_mode'] = b[0], "preview"
                        
                        if b[5] > 0:
                            if btn_c2.button(f"₹{b[5]} Buy", key=f"b_{cat}_{b[0]}"):
                                st.session_state['active_book'], st.session_state['active_mode'] = b[0], "pay"
                        else:
                            if btn_c2.button("📥 Get", key=f"d_{cat}_{b[0]}"):
                                st.session_state['active_book'], st.session_state['active_mode'] = b[0], "download"

                # Central Viewer (Logic for GitHub Previews and Drive Downloads)
                if st.session_state['active_book']:
                    active_b = next((x for x in data if x[0] == st.session_state['active_book']), None)
                    if active_b:
                        st.divider()
                        if st.button("❌ Close Viewer", key=f"close_btn_{cat}"):
                            st.session_state['active_book'] = None; st.rerun()
                        
                        mode = st.session_state['active_mode']
                        if mode == "preview": 
                            show_pdf(active_b[6]) # Uses GitHub Path
                        
                        elif mode in ["pay", "download"]:
                            pay_ready = payment_gateway(active_b[1], active_b[5], cat) if mode == "pay" else True
                            
                            if pay_ready:
                                full_path = active_b[7]
                                # HYBRID CHECK: Drive Link vs GitHub File
                                if str(full_path).startswith("http"):
                                    st.link_button("📂 Download Full Book", full_path, use_container_width=True)
                                else:
                                    try:
                                        with open(full_path, "rb") as f:
                                            st.download_button("📂 Download Full Book", f, file_name=f"{active_b[1]}.pdf", key=f"dl_{cat}")
                                    except:
                                        st.error("File not found on server.")

    # C. LIBRARIAN DESK
    elif choice == "⚙️ Librarian Desk":
        st.title("🔐 Admin Control Panel")
        if st.button("🧹 Refresh System Cache", key="refresh_cache_admin"):
            st.cache_data.clear(); st.success("Refreshed!"); st.rerun()

        with st.form("add_book_form", clear_on_submit=True):
            col_in1, col_in2 = st.columns(2)
            t = col_in1.text_input("Title")
            a = col_in2.text_input("Author")
            cat = st.selectbox("Genre", ["B.Tech", "Telugu", "Mythology"])
            pr = st.number_input("Price (0 for Free)", 0.0)
            
            use_link = st.checkbox("External Link (Use for Drive/Large Files)")
            pre_file = st.file_uploader("10-Page Preview PDF", type="pdf")
            
            if use_link:
                full_val = st.text_input("Direct Download Link")
                full_file = None
            else:
                full_file = st.file_uploader("Full Book PDF", type="pdf")
                full_val = ""

            if st.form_submit_button("🚀 Finalize & Register Book"):
                if t and a and pre_file and (full_file or full_val):
                    ts = int(time.time())
                    pre_p = os.path.join("previews", f"{ts}_{pre_file.name}")
                    with open(pre_p, "wb") as f: f.write(pre_file.getbuffer())
                    
                    if use_link:
                        full_p = full_val
                    else:
                        full_p = os.path.join("full_books", f"{ts}_{full_file.name}")
                        with open(full_p, "wb") as f: f.write(full_file.getbuffer())
                    
                    database.add_book(t, a, cat, 1, pr, pre_p, full_p)
                    st.success("Book Added!")
                else: st.error("All fields required.")
