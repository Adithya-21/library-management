import streamlit as st
import database
import pandas as pd
import os, base64, time

# ------------------ 1. CONFIG & ADMIN SETUP ------------------
st.set_page_config(page_title="Lumina Pro | Library", layout="wide", page_icon="✨")
database.create_tables()

# THE OFFICIAL ADMIN EMAIL
ADMIN_EMAIL = "adithya@example.com" 

# Folder setup
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
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
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
    .payment-box {
        background: #ffffff; padding: 30px; border-radius: 20px;
        border: 2px solid #3b82f6; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
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
                <object data="data:application/pdf;base64,{b64}" width="100%" height="750px" type="application/pdf" style="border-radius:15px; border:2px solid #3b82f6;">
                    <div style="padding:40px; text-align:center; background:#f8f9fa; border-radius:15px;">
                        <h4>Preview Mode</h4>
                        <a href="data:application/pdf;base64,{b64}" download="preview_sample.pdf" 
                           style="background-color:#3b82f6; color:white; padding:10px 20px; border-radius:8px; text-decoration:none; font-weight:bold;">
                           📥 Download Preview PDF
                        </a>
                    </div>
                </object>'''
            st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.error(f"Preview not found: {path}")

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
            with st.spinner("Processing Payment..."): time.sleep(2)
            st.balloons(); st.success("Payment Successful!"); return True
        else: st.error("Invalid Card Details")
    st.markdown("</div>", unsafe_allow_html=True)
    return False

# ------------------ 4. AUTH & SESSION ------------------
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': None, 'email': None, 'active_book': None, 'active_mode': None})

if not st.session_state['auth']:
    st.markdown("<div class='hero-bg'><h1>🏛️ Lumina Library</h1><p>Premium Digital Archives</p></div>", unsafe_allow_html=True)
    c1, col, c2 = st.columns([1, 2, 1])
    with col:
        t1, t2 = st.tabs(["🔒 Login", "📝 Register"])
        with t1:
            e_in = st.text_input("Email", key="l_email").lower().strip()
            p_in = st.text_input("Password", type="password", key="l_pass")
            if st.button("Access Library", key="l_btn"):
                user = database.verify_login(e_in, p_in)
                if user:
                    st.session_state.update({'auth': True, 'user': user[0], 'email': e_in})
                    st.rerun()
                else: st.error("Invalid credentials.")
        with t2:
            n_reg = st.text_input("Full Name", key="r_name")
            e_reg = st.text_input("Email", key="r_email").lower().strip()
            p_reg = st.text_input("Password", type="password", key="r_pass")
            if st.button("Create My Account", key="r_btn"):
                database.add_user(n_reg, e_reg, p_reg); st.success("Account Created!")

# ------------------ 5. MAIN APP ------------------
else:
    # --- ADMIN CHECK ---
    user_email = str(st.session_state['email']).lower().strip()
    is_admin = (user_email == ADMIN_EMAIL or user_email == "adithya@example.com")
    
    st.sidebar.title(f"👋 Hi, {st.session_state['user']}")
    menu = ["📊 Dashboard", "📖 Explore Catalog"]
    if is_admin:
        menu.append("⚙️ Librarian Desk")
        st.sidebar.success("🛡️ Admin Mode Active")
    
    choice = st.sidebar.selectbox("Navigation", menu)
    if st.sidebar.button("Logout"):
        st.session_state.update({'auth': False, 'active_book': None}); st.rerun()

    # A. DASHBOARD
    if choice == "📊 Dashboard":
        st.header("Library Inventory")
        books = database.get_all_books()
        st.metric("Total Books", len(books))
        if books:
            df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Category", "Stock", "Price", "URL", "Path"])
            st.dataframe(df.drop(columns=["URL", "Path"]), use_container_width=True, hide_index=True)

    # B. EXPLORE CATALOG (Includes Payment Logic)
    elif choice == "📖 Explore Catalog":
        st.title("Resource Gallery")
        tabs = st.tabs(["🎓 B.Tech", "📜 Telugu", "🕉️ Mythology"])
        genres = ["B.Tech", "Telugu", "Mythology"]
        
        for i, cat in enumerate(genres):
            with tabs[i]:
                data = database.get_books_by_category(cat)
                if not data: st.info("This shelf is empty.")
                
                cols = st.columns(3)
                for idx, b in enumerate(data):
                    with cols[idx % 3]:
                        st.markdown(f"<div class='book-card'><div class='book-title'>{b[1]}</div><div>{b[2]}</div></div>", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        
                        if c1.button("👁️ Preview", key=f"v_{cat}_{b[0]}"):
                            st.session_state.update({'active_book': b[0], 'active_mode': 'preview'})
                        
                        # Price Logic for Buy vs Get
                        if b[5] > 0:
                            if c2.button(f"₹{b[5]} Buy", key=f"b_{cat}_{b[0]}"):
                                st.session_state.update({'active_book': b[0], 'active_mode': 'pay'})
                        else:
                            if c2.button("📥 Get", key=f"d_{cat}_{b[0]}"):
                                st.session_state.update({'active_book': b[0], 'active_mode': 'download'})

                # VIEWER SECTION
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
                            # Triggers gateway if priced, otherwise passes through
                            payment_done = payment_gateway(active_b[1], active_b[5], cat) if mode == "pay" else True
                            
                            if payment_done:
                                f_path = active_b[7]
                                if str(f_path).startswith("http"):
                                    st.link_button("📥 Download Full Book (Drive)", f_path, use_container_width=True)
                                else:
                                    with open(f_path, "rb") as f:
                                        st.download_button("📥 Download Full Book (Local)", f, file_name=f"{active_b[1]}.pdf")

    # C. LIBRARIAN DESK
    elif choice == "⚙️ Librarian Desk":
        st.title("Admin Desk")
        with st.form("add_book_form"):
            t = st.text_input("Title")
            a = st.text_input("Author")
            c = st.selectbox("Genre", ["B.Tech", "Telugu", "Mythology"])
            p = st.number_input("Price (₹)", 0.0)
            is_link = st.checkbox("External Link (Drive)")
            pre_f = st.file_uploader("Preview (GitHub)", type="pdf")
            if is_link: val = st.text_input("Direct Link")
            else: val = st.file_uploader("Full PDF (GitHub)", type="pdf")
            
            if st.form_submit_button("🚀 Add Book"):
                if t and a and pre_f and val:
                    ts = int(time.time())
                    pre_p = f"previews/{ts}_{pre_f.name}"
                    with open(pre_p, "wb") as f: f.write(pre_f.getbuffer())
                    if is_link: fin_p = val
                    else:
                        fin_p = f"full_books/{ts}_{val.name}"
                        with open(fin_p, "wb") as f: f.write(val.getbuffer())
                    database.add_book(t, a, c, 1, p, pre_p, fin_p)
                    st.success("Book Registered!")
