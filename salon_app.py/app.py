import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; height: 3.2em; transition: 0.3s;}
        
        /* สไตล์กล่องแชท */
        .chat-container {
            background-color: #f9f9f9; padding: 15px; border-radius: 15px; 
            border: 1px solid #ddd; height: 400px; overflow-y: auto; margin-bottom: 15px;
        }
        .my-msg { 
            background-color: #DCF8C6; padding: 10px; border-radius: 15px 15px 0px 15px; 
            margin-bottom: 10px; text-align: right; margin-left: 25%; box-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .other-msg { 
            background-color: #FFFFFF; padding: 10px; border-radius: 15px 15px 15px 0px; 
            margin-bottom: 10px; text-align: left; margin-right: 25%; border: 1px solid #eee; box-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .msg-info { font-size: 0.75rem; color: #555; font-weight: bold; display: block; margin-bottom: 3px; }
        .msg-time { font-size: 0.65rem; color: #999; }
        
        .price-card {
            background-color: #ffffff !important; padding: 15px; border-radius: 12px;
            border-left: 5px solid #FF4B4B; margin-bottom: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- ฟังก์ชันดึงข้อมูลแบบแยกส่วน ---
@st.cache_data(ttl=30)
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name)
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
        return df
    except:
        return pd.DataFrame()

# ฟังก์ชันดึงแชทแบบ Force Refresh (ห้ามใช้ Cache)
def get_chat_now():
    try:
        # บังคับดึงใหม่ทุกครั้ง (ttl=0)
        df = conn.read(worksheet="Chats", ttl=0)
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        # ถ้าพังให้คืนค่าโครงสร้างว่าง
        return pd.DataFrame(columns=['username', 'fullname', 'message', 'time'])

# --- 2. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)

m_cols = st.columns(5)
with m_cols[0]:
    if st.button("🏠 หน้าแรก"): navigate("Home")
with m_cols[1]:
    if st.button("📅 คิววันนี้"): navigate("ViewQueues")

if not st.session_state.logged_in:
    with m_cols[3]: 
        if st.button("📝 สมัคร"): navigate("Register")
    with m_cols[4]: 
        if st.button("🔑 เข้าสู่ระบบ"): navigate("Login")
else:
    role = st.session_state.get('user_role')
    with m_cols[2]:
        lbl = "📊 จัดการร้าน" if role == 'admin' else "✂️ จอง/แชท"
        if st.button(lbl): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]:
        if st.button("🚪 ออก"):
            st.session_state.clear()
            st.cache_data.clear()
            navigate("Home")

st.divider()

# --- 3. PAGE LOGIC ---

# หน้าแรก
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ 09:30 - 19:30 น. | 📍 222 ซอย.พิรม สงขลา.")
    st.link_button("📍 แผนที่ Google Maps (GPS)", "http://maps.google.com", type="primary", use_container_width=True)

# สมัครสมาชิก
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        u, f, p = st.text_input("เบอร์โทร"), st.text_input("ชื่อ-นามสกุล"), st.text_input("รหัส", type="password")
        if st.form_submit_button("ตกลง"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"phone":u, "password":p, "fullname":f, "role":"user"}]).astype(str)
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
            st.cache_data.clear()
            navigate("Login")

# เข้าสู่ระบบ
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทร")
    p_in = st.text_input("รหัสผ่าน", type="password")
    if st.button("ตกลง"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'admin', 'fullname': 'แอดมิน'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)]
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("ข้อมูลผิด")

# หน้าจองคิว + แชท (จุดที่มีปัญหา)
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 แชทกับร้าน"])
    
    with t1:
        with st.form("book"):
            d = st.date_input("เลือกวันที่")
            tm = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            s = st.selectbox("บริการ", ["ตัดผม", "สระ-ไดร์", "ทำสี"])
            if st.form_submit_button("ยืนยัน"):
                df_b = get_data("Bookings")
                new_q = pd.DataFrame([{"id":str(int(time.time())), "username":st.session_state.username, "fullname":st.session_state.fullname, "date":str(d), "time":tm, "service":s, "status":"รอรับบริการ", "price":"0"}]).astype(str)
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                st.cache_data.clear()
                st.success("จองแล้ว!")

    with t2:
        df_b = get_data("Bookings")
        st.dataframe(df_b[df_b['username'] == st.session_state.username], use_container_width=True)

    with t3:
        st.subheader("💬 ห้องสนทนา")
        # --- ดึงแชทแบบ Real-time ---
        df_c = get_chat_now()
        
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        if not df_c.empty and 'message' in df_c.columns:
            for _, msg in df_c.iterrows():
                is_me = str(msg['username']) == str(st.session_state.username)
                cls = "my-msg" if is_me else "other-msg"
                st.markdown(f"""
                    <div class='{cls}'>
                        <span class='msg-info'>{msg['fullname']}</span>
                        {msg['message']}<br>
                        <span class='msg-time'>{msg['time']}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ยังไม่มีข้อความ หรือหัวตารางไม่ถูกต้อง (username, fullname, message, time)")
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.form("send_chat_form", clear_on_submit=True):
            m_text = st.text_input("พิมพ์ข้อความที่นี่...")
            if st.form_submit_button("ส่งข้อความ"):
                if m_text:
                    new_m = pd.DataFrame([{
                        "username": str(st.session_state.username),
                        "fullname": str(st.session_state.fullname),
                        "message": str(m_text),
                        "time": datetime.now().strftime("%H:%M")
                    }]).astype(str)
                    # อัปเดตข้อมูลแชท
                    conn.update(worksheet="Chats", data=pd.concat([df_c, new_m], ignore_index=True))
                    st.rerun()

# หน้า Admin
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    a1, a2 = st.tabs(["📊 จัดการคิว", "💬 แชทลูกค้า"])
    with a1:
        st.dataframe(get_data("Bookings"))
    with a2:
        df_c = get_chat_now()
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        if not df_c.empty:
            for _, msg in df_c.iterrows():
                is_me = msg['username'] == 'admin'
                cls = "my-msg" if is_me else "other-msg"
                st.markdown(f"<div class='{cls}'><span class='msg-info'>{msg['fullname']}</span>{msg['message']}<br><span class='msg-time'>{msg['time']}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        with st.form("admin_send", clear_on_submit=True):
            atxt = st.text_input("ตอบกลับ...")
            if st.form_submit_button("ส่ง"):
                new_am = pd.DataFrame([{"username":"admin", "fullname":"แอดมิน", "message":atxt, "time":datetime.now().strftime("%H:%M")}]).astype(str)
                conn.update(worksheet="Chats", data=pd.concat([df_c, new_am], ignore_index=True))
                st.rerun()

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    st.table(get_data("Bookings"))
