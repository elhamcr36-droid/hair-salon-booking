import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & UI STYLE (ดึงชิดขอบ + ลบกล่องขาว + ลดช่องว่าง) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        /* ⬆️ ดึงเนื้อหาทั้งหน้าขึ้นชิดขอบบนสุด */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            margin-top: -30px !important;
        }
        
        /* 🚫 ลบ Header และช่องว่างมาตรฐานของระบบ */
        header {visibility: hidden !important; height: 0px !important;}
        [data-testid="stHeader"] {display: none !important;}
        [data-testid="stVerticalBlock"] { gap: 0rem !important; }
        
        /* 🏷️ ชื่อร้าน (ดึงขึ้นสูงที่สุด) */
        .main-header {
            text-align: center; color: #FF4B4B; 
            margin-top: -35px !important; 
            margin-bottom: 5px !important;
            font-size: 1.5rem;
            font-weight: bold;
        }

        /* 💬 ส่วนแชท (ดึงข้อความขึ้นชิด Tab ลบช่องว่างสีดำ) */
        .chat-container { 
            background-color: transparent !important; 
            margin-top: -30px !important; 
            padding-top: 0px !important;
            display: flex;
            flex-direction: column;
            gap: 4px;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .bubble { 
            padding: 8px 12px; 
            border-radius: 15px; 
            margin-bottom: 2px; 
            max-width: 85%; 
            font-size: 14px;
            line-height: 1.2;
        }
        .user-msg { background-color: #0084FF; color: white !important; align-self: flex-end; }
        .admin-msg { background-color: #333333; color: white !important; align-self: flex-start; border: 1px solid #444; }

        /* 📱 ปรับแต่ง Tabs และปุ่มเมนูให้ประหยัดพื้นที่ */
        .stTabs [data-baseweb="tab-list"] { gap: 5px; }
        .stTabs [data-baseweb="tab"] { padding-top: 0px; padding-bottom: 5px; }
        .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 35px; }

        /* 🧊 รายการบริการและคิว (แบบโปร่งใส) */
        .glass-card {
            background-color: transparent !important; 
            padding: 5px 0px; 
            border-bottom: 1px solid rgba(255,255,255,0.1);
            color: #ffffff;
        }
        .glass-card b { color: #FF4B4B !important; }

        /* Social Buttons */
        .social-container { display: flex; justify-content: center; gap: 8px; margin: 10px 0; }
        .social-btn {
            padding: 5px 15px; border-radius: 20px; color: white !important;
            text-decoration: none; font-weight: bold; font-size: 12px;
        }
        .fb-color { background-color: #1877F2; }
        .line-color { background-color: #00B900; }
        .gps-color { background-color: #EA4335; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. CORE FUNCTIONS ---
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
    except: return pd.DataFrame()

# --- 3. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

# --- HEADER & NAVIGATION ---
st.markdown("<div class='main-header'>✂️ 222-Salon</div>", unsafe_allow_html=True)
m_cols = st.columns(5)
with m_cols[0]: 
    if st.button("🏠"): navigate("Home")
with m_cols[1]: 
    if st.button("📅 คิว"): navigate("ViewQueues")

if st.session_state.logged_in:
    role = st.session_state.get('user_role')
    with m_cols[2]: 
        lbl = "📊 จัดการ" if role == 'admin' else "✂️ จองคิว"
        if st.button(lbl): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪 ออก"):
            st.session_state.clear()
            navigate("Home")
else:
    with m_cols[3]: 
        if st.button("📝 สมัคร"): navigate("Register")
    with m_cols[4]: 
        if st.button("🔑 Login"): navigate("Login")

st.markdown("<hr style='margin: 5px 0; border: 0.1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

# --- 4. PAGE: HOME ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.markdown("""
        <div style='text-align:center;'>
            <p style='margin:0;'>📞 0875644928 | 09:30-19:30 (หยุดพุธ)</p>
        </div>
        <div class="social-container">
            <a href="https://facebook.com" class="social-btn fb-color">Facebook</a>
            <a href="https://line.me" class="social-btn line-color">Line</a>
            <a href="https://maps.google.com" class="social-btn gps-color">Map</a>
        </div>
    """, unsafe_allow_html=True)
    services = {"✂️ ตัดผมชาย": "150-350", "💇‍♀️ ตัดผมหญิง": "350-800", "🚿 สระ-ไดร์": "200-450", "🎨 ทำสี": "1,500+", "✨ ยืดวอลลุ่ม": "1,000+"}
    p_col1, p_col2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p_col1 if i % 2 == 0 else p_col2
        target.markdown(f'<div class="glass-card"><b>{name}</b> {price} บ.</div>', unsafe_allow_html=True)

# --- 5. PAGE: BOOKING & CHAT ---
elif st.session_state.page == "Booking":
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 คิวของฉัน", "💬 แชท"])
    with t1:
        svc = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืดผมวอลลุ่ม"])
        d = st.date_input("วันที่", min_value=datetime.now().date())
        t = st.selectbox("เวลา", [f"{h:02d}:00" for h in range(10, 20)])
        if st.button("✅ ยืนยันการจอง"):
            df_b = get_data("Bookings")
            new_r = pd.DataFrame([{"id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "service":svc, "date":str(d), "time":t, "status":"รอรับบริการ"}])
            conn.update(worksheet="Bookings", data=pd.concat([df_b, new_r])); st.success("จองสำเร็จ!"); st.rerun()

    with t2:
        df_b = get_data("Bookings")
        my_active = df_b[(df_b['username'] == st.session_state.username) & (df_b['status'] == 'รอรับบริการ')]
        for _, r in my_active.iterrows():
            st.markdown(f'<div class="glass-card"><b>📅 {r["date"]} {r["time"]}</b> {r["service"]}</div>', unsafe_allow_html=True)
            if st.button("❌ ยกเลิก", key=r['id']):
                conn.update(worksheet="Bookings", data=df_b[df_b['id'] != r['id']]); st.rerun()

    with t3:
        df_msg = get_data("Messages")
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        my_chat = df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id')
        for _, m in my_chat.iterrows():
            cls = "user-msg" if m['sender'] == "user" else "admin-msg"
            st.markdown(f'<div class="bubble {cls}">{m["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        with st.form("u_msg", clear_on_submit=True):
            c1, c2 = st.columns([4,1])
            txt = c1.text_input("พิมพ์...", label_visibility="collapsed")
            if c2.form_submit_button("ส่ง") and txt:
                new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "sender":"user", "text":txt, "timestamp":datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- 6. PAGE: ADMIN ---
elif st.session_state.page == "Admin":
    adm_t1, adm_t2 = st.tabs(["📉 จัดการคิว", "💬 ตอบแชท"])
    with adm_t1:
        df_b = get_data("Bookings")
        pending = df_b[df_b['status'] == 'รอรับบริการ']
        for _, r in pending.sort_values(['date','time']).iterrows():
            c1, c2 = st.columns([4,1])
            c1.markdown(f'<div class="glass-card">👤 {r["username"]} | {r["date"]} {r["time"]}</div>', unsafe_allow_html=True)
            if c2.button("✅ เสร็จ", key=f"adm_{r['id']}"):
                df_b.loc[df_b['id'] == r['id'], 'status'] = 'เสร็จสิ้น'
                conn.update(worksheet="Bookings", data=df_b); st.rerun()
    with adm_t2:
        df_msg = get_data("Messages")
        if not df_msg.empty:
            target = st.selectbox("เลือกลูกค้า", df_msg['username'].unique())
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for _, m in df_msg[df_msg['username'] == target].sort_values('msg_id').iterrows():
                cls = "user-msg" if m['sender'] == "user" else "admin-msg"
                st.markdown(f'<div class="bubble {cls}">{m["text"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            with st.form("a_msg", clear_on_submit=True):
                c1, c2 = st.columns([4,1])
                rep = c1.text_input("ตอบกลับ...", label_visibility="collapsed")
                if c2.form_submit_button("ส่ง"):
                    new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":target, "sender":"admin", "text":rep, "timestamp":datetime.now().strftime("%H:%M")}])
                    conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- AUTH (LOGIN/REGISTER) ---
elif st.session_state.page == "Login":
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("เข้าสู่ระบบ"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin'}); navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not user.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u, 'fullname':user.iloc[0]['fullname']}); navigate("Booking")
            else: st.error("ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Register":
    with st.form("reg"):
        nu, np, nf, nt = st.text_input("Username"), st.text_input("Password"), st.text_input("ชื่อจริง"), st.text_input("เบอร์โทร")
        if st.form_submit_button("สมัครสมาชิก"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "phone":nt, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u])); navigate("Login")
