import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & UI STYLE (ดึงชิดขอบ + แยกแชท ซ้าย-ขวา + ลบกล่องขาว) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        /* ⬆️ 1. ดึงเนื้อหาทั้งหน้าขึ้นชิดขอบบนสุด */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            margin-top: -40px !important;
        }
        header {visibility: hidden !important; height: 0px !important;}
        [data-testid="stHeader"] {display: none !important;}
        [data-testid="stVerticalBlock"] { gap: 0rem !important; }
        
        /* 🏷️ 2. ชื่อร้าน (ดึงขึ้นสูงที่สุด) */
        .main-header {
            text-align: center; color: #FF4B4B; 
            margin-top: -30px !important; 
            margin-bottom: 5px !important;
            font-size: 1.5rem;
            font-weight: bold;
        }

        /* 💬 3. ระบบแชทแบบแยก ซ้าย-ขวา และดึงขึ้นชิด */
        .chat-wrapper {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding-top: 0px !important;
            margin-top: -25px !important; /* ดึงข้อความแชทขึ้นชิด Tab */
            max-height: 400px;
            overflow-y: auto;
        }
        /* ฝั่งขวา (User/ตัวเอง) */
        .bubble-right {
            align-self: flex-end;
            background-color: #0084FF;
            color: white !important;
            padding: 8px 14px;
            border-radius: 15px 15px 2px 15px;
            max-width: 75%;
            font-size: 14px;
            margin-bottom: 2px;
        }
        /* ฝั่งซ้าย (Admin/อีกฝ่าย) */
        .bubble-left {
            align-self: flex-start;
            background-color: #333333;
            color: white !important;
            padding: 8px 14px;
            border-radius: 15px 15px 15px 2px;
            max-width: 75%;
            font-size: 14px;
            border: 1px solid #444;
            margin-bottom: 2px;
        }

        /* 📱 4. ปรับแต่งเมนูและรายการ (Transparent) */
        .stTabs [data-baseweb="tab-list"] { gap: 5px; }
        .stTabs [data-baseweb="tab"] { padding-top: 0px; padding-bottom: 5px; }
        .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 35px; }
        
        .glass-card {
            background-color: transparent !important; 
            padding: 5px 0px; 
            border-bottom: 1px solid rgba(255,255,255,0.1);
            color: #ffffff;
        }
        .glass-card b { color: #FF4B4B !important; }

        /* Social Buttons */
        .social-container { display: flex; justify-content: center; gap: 8px; margin: 5px 0; }
        .social-btn {
            padding: 4px 12px; border-radius: 15px; color: white !important;
            text-decoration: none; font-weight: bold; font-size: 11px;
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

# --- HEADER ---
st.markdown("<div class='main-header'>✂️ 222-Salon</div>", unsafe_allow_html=True)
m_cols = st.columns(5)
with m_cols[0]: 
    if st.button("🏠"): navigate("Home")
with m_cols[1]: 
    if st.button("📅"): navigate("ViewQueues")

if st.session_state.logged_in:
    role = st.session_state.get('user_role')
    with m_cols[2]: 
        lbl = "📊" if role == 'admin' else "✂️"
        if st.button(lbl): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪"):
            st.session_state.clear()
            navigate("Home")
else:
    with m_cols[3]: 
        if st.button("📝"): navigate("Register")
    with m_cols[4]: 
        if st.button("🔑"): navigate("Login")

st.markdown("<hr style='margin: 5px 0; border: 0.1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

# --- 4. PAGE: BOOKING & CHAT (หัวใจสำคัญ) ---
if st.session_state.page == "Booking":
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 คิวของฉัน", "💬 แชท"])
    
    with t3:
        df_msg = get_data("Messages")
        st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
        my_chat = df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id')
        
        for _, m in my_chat.iterrows():
            # ถ้าลูกค้าเปิด: sender=user อยู่ขวา (bubble-right), sender=admin อยู่ซ้าย (bubble-left)
            cls = "bubble-right" if m['sender'] == "user" else "bubble-left"
            st.markdown(f'<div class="{cls}">{m["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("u_msg", clear_on_submit=True):
            c1, c2 = st.columns([4,1])
            txt = c1.text_input("พิมพ์...", label_visibility="collapsed")
            if c2.form_submit_button("ส่ง") and txt:
                new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "sender":"user", "text":txt, "timestamp":datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- 5. PAGE: ADMIN ---
elif st.session_state.page == "Admin":
    adm_t1, adm_t2 = st.tabs(["📉 คิว", "💬 แชท"])
    with adm_t2:
        df_msg = get_data("Messages")
        user_list = df_msg['username'].unique()
        if len(user_list) > 0:
            target = st.selectbox("ลูกค้า", user_list)
            st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
            for _, m in df_msg[df_msg['username'] == target].sort_values('msg_id').iterrows():
                # ถ้าแอดมินเปิด: sender=admin อยู่ขวา (bubble-right), sender=user อยู่ซ้าย (bubble-left)
                cls = "bubble-right" if m['sender'] == "admin" else "bubble-left"
                st.markdown(f'<div class="{cls}">{m["text"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            with st.form("a_msg", clear_on_submit=True):
                c1, c2 = st.columns([4,1])
                rep = c1.text_input("ตอบกลับ...", label_visibility="collapsed")
                if c2.form_submit_button("ส่ง"):
                    new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":target, "sender":"admin", "text":rep, "timestamp":datetime.now().strftime("%H:%M")}])
                    conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- 6. หน้าอื่นๆ (HOME / LOGIN) ---
elif st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.markdown("""
        <div class="social-container">
            <a href="#" class="social-btn fb-color">FB</a>
            <a href="#" class="social-btn line-color">Line</a>
            <a href="#" class="social-btn gps-color">Map</a>
        </div>
    """, unsafe_allow_html=True)
    services = {"✂️ ตัดผมชาย": "150-350", "💇‍♀️ ตัดผมหญิง": "350-800", "🚿 สระ-ไดร์": "200-450"}
    for name, price in services.items():
        st.markdown(f'<div class="glass-card"><b>{name}</b> {price} บ.</div>', unsafe_allow_html=True)

elif st.session_state.page == "Login":
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Login"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin'}); navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not user.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u, 'fullname':user.iloc[0]['fullname']}); navigate("Booking")
            else: st.error("ผิดพลาด")
