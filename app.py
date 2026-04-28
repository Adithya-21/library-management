import streamlit as st
import database
import pandas as pd
import os, base64, time
from pathlib import Path

# ------------------ 1. CONFIG & SYSTEM SETUP ------------------
st.set_page_config(page_title="Lumina Pro | Digital Library", layout="wide", page_icon="🌿")
database.create_tables()

# !!! SECURITY: Ensure this email is ALL LOWERCASE !!!
ADMIN_EMAIL = "adithya@example.com" 

# Robust folder creation for Cloud
for folder in ["previews", "full_books"]:
    Path(folder).mkdir(parents=True, exist_ok=True)

# ------------------ 2. DYNAMIC CSS ENGINE ------------------
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': None, 'email': None, 'active_book': None, 'active_mode': None})

if not st.session_state['auth']:
    # --- GRAND LOGIN: WARM WORKSPACE ---
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #D96846;
            background-image: radial-gradient(circle at 20% 30%, rgba(255,255,255,0.1) 0%, transparent 50%);
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 24px; padding: 40px;
            box-shadow: 0 15px 35px rgba(47, 48, 32, 0.2);
        }
        [data-testid="stWidgetLabel"] p { color: #2F3020 !important; font-weight: 600; }
        h1 { color: white !important; text-align: center; font-weight: 800; letter-spacing: -1px; }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-15px); }
            100% { transform: translateY(0px); }
        }
        .floating-icon { font-size: 50px; text-align: center; animation: float 3s ease-in-out infinite; }
        </style>
        """, unsafe_allow_html=True)
else:
    # --- SIMPLE INTERIOR: PROFESSIONAL CLEAN ---
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #f8fafc; }
        .stMetric { background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }
        .book-card { 
            background: white; padding: 20px; border-radius: 12px; 
            border-left: 6px solid #596235; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        }
        h1, h2, h3, p, [data-testid="stWidgetLabel"] p { color: #1e293b !important; }
        </style>
        """, unsafe_allow_html=True)

# ------------------ 3. CORE UTILITIES ------------------
@st.cache_data
def get_pdf_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        return None

def show_pdf(path):
    # Debugging check for Cloud
    if os.path.exists(path):
        b64 = get_pdf_base64(path)
        if b64:
            pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="800px" style="border:none; border-radius:15px;"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error("Could not encode the PDF file.")
    else:
        st.error(f"📂 File missing on server at: {path}")
        st.info("On Streamlit Cloud, files disappear if the app reboots. Please re-upload via Librarian Desk.")

# ------------------ 4. EXTERIOR: THE VAULT ------------------
if not st.session_state['auth']:
    st.markdown("<div class='floating-icon'>📖</div>", unsafe_allow_html=True)
    st.markdown("<h1>LUMINA PRO</h1>", unsafe_allow_html=True)
    
    _, col_m, _ = st.columns([1, 1.5, 1])
    with col_m:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["🔒 Secure Entry", "🌱 New Registry"])
        with t1:
            e = st.text_input("Email", key="login_email_input").lower().strip()
            p = st.text_input("Password", type="password", key="login_pass_input")
            if st.button("Unlock The Library", use_container_width=True):
                user = database.verify_login(e, p)
                if user:
                    st.session_state.update({'auth': True, 'user': user[1], 'email': user[2]})
                    st.rerun()
                else: st.error("Verification Failed.")
        with t2:
            n = st.text_input("Full Name", key="reg_name")
            em = st.text_input("Email", key="reg_email").lower().strip()
            pw = st.text_input("Password", type="password", key="reg_pass")
            if st.button("Initialize Membership", use_container_width=True):
                database.add_user(n, em, pw); st.success("Registry Successful!")
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------ 5. INTERIOR: THE WORKSPACE ------------------
else:
    st.sidebar.markdown(f"### 🌿 {st.session_state['user']}")
    menu = ["📊 Dashboard", "📖 Explore Catalog"]
    if st.session_state['email'] == ADMIN_EMAIL:
        menu.append("⚙️ Librarian Desk")
    
    choice = st.sidebar.selectbox("System Navigation", menu)
    if st.sidebar.button("Logout System"):
        st.session_state.update({'auth': False, 'active_book': None})
        st.rerun()

    # --- DASHBOARD ---
    if choice == "📊 Dashboard":
        st.title("Workspace Insights")
        books = database.get_all_books()
        c1, c2, c3 = st.columns(3)
        c1.metric("Catalog Size", len(books))
        c2.metric("Server Status", "Active", delta="Stable")
        c3.metric("Cloud Storage", "Ephemeral")
        
        if books:
            df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Genre", "Stock", "Price", "P_Path", "F_Path"])
            st.dataframe(df.drop(columns=["P_Path", "F_Path"]), use_container_width=True, hide_index=True)

    # --- CATALOG ---
    elif choice == "📖 Explore Catalog":
        st.title("Digital Archives")
        genres = ["B.Tech", "Telugu", "Mythology"]
        tabs = st.tabs([f"📂 {g}" for g in genres])
        
        for i, cat in enumerate(genres):
            with tabs[i]:
                data = database.get_books_by_category(cat)
                if not data: st.info(f"The {cat} archive is currently empty.")
                
                cols = st.columns(3)
                for idx, b in enumerate(data):
                    with cols[idx % 3]:
                        st.markdown(f"<div class='book-card'><h4>{b[1]}</h4><p>By {b[2]}</p></div>", unsafe_allow_html=True)
                        bc1, bc2 = st.columns(2)
                        if bc1.button("👁️ Preview", key=f"pre_{cat}_{b[0]}"):
                            st.session_state['active_book'], st.session_state['active_mode'] = b[0], "preview"
                        if bc2.button("📥 Get Full", key=f"get_{cat}_{b[0]}"):
                            st.session_state['active_book'], st.session_state['active_mode'] = b[0], "download"
                
                # Global Viewer (Below the grid)
                if st.session_state['active_book']:
                    st.divider()
                    if st.button("❌ Close Viewer", key=f"close_{cat}"):
                        st.session_state['active_book'] = None; st.rerun()
                    
                    # Logic to find the active book's paths
                    all_b = database.get_all_books()
                    active_b = next((x for x in all_b if x[0] == st.session_state['active_book']), None)
                    
                    if active_b:
                        if st.session_state['active_mode'] == "preview":
                            show_pdf(active_b[6])
                        else:
                            with open(active_b[7], "rb") as f:
                                st.download_button("💾 Download Master File", f, file_name=f"{active_b[1]}.pdf", key=f"dl_btn_{cat}")

    # --- LIBRARIAN DESK ---
    elif choice == "⚙️ Librarian Desk":
        st.title("Librarian Authority")
        if st.button("🧹 Clear System Cache"):
            st.cache_data.clear(); st.success("Cache Cleared!"); st.rerun()
            
        with st.form("add_book_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            t = col1.text_input("Book Title")
            a = col2.text_input("Author Name")
            cat = st.selectbox("Assign Genre", ["B.Tech", "Telugu", "Mythology"])
            pr = st.number_input("Set Price (0 for Free)", 0.0)
            pre_f = st.file_uploader("Upload 10-Page Preview", type="pdf")
            full_f = st.file_uploader("Upload Complete Book", type="pdf")
            
            if st.form_submit_button("🚀 Finalize Archive"):
                if t and pre_f and full_f:
                    ts = int(time.time())
                    p1 = os.path.join("previews", f"{ts}_{pre_f.name}")
                    p2 = os.path.join("full_books", f"{ts}_{full_f.name}")
                    with Path(p1).open("wb") as f: f.write(pre_f.getbuffer())
                    with Path(p2).open("wb") as f: f.write(full_f.getbuffer())
                    database.add_book(t, a, cat, 1, pr, p1, p2)
                    st.success(f"'{t}' has been successfully archived!")
                else: st.error("Missing required files or information.")
