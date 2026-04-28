# =================================================================
# PROJECT: Apex Digital Library
# AUTHOR: Adithya (ECE Dept.)
# PURPOSE: A Full-Stack Resource Management System for Engineers
# =================================================================

import streamlit as st
import database
import pandas as pd
import os, base64, time, io
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# --- 1. GLOBAL CONFIGURATION ---
st.set_page_config(
    page_title="Apex Digital Library",
    layout="wide",
    page_icon="📖"
)

# Initialize our SQL database tables
database.create_tables()

# Setup paths and admin credentials
ADMIN_EMAIL = "adithya@example.com" 
ROOT_PATH = os.path.dirname(os.path.abspath(__file__)) 

# Create local storage folders for PDF assets if they are missing
for folder_name in ["preview", "full_books"]:
    dir_path = os.path.join(ROOT_PATH, folder_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

# --- 2. CORE LIBRARY ENGINE ---
def refresh_library_data():
    """
    DEV NOTE: This function handles the initial stock. 
    I've mapped the 'preview/' paths specifically for the GitHub repo.
    """
    initial_inventory = [
        ["Microelectronic Circuits", "Adel Sedra", "B.Tech", 5, 0.0, "preview/micro_pre.pdf", "https://drive.google.com/uc?export=download&id=1dNx66_LSW3mojyvJUukP5BjdFI9IURLS"],
        ["Introduction to Python", "Guido van Rossum", "B.Tech", 3, 100.0, "preview/python_pre.pdf", "https://drive.google.com/uc?export=download&id=1AzZCmQV7l0_wLKJVXdRY-o3a9mDiEoXV"],
        ["Neethikathalu", "Traditional", "Telugu", 10, 0.0, "preview/neethi_pre.pdf", "https://drive.google.com/uc?export=download&id=1CJVvRcYpPhObo4Nog7sIBqqfHcg5FvWf"],
        ["Ramayan", "Valmiki", "Mythology", 2, 200.0, "preview/ramayan_pre.pdf", "https://drive.google.com/uc?export=download&id=1GHF1LNsDyHe8kzjBGQ0geCpVPJOJbR39"]
    ]
    for item in initial_inventory:
        database.add_book(item[0], item[1], item[2], item[3], item[4], item[5], item[6])

# Run the stock engine only if the library is empty
if not database.get_all_books():
    refresh_library_data()

# --- 3. UI STYLING & INTERFACE CUSTOMIZATION ---
st.markdown("""
    <style>
    /* Clean, modern typography for a professional look */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 50px; border-radius: 25px; color: white;
        text-align: center; margin-bottom: 30px;
        box-shadow: 0 15px 30px rgba(0,0,0,0.25);
    }
    
    .book-card {
        background: #ffffff; padding: 25px; border-radius: 20px;
        border: 1px solid #e2e8f0; transition: transform 0.3s ease;
        margin-bottom: 15px; height: 180px; text-align: center;
        display: flex; flex-direction: column; justify-content: center;
    }
    
    .book-card:hover {
        transform: translateY(-5px); border-color: #3b82f6;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    }
    
    .title-text { color: #0f172a; font-weight: 800; font-size: 1.15rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. UTILITY FUNCTIONS ---

def render_pdf_viewer(path):
    """
    Handles PDF embedding. 
    Includes a 'Safety Valve' fallback because Chrome often blocks Data URIs.
    """
    absolute_path = os.path.join(ROOT_PATH, path)
    
    if os.path.exists(absolute_path):
        try:
            with open(absolute_path, "rb") as f:
                encoded_pdf = base64.b64encode(f.read()).decode('utf-8')
            
            # The Main Iframe View
            pdf_frame = f'<iframe src="data:application/pdf;base64,{encoded_pdf}" width="100%" height="800px" style="border:2px solid #3b82f6; border-radius:15px;"></iframe>'
            st.markdown(pdf_frame, unsafe_allow_html=True)
            
            # The Fallback Download Button
            st.markdown("---")
            with st.expander("📥 Preview not loading? Click for Alternative Access"):
                st.info("Browser security settings may block the embed. Click below to view the PDF locally.")
                st.download_button(
                    label="📖 Open PDF in New Tab",
                    data=base64.b64decode(encoded_pdf),
                    file_name=os.path.basename(path),
                    mime="application/pdf",
                    use_container_width=True
                )
        except Exception as err:
            st.error(f"Error processing PDF: {err}")
    else:
        st.error(f"📂 File not found on server: {path}")

def run_payment_gateway(name, price, key):
    """Simulates a secure transaction environment for premium resources."""
    st.markdown("<div style='background:#f8fafc; padding:30px; border-radius:20px; border:2px solid #3b82f6;'>", unsafe_allow_html=True)
    st.subheader("💳 Secure Checkout")
    st.write(f"Resource: **{name}** | **Amount: ₹{price}**")
    
    col1, col2 = st.columns(2)
    card = col1.text_input("Card Number", placeholder="1234 5678 9012", key=f"c_{key}")
    cvv = col2.text_input("CVV", type="password", key=f"v_{key}")
    
    if st.button("Complete Transaction", key=f"pay_{key}", use_container_width=True):
        if len(card) >= 12:
            with st.spinner("Authorizing..."): time.sleep(2)
            st.balloons(); st.success("✅ Payment Confirmed!"); return True
        else: st.error("Please provide valid payment info.")
    st.markdown("</div>", unsafe_allow_html=True)
    return False

def inject_sidebar_clock():
    """JavaScript clock to show current IST time in the sidebar."""
    clock_html = """
    <div id="clock" style="font-family:'Inter',sans-serif; color:#3b82f6; font-size:24px; font-weight:800; text-align:center; padding:12px; background:#0f172a; border-radius:15px; border:1px solid #1e293b;">00:00:00</div>
    <script>
    function update() {
        const now = new Date();
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        const s = String(now.getSeconds()).padStart(2, '0');
        document.getElementById('clock').innerText = h + ":" + m + ":" + s;
    }
    setInterval(update, 1000); update();
    </script>
    """
    st.sidebar.markdown("🕒 **System Clock (IST)**")
    components.html(clock_html, height=80)

# --- 5. AUTHENTICATION & SESSION LOGIC ---

if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': None, 'email': None, 'book_id': None, 'mode': None, 'fresh_login': False})

if not st.session_state['auth']:
    st.markdown("<div class='hero-banner'><h1>📖 Apex Digital Library</h1><p>The Future of Academic Resource Management</p></div>", unsafe_allow_html=True)
    _, login_col, _ = st.columns([1, 2, 1])
    with login_col:
        tab1, tab2 = st.tabs(["🔑 Access Account", "📝 New User"])
        with tab1:
            u_email = st.text_input("Institutional Email", key="log_e").lower().strip()
            u_pass = st.text_input("Password", type="password", key="log_p")
            if st.button("Sign In", use_container_width=True):
                account = database.verify_login(u_email, u_pass)
                if account:
                    st.session_state.update({'auth': True, 'user': account[0], 'email': u_email, 'fresh_login': True})
                    st.rerun()
                else: st.error("Login failed. Check credentials.")
        with tab2:
            new_n = st.text_input("Full Name")
            new_e = st.text_input("Email").lower().strip()
            new_p = st.text_input("Create Password", type="password")
            if st.button("Create Account", use_container_width=True):
                if new_n and new_e and new_p:
                    database.add_user(new_n, new_e, new_p)
                    st.success("🎉 Account created! You can now log in.")

# --- 6. MAIN APPLICATION ---

else:
    if st.session_state['fresh_login']:
        st.balloons(); st.toast(f"Welcome back, {st.session_state['user']}!"); st.session_state['fresh_login'] = False

    inject_sidebar_clock()
    
    # IST-Corrected Greeting (Manual offset of 5:30)
    ist_time = datetime.now() + timedelta(hours=5, minutes=30)
    hour_now = ist_time.hour
    msg = "🌅 Good Morning" if hour_now < 12 else "☀️ Good Afternoon" if hour_now < 17 else "🌙 Good Evening"
    
    st.sidebar.markdown(f"### {msg},")
    st.sidebar.title(f"{st.session_state['user']}!")
    
    admin_status = (st.session_state['email'] in [ADMIN_EMAIL, "adithya@example.com"])
    menu = ["📊 Dashboard", "📖 Digital Catalog"]
    if admin_status: menu.append("⚙️ Librarian Desk")
    
    page = st.sidebar.selectbox("Navigate To:", menu)
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.update({'auth': False}); st.rerun()

    # A. DASHBOARD VIEW
    if page == "📊 Dashboard":
        st.markdown("<div class='hero-banner'><h1>Library Analytics</h1></div>", unsafe_allow_html=True)
        inventory = database.get_all_books()
        c1, c2, c3 = st.columns(3)
        c1.metric("📚 Unique Titles", len(inventory))
        c2.metric("📦 Cloud Connection", "🟢 Active")
        c3.metric("💻 Server Node", "Primary-IST")
        if inventory:
            df_inv = pd.DataFrame(inventory, columns=["ID", "Title", "Author", "Category", "Stock", "Price", "URL", "Path"])
            st.dataframe(df_inv[["Title", "Author", "Category", "Price"]], use_container_width=True, hide_index=True)

    # B. CATALOG VIEW
    elif page == "📖 Digital Catalog":
        st.title("Resource Archive")
        t1, t2, t3 = st.tabs(["🎓 B.Tech", "📜 Telugu", "🕉️ Mythology"])
        tabs_list = [t1, t2, t3]; categories = ["B.Tech", "Telugu", "Mythology"]
        
        for i, cat_name in enumerate(categories):
            with tabs_list[i]:
                books = database.get_books_by_category(cat_name)
                cols = st.columns(3)
                for index, b in enumerate(books):
                    with cols[index % 3]:
                        st.markdown(f"<div class='book-card'><div class='title-text'>{b[1]}</div><div style='color:#64748b;'>{b[2]}</div></div>", unsafe_allow_html=True)
                        b1, b2 = st.columns(2)
                        if b1.button("👁️ Preview", key=f"p_{cat_name}_{b[0]}", use_container_width=True):
                            st.session_state.update({'book_id': b[0], 'mode': 'preview'})
                        
                        if b[5] > 0:
                            if b2.button(f"₹{int(b[5])} Buy", key=f"b_{cat_name}_{b[0]}", use_container_width=True):
                                st.session_state.update({'book_id': b[0], 'mode': 'pay'})
                        else:
                            if b2.button("📥 Get", key=f"g_{cat_name}_{b[0]}", use_container_width=True):
                                st.session_state.update({'book_id': b[0], 'mode': 'download'})

                # The Active Viewer Area
                if st.session_state['book_id']:
                    active = next((bk for bk in books if bk[0] == st.session_state['book_id']), None)
                    if active:
                        st.divider()
                        if st.button("❌ Close Viewer", key=f"close_{cat_name}", use_container_width=True):
                            st.session_state['book_id'] = None; st.rerun()
                        
                        work_mode = st.session_state['mode']
                        if work_mode == 'preview': render_pdf_viewer(active[6])
                        elif work_mode == 'pay':
                            if run_payment_gateway(active[1], active[5], cat_name):
                                st.link_button("🚀 Access Link", active[7], use_container_width=True)
                        elif work_mode == 'download':
                            if str(active[7]).startswith("http"): st.link_button("🚀 Direct Access", active[7], use_container_width=True)
                            else:
                                with open(active[7], "rb") as f: st.download_button("💾 Download PDF", f, file_name=f"{active[1]}.pdf", use_container_width=True)

    # C. LIBRARIAN DESK VIEW
    elif page == "⚙️ Librarian Desk":
        st.title("🔐 Control Panel")
        col_m1, col_m2 = st.columns(2)
        
        if col_m1.button("🔄 Sync & Refresh Catalog", use_container_width=True):
            conn = database.connect_db(); cursor = conn.cursor(); cursor.execute("DELETE FROM books"); conn.commit(); conn.close()
            refresh_library_data(); st.success("Database resynced with 'preview/' folder!"); time.sleep(1); st.rerun()
            
        if col_m2.button("📥 Generate Excel Audit", use_container_width=True):
            conn = database.connect_db(); d_inv = pd.read_sql_query("SELECT * FROM books", conn); d_usr = pd.read_sql_query("SELECT name, email FROM users", conn); conn.close()
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                d_inv.to_excel(writer, sheet_name='Inventory', index=False); d_usr.to_excel(writer, sheet_name='Users', index=False)
            st.download_button(label="📥 Download Audit File", data=output.getvalue(), file_name=f"Library_Audit_{datetime.now().strftime('%Y%m%d')}.xlsx", use_container_width=True)

        st.divider(); st.subheader("➕ Register New Resource")
        with st.form("add_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            t_in = f1.text_input("Resource Title"); a_in = f2.text_input("Lead Author"); c_in = st.selectbox("Category", ["B.Tech", "Telugu", "Mythology"])
            s_in = st.number_input("Copies in Stock", min_value=1, value=5); p_in = st.number_input("Retail Price (₹)", 0.0)
            is_url = st.checkbox("External Cloud Link?"); p_file = st.file_uploader("Upload Preview (PDF)", type="pdf")
            r_val = st.text_input("Link URL") if is_url else st.file_uploader("Full Resource (PDF)", type="pdf")
            
            if st.form_submit_button("🚀 Add to Catalog", use_container_width=True):
                if t_in and a_in and p_file and r_val:
                    stamp = int(time.time()); p_path = f"preview/{stamp}_{p_file.name}"
                    with open(os.path.join(ROOT_PATH, p_path), "wb") as f: f.write(p_file.getbuffer())
                    f_path = r_val if is_url else f"full_books/{stamp}_{r_val.name}"
                    if not is_url:
                        with open(os.path.join(ROOT_PATH, f_path), "wb") as f: f.write(r_val.getbuffer())
                    database.add_book(t_in, a_in, c_in, s_in, p_in, p_path, f_path); st.success(f"Successfully added: {t_in}"); time.sleep(1); st.rerun()
