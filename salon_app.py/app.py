import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- 1. การตั้งค่าหน้าตาเว็บ (UI) ---
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
        .summary-box {
            text-align: center; background: #FF4B4B; color: white; padding: 15px;
            border-radius: 10px; margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. ฟังก์ชันจัดการข้อมูล (แก้ Error 429 & แชทขาว) ---

# สำหรับข้อมูลทั่วไป (ใช้ Cache 30 วิ เพื่อลดภาระ API)
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

# สำหรับแชท (Force Refresh: บังคับโหลดใหม่ตลอดเวลา)
def get_chat_now():
    try:
        # บังคับดึงข้อมูลใหม่ (ttl=0) เพื่อแก้ปัญหาหน้าขาว
        df = conn.read(worksheet="Chats", ttl=0)
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=['username', 'fullname', 'message', 'time'])

# --- 3. ระบบจัดการหน้าเว็บ ---
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
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            st.cache_data.clear()
            navigate("Home")

st.divider()

# --- 4. เนื้อหาแต่ละหน้า ---

# --- หน้าแรก ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ 09:30 - 19:30 น. | 📍 222 ซอย.พิรม สงขลา.")
    
    # บริการและราคา
    st.subheader("📋 ราคาค่าบริการ")
    services = {"✂️ ตัดผมชาย": "150 บ.", "💇‍♀️ ตัดผมหญิง": "350 บ.", "🚿 สระ-ไดร์": "200 บ.", "🎨 ทำสีผม": "1,500 บ.+"}
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><br><span style="color:#FF4B4B;">{price}</span></div>', unsafe_allow_html=True)
    
    # ปุ่ม GPS (ตามคำสั่ง)
    st.link_button("📍 นำทางด้วย Google Maps (GPS)", "https://maps.google.com", type="primary", use_container_width=True)

# --- สมัครสมาชิก ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg"):
        u = st.text_input("เบอร์โทรศัพท์ (สิบลัก)")
        f = st.text_input("ชื่อ-นามสกุล")
        p = st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ยืนยันการสมัคร"):
            if u and f and p:
                df_u = get_data("Users")
                new_u = pd.DataFrame([{"phone":u, "password":p, "fullname":f, "role":"user"}]).astype(str)
                conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                st.cache_data.clear()
                st.success("ลงทะเบียนสำเร็จ!"); navigate("Login")

# --- เข้าสู่ระบบ ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์")
    p_in = st.text_input("รหัสผ่าน", type="password")
    if st.button("เข้าสู่ระบบ"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'admin', 'fullname': 'แอดมิน'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)]
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("ข้อมูลไม่ถูกต้อง")

# --- หน้าจองคิว + แชท (จุดที่รวมคำสั่งแก้แชทขาว) ---
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิว", "💬 แชทกับร้าน"])
    
    with t1:
        with st.form("booking"):
            d = st.date_input("เลือกวันที่")
            tm = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสี"])
            if st.form_submit_button("ยืนยันการจอง"):
                df_b = get_data("Bookings")
                new_q = pd.DataFrame([{"id":str(int(time.time())), "username":st.session_state.username, "fullname":st.session_state.fullname, "date":str(d), "time":tm, "service":s, "status":"รอรับบริการ", "price":"0"}]).astype(str)
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                st.cache_data.clear()
                st.success("จองสำเร็จ!")

    with t2:
        df_b = get_data("Bookings")
        st.dataframe(df_b[df_b['username'] == st.session_state.username], use_container_width=True)

    with t3:
        st.subheader("💬 สนทนากับแอดมิน")
        df_c = get_chat_now() # เรียกใช้ฟังก์ชันดึงแชทแบบ Real-time
        
        # แสดงผลแชท
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        if not df_c.empty:
            for _, msg in df_c.iterrows():
                is_me = str(msg['username']) == str(st.session_state.username)
                cls = "my-msg" if is_me else "other-msg"
                st.markdown(f"<div class='{cls}'><span class='msg-info'>{msg['fullname']}</span>{msg['message']}<br><span class='msg-time'>{msg['time']}</span></div>", unsafe_allow_html=True)
        else:
            st.write("ยังไม่มีข้อความคุยกันเลย...")
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.form("chat_form", clear_on_submit=True):
            m_text = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง"):
                if m_text:
                    new_m = pd.DataFrame([{
                        "username": str(st.session_state.username),
                        "fullname": str(st.session_state.fullname),
                        "message": str(m_text),
                        "time": datetime.now().strftime("%H:%M")
                    }]).astype(str)
                    conn.update(worksheet="Chats", data=pd.concat([df_c, new_m], ignore_index=True))
                    st.rerun() # บังคับรีเฟรชหน้าจอทันที

# --- หน้า Admin (จัดการยอดเงินและแชท) ---
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    a1, a2 = st.tabs(["📊 คิววันนี้/ยอดเงิน", "💬 ตอบแชทลูกค้า"])
    
    with a1:
        df_b = get_data("Bookings")
        t_str = datetime.now().strftime("%Y-%m-%d")
        today = df_b[df_b['date'] == t_str]
        income = pd.to_numeric(today[today['status'] == "รับบริการเสร็จสิ้น"]['price'], errors='coerce').sum()
        
        col1, col2 = st.columns(2)
        col1.markdown(f"<div class='summary-box'><h3>คิววันนี้</h3><h2>{len(today)}</h2></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='summary-box' style='background:#28a745;'><h3>ยอดเงิน</h3><h2>{income:,.0f} บ.</h2></div>", unsafe_allow_html=True)
        st.dataframe(df_b)

    with a2:
        df_c = get_chat_now()
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        if not df_c.empty:
            for _, msg in df_c.iterrows():
                is_adm = msg['username'] == 'admin'
                cls = "my-msg" if is_adm else "other-msg"
                st.markdown(f"<div class='{cls}'><span class='msg-info'>{msg['fullname']}</span>{msg['message']}<br><span class='msg-time'>{msg['time']}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        with st.form("admin_chat", clear_on_submit=True):
            atxt = st.text_input("พิมพ์ตอบกลับลูกค้า...")
            if st.form_submit_button("ส่งในนามร้าน"):
                new_am = pd.DataFrame([{"username":"admin", "fullname":"แอดมิน (ร้าน)", "message":atxt, "time":datetime.now().strftime("%H:%M")}]).astype(str)
                conn.update(worksheet="Chats", data=pd.concat([df_c, new_am], ignore_index=True))
                st.rerun()

# --- คิววันนี้ (บุคคลทั่วไป) ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิวรับบริการวันนี้")
    df_b = get_data("Bookings")
    st.table(df_b[df_b['date'] == datetime.now().strftime("%Y-%m-%d")])
