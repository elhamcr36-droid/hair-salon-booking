import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Barber Pro Booking", layout="wide", initial_sidebar_state="collapsed")

# CSS ตกแต่งให้เหมือน Mobile App และซ่อน Sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; height: 3.5em;}
        .main-header {text-align: center; color: #FF4B4B;}
        div[data-testid="stMetricValue"] {font-size: 24px;}
    </style>
""", unsafe_allow_html=True)

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ข้อมูลบริการและราคา (ราคากลางประเทศไทย) ---
SERVICES = {
    "ตัดผมชาย": 150, "ตัดผมหญิง": 300, "สระ-ไดร์": 150,
    "ทำสีผม": 1200, "ดัดผม": 1500, "ยืดผม": 2000
}

# --- การจัดการสถานะหน้าจอ (Navigation) ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- ฟังก์ชันอ่าน/เขียนข้อมูล ---
def get_data(sheet):
    return conn.read(worksheet=sheet, ttl=0)

# --- แถบเมนูด้านบน (แทน Sidebar) ---
st.markdown("<h1 class='main-header'>✂️ Barber & Salon Online</h1>", unsafe_allow_html=True)
cols = st.columns(5)
with cols[0]: 
    if st.button("🏠 หน้าแรก"): navigate("Home")
with cols[1]: 
    if st.button("📅 ดูคิวว่าง"): navigate("ViewQueues")

if not st.session_state.logged_in:
    with cols[3]: 
        if st.button("📝 สมัคร"): navigate("Register")
    with cols[4]: 
        if st.button("🔑 เข้าสู่ระบบ"): navigate("Login")
else:
    if st.session_state.user_role == 'admin':
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

# --- LOGIC หน้าต่างๆ ---

# 1. หน้าแรก & GPS
if st.session_state.page == "Home":
    st.subheader("ยินดีต้อนรับสู่ร้านของเรา")
    st.image("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=800")
    
    st.markdown("### 📍 พิกัดร้าน")
    map_url = "https://www.google.com/maps/search/?api=1&query=13.7563,100.5018" # เปลี่ยนเป็นพิกัดร้านคุณ
    st.markdown(f'<a href="{map_url}" target="_blank"><button style="width:100%; background-color:#FF4B4B; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; font-size:16px;">🛰️ เปิด Google Maps นำทางมาที่ร้าน</button></a>', unsafe_allow_html=True)

# 2. ดูคิวว่าง (สำหรับลูกค้าทั่วไป)
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 ตรวจสอบคิวว่างวันนี้")
    df_b = get_data("Bookings")
    today = str(datetime.now().date())
    q_today = df_b[(df_b['date'] == today) & (df_b['status'] != 'ยกเลิก')]
    if not q_today.empty:
        st.write("ช่วงเวลาที่มีการจองแล้ว:")
        st.dataframe(q_today[['time', 'service']].sort_values('time'), use_container_width=True)
    else:
        st.success("วันนี้ยังไม่มีการจอง สามารถเลือกเวลาที่ต้องการได้เลย!")

# 3. สมัครสมาชิก
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg"):
        u = st.text_input("ชื่อผู้ใช้ (Username)")
        p = st.text_input("รหัสผ่าน (Password)", type="password")
        t = st.text_input("เบอร์โทรศัพท์")
        if st.form_submit_button("ยืนยันการสมัคร"):
            df_u = get_data("Users")
            if u in df_u['username'].values:
                st.error("ชื่อผู้ใช้นี้ถูกใช้ไปแล้ว")
            else:
                new_user = pd.DataFrame([{"username": u, "password": p, "phone": t, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_user], ignore_index=True))
                st.success("สมัครสำเร็จ! กรุณาเข้าสู่ระบบ")

# 4. เข้าสู่ระบบ
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
            check = df_u[(df_u['username'] == user_in) & (df_u['password'] == str(pass_in))]
            if not check.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': user_in})
                navigate("Booking")
            else: st.error("ข้อมูลไม่ถูกต้อง")

# 5. จองคิว & ยกเลิกคิว
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.username}")
    t1, t2 = st.tabs(["🆕 จองคิว", "📋 จัดการคิวของฉัน"])
    
    with t1:
        svc = st.selectbox("เลือกบริการ", list(SERVICES.keys()))
        d = st.date_input("เลือกวันที่")
        # สร้างตัวเลือกเวลาทีละ 30 นาที
        times = [f"{h:02d}:{m:02d}" for h in range(9, 20) for m in (0, 30)]
        t = st.selectbox("เลือกเวลา", times)
        
        if st.button("ยืนยันการจอง"):
            df_b = get_data("Bookings")
            # --- กันจองซ้ำ ---
            conflict = df_b[(df_b['date'] == str(d)) & (df_b['time'] == t) & (df_b['status'] != 'ยกเลิก')]
            if not conflict.empty:
                st.error("❌ เวลานี้มีคนจองแล้ว กรุณาเลือกเวลาอื่น")
            else:
                new_b = pd.DataFrame([{"id": len(df_b)+1, "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "price": SERVICES[svc], "status": "รอรับบริการ"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_b], ignore_index=True))
                st.success("✅ จองคิวสำเร็จ!")
                st.balloons()

    with t2:
        df_b = get_data("Bookings")
        my_q = df_b[(df_b['username'] == st.session_state.username) & (df_b['status'] == 'รอรับบริการ')]
        if not my_q.empty:
            st.dataframe(my_q[['id', 'service', 'date', 'time', 'status']], use_container_width=True)
            cid = st.number_input("ใส่ ID ที่ต้องการยกเลิก", step=1, min_value=1)
            if st.button("❌ ยกเลิกการจองนี้"):
                df_b.loc[df_b['id'] == cid, 'status'] = 'ยกเลิก'
                conn.update(worksheet="Bookings", data=df_b)
                st.warning("ยกเลิกคิวแล้ว")
                st.rerun()
        else: st.info("ไม่มีคิวค้างอยู่")

# 6. หลังบ้าน Admin
elif st.session_state.page == "Admin":
    st.subheader("📊 รายงานสำหรับผู้ดูแลร้าน")
    df_b = get_data("Bookings")
    df_active = df_b[df_b['status'] != 'ยกเลิก']
    
    # ยอดขาย
    today = str(datetime.now().date())
    c1, c2 = st.columns(2)
    with c1: st.metric("ยอดขายวันนี้", f"{df_active[df_active['date'] == today]['price'].sum()} บาท")
    with c2: st.metric("ยอดขายเดือนนี้", f"{df_active[df_active['date'].str.contains(today[:7])]['price'].sum()} บาท")
    
    st.write("---")
    st.write("🗓️ ตารางคิวทั้งหมด (สามารถแก้ไข/ลบ)")
    st.dataframe(df_b.sort_values(['date', 'time'], ascending=False), use_container_width=True)
    
    edit_id = st.number_input("ระบุ ID เพื่อจัดการ", step=1)
    col_x, col_y = st.columns(2)
    if col_x.button("🗑️ ลบข้อมูลถาวร"):
        df_b = df_b[df_b['id'] != edit_id]
        conn.update(worksheet="Bookings", data=df_b)
        st.rerun()
    if col_y.button("✅ งานเสร็จสิ้น"):
        df_b.loc[df_b['id'] == edit_id, 'status'] = 'เสร็จสิ้น'
        conn.update(worksheet="Bookings", data=df_b)
        st.rerun()


