📖 Apex Digital Library
Modern Solutions for Modern Learning

Apex Digital Library is a comprehensive, web-based resource management system designed for engineering students and educators. Built using Python and Streamlit, it offers a seamless interface for accessing academic resources, managing inventory, and simulating digital commerce.

🚀 Live Demo
Check out the live application here:

👉 Apex Digital Library

✨ Key Features
🏛️ Smart Cataloging
Segmented Shelves: Resources organized into categories: B.Tech (ECE/CSE), Telugu Literature, and Mythology.

Instant Previews: Integrated PDF viewer allowing users to read samples before downloading.

Hybrid Downloads: Support for both local GitHub-hosted files and cloud-based Google Drive resources.

🔐 Librarian Control Panel (Admin)
Bypass Authentication: Secure access for authorized administrators (adithya@example.com).

Inventory Management: Add new titles, set pricing, and manage physical/digital stock levels (copies).

Audit Reporting: One-click Excel export of the entire user database and book inventory for offline reporting.

📊 Real-Time Analytics
Live Dashboard: Monitors unique titles, total available stock, and system status.

System Sync: Real-time timestamp tracking to ensure data consistency.

💳 Simulated Commerce
Payment Gateway: A secure-style checkout mockup to simulate premium resource unlocking via virtual transactions.

🛠️ Tech Stack
Frontend/UI: Streamlit (Python Framework)

Database: SQLite3 (Relational Database Management)

Data Processing: Pandas

File Handling: OpenPyXL (Excel Exports) & Base64 Encoding (PDF Rendering)

📂 Project Structure
Plaintext
├── app.py              # Main application logic & UI
├── database.py         # SQLite schema and query functions
├── export_data.py      # Independent data export script
├── requirements.txt    # Project dependencies
├── previews/           # Directory for sample PDF previews
└── full_books/         # Directory for local full-text resources
⚙️ Setup & Installation
Clone the Repo: git clone https://github.com/adithya-21/library-management.git

Install Requirements: pip install -r requirements.txt

Run the App: streamlit run app.py

🔮 Future Roadmap
IoT Integration: Connecting physical book drops using ESP32-CAM modules.

AI Recommendations: implementing a deep learning model for personalized book suggestions.

Cloud Database: Moving from SQLite to PostgreSQL for permanent data storage.

👤 Author
Adithya Undergraduate Student in Electronics and Communication Engineering (ECE) Marri Laxman Reddy Institute of Technology and Management (MLRITM)

An aspiring engineer with a passion for blending hardware logic with software efficiency. Currently focused on building scalable web applications and exploring the intersection of IoT and Full-Stack Development.

🎓 Education: Pursuing B.Tech in ECE at MLRITM

💻 Technical Interests: Python, Streamlit, Embedded Systems, and Database Management

🔗 Connect with me: LinkedIn | GitHub
