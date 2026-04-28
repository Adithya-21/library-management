import streamlit as st
import database
import pandas as pd
import os
import base64
import time
import io
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# =================================================================
# 1. SYSTEM CONFIGURATION & DATABASE INITIALIZATION
# =================================================================
st.set_page_config(
    page_title="Apex Digital Library",
    layout="wide",
    page_icon="📖"
)

# Initialize the SQLite backend
database.create_tables()

# Administrative Settings
ADMIN_EMAIL = "adithya@example.com" 
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

# Ensure storage folders exist - Using 'preview' (singular)
for folder in ["preview", "full_books"]:
    full_path = os.path.join(BASE_DIR, folder)
    if not os.path.exists(full_path):
        os.makedirs(full_path, exist_ok=True)

# --- AUTO-STOCK ENGINE: Loads Initial Catalog ---
def refresh_library_data():
    """Wipes and reloads the default book inventory with absolute paths."""
    books_to_add = [
        ["Microelectronic Circuits", "Adel Sedra", "B.Tech", 5, 0.0, "preview/micro_pre.pdf", "https://drive.google.com/uc?export=download&id=1dNx66_LSW3mojyvJUukP5BjdFI9IURLS"],
        ["Introduction to Python", "Guido van Rossum", "B.Tech", 3, 100.0, "preview/python_pre.pdf", "https://drive.google.com/uc?export=download&id=1AzZCmQV7l0_wLKJVXdRY-o3a9mDiEoXV"],
        ["Neethikathalu", "Traditional", "Telugu", 10, 0.0, "preview/neethi_pre.pdf", "https://drive.google.com/uc?export=download&id=1CJVvRcYpPhObo4Nog7sIBqqfHcg5FvWf"],
        ["Ramayan", "Valmiki", "Mythology", 2, 200.0, "preview/ramayan_pre.pdf", "https://drive.google.com/uc?export=download&id=1GHF1LNsDyHe8kzjBGQ0geCpVPJOJbR39"]
    ]
    for b in books_to_add:
        database.add_book(b[0], b[1], b[2], b[3], b[4], b[5], b[6])

# Initial load if database is empty
if not database.get_all_books():
    refresh_library_data()

# =================================================================
# 2. CUSTOM UI STYLING (CSS)
# =================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .hero-section {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 60px; border-radius: 30px; color: white;
        text-align: center; margin-bottom: 40px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }
    
    .book-card {
        background: white; padding: 25px; border-radius: 20px;
        border: 1px solid #e2e8f0; transition: all 0.3s ease;
        margin-bottom: 20px; height: 200px; text-align: center;
        display: flex; flex-direction: column; justify-content: center;
    }
    
    .book-card:hover {
        transform: translateY(-8px); border-color: #3b82f6;
        box-shadow: 0 20px 30px rgba(0,0,0,0.1);
    }
    
    .book-title { color: #0f172a; font-weight: 800; font-size: 1.2rem; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. HELPER FUNCTIONS & COMPONENTS
# =================================================================

def get_pdf_base64(full_path):
    """Encodes PDF to base64 for embedding."""
    try:
        with open(full_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except: return None

def show_pdf(relative_path):
    """Renders PDF in an iframe with a Safety Valve fallback for Chrome."""
    abs_path = os.path.join(BASE_DIR, relative_path)
    filename = os.path.basename(relative_path)
    
    if os.path.exists(abs_path):
        b64 = get_pdf_base64(abs_path)
        if b64:
            # 1. THE MAIN IFRAME VIEWER
            pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="850px" style="border:3px solid #3b82f6; border-radius:20px;"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            # 2. THE SAFETY VALVE (Alternative Access)
            st.markdown("---")
            with st.expander("📥 Preview Blocked? Use Alternative Access"):
                st.info("If the preview above is blank, your browser security settings (like Chrome's Sandbox) are blocking the embed. Use the button below to view it locally.")
                pdf_bytes = base64.b64decode(b64)
                st.download_button(
                    label=f"📖 Open {filename} Locally",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.error("Encoding Error: Unable to process the file.")
    else:
        st.error(f"📂 Path Error: The server cannot locate: {abs_path}")

def payment_gateway(book_title, price, session_key):
    """Full-featured interactive payment simulation."""
    st.markdown("<div style='background:white; padding:35px; border-radius:25px; border:2px solid #3b82f6;'>", unsafe_allow_html=True)
    st.subheader("💳 Secure Payment Gateway")
    st.write(f"Order: **{book_title}** | Amount: **₹{price}**")
    
    col1, col2 = st.columns(2)
    card_num = col1.text_input("Card Number", placeholder="XXXX XXXX XXXX XXXX", key=f"card_{session_key}")
    cvv = col2.text_input("CVV", type="password", key=f"cvv_{session_key}")
    
    if st.button("Authorize Transaction", key=f"pay_btn_{session_key}", use_container_width=True):
        if len(card_num) >= 12:
            with st.spinner("Processing..."): time.sleep(2)
            st.balloons(); st.success("✅ Payment Successful!"); return True
        else: st.error("Invalid details.")
    st.markdown("</div>", unsafe_allow_html=True)
    return False

def draw_clock():
    """Injects a real-time ticking clock using JavaScript."""
    clock_js = """
    <div id="clock" style="font-family:'Inter', sans-serif; color:#3b82f6; font-size:24px; font-weight:800; text-align:center; padding:12px; background:#0f172a; border-radius:15px; border:1px solid #1e293b;">00:00:00</div>
    <script>
    function updateTime() {
        const now = new Date();
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        const s = String(now.getSeconds()).padStart(2, '0');
        document.getElementById('clock').innerText = h + ":" + m + ":" + s;
    }
    setInterval(updateTime, 1000); updateTime();
    </script>
    """
    st.sidebar.markdown("🕒 **System Time (IST)**")
    components.html(clock_js, height=80)

# =================================================================
# 4. AUTHENTICATION & SESSION MANAGEMENT
# =================================================================

if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': None, 'email': None, 'active_book': None, 'active_mode': None, 'celebrate': False})

if not st.session_state['auth']:
    st.markdown("<div class='hero-section'><h1>📖 Apex Digital Library</h1><p>Modern Engineering Learning</p></div>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        t_log, t_reg = st.tabs(["🔑 Login", "📝 Register"])
        with t_log:
            le = st.text_input("Email", key="log_e").lower().strip()
            lp = st.text_input("Password", type="password", key="log_p")
            if st.button("Enter Library", use_container_width=True):
                user = database.verify_login(le, lp)
                if user:
                    st.session_state.update({'auth': True, 'user': user[0], 'email': le, 'celebrate': True})
                    st.rerun()
                else: st.error("Invalid Email or Password.")
        with t_reg:
            rn = st.text_input("Full Name")
            re = st.text_input("Email").lower().strip()
            rp = st.text_input("Password", type="password")
            if st.button("Join Apex Family", use_container_width=True):
                if rn and re and rp:
                    database.add_user(rn, re, rp)
                    st.success("🎉 Hurrah! Thank you for joining our Apex family. Please login.")

# =================================================================
# 5. MAIN APPLICATION INTERFACE
# =================================================================

else:
    if st.session_state['celebrate']:
        st.balloons(); st.session_state['celebrate'] = False

    draw_clock()
    ist_now = datetime.now() + timedelta(hours=5, minutes=30)
    hour = ist_now.hour
    greet = "🌅 Good Morning" if hour < 12 else "☀️ Good Afternoon" if hour < 17 else "🌙 Good Evening"
    st.sidebar.markdown(f"### {greet},")
    st.sidebar.title(f"{st.session_state['user']}!")
    
    is_admin = (st.session_state['email'] == ADMIN_EMAIL or st.session_state['email'] == "adithya@example.com")
    nav = ["📊 Dashboard", "📖 Explore Catalog"]
    if is_admin: nav.append("⚙️ Librarian Desk")
    
    app_mode = st.sidebar.selectbox("Navigation", nav)
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.update({'auth': False, 'active_book': None}); st.rerun()

    # --- A. DASHBOARD ---
    if app_mode == "📊 Dashboard":
        st.markdown("<div class='hero-section'><h1>Library Dashboard</h1></div>", unsafe_allow_html=True)
        all_books = database.get_all_books()
        m1, m2, m3 = st.columns(3)
        m1.metric("📚 Titles", len(all_books))
        m2.metric("📦 Status", "🟢 Online")
        m3.metric("🇮🇳 Region", "India-South")
        if all_books:
            df = pd.DataFrame(all_books, columns=["ID", "Title", "Author", "Category", "Stock", "Price", "URL", "Path"])
            st.dataframe(df[["Title", "Author", "Category", "Price"]], use_container_width=True, hide_index=True)

    # --- B. CATALOG ---
    elif app_mode == "📖 Explore Catalog":
        st.title("Resource Gallery")
        tabs = st.tabs(["🎓 B.Tech", "📜 Telugu", "🕉️ Mythology"])
        cats = ["B.Tech", "Telugu", "Mythology"]
        for i, c_name in enumerate(cats):
            with tabs[i]:
                b_data = database.get_books_by_category(c_name)
                cols = st.columns(3)
                for idx, b in enumerate(b_data):
                    with cols[idx % 3]:
                        st.markdown(f"<div class='book-card'><div class='book-title'>{b[1]}</div><div>{b[2]}</div></div>", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        if c1.button("👁️ Preview", key=f"p_{c_name}_{b[0]}", use_container_width=True):
                            st.session_state.update({'active_book': b[0], 'active_mode': 'preview'})
                        if b[5] > 0:
                            if c2.button(f"₹{int(b[5])} Buy", key=f"b_{c_name}_{b[0]}", use_container_width=True):
                                st.session_state.update({'active_book': b[0], 'active_mode': 'pay'})
                        else:
                            if c2.button("📥 Get", key=f"g_{c_name}_{b[0]}", use_container_width=True):
                                st.session_state.update({'active_book': b[0], 'active_mode': 'download'})

                if st.session_state['active_book']:
                    sel = next((bk for bk in b_data if bk[0] == st.session_state['active_book']), None)
                    if sel:
                        st.divider()
                        if st.button("❌ Close Viewer", key=f"cl_{c_name}", use_container_width=True):
                            st.session_state['active_book'] = None; st.rerun()
                        m = st.session_state['active_mode']
                        if m == 'preview': show_pdf(sel[6])
                        elif m == 'pay':
                            if payment_gateway(sel[1], sel[5], c_name): st.link_button("🚀 Download", sel[7], use_container_width=True)
                        elif m == 'download':
                            if str(sel[7]).startswith("http"): st.link_button("🚀 Access", sel[7], use_container_width=True)
                            else:
                                with open(sel[7], "rb") as f: st.download_button("💾 Save PDF", f, file_name=f"{sel[1]}.pdf", use_container_width=True)

    # --- C. LIBRARIAN DESK ---
    elif app_mode == "⚙️ Librarian Desk":
        st.title("🔐 Librarian Control Panel")
        col_t1, col_t2 = st.columns(2)
        if col_t1.button("🔄 Reset & Refresh Database", use_container_width=True):
            conn = database.connect_db(); cursor = conn.cursor(); cursor.execute("DELETE FROM books"); conn.commit(); conn.close()
            refresh_library_data(); st.success("System Restored!"); time.sleep(1); st.rerun()
        if col_t2.button("📥 Export Audit Report (Excel)", use_container_width=True):
            conn = database.connect_db(); d1 = pd.read_sql_query("SELECT * FROM books", conn); d2 = pd.read_sql_query("SELECT name, email FROM users", conn); conn.close()
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                d1.to_excel(writer, sheet_name='Inventory', index=False); d2.to_excel(writer, sheet_name='Users', index=False)
            st.download_button(label="📥 Download Excel", data=buf.getvalue(), file_name=f"Audit_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        st.divider(); st.subheader("➕ Register New Resource")
        with st.form("add_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            nt = f1.text_input("Title"); na = f2.text_input("Author"); nc = st.selectbox("Category", ["B.Tech", "Telugu", "Mythology"])
            f3, f4 = st.columns(2)
            ns = f3.number_input("Stock", min_value=1, value=5); np = f4.number_input("Price (₹)", 0.0)
            ul = st.checkbox("External URL"); pf = st.file_uploader("Preview (PDF)", type="pdf")
            rv = st.text_input("URL") if ul else st.file_uploader("Full PDF", type="pdf")
            if st.form_submit_button("🚀 Commit to Database", use_container_width=True):
                if nt and na and pf and rv:
                    ts = int(time.time()); pp = f"preview/{ts}_{pf.name}"
                    with open(os.path.join(BASE_DIR, pp), "wb") as f: f.write(pf.getbuffer())
                    fp = rv if ul else f"full_books/{ts}_{rv.name}"
                    if not ul:
                        with open(os.path.join(BASE_DIR, fp), "wb") as f: f.write(rv.getbuffer())
                    database.add_book(nt, na, nc, ns, np, pp, fp); st.success(f"Added {nt}!"); time.sleep(1); st.rerun()
