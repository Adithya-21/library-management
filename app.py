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

# Create necessary directories for local file storage
for folder in ["preview", "full_books"]:
    full_path = os.path.join(BASE_DIR, folder)
    if not os.path.exists(full_path):
        os.makedirs(full_path, exist_ok=True)

# --- AUTO-STOCK ENGINE: Loads Initial Catalog ---
def refresh_library_data():
    """Wipes and reloads the default book inventory with correct paths."""
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
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .hero-section {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 60px;
        border-radius: 30px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }
    
    .book-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        height: 200px;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .book-card:hover {
        transform: translateY(-8px);
        border-color: #3b82f6;
        box-shadow: 0 20px 30px rgba(0,0,0,0.1);
    }
    
    .book-title {
        color: #0f172a;
        font-weight: 800;
        font-size: 1.2rem;
        margin-bottom: 5px;
    }
    
    .sidebar-clock {
        background: #0f172a;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #1e293b;
        margin-bottom: 20px;
    }
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
    except:
        return None

def show_pdf(relative_path):
    """Renders PDF in an iframe with absolute path resolution."""
    abs_path = os.path.join(BASE_DIR, relative_path)
    if os.path.exists(abs_path):
        b64 = get_pdf_base64(abs_path)
        if b64:
            pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="900px" style="border:3px solid #3b82f6; border-radius:20px;"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error("Encoding Error: Unable to process the file.")
    else:
        st.error(f"📂 Path Error: The server cannot locate: {abs_path}")
        st.info("💡 Pro-Tip: Ensure your GitHub folder is named 'preview' and use the Librarian Reset button.")

def payment_gateway(book_title, price, session_key):
    """Full-featured interactive payment simulation."""
    st.markdown("<div style='background:white; padding:35px; border-radius:25px; border:2px solid #3b82f6; box-shadow: 0 10px 20px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
    st.subheader("💳 Secure Payment Gateway")
    st.write(f"Order: **{book_title}**")
    st.markdown(f"<h2 style='color:#2563eb;'>Amount: ₹{price}</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    card_num = col1.text_input("Debit/Credit Card Number", placeholder="XXXX XXXX XXXX XXXX", key=f"card_{session_key}")
    expiry = col2.text_input("Expiry Date", placeholder="MM/YY", key=f"exp_{session_key}")
    cvv = st.text_input("CVV", type="password", help="3-digit security code", key=f"cvv_{session_key}")
    
    if st.button("Authorize Transaction", key=f"pay_btn_{session_key}", use_container_width=True):
        if len(card_num) >= 12 and len(cvv) == 3:
            with st.spinner("Communicating with Bank..."):
                time.sleep(2.5)
            st.balloons()
            st.success("✅ Transaction Successful! Your digital copy is ready.")
            return True
        else:
            st.error("Invalid payment details. Please check your card info.")
    st.markdown("</div>", unsafe_allow_html=True)
    return False

def draw_clock():
    """Injects a real-time ticking clock using JavaScript."""
    clock_js = """
    <div id="clock" style="font-family:'Inter', sans-serif; color:#3b82f6; font-size:26px; font-weight:800; text-align:center; padding:12px; background:#0f172a; border-radius:15px; border:1px solid #1e293b; box-shadow: inset 0 0 10px rgba(59,130,246,0.1);">
        00:00:00
    </div>
    <script>
    function updateTime() {
        const now = new Date();
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        const s = String(now.getSeconds()).padStart(2, '0');
        document.getElementById('clock').innerText = h + ":" + m + ":" + s;
    }
    setInterval(updateTime, 1000);
    updateTime();
    </script>
    """
    st.sidebar.markdown("🕒 **Current System Time**")
    components.html(clock_js, height=85)

# =================================================================
# 4. AUTHENTICATION & SESSION MANAGEMENT
# =================================================================

if 'auth' not in st.session_state:
    st.session_state.update({
        'auth': False,
        'user': None,
        'email': None,
        'active_book': None,
        'active_mode': None,
        'celebrate': False
    })

# --- LANDING PAGE: Login & Registration ---
if not st.session_state['auth']:
    st.markdown("<div class='hero-section'><h1>📖 Apex Digital Library</h1><p>Engineering Excellence • Modern Pedagogy</p></div>", unsafe_allow_html=True)
    
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        tab_login, tab_reg = st.tabs(["🔑 Access Account", "📝 New Registration"])
        
        with tab_login:
            login_email = st.text_input("Institutional Email", key="log_e").lower().strip()
            login_pass = st.text_input("Password", type="password", key="log_p")
            if st.button("Enter Library", use_container_width=True):
                user_record = database.verify_login(login_email, login_pass)
                if user_record:
                    st.session_state.update({
                        'auth': True,
                        'user': user_record[0],
                        'email': login_email,
                        'celebrate': True
                    })
                    st.rerun()
                else:
                    st.error("Authentication Failed: Invalid Email or Password.")
        
        with tab_reg:
            reg_name = st.text_input("Full Name (Official)")
            reg_email = st.text_input("Email Address").lower().strip()
            reg_pass = st.text_input("Create Secure Password", type="password")
            if st.button("Join Apex Family", use_container_width=True):
                if reg_name and reg_email and reg_pass:
                    database.add_user(reg_name, reg_email, reg_pass)
                    st.success("🎉 Hurrah! Thank you for joining our Apex family. You may now proceed to login.")
                else:
                    st.warning("Please complete all fields to register.")

# =================================================================
# 5. MAIN APPLICATION INTERFACE
# =================================================================

else:
    # --- LOGIN CELEBRATION ---
    if st.session_state['celebrate']:
        st.balloons()
        st.toast(f"Welcome back, {st.session_state['user']}! System online.")
        st.session_state['celebrate'] = False

    # --- SIDEBAR NAVIGATION ---
    draw_clock()
    
    # IST Time Greeting Logic
    ist_now = datetime.now() + timedelta(hours=5, minutes=30)
    current_hour = ist_now.hour
    if current_hour < 12:
        greeting = "🌅 Good Morning"
    elif 12 <= current_hour < 17:
        greeting = "☀️ Good Afternoon"
    else:
        greeting = "🌙 Good Evening"
        
    st.sidebar.markdown(f"### {greeting},")
    st.sidebar.title(f"{st.session_state['user']}!")
    
    # Admin Privileges Check
    user_email = st.session_state['email']
    is_admin = (user_email == ADMIN_EMAIL or user_email == "adithya@example.com")
    
    nav_options = ["📊 Dashboard", "📖 Explore Catalog"]
    if is_admin:
        nav_options.append("⚙️ Librarian Desk")
        st.sidebar.info("🛡️ Administrative Access Active")

    app_mode = st.sidebar.selectbox("Navigation Menu", nav_options)
    
    if st.sidebar.button("Secure Logout", use_container_width=True):
        st.session_state.update({'auth': False, 'active_book': None})
        st.rerun()

    # --- A. DASHBOARD SECTION ---
    if app_mode == "📊 Dashboard":
        st.markdown("<div class='hero-section'><h1>Library Analytics Dashboard</h1></div>", unsafe_allow_html=True)
        all_books = database.get_all_books()
        
        metric_1, metric_2, metric_3 = st.columns(3)
        metric_1.metric("📚 Total Titles", len(all_books))
        metric_2.metric("📦 Cloud Status", "🟢 Operational")
        metric_3.metric("🇮🇳 Region", "Asia-South (Mumbai)")
        
        if all_books:
            st.subheader("Current Inventory Snapshot")
            df = pd.DataFrame(all_books, columns=["ID", "Title", "Author", "Category", "Stock", "Price", "URL", "Path"])
            st.dataframe(df[["Title", "Author", "Category", "Stock", "Price"]], use_container_width=True, hide_index=True)

    # --- B. EXPLORE CATALOG SECTION ---
    elif app_mode == "📖 Explore Catalog":
        st.title("Digital Resource Archive")
        cat_tabs = st.tabs(["🎓 B.Tech Engineering", "📜 Telugu Literature", "🕉️ Mythology"])
        category_list = ["B.Tech", "Telugu", "Mythology"]
        
        for i, category_name in enumerate(category_list):
            with cat_tabs[i]:
                books_data = database.get_books_by_category(category_name)
                book_cols = st.columns(3)
                
                for idx, book in enumerate(books_data):
                    with book_cols[idx % 3]:
                        st.markdown(f"""
                            <div class='book-card'>
                                <div class='book-title'>{book[1]}</div>
                                <div style='color: #64748b;'>By {book[2]}</div>
                                <div style='font-size: 0.85rem; margin-top: 10px;'>Inventory: {book[4]} Copies</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        btn_col_1, btn_col_2 = st.columns(2)
                        if btn_col_1.button("👁️ Preview", key=f"prev_{category_name}_{book[0]}", use_container_width=True):
                            st.session_state.update({'active_book': book[0], 'active_mode': 'preview'})
                        
                        # Dynamic Button Logic for Price
                        if book[5] > 0:
                            if btn_col_2.button(f"₹{int(book[5])} Buy", key=f"buy_{category_name}_{book[0]}", use_container_width=True):
                                st.session_state.update({'active_book': book[0], 'active_mode': 'pay'})
                        else:
                            if btn_col_2.button("📥 Get Free", key=f"get_{category_name}_{book[0]}", use_container_width=True):
                                st.session_state.update({'active_book': book[0], 'active_mode': 'download'})

                # Display Area for Selected Resource
                if st.session_state['active_book']:
                    selected_book = next((b for b in books_data if b[0] == st.session_state['active_book']), None)
                    if selected_book:
                        st.divider()
                        if st.button("❌ Close Viewer", key=f"close_view_{category_name}", use_container_width=True):
                            st.session_state['active_book'] = None
                            st.rerun()
                        
                        current_mode = st.session_state['active_mode']
                        if current_mode == 'preview':
                            show_pdf(selected_book[6])
                        elif current_mode == 'pay':
                            if payment_gateway(selected_book[1], selected_book[5], category_name):
                                st.link_button("🚀 Access Full Resource", selected_book[7], use_container_width=True)
                        elif current_mode == 'download':
                            if str(selected_book[7]).startswith("http"):
                                st.link_button("🚀 Access Digital Copy", selected_book[7], use_container_width=True)
                            else:
                                with open(selected_book[7], "rb") as f:
                                    st.download_button("💾 Download PDF", f, file_name=f"{selected_book[1]}.pdf", use_container_width=True)

    # --- C. LIBRARIAN DESK SECTION ---
    elif app_mode == "⚙️ Librarian Desk":
        st.title("🔐 Librarian Control Panel")
        
        # --- SYSTEM TOOLS ---
        st.subheader("System Maintenance")
        tool_col_1, tool_col_2 = st.columns(2)
        
        if tool_col_1.button("🔄 Reset & Refresh Database", use_container_width=True, help="Wipes and reloads default resources."):
            conn = database.connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM books")
            conn.commit()
            conn.close()
            refresh_library_data()
            st.success("System Restored: Catalog has been resynced with default resources.")
            time.sleep(1)
            st.rerun()
            
        if tool_col_2.button("📥 Export Audit Report (Excel)", use_container_width=True, help="Generates a full inventory and user report."):
            conn = database.connect_db()
            df_inv = pd.read_sql_query("SELECT * FROM books", conn)
            df_usr = pd.read_sql_query("SELECT name, email FROM users", conn)
            conn.close()
            
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_inv.to_excel(writer, sheet_name='Book_Inventory', index=False)
                df_usr.to_excel(writer, sheet_name='Registered_Users', index=False)
            
            st.download_button(
                label="📥 Download Excel Audit File",
                data=excel_buffer.getvalue(),
                file_name=f"Apex_Library_Audit_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # --- ADD NEW RESOURCE FORM ---
        st.divider()
        st.subheader("➕ Register New Library Resource")
        with st.form("new_resource_form", clear_on_submit=True):
            form_col_1, form_col_2 = st.columns(2)
            new_title = form_col_1.text_input("Resource Title")
            new_author = form_col_2.text_input("Lead Author / Publisher")
            new_cat = st.selectbox("Assign Category", ["B.Tech", "Telugu", "Mythology"])
            
            form_col_3, form_col_4 = st.columns(2)
            new_stock = form_col_3.number_input("Initial Stock Level", min_value=1, value=5)
            new_price = form_col_4.number_input("Resource Price (₹) - Enter 0 for Free", 0.0)
            
            use_link = st.checkbox("External Hosting (Google Drive / URL)")
            preview_file = st.file_uploader("Upload Sample Preview (PDF Only)", type="pdf")
            
            if use_link:
                resource_val = st.text_input("Direct Resource URL")
            else:
                resource_val = st.file_uploader("Upload Full Digital Resource (PDF Only)", type="pdf")
            
            if st.form_submit_button("🚀 Commit Resource to Database", use_container_width=True):
                if new_title and new_author and preview_file and resource_val:
                    timestamp = int(time.time())
                    # Handle Preview Path
                    prev_path = f"preview/{timestamp}_{preview_file.name}"
                    with open(os.path.join(BASE_DIR, prev_path), "wb") as f:
                        f.write(preview_file.getbuffer())
                    
                    # Handle Full Resource Path
                    if use_link:
                        full_path = resource_val
                    else:
                        full_path = f"full_books/{timestamp}_{resource_val.name}"
                        with open(os.path.join(BASE_DIR, full_path), "wb") as f:
                            f.write(resource_val.getbuffer())
                    
                    database.add_book(new_title, new_author, new_cat, new_stock, new_price, prev_path, full_path)
                    st.success(f"Resource Successfully Cataloged: {new_title}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Submission Incomplete: Please ensure all fields are populated and files are uploaded.")
