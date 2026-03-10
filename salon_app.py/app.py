import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & UI STYLE (ดึงขึ้นบน + ลบที่ว่าง + ลบกล่องขาว) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# 📍 ข้อมูลติดต่อ
SHOP_TEL = "0875644928"
FACEBOOK_URL = "https://www.facebook.com/share/18Yv8zGNoG/?mibextid=wwXIfr" 
LINE_URL = "https://line.me/ti/p/yourid" 
SHOP_LOCATION_URL = "https://www.google.com/maps/place/222+%E0%B8%96%E0%B8%99%E0%B8%99+%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B8%9A%E0%B8%B2%E0%B8%A5+1+%E0%B8%95%E0%B8%B3%E0%B8%9A%E0%B8%A5%E0%B8%9A%E0%B9%88%E0%B8%AD%E0%B8%A2%E0%B8%B2%E0%B8%87+%E0%B8%AD%E0%B8%B3%E0%B9%80%E0%B8%A0%E0%B8%AD%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+90000/@7.1915128,100.6007972,17z/data=!3m1!4b1!4m6!3m5!1s0x304d3323c7ad029d:0x7cfb098f4f859e4c!8m2!3d7.1915128!4d100.6007972!16s%2Fg%2F11jylj3r6y?entry=ttu&g_ep=EgoyMDI2MDMwOC4wIKXMDSoASAFQAw%3D%3D" 

st.markdown(f"""
    <style>
        /* ⬆️ ดึงเนื้อหาชิดขอบบนสุด */
        .block-container {{
            padding-top: 0.5rem !important;
            padding-bottom: 0rem !important;
        }}
        header {{visibility: hidden !important; height: 0px !important;}}
        [data-testid="stHeader"] {{display: none !important;}}
        
        /* 🚫 ลบที่ว่างและจัดการปุ่ม */
        [data-testid="stSidebar"] {{display: none;}}
        .stButton>button {{width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}}
        .main-header {{
            text-align: center; color: #FF4B4B; 
            margin-top: -20px !important; margin-bottom: 10px;
            font-size: 1.8rem;
        }}
        
        /* 🧊 สไตล์โปร่งใส (ลบกล่องขาว) */
        .glass-card {{
            background-color: transparent !important; 
            padding: 10px 0px; margin-bottom: 5px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: #ffffff !important;
        }}
        .glass-card b {{ color: #FF4B4B !important; }}

        /* 💬 แชทแบบชิดขอบ */
        .chat-container {{ 
            background-color: transparent !important; 
            height: 380px; overflow-y: auto; margin-top: -10px;
        }}
        .bubble {{ padding: 10px 15px; border-radius: 18px; margin-bottom: 8px; max-width: 85%; clear: both; display: block; }}
        .user-msg {{ background-color: #0084FF; color: white !important; float: right; border-bottom-right-radius: 2px; }}
        .admin-msg {{ background-color: #333333; color: white !important; float: left; border-bottom-left-radius: 2px; border: 1px solid #444; }}

        /* Social Buttons แบบ Compact */
        .social-container {{ display: flex; justify-content: center; gap: 5px; margin-bottom: 10px; }}
        .social-btn {{
            padding: 5px 15px; border-radius: 15px; color: white !important;
            text-decoration: none; font-weight: bold; font-size: 12px;
        }}
        .fb-color {{ background-color: #1877F2; }}
        .line-color {{ background-color: #00B900; }}
        .gps-color {{ background-color: #EA4335; }}
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. CORE FUNCTIONS ---
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        return df
    except: return pd.DataFrame()

# --- 3. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

# --- HEADER & MENU ---
st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)
m_cols = st.columns(5)
with m_cols[0]: 
    if st.button("🏠"): navigate("Home")
with m_cols[1]: 
    if st.button("📅 คิว"): navigate("ViewQueues")

if not st.session_state.logged_in:
    with m_cols[3]: 
        if st.button("📝 สมัคร"): navigate("Register")
    with m_cols[4]: 
        if st.button("🔑 Login"): navigate("Login")
else:
    role = st.session_state.get('user_role')
    with m_cols[2]: 
        label = "📊 แอดมิน" if role == 'admin' else "✂️ จองคิว"
        if st.button(label): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪 ออก"):
            st.session_state.clear()
            navigate("Home")

st.divider()

# --- 4. PAGE: HOME ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.markdown(f"""
        <div style="text-align:center; margin-bottom:10px;">
            <p style='color:white; margin:0; font-size:14px;'>📞 {SHOP_TEL} (09:30-19:30 หยุดพุธ)</p>
        </div>
        <div class="social-container">
            <a href="{FACEBOOK_URL}" target="_blank" class="social-btn fb-color">Facebook</a>
            <a href="{LINE_URL}" target="_blank" class="social-btn line-color">Line</a>
            <a href="{SHOP_LOCATION_URL}" target="_blank" class="social-btn gps-color">Map</a>
        </div>
    """, unsafe_allow_html=True)
    
    services = {"✂️ ตัดผมชาย": "150-350", "💇‍♀️ ตัดผมหญิง": "350-800", "🚿 สระ-ไดร์": "200-450", "🎨 ทำสี": "1,500+", "✨ ยืดวอลลุ่ม": "1,000+"}
    p_col1, p_col2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p_col1 if i % 2 == 0 else p_col2
        target.markdown(f'<div class="glass-card"><b>{name}</b> {price} บ.</div>', unsafe_allow_html=True)

# --- 5. PAGE: VIEW QUEUES ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_b = get_data("Bookings")
    active = df_b[(df_b['date'] == datetime.now().strftime("%Y-%m-%d")) & (df_b['status'] == 'รอรับบริการ')]
    if active.empty: st.info("ไม่มีคิวค้าง")
    else: st.dataframe(active[['time', 'service']].sort_values('time'), use_container_width=True)

# --- 6. PAGE: BOOKING & CHAT ---
elif st.session_state.page == "Booking":
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 คิวของฉัน", "💬 แชท"])
    with t1:
        svc = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืดผมวอลลุ่ม"])
        d = st.date_input("วันที่", min_value=datetime.now().date())
        t = st.selectbox("เวลา", [f"{h:02d}:00" for h in range(10, 20)])
        if st.button("✅ ยืนยันการจอง"):
            df_check = get_data("Bookings")
            new_r = pd.DataFrame([{"id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "service":svc, "date":str(d), "time":t, "status":"รอรับบริการ"}])
            conn.update(worksheet="Bookings", data=pd.concat([df_check, new_r])); st.rerun()
    
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
        for _, m in df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id').iterrows():
            cls = "user-msg" if m['sender'] == "user" else "admin-msg"
            st.markdown(f'<div class="bubble {cls}">{m["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        with st.form("u_msg", clear_on_submit=True):
            txt = st.text_input("ถามแอดมิน...")
            if st.form_submit_button("ส่ง") and txt:
                new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "sender":"user", "text":txt, "timestamp":datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- 7. PAGE: ADMIN ---
elif st.session_state.page == "Admin":
    adm_t1, adm_t2 = st.tabs(["📉 คิว", "💬 แชท"])
    with adm_t1:
        df_b = get_data("Bookings")
        pending = df_b[df_b['status'] == 'รอรับบริการ']
        for _, r in pending.sort_values(['date','time']).iterrows():
            st.write(f"👤 {r['username']} | {r['date']} {r['time']}")
            if st.button("✅ เสร็จสิ้น", key=f"adm_{r['id']}"):
                df_b.loc[df_b['id'] == r['id'], 'status'] = 'เสร็จสิ้น'
                conn.update(worksheet="Bookings", data=df_b); st.rerun()
    with adm_t2:
        df_msg = get_data("Messages")
        if not df_msg.empty:
            target = st.selectbox("ลูกค้า", df_msg['username'].unique())
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for _, m in df_msg[df_msg['username'] == target].sort_values('msg_id').iterrows():
                cls = "user-msg" if m['sender'] == "user" else "admin-msg"
                st.markdown(f'<div class="bubble {cls}">{m["text"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            with st.form("a_msg", clear_on_submit=True):
                rep = st.text_input("ตอบกลับ...")
                if st.form_submit_button("ส่ง"):
                    new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":target, "sender":"admin", "text":rep, "timestamp":datetime.now().strftime("%H:%M")}])
                    conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- AUTH ---
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
        nu, np, nf, nt = st.text_input("Username"), st.text_input("Password"), st.text_input("ชื่อ"), st.text_input("โทร")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "phone":nt, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u])); navigate("Login")
