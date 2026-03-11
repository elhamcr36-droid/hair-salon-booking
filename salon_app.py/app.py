import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & UI STYLE (ดึงชิดขอบ + แยกแชท + ลบที่ว่าง) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# 📍 ลิงก์ GPS
SHOP_LOCATION_URL = "https://www.google.com/maps/place/222+%E0%B8%96%E0%B8%99%E0%B8%99+%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B8%9A%E0%B8%B2%E0%B8%A5+1+%E0%B8%95%E0%B8%B3%E0%B8%9A%E0%B8%A5%E0%B8%9A%E0%B9%88%E0%B8%AD%E0%B8%A2%E0%B8%B2%E0%B8%87+%E0%B8%AD%E0%B8%B3%E0%B9%80%E0%B8%A0%E0%B8%AD%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+90000/@7.1915128,100.6007972,17z/data=!3m1!4b1!4m6!3m5!1s0x304d3323c7ad029d:0x7cfb098f4f859e4c!8m2!3d7.1915128!4d100.6007972!16s%2Fg%2F11jylj3r6y?entry=ttu&g_ep=EgoyMDI2MDMwOC4wIKXMDSoASAFQAw%3D%3D" 

st.markdown("""
    <style>
        /* ⬆️ 1. ดึงเนื้อหาขึ้นชิดขอบบนสุด */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            margin-top: -45px !important;
        }
        header {visibility: hidden !important; height: 0px !important;}
        [data-testid="stHeader"] {display: none !important;}
        [data-testid="stVerticalBlock"] { gap: 0rem !important; }
        
        /* 🏷️ 2. ชื่อร้าน (ดึงขึ้นสูงที่สุด) */
        .main-header {
            text-align: center; color: #FF4B4B; 
            margin-top: -20px !important; 
            margin-bottom: 5px !important;
            font-size: 1.6rem;
            font-weight: bold;
        }

        /* 💬 3. ระบบแชทแบบแยก ซ้าย-ขวา (ดึงขึ้นชิด) */
        .chat-wrapper {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: -25px !important; /* ดึงแชทขึ้นชิด Tab */
            max-height: 400px;
            overflow-y: auto;
            padding: 10px 0;
        }
        .bubble-right {
            align-self: flex-end; background-color: #0084FF; color: white !important;
            padding: 8px 14px; border-radius: 15px 15px 2px 15px;
            max-width: 75%; font-size: 14px; margin-bottom: 2px;
        }
        .bubble-left {
            align-self: flex-start; background-color: #333333; color: white !important;
            padding: 8px 14px; border-radius: 15px 15px 15px 2px;
            max-width: 75%; font-size: 14px; border: 1px solid #444; margin-bottom: 2px;
        }

        /* 📱 4. ปรับแต่งปุ่มและ Price Card */
        .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 35px; transition: 0.3s; }
        .stTabs [data-baseweb="tab-list"] { gap: 5px; }
        .stTabs [data-baseweb="tab"] { padding-top: 0px; padding-bottom: 5px; }
        
        .price-card {
            background-color: transparent !important; 
            padding: 8px 0px; border-bottom: 1px solid rgba(255,255,255,0.1);
            color: #ffffff !important;
        }
        .price-card b { color: #FF4B4B !important; font-size: 1.1rem; }
    </style>
""", unsafe_allow_html=True)

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. ฟังก์ชันดึงข้อมูล ---
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
    except: return pd.DataFrame()

# --- 3. ระบบนำทาง ---
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

if not st.session_state.logged_in:
    with m_cols[3]: 
        if st.button("📝"): navigate("Register")
    with m_cols[4]: 
        if st.button("🔑"): navigate("Login")
else:
    role = st.session_state.get('user_role')
    with m_cols[2]: 
        lbl = "📊" if role == 'admin' else "✂️"
        if st.button(lbl): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪"):
            st.session_state.clear()
            navigate("Home")

st.markdown("<hr style='margin: 5px 0; border: 0.1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

# --- 4. หน้าจองคิวและแชท (แก้ไขดึงข้อความขึ้นและแยกซ้ายขวา) ---
if st.session_state.page == "Booking":
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 แชท"])
    
    with t3:
        df_msg = get_data("Messages")
        st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
        my_chat = df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id')
        
        for _, m in my_chat.iterrows():
            # ลูกค้าเปิด: ตัวเอง(user)=ขวา-น้ำเงิน, แอดมิน(admin)=ซ้าย-เทา
            cls = "bubble-right" if m['sender'] == "user" else "bubble-left"
            st.markdown(f'<div class="{cls}">{m["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("u_msg", clear_on_submit=True):
            c1, c2 = st.columns([4,1])
            txt = c1.text_input("พิมพ์...", label_visibility="collapsed")
            if c2.form_submit_button("ส่ง") and txt:
                new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "sender":"user", "text":txt, "timestamp":datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- 5. หน้าแอดมิน (แยกซ้ายขวาสำหรับแอดมิน) ---
elif st.session_state.page == "Admin":
    adm_t1, adm_t2 = st.tabs(["📉 จัดการคิว", "💬 ตอบแชท"])
    with adm_t2:
        df_msg = get_data("Messages")
        user_list = df_msg['username'].unique()
        if len(user_list) > 0:
            target = st.selectbox("เลือกลูกค้า", user_list)
            st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
            for _, m in df_msg[df_msg['username'] == target].sort_values('msg_id').iterrows():
                # แอดมินเปิด: ตัวเอง(admin)=ขวา-น้ำเงิน, ลูกค้า(user)=ซ้าย-เทา
                cls = "bubble-right" if m['sender'] == "admin" else "bubble-left"
                st.markdown(f'<div class="{cls}">{m["text"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            with st.form("a_msg", clear_on_submit=True):
                c1, c2 = st.columns([4,1])
                rep = c1.text_input("ตอบกลับ...", label_visibility="collapsed")
                if c2.form_submit_button("ส่ง") and rep:
                    new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":target, "sender":"admin", "text":rep, "timestamp":datetime.now().strftime("%H:%M")}])
                    conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- 6. หน้าแรก (Home) ---
elif st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.markdown(f"<div style='text-align:center; margin-bottom:10px;'><a href='{SHOP_LOCATION_URL}' style='color:#FF4B4B; text-decoration:none;'>📍 นำทางไปยังร้าน (GPS)</a></div>", unsafe_allow_html=True)
    
    SERVICES_DISPLAY = {"✂️ ตัดผมชาย": "150 - 350", "💇‍♀️ ตัดผมหญิง": "350 - 800", "🚿 สระ-ไดร์": "200 - 450", "🎨 ทำสีผม": "1,500+", "✨ ยืดวอลลุ่ม": "1,000+"}
    for name, price in SERVICES_DISPLAY.items():
        st.markdown(f'<div class="price-card"><b>{name}</b><br>{price} บาท</div>', unsafe_allow_html=True)

# --- หน้า Login / Register (ใช้ Logic เดิมของคุณ) ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin'}); navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not user.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u, 'fullname':user.iloc[0]['fullname']}); navigate("Booking")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")
