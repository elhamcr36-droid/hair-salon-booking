import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Barber Pro Booking", layout="wide", initial_sidebar_state="collapsed")

# ตกแต่ง UI และซ่อน Sidebar
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

# --- ข้อมูลบริการ ---
SERVICES = {"ตัดผมชาย": 150, "ตัดผมหญิง": 300, "สระ-ไดร์": 150, "ทำสีผม": 1200}

# --- ระบบจัดการสถานะหน้า ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(page):
    st.session_state.page = page
    st.rerun()

# ฟังก์ชันอ่านข้อมูล (ดักจับช่องว่างและแปลงเป็น String)
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        # ล้างช่องว่างที่ชื่อคอลัมน์ (หัวตาราง)
        df.columns = [str(c).strip() for c in df.columns]
        # แปลงข้อมูลทั้งหมดเป็น String และลบช่องว่างแฝง
        return df.fillna("").astype(str).apply(lambda x: x.str.strip())
    except Exception as e:
        st.error(f"❌ เชื่อมต่อไม่ได้: {e}")
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
    label = "📊 หลังบ้าน" if st.session_state.user_role == 'admin' else "✂️ จองคิว"
    with menu_cols[2]: 
        if st.button(label): navigate("Admin" if st.session_state.user_role == 'admin' else "Booking")
    with menu_cols[4]: 
        if st.button("🚪 ออก"):
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 1. หน้าแรก ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=800")
    st.subheader("📍 พิกัดร้านและนำทาง")
    map_url = "https://www.google.com/maps/search/?api=1&query=13.7563,100.5018" 
    st.markdown(f'<a href="{map_url}" target="_blank"><button style="width:100%; background-color:#FF4B4B; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; font-size:16px;">🛰️ เปิด Google Maps</button></a>', unsafe_allow_html=True)

# --- 2. ดูคิวว่าง ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 ตารางการจองวันนี้")
    df_b = get_data("Bookings")
    if not df_b.empty:
        today = str(datetime.now().date())
        q_today = df_b[(df_b['date'] == today) & (df_b['status'] != 'ยกเลิก')]
        if not q_today.empty:
            st.dataframe(q_today[['time', 'service']].sort_values('time'), use_container_width=True)
        else:
            st.success("วันนี้ยังว่างทุกช่วงเวลา!")

# --- 3. เข้าสู่ระบบ (ดักช่องว่าง 100%) ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_input = st.text_input("Username").strip()
    p_input = st.text_input("Password", type="password").strip()
    
    if st.button("Login"):
        if u_input == "admin222" and p_input == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'Admin'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            if not df_u.empty:
                user_found = df_u[(df_u['username'] == u_input) & (df_u['password'] == p_input)]
                if not user_found.empty:
                    role = user_found.iloc[0]['role']
                    st.session_state.update({'logged_in': True, 'user_role': role, 'username': u_input})
                    navigate("Admin" if role == 'admin' else "Booking")
                else:
                    st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

# --- 4. สมัครสมาชิก ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nu = st.text_input("Username").strip()
        np = st.text_input("Password", type="password").strip()
        nt = st.text_input("เบอร์โทร")
        if st.form_submit_button("ยืนยัน"):
            df_u = get_data("Users")
            if nu in df_u['username'].values:
                st.error("Username นี้มีคนใช้แล้ว")
            else:
                new_data = pd.DataFrame([{"username": nu, "password": np, "phone": nt, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_data], ignore_index=True))
                st.success("สมัครสำเร็จ!")

# --- 5. จองคิว & ยกเลิก ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.username}")
    t1, t2 = st.tabs(["🆕 จองคิว", "📋 ของฉัน"])
    with t1:
        svc = st.selectbox("บริการ", list(SERVICES.keys()))
        d_sel = st.date_input("วันที่")
        time_opts = [f"{h:02d}:{m:02d}" for h in range(9, 21) for m in (0, 30)]
        t_sel = st.selectbox("เวลา", time_opts)
        if st.button("ยืนยันการจอง"):
            df_b = get_data("Bookings")
            if not df_b[(df_b['date'] == str(d_sel)) & (df_b['time'] == t_sel) & (df_b['status'] != 'ยกเลิก')].empty:
                st.error("❌ เวลานี้มีคนจองแล้ว")
            else:
                new_b = pd.DataFrame([{"id": str(len(df_b)+1), "username": st.session_state.username, "service": svc, "date": str(d_sel), "time": t_sel, "price": str(SERVICES[svc]), "status": "รอรับบริการ"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_b], ignore_index=True))
                st.success("จองสำเร็จ!")
    with t2:
        df_b = get_data("Bookings")
        my_q = df_b[(df_b['username'] == st.session_state.username) & (df_b['status'] == 'รอรับบริการ')]
        st.dataframe(my_q[['id', 'service', 'date', 'time']], use_container_width=True)
        cid = st.text_input("ใส่ ID เพื่อยกเลิก")
        if st.button("❌ ยกเลิก"):
            df_b.loc[df_b['id'] == cid, 'status'] = 'ยกเลิก'
            conn.update(worksheet="Bookings", data=df_b)
            st.rerun()

# --- 6. หลังบ้าน Admin ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการร้าน")
    df_b = get_data("Bookings")
    if not df_b.empty:
        st.write("คิวทั้งหมด:")
        st.dataframe(df_b.sort_values(['date','time']), use_container_width=True)
        tid = st.text_input("จัดการ ID")
        c1, c2 = st.columns(2)
        if c1.button("✅ งานเสร็จสิ้น"):
            df_b.loc[df_b['id'] == tid, 'status'] = 'เสร็จสิ้น'
            conn.update(worksheet="Bookings", data=df_b)
            st.rerun()
        if c2.button("🗑️ ลบข้อมูล"):
            conn.update(worksheet="Bookings", data=df_b[df_b['id'] != tid])
            st.rerun()
