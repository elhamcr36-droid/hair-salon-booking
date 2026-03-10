import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. UI Setup ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

SHOP_LOCATION_URL = "https://www.google.com/maps/place/222+%E0%B8%96%E0%B8%99%E0%B8%99+%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B8%9A%E0%B8%B2%E0%B8%A5+1+%E0%B8%95%E0%B8%B3%E0%B8%9A%E0%B8%A5%E0%B8%9A%E0%B9%88%E0%B8%AD%E0%B8%A2%E0%B8%B2%E0%B8%87+%E0%B8%AD%E0%B8%B3%E0%B9%80%E0%B8%A0%E0%B8%AD%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+90000/@7.1915128,100.6007972,17z/data=!3m1!4b1!4m6!3m5!1s0x304d3323c7ad029d:0x7cfb098f4f859e4c!8m2!3d7.1915128!4d100.6007972!16s%2Fg%2F11jylj3r6y?entry=ttu&g_ep=EgoyMDI2MDMwOC4wIKXMDSoASAFQAw%3D%3D" 

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        .price-card {
            background-color: #ffffff; padding: 20px; border-radius: 15px;
            border-left: 8px solid #FF4B4B; margin-bottom: 15px; color: #1A1A1A;
        }
        .chat-bubble { padding: 10px 15px; border-radius: 15px; margin-bottom: 5px; display: inline-block; max-width: 80%; }
        .user-bubble { background-color: #E1FFC7; color: #000; border-bottom-right-radius: 2px; }
        .admin-bubble { background-color: #F0F0F0; color: #000; border-bottom-left-radius: 2px; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. Data Functions ---
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        return df
    except: return pd.DataFrame()

# ฟังก์ชันช่วยแปลง username เป็น fullname
def get_user_map():
    df_u = get_data("Users")
    if not df_u.empty:
        return dict(zip(df_u['username'], df_u['fullname']))
    return {}

# --- 3. Navigation ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon Online</h1>", unsafe_allow_html=True)
m_cols = st.columns(5)
with m_cols[0]: 
    if st.button("🏠 หน้าแรก"): navigate("Home")
with m_cols[1]: 
    if st.button("📅 คิววันนี้"): navigate("ViewQueues")

if not st.session_state.logged_in:
    with m_cols[3]: 
        if st.button("📝 สมัครสมาชิก"): navigate("Register")
    with m_cols[4]: 
        if st.button("🔑 เข้าสู่ระบบ"): navigate("Login")
else:
    role = st.session_state.get('user_role')
    with m_cols[2]: 
        if st.button("📊 หลังบ้าน" if role == 'admin' else "✂️ จองคิว"): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 4. Admin Page ---
if st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการร้านและข้อความ")
    t_admin1, t_admin2 = st.tabs(["📈 จัดการคิว", "💬 แชทกับลูกค้า"])
    
    with t_admin1:
        df_b = get_data("Bookings")
        df_u = get_data("Users")
        if not df_b.empty:
            df_admin = pd.merge(df_b, df_u[['username', 'fullname', 'phone']], on='username', how='left')
            for _, row in df_admin.sort_values(['date','time'], ascending=[False, True]).iterrows():
                with st.expander(f"⏰ {row['time']} | {row['fullname']}"):
                    if st.button("🗑️ ลบคิว", key=f"del_{row['id']}"):
                        conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']]); st.rerun()

    with t_admin2:
        df_msg = get_data("Messages")
        user_map = get_user_map() # ดึงแผนผังชื่อจริง
        
        if not df_msg.empty:
            # สร้างรายการตัวเลือกที่เป็น "ชื่อจริง (username)" เพื่อให้แอดมินเลือกง่าย
            u_options = {u: f"{user_map.get(u, u)} (@{u})" for u in df_msg['username'].unique()}
            selected_username = st.selectbox("เลือกแชทกับลูกค้า:", options=list(u_options.keys()), format_func=lambda x: u_options[x])
            
            chat_box = df_msg[df_msg['username'] == selected_username].sort_values('msg_id')
            for _, m in chat_box.iterrows():
                align = "left" if m['sender'] == "user" else "right"
                cls = "user-bubble" if m['sender'] == "user" else "admin-bubble"
                display_name = user_map.get(selected_username, selected_username) if m['sender'] == "user" else "แอดมิน"
                st.markdown(f"<div style='text-align: {align};'><div class='chat-bubble {cls}'><b>{display_name}:</b> {m['text']}</div></div>", unsafe_allow_html=True)
            
            with st.form("admin_reply", clear_on_submit=True):
                rep = st.text_input("พิมพ์ข้อความตอบกลับ...")
                if st.form_submit_button("ส่ง") and rep:
                    new_r = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": selected_username, "sender": "admin", "text": rep, "timestamp": datetime.now().strftime("%H:%M")}])
                    conn.update(worksheet="Messages", data=pd.concat([df_msg, new_r], ignore_index=True)); st.rerun()

# --- 5. Booking & Chat Page (User) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 คุณ {st.session_state.get('fullname')}")
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 ติดต่อเรา"])
    
    with t1: # (ส่วนจองคิวเดิม...)
        svc = st.selectbox("เลือกบริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์"])
        d = st.date_input("วันที่")
        if st.button("ยืนยัน"):
            st.success("จองสำเร็จ (จำลอง)")
            
    with t3:
        st.write(f"### 💬 คุยกับแอดมิน (ในนาม: {st.session_state.fullname})")
        df_msg = get_data("Messages")
        my_msgs = df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id')
        
        for _, m in my_msgs.iterrows():
            align = "right" if m['sender'] == "user" else "left"
            cls = "user-bubble" if m['sender'] == "user" else "admin-bubble"
            # แสดงชื่อจริงในแชทฝั่งลูกค้า
            d_name = st.session_state.fullname if m['sender'] == "user" else "แอดมิน"
            st.markdown(f"<div style='text-align: {align};'><div class='chat-bubble {cls}'><b>{d_name}:</b> {m['text']}</div></div>", unsafe_allow_html=True)
            
            if m['sender'] == "user":
                with st.popover("📝 จัดการ"):
                    new_txt = st.text_input("แก้ไข", value=m['text'], key=f"e_{m['msg_id']}")
                    c1, c2 = st.columns(2)
                    if c1.button("💾 บันทึก", key=f"s_{m['msg_id']}"):
                        df_msg.loc[df_msg['msg_id'] == m['msg_id'], 'text'] = new_txt
                        conn.update(worksheet="Messages", data=df_msg); st.rerun()
                    if c2.button("🗑️ ลบ", key=f"d_{m['msg_id']}", type="primary"):
                        conn.update(worksheet="Messages", data=df_msg[df_msg['msg_id'] != m['msg_id']]); st.rerun()

        with st.form("u_send", clear_on_submit=True):
            msg = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง") and msg:
                new_row = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "sender": "user", "text": msg, "timestamp": datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_row], ignore_index=True)); st.rerun()

# --- 6. Home, Login, Register (ส่วนเดิม...) ---
elif st.session_state.page == "Home":
    st.write("หน้าหลักร้าน 222-Salon")
elif st.session_state.page == "Login":
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
        df_u = get_data("Users")
        user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
        if not user.empty:
            st.session_state.update({'logged_in':True, 'user_role':user.iloc[0]['role'], 'username':u, 'fullname':user.iloc[0]['fullname']})
            navigate("Admin" if user.iloc[0]['role'] == 'admin' else "Booking")
