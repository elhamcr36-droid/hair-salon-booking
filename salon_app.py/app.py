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
        
        /* สไตล์แชท */
        .chat-container {
            background-color: #f9f9f9; padding: 15px; border-radius: 15px; 
            border: 1px solid #ddd; height: 400px; overflow-y: auto; margin-bottom: 15px;
        }
        .my-msg { 
            background-color: #DCF8C6; padding: 10px; border-radius: 15px 15px 0px 15px; 
            margin-bottom: 10px; text-align: right; margin-left: 20%; box-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .other-msg { 
            background-color: #FFFFFF; padding: 10px; border-radius: 15px 15px 15px 0px; 
            margin-bottom: 10px; text-align: left; margin-right: 20%; border: 1px solid #eee; box-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .msg-info { font-size: 0.75rem; color: #555; font-weight: bold; display: block; margin-bottom: 3px; }
        
        .price-card {
            background-color: #ffffff !important; padding: 15px; border-radius: 12px;
            border-left: 5px solid #FF4B4B; margin-bottom: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. ฟังก์ชันดึงข้อมูล (เน้นแก้ปัญหาข้อมูลไม่ขึ้น) ---
def get_all_data(sheet_name, live=False):
    try:
        # ถ้า live=True จะบังคับโหลดใหม่ (ttl=0) เพื่อให้แชทและประวัติคิวขึ้นทันที
        ttl_val = 0 if live else 30
        df = conn.read(worksheet=sheet_name, ttl=ttl_val)
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        # บังคับทุกอย่างเป็น String ป้องกัน Error เวลาเปรียบเทียบเบอร์โทร
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
        return df
    except:
        return pd.DataFrame()

# --- 3. NAVIGATION ---
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

# --- 4. PAGE LOGIC ---

# หน้าแรก
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ 09:30 - 19:30 น. | 📍 222 ซอย.พิรม สงขลา.")
    
    st.subheader("📋 ราคาค่าบริการ")
    c1, c2 = st.columns(2)
    c1.markdown('<div class="price-card"><b>✂️ ตัดผมชาย</b><br>150 บ.</div>', unsafe_allow_html=True)
    c2.markdown('<div class="price-card"><b>🚿 สระ-ไดร์</b><br>200 บ.</div>', unsafe_allow_html=True)
    
    st.link_button("📍 นำทางด้วย Google Maps (GPS)", "https://maps.google.com", type="primary", use_container_width=True)

# สมัครสมาชิก
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        u = st.text_input("เบอร์โทรศัพท์")
        f = st.text_input("ชื่อ-นามสกุล")
        p = st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ตกลง"):
            df_u = get_all_data("Users")
            new_u = pd.DataFrame([{"phone":u, "password":p, "fullname":f, "role":"user"}]).astype(str)
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
            st.cache_data.clear()
            st.success("สำเร็จ!"); navigate("Login")

# เข้าสู่ระบบ
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์")
    p_in = st.text_input("รหัสผ่าน", type="password")
    if st.button("ตกลง"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'admin', 'fullname':'แอดมิน'})
            navigate("Admin")
        else:
            df_u = get_all_data("Users")
            user = df_u[(df_u['phone'] == str(u_in)) & (df_u['password'] == str(p_in))]
            if not user.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':str(u_in), 'fullname':user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("ข้อมูลผิดพลาด")

# หน้าจอง/ประวัติ/แชท (ส่วนที่แก้ปัญหา)
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิว", "💬 แชทกับร้าน"])
    
    with t1:
        with st.form("book"):
            d = st.date_input("วันที่")
            tm = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            s = st.selectbox("บริการ", ["ตัดผม", "สระ-ไดร์", "ทำสี"])
            if st.form_submit_button("ยืนยัน"):
                df_b = get_all_data("Bookings", live=True)
                new_q = pd.DataFrame([{"id":str(int(time.time())), "username":st.session_state.username, "fullname":st.session_state.fullname, "date":str(d), "time":tm, "service":s, "status":"รอรับบริการ", "price":"0"}]).astype(str)
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                st.cache_data.clear()
                st.success("จองแล้ว!")
                time.sleep(1)
                st.rerun()

    with t2:
        st.subheader("📋 รายการจองของคุณ")
        df_b = get_all_data("Bookings", live=True) # บังคับดึงใหม่
        if not df_b.empty:
            my_q = df_b[df_b['username'] == st.session_state.username]
            if not my_q.empty:
                st.dataframe(my_q[['date', 'time', 'service', 'status']], use_container_width=True)
            else: st.info("ยังไม่มีประวัติการจอง")
        else: st.info("ไม่พบข้อมูล")

    with t3:
        st.subheader("💬 สนทนากับแอดมิน")
        df_c = get_all_data("Chats", live=True) # บังคับดึงใหม่
        
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        if not df_c.empty:
            for _, m in df_c.iterrows():
                is_me = str(m['username']) == str(st.session_state.username)
                cls = "my-msg" if is_me else "other-msg"
                st.markdown(f"<div class='{cls}'><span class='msg-info'>{m['fullname']} ({m['time']})</span>{m['message']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.form("send_msg", clear_on_submit=True):
            txt = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง"):
                if txt:
                    new_m = pd.DataFrame([{"username":st.session_state.username, "fullname":st.session_state.fullname, "message":txt, "time":datetime.now().strftime("%H:%M")}]).astype(str)
                    conn.update(worksheet="Chats", data=pd.concat([df_c, new_m], ignore_index=True))
                    st.rerun()

# หน้าแอดมิน
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    a1, a2 = st.tabs(["📊 จัดการคิว", "💬 ตอบแชท"])
    with a1:
        st.dataframe(get_all_data("Bookings", live=True))
    with a2:
        df_c = get_all_data("Chats", live=True)
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        if not df_c.empty:
            for _, m in df_c.iterrows():
                is_adm = str(m['username']) == 'admin'
                cls = "my-msg" if is_adm else "other-msg"
                st.markdown(f"<div class='{cls}'><span class='msg-info'>{m['fullname']}</span>{m['message']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        with st.form("adm_send"):
            atxt = st.text_input("ตอบลูกค้า...")
            if st.form_submit_button("ส่ง"):
                new_am = pd.DataFrame([{"username":"admin", "fullname":"แอดมิน", "message":atxt, "time":datetime.now().strftime("%H:%M")}]).astype(str)
                conn.update(worksheet="Chats", data=pd.concat([df_c, new_am], ignore_index=True))
                st.rerun()

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_v = get_all_data("Bookings", live=True)
    st.table(df_v[df_v['date'] == datetime.now().strftime("%Y-%m-%d")])
