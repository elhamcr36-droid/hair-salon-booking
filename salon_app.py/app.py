import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS (ปรับแต่ง UI) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# 📍 ข้อมูลติดต่อร้าน (เปลี่ยนลิงก์ตามจริงที่นี่)
SHOP_LOCATION_URL = "https://www.google.com/maps/place/222+%E0%B8%96%E0%B8%99%E0%B8%99+%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B8%9A%E0%B8%B2%E0%B8%A5+1+%E0%B8%95%E0%B8%B3%E0%B8%9A%E0%B8%A5%E0%B8%9A%E0%B9%88%E0%B8%AD%E0%B8%A2%E0%B8%B2%E0%B8%87+%E0%B8%AD%E0%B8%B3%E0%B9%80%E0%B8%A0%E0%B8%AD%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+90000/@7.1915128,100.6007972,17z/data=!3m1!4b1!4m6!3m5!1s0x304d3323c7ad029d:0x7cfb098f4f859e4c!8m2!3d7.1915128!4d100.6007972!16s%2Fg%2F11jylj3r6y?entry=ttu&g_ep=EgoyMDI2MDMwOC4wIKXMDSoASAFQAw%3D%3D" 
FACEBOOK_URL = "https://facebook.com"
LINE_URL = "https://line.me"

st.markdown("""
    <style>
        /* จัดการพื้นฐาน */
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px; font-weight: bold;}
        
        /* 💬 แชทแยกซ้าย-ขวา + ดึงขึ้นชิด */
        .chat-container {
            display: flex; flex-direction: column; gap: 10px;
            margin-top: -35px !important; /* ดึงเฉพาะแชทขึ้นชิด Tab */
            padding-bottom: 20px;
        }
        .chat-bubble {
            padding: 10px 15px; border-radius: 18px;
            max-width: 75%; font-size: 14px; line-height: 1.4;
        }
        /* เราส่ง (User ในหน้าจอง / Admin ในหน้าแอดมิน) */
        .msg-me {
            align-self: flex-end; background-color: #0084FF; color: white !important;
            border-bottom-right-radius: 2px;
        }
        /* อีกฝ่ายส่ง */
        .msg-them {
            align-self: flex-start; background-color: #333333; color: white !important;
            border-bottom-left-radius: 2px; border: 1px solid #444;
        }

        /* Price Card หน้าแรก */
        .price-card {
            background-color: #ffffff !important; padding: 15px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 10px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #1A1A1A !important;
        }
        .price-card b { color: #000000 !important; display: block; font-size: 1.1rem; }
        .price-text { color: #FF4B4B !important; font-weight: bold; }

        /* Dashboard แอดมิน */
        .metric-card {
            background-color: #ffffff; padding: 15px; border-radius: 15px;
            border: 2px solid #FF4B4B; text-align: center; color: #1A1A1A;
        }
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

# --- HEADER & GLOBAL MENU ---
st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)
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

# --- 3. PAGE: HOME ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิด 09:30 - 19:30 น. (หยุดทุกวันพุธ)")
    
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350", "💇‍♀️ ตัดผมหญิง": "350-800", "🚿 สระ-ไดร์": "200-450", "🎨 ทำสีผม": "1,500+", "✨ ยืดวอลลุ่ม": "1,000+"}
    p1, p2 = st.columns(2)
    for i, (n, p) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{n}</b><span class="price-text">{p} บาท</span></div>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📞 ติดต่อเรา")
    c1, c2, c3 = st.columns(3)
    c1.link_button("🔵 Facebook", FACEBOOK_URL)
    c2.link_button("🟢 Line Official", LINE_URL)
    c3.link_button("📍 แผนที่ GPS", SHOP_LOCATION_URL, type="primary")

# --- 4. PAGE: BOOKING & CHAT (ฝั่งลูกค้า) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.get('fullname', st.session_state.username)}")
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 แชทสอบถาม"])
    
    with t1:
        # (ส่วน Logic การจองเดิมของคุณ)
        svc = st.selectbox("เลือกบริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืดผมวอลลุ่ม"])
        d = st.date_input("เลือกวันที่")
        t = st.selectbox("เลือกเวลา", [f"{h:02d}:{m}" for h in range(9, 20) for m in ["00", "30"] if "09:30" <= f"{h:02d}:{m}" <= "19:30"])
        if st.button("ยืนยันการจอง"):
            df_b = get_data("Bookings")
            booked = len(df_b[(df_b['date'] == str(d)) & (df_b['time'] == t) & (df_b['status'] == 'รอรับบริการ')])
            if d.weekday() == 2: st.error("ร้านหยุดวันพุธ")
            elif booked >= 2: st.error("เวลานี้เต็มแล้ว (ช่าง 2 ท่าน)")
            else:
                new_q = pd.DataFrame([{"id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "service":svc, "date":str(d), "time":t, "price":"150", "status":"รอรับบริการ"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q])); st.success("จองสำเร็จ!"); st.rerun()

    with t3:
        df_msg = get_data("Messages")
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        my_chat = df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id')
        for _, m in my_chat.iterrows():
            cls = "msg-me" if m['sender'] == "user" else "msg-them"
            st.markdown(f'<div class="chat-bubble {cls}">{m["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        with st.form("u_send", clear_on_submit=True):
            c1, c2 = st.columns([4,1])
            txt = c1.text_input("พิมพ์...", label_visibility="collapsed")
            if c2.form_submit_button("ส่ง") and txt:
                new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "sender":"user", "text":txt}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- 5. PAGE: ADMIN & CHAT (ฝั่งแอดมิน) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 แผงควบคุมแอดมิน")
    a1, a2 = st.tabs(["📉 สรุปคิว", "💬 ตอบแชทลูกค้า"])
    
    with a1:
        df_b = get_data("Bookings")
        if not df_b.empty:
            today = datetime.now().strftime("%Y-%m-%d")
            df_today = df_b[df_b['date'] == today]
            c1, c2 = st.columns(2)
            c1.markdown(f"<div class='metric-card'>ลูกค้าวันนี้: {len(df_today)} ท่าน</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-card'>วันที่: {today}</div>", unsafe_allow_html=True)
            st.write("---")
            for _, row in df_b[df_b['status'] == 'รอรับบริการ'].iterrows():
                st.write(f"⏰ {row['time']} | {row['username']} - {row['service']}")
                if st.button("✅ เสร็จสิ้น", key=row['id']):
                    df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                    conn.update(worksheet="Bookings", data=df_b); st.rerun()

    with a2:
        df_msg = get_data("Messages")
        u_list = df_msg['username'].unique()
        if len(u_list) > 0:
            target = st.selectbox("คุยกับคุณ:", u_list)
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for _, m in df_msg[df_msg['username'] == target].sort_values('msg_id').iterrows():
                cls = "msg-me" if m['sender'] == "admin" else "msg-them"
                st.markdown(f'<div class="chat-bubble {cls}">{m["text"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            with st.form("a_send", clear_on_submit=True):
                c1, c2 = st.columns([4,1])
                rep = c1.text_input("พิมพ์ตอบกลับ...", label_visibility="collapsed")
                if c2.form_submit_button("ส่ง") and rep:
                    new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":target, "sender":"admin", "text":rep}])
                    conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- LOGIN / REGISTER / VIEWQUEUES (ส่วนเสริม) ---
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
        nu, np, nf = st.text_input("User"), st.text_input("Pass"), st.text_input("ชื่อจริง")
        if st.form_submit_button("สมัครสมาชิก"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u])); navigate("Login")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_b = get_data("Bookings")
    active = df_b[(df_b['date'] == str(datetime.now().date())) & (df_b['status'] == 'รอรับบริการ')]
    st.dataframe(active[['time', 'service']].sort_values('time'), use_container_width=True)
