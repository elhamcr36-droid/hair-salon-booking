import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS (ดึงขึ้นบนสุด + แยกซ้ายขวา) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        /* ⬆️ ดึงเนื้อหาขึ้นบนสุด */
        .block-container {
            padding-top: 0.5rem !important;
            margin-top: -40px !important;
        }
        header {visibility: hidden !important; height: 0px !important;}
        [data-testid="stHeader"] {display: none !important;}
        
        /* 🏷️ หัวข้อหลัก */
        .main-header {
            text-align: center; color: #FF4B4B; 
            margin-top: -10px !important; margin-bottom: 10px;
            font-size: 1.8rem; font-weight: bold;
        }

        /* 💬 แชทแยก ซ้าย-ขวา (แบบคลีน) */
        .chat-box {
            display: flex; flex-direction: column; gap: 8px;
            margin-top: -20px !important; /* ดึงแชทขึ้นชิด Tab */
        }
        .msg-right {
            align-self: flex-end; background-color: #0084FF; color: white !important;
            padding: 8px 15px; border-radius: 15px 15px 2px 15px; max-width: 80%;
        }
        .msg-left {
            align-self: flex-start; background-color: #333333; color: white !important;
            padding: 8px 15px; border-radius: 15px 15px 15px 2px; max-width: 80%;
            border: 1px solid #444;
        }

        /* 🧊 Price Card แบบดั้งเดิมแต่ดูดี */
        .price-item {
            padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex; justify-content: space-between;
        }
        .price-item b { color: #FF4B4B; }
    </style>
""", unsafe_allow_html=True)

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
    except: return pd.DataFrame()

# --- 2. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

# --- 3. HEADER & MENU ---
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

st.divider()

# --- 4. PAGE: HOME ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ 09:30 - 19:30 น. (หยุดวันพุธ)")
    services = {"ตัดผมชาย": "150-350", "ตัดผมหญิง": "350-800", "สระ-ไดร์": "200-450", "ทำสีผม": "1,500+"}
    for name, price in services.items():
        st.markdown(f'<div class="price-item"><span>{name}</span> <b>{price} บ.</b></div>', unsafe_allow_html=True)

# --- 5. PAGE: BOOKING & CHAT ---
elif st.session_state.page == "Booking":
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 แชท"])
    
    with t3:
        df_msg = get_data("Messages")
        st.markdown('<div class="chat-box">', unsafe_allow_html=True)
        my_chat = df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id')
        for _, m in my_chat.iterrows():
            # ลูกค้า: ตัวเอง(user)=ขวา, แอดมิน(admin)=ซ้าย
            cls = "msg-right" if m['sender'] == "user" else "msg-left"
            st.markdown(f'<div class="{cls}">{m["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("u_msg", clear_on_submit=True):
            c1, c2 = st.columns([4,1])
            txt = c1.text_input("พิมพ์...", label_visibility="collapsed")
            if c2.form_submit_button("ส่ง") and txt:
                new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "sender":"user", "text":txt}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- 6. PAGE: ADMIN ---
elif st.session_state.page == "Admin":
    a1, a2 = st.tabs(["📉 คิววันนี้", "💬 ตอบแชท"])
    with a2:
        df_msg = get_data("Messages")
        user_list = df_msg['username'].unique()
        if len(user_list) > 0:
            target = st.selectbox("เลือกลูกค้า", user_list)
            st.markdown('<div class="chat-box">', unsafe_allow_html=True)
            for _, m in df_msg[df_msg['username'] == target].sort_values('msg_id').iterrows():
                # แอดมิน: ตัวเอง(admin)=ขวา, ลูกค้า(user)=ซ้าย
                cls = "msg-right" if m['sender'] == "admin" else "msg-left"
                st.markdown(f'<div class="{cls}">{m["text"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            with st.form("a_msg", clear_on_submit=True):
                c1, c2 = st.columns([4,1])
                rep = c1.text_input("ตอบ...", label_visibility="collapsed")
                if c2.form_submit_button("ส่ง") and rep:
                    new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":target, "sender":"admin", "text":rep}])
                    conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- 7. AUTH (LOGIN / REGISTER) ---
elif st.session_state.page == "Login":
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
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
        nu, np, nf = st.text_input("User"), st.text_input("Pass"), st.text_input("Name")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u])); navigate("Login")
