import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Barber Online Booking", layout="wide", initial_sidebar_state="collapsed")

# ซ่อน Sidebar และปรับแต่ง UI
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        div[data-testid="stMetricValue"] {font-size: 22px;}
    </style>
""", unsafe_allow_html=True)

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ข้อมูลบริการ ---
SERVICES = {"ตัดผมชาย": 150, "ตัดผมหญิง": 300, "สระ-ไดร์": 150, "ทำสีผม": 1200}

# --- ระบบจัดการสถานะหน้า ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(page):
    st.session_state.page = page
    st.rerun()

# ฟังก์ชันอ่านข้อมูลที่ป้องกันปัญหาเรื่องชนิดข้อมูล
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        return df.fillna("").astype(str) # แปลงทุกอย่างเป็น String และล้างค่าว่าง
    except Exception as e:
        st.error(f"❌ ไม่สามารถดึงข้อมูลจาก {sheet_name} ได้: {e}")
        return pd.DataFrame()

# --- เมนูหลัก (Top Navigation) ---
st.markdown("<h1 class='main-header'>✂️ Barber & Salon Online</h1>", unsafe_allow_html=True)
menu_cols = st.columns(5)
with menu_cols[0]: 
    if st.button("🏠 หน้าแรก"): navigate("Home")
with menu_cols[1]: 
    if st.button("📅 คิวว่าง"): navigate("ViewQueues")

if not st.session_state.logged_in:
    with menu_cols[3]: 
        if st.button("📝 สมัคร"): navigate("Register")
    with menu_cols[4]: 
        if st.button("🔑 เข้าสู่ระบบ"): navigate("Login")
else:
    if st.session_state.get('user_role') == 'admin':
        with menu_cols[2]: 
            if st.button("📊 หลังบ้าน"): navigate("Admin")
    else:
        with menu_cols[2]: 
            if st.button("✂️ จองคิว"): navigate("Booking")
    with menu_cols[4]: 
        if st.button("🚪 ออก"):
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- LOGIC รายหน้า ---

# 1. หน้าแรก
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=800")
    st.subheader("📍 พิกัดร้านและนำทาง")
    map_url = "https://www.google.com/maps/search/?api=1&query=13.7563,100.5018" # ใส่พิกัดจริงของคุณ
    st.markdown(f'<a href="{map_url}" target="_blank"><button style="width:100%; background-color:#FF4B4B; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; font-size:16px;">🛰️ เปิด Google Maps นำทาง</button></a>', unsafe_allow_html=True)

# 2. ดูคิวว่าง
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 ตารางการจองวันนี้")
    df_b = get_data("Bookings")
    if not df_b.empty:
        today = str(datetime.now().date())
        q_today = df_b[(df_b['date'] == today) & (df_b['status'] != 'ยกเลิก')]
        if not q_today.empty:
            st.dataframe(q_today[['time', 'service']].sort_values('time'), use_container_width=True)
        else:
            st.success("วันนี้ยังไม่มีคิวจอง สามารถจองได้เลย!")

# 3. เข้าสู่ระบบ (แก้ไขการตรวจสอบ)
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_input = st.text_input("Username").strip()
    p_input = st.text_input("Password", type="password").strip()
    
    if st.button("Login"):
        # เช็ค Admin Hardcoded
        if u_input == "admin222" and p_input == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'Admin'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            # ค้นหาโดยลบช่องว่างแฝง
            user_found = df_u[(df_u['username'].str.strip() == u_input) & 
                              (df_u['password'].str.strip() == p_input)]
            
            if not user_found.empty:
                role = user_found.iloc[0]['role']
                st.session_state.update({'logged_in': True, 'user_role': role, 'username': u_input})
                navigate("Booking" if role != 'admin' else "Admin")
            else:
                st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

# 4. สมัครสมาชิก
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        new_u = st.text_input("Username").strip()
        new_p = st.text_input("Password", type="password").strip()
        new_t = st.text_input("เบอร์โทรศัพท์")
        if st.form_submit_button("ยืนยันการสมัคร"):
            df_u = get_data("Users")
            if new_u in df_u['username'].values:
                st.error("ชื่อผู้ใช้นี้มีคนใช้แล้ว")
            else:
                new_data = pd.DataFrame([{"username": new_u, "password": new_p, "phone": new_t, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_data], ignore_index=True))
                st.success("สมัครสำเร็จ! กรุณาเข้าสู่ระบบ")

# 5. จองคิว & ยกเลิก (กันจองซ้ำ)
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.username}")
    tab_new, tab_my = st.tabs(["🆕 จองคิว", "📋 รายการของฉัน"])
    
    with tab_new:
        svc = st.selectbox("เลือกบริการ", list(SERVICES.keys()))
        date_sel = st.date_input("วันที่")
        time_opts = [f"{h:02d}:{m:02d}" for h in range(9, 21) for m in (0, 30)]
        time_sel = st.selectbox("เวลา", time_opts)
        
        if st.button("🚀 ยืนยันการจอง"):
            df_b = get_data("Bookings")
            # เช็คคิวซ้ำ
            is_taken = df_b[(df_b['date'] == str(date_sel)) & (df_b['time'] == time_sel) & (df_b['status'] != 'ยกเลิก')]
            if not is_taken.empty:
                st.error("❌ เวลานี้มีคนจองแล้ว")
            else:
                booking_data = pd.DataFrame([{
                    "id": str(len(df_b)+1), "username": st.session_state.username, 
                    "service": svc, "date": str(date_sel), "time": time_sel, 
                    "price": str(SERVICES[svc]), "status": "รอรับบริการ"
                }])
                conn.update(worksheet="Bookings", data=pd.concat([df_b, booking_data], ignore_index=True))
                st.success("✅ จองสำเร็จ!")
                st.balloons()

    with tab_my:
        df_b = get_data("Bookings")
        my_q = df_b[(df_b['username'] == st.session_state.username) & (df_b['status'] == 'รอรับบริการ')]
        if not my_q.empty:
            st.dataframe(my_q[['id', 'service', 'date', 'time']], use_container_width=True)
            cancel_id = st.text_input("ใส่ ID ที่ต้องการยกเลิก")
            if st.button("❌ ยกเลิกคิว"):
                df_b.loc[df_b['id'] == cancel_id, 'status'] = 'ยกเลิก'
                conn.update(worksheet="Bookings", data=df_b)
                st.warning("ยกเลิกคิวแล้ว")
                st.rerun()
        else: st.info("ยังไม่มีคิวที่จองไว้")

# 6. หลังบ้าน (Admin)
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการร้าน")
    df_b = get_data("Bookings")
    if not df_b.empty:
        today = str(datetime.now().date())
        # ยอดขาย
        sales_today = pd.to_numeric(df_b[(df_b['date'] == today) & (df_b['status'] == 'เสร็จสิ้น')]['price']).sum()
        st.metric("ยอดขายที่สำเร็จวันนี้", f"{sales_today} บาท")
        
        st.write("🗓️ คิววันนี้:")
        st.dataframe(df_b[df_b['status'] != 'ยกเลิก'].sort_values(['date','time']), use_container_width=True)
        
        target_id = st.text_input("จัดการ ID")
        c_done, c_del = st.columns(2)
        if c_done.button("✅ งานเสร็จสิ้น"):
            df_b.loc[df_b['id'] == target_id, 'status'] = 'เสร็จสิ้น'
            conn.update(worksheet="Bookings", data=df_b)
            st.rerun()
        if c_del.button("🗑️ ลบข้อมูล"):
            conn.update(worksheet="Bookings", data=df_b[df_b['id'] != target_id])
            st.rerun()
