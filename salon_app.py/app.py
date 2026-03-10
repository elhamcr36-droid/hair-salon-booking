import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Barber Pro Booking", layout="wide", initial_sidebar_state="collapsed")

# CSS ตกแต่ง UI และซ่อน Sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        .stTabs [data-baseweb="tab-list"] {gap: 10px; justify-content: center;}
    </style>
""", unsafe_allow_html=True)

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ข้อมูลบริการและราคา ---
SERVICES = {
    "ตัดผมชาย": 150, "ตัดผมหญิง": 300, "สระ-ไดร์": 150,
    "ทำสีผม": 1200, "ดัดผม": 1500, "ยืดผม": 2000
}

# --- ระบบ Navigation ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(page_name):
    st.session_state.page = page_name
    st.rerun()

# ฟังก์ชันอ่านข้อมูล (เพิ่ม Error Handling)
def get_data(sheet_name):
    try:
        return conn.read(worksheet=sheet_name, ttl=0)
    except Exception as e:
        st.error(f"❌ เชื่อมต่อ Google Sheets ไม่ได้: {e}")
        st.info("กรุณาตรวจสอบว่าได้ Share สิทธิ์ Editor ให้ Email ใน Secrets หรือยัง?")
        return pd.DataFrame()

# --- เมนูหลักด้านบน ---
st.markdown("<h1 class='main-header'>✂️ Barber & Salon Online</h1>", unsafe_allow_html=True)
cols = st.columns(5)
with cols[0]: 
    if st.button("🏠 หน้าแรก"): navigate("Home")
with cols[1]: 
    if st.button("📅 คิวว่าง"): navigate("ViewQueues")

if not st.session_state.logged_in:
    with cols[3]: 
        if st.button("📝 สมัคร"): navigate("Register")
    with cols[4]: 
        if st.button("🔑 เข้าสู่ระบบ"): navigate("Login")
else:
    if st.session_state.get('user_role') == 'admin':
        with cols[2]: 
            if st.button("📊 หลังบ้าน"): navigate("Admin")
    else:
        with cols[2]: 
            if st.button("✂️ จองคิว"): navigate("Booking")
    with cols[4]: 
        if st.button("🚪 ออก"):
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- หน้าแรก & GPS ---
if st.session_state.page == "Home":
    st.subheader("📍 พิกัดร้านและนำทาง")
    st.image("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=800")
    map_url = "https://www.google.com/maps/search/?api=1&query=13.7563,100.5018" # ใส่พิกัดร้านคุณ
    st.markdown(f'<a href="{map_url}" target="_blank"><button style="width:100%; background-color:#FF4B4B; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; font-size:16px;">🛰️ เปิด Google Maps นำทางมาที่ร้าน</button></a>', unsafe_allow_html=True)

# --- ดูคิวว่าง ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 ตรวจสอบคิวว่างวันนี้")
    df_b = get_data("Bookings")
    if not df_b.empty:
        today = str(datetime.now().date())
        q_today = df_b[(df_b['date'].astype(str) == today) & (df_b['status'] != 'ยกเลิก')]
        if not q_today.empty:
            st.write("ช่วงเวลาที่มีผู้จองแล้ว:")
            st.dataframe(q_today[['time', 'service']].sort_values('time'), use_container_width=True)
        else:
            st.success("วันนี้ยังไม่มีการจอง สามารถเลือกเวลาได้ตามสะดวก!")

# --- สมัครสมาชิก ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        t = st.text_input("เบอร์โทรศัพท์")
        if st.form_submit_button("สมัครสมาชิก"):
            df_u = get_data("Users")
            if u in df_u['username'].astype(str).values:
                st.error("ชื่อผู้ใช้นี้ถูกใช้ไปแล้ว")
            else:
                new_user = pd.DataFrame([{"username": u, "password": p, "phone": t, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_user], ignore_index=True))
                st.success("สมัครสำเร็จ! กรุณาเข้าสู่ระบบ")

# --- เข้าสู่ระบบ ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    user_in = st.text_input("Username")
    pass_in = st.text_input("Password", type="password")
    if st.button("Login"):
        if user_in == "admin222" and pass_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'Admin'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            # แก้ไขเรื่อง Data Type: แปลงทั้งคู่เป็น String ก่อนเช็ค
            user_check = df_u[(df_u['username'].astype(str) == str(user_in)) & 
                              (df_u['password'].astype(str) == str(pass_in))]
            if not user_check.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': str(user_in)})
                navigate("Booking")
            else:
                st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

# --- จองคิว & ยกเลิกคิว ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.username}")
    t1, t2 = st.tabs(["🆕 จองคิวใหม่", "📋 คิวของฉัน / ยกเลิก"])
    
    with t1:
        svc = st.selectbox("เลือกบริการ", list(SERVICES.keys()))
        d = st.date_input("เลือกวันที่")
        times = [f"{h:02d}:{m:02d}" for h in range(9, 21) for m in (0, 30)]
        t = st.selectbox("เลือกเวลา", times)
        
        if st.button("ยืนยันการจอง"):
            df_b = get_data("Bookings")
            # กันจองซ้ำ (แปลงเป็น String ทั้งหมดเพื่อความแม่นยำ)
            conflict = df_b[(df_b['date'].astype(str) == str(d)) & 
                            (df_b['time'].astype(str) == str(t)) & 
                            (df_b['status'] != 'ยกเลิก')]
            if not conflict.empty:
                st.error("❌ เวลานี้มีคนจองแล้ว กรุณาเลือกเวลาอื่น")
            else:
                new_row = pd.DataFrame([{"id": len(df_b)+1, "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "price": SERVICES[svc], "status": "รอรับบริการ"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_row], ignore_index=True))
                st.success("✅ จองสำเร็จ!")
                st.balloons()

    with t2:
        df_b = get_data("Bookings")
        my_q = df_b[(df_b['username'].astype(str) == st.session_state.username) & (df_b['status'] == 'รอรับบริการ')]
        if not my_q.empty:
            st.dataframe(my_q[['id', 'service', 'date', 'time', 'price']], use_container_width=True)
            cid = st.number_input("ใส่ ID คิวที่ต้องการยกเลิก", step=1, min_value=1)
            if st.button("❌ ยกเลิกคิวนี้"):
                df_b.loc[df_b['id'] == cid, 'status'] = 'ยกเลิก'
                conn.update(worksheet="Bookings", data=df_b)
                st.warning("ยกเลิกคิวเรียบร้อย")
                st.rerun()
        else: st.info("คุณยังไม่มีคิวที่จองไว้")

# --- หลังบ้าน Admin ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการหลังบ้าน")
    df_b = get_data("Bookings")
    if not df_b.empty:
        df_active = df_b[df_b['status'] != 'ยกเลิก']
        today = str(datetime.now().date())
        
        c1, c2 = st.columns(2)
        with c1: st.metric("ยอดขายวันนี้", f"{df_active[df_active['date'].astype(str) == today]['price'].sum()} บ.")
        with c2: st.metric("ยอดขายเดือนนี้", f"{df_active[df_active['date'].astype(str).str.contains(today[:7])]['price'].sum()} บ.")
        
        st.write("🗓️ ตารางคิวทั้งหมด")
        st.dataframe(df_b.sort_values(['date', 'time'], ascending=False), use_container_width=True)
        
        edit_id = st.number_input("ระบุ ID เพื่อจัดการ", step=1)
        ca, cb = st.columns(2)
        if ca.button("🗑️ ลบข้อมูล"):
            conn.update(worksheet="Bookings", data=df_b[df_b['id'] != edit_id])
            st.rerun()
        if cb.button("✅ งานเสร็จสิ้น"):
            df_b.loc[df_b['id'] == edit_id, 'status'] = 'เสร็จสิ้น'
            conn.update(worksheet="Bookings", data=df_b)
            st.rerun()
