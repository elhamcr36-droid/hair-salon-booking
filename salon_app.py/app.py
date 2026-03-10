import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Barber Pro Booking", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df.columns = [str(c).strip() for c in df.columns]
        # ฟังก์ชันพิเศษ: ล้างช่องว่าง และ ล้าง .0 ที่เกิดจากตัวเลขทศนิยม
        def clean_val(v):
            v = str(v).strip()
            if v.endswith('.0'): v = v[:-2]
            return v
        return df.fillna("").applyview(lambda x: x.map(clean_val)) if hasattr(df, 'applymap') else df.fillna("").apply(lambda x: x.map(clean_val))
    except:
        # กรณี pandas version ใหม่ใช้ map แทน applymap
        df = conn.read(worksheet=sheet_name, ttl=0)
        df.columns = [str(c).strip() for c in df.columns]
        return df.fillna("").map(lambda x: str(x).strip().replace('.0', '') if str(x).endswith('.0') else str(x).strip())

SERVICES = {"ตัดผมชาย": 150, "ตัดผมหญิง": 300, "สระ-ไดร์": 150, "ทำสีผม": 1200}

if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ Barber & Salon Online</h1>", unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1: 
    if st.button("🏠 หน้าแรก"): navigate("Home")
with c2: 
    if st.button("📅 คิวว่าง"): navigate("ViewQueues")

if not st.session_state.logged_in:
    with c4: 
        if st.button("📝 สมัคร"): navigate("Register")
    with c5: 
        if st.button("🔑 เข้าสู่ระบบ"): navigate("Login")
else:
    target = "Admin" if st.session_state.user_role == 'admin' else "Booking"
    btn_text = "📊 หลังบ้าน" if st.session_state.user_role == 'admin' else "✂️ จองคิว"
    with c3: 
        if st.button(btn_text): navigate(target)
    with c5: 
        if st.button("🚪 ออก"):
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=800")
    st.info("ยินดีต้อนรับ! กรุณาเข้าสู่ระบบเพื่อจองคิว")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_b = get_data("Bookings")
    if not df_b.empty:
        today = str(datetime.now().date())
        q = df_b[(df_b['date'] == today) & (df_b['status'] != 'ยกเลิก')]
        st.dataframe(q[['time', 'service']].sort_values('time'), use_container_width=True)

elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u = st.text_input("Username").strip()
    p = st.text_input("Password", type="password").strip()
    if st.button("Login"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            check = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not check.empty:
                role = check.iloc[0]['role']
                st.session_state.update({'logged_in':True, 'user_role':role, 'username':u})
                navigate("Admin" if role == 'admin' else "Booking")
            else:
                st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nu, np, nt = st.text_input("Username"), st.text_input("Password", type="password"), st.text_input("เบอร์โทร")
        if st.form_submit_button("ตกลง"):
            df_u = get_data("Users")
            if nu.strip() in df_u['username'].values: st.error("ชื่อนี้มีคนใช้แล้ว")
            else:
                new_u = pd.DataFrame([{"username":nu.strip(), "password":np.strip(), "phone":nt.strip(), "role":"user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                st.success("สำเร็จ!")

elif st.session_state.page == "Booking":
    st.subheader(f"สวัสดีคุณ {st.session_state.username}")
    svc = st.selectbox("บริการ", list(SERVICES.keys()))
    d = st.date_input("วันที่")
    t = st.selectbox("เวลา", [f"{h:02d}:00" for h in range(9, 20)])
    if st.button("ยืนยันจอง"):
        df_b = get_data("Bookings")
        new_b = pd.DataFrame([{"id":str(len(df_b)+1), "username":st.session_state.username, "service":svc, "date":str(d), "time":t, "price":str(SERVICES[svc]), "status":"รอรับบริการ"}])
        conn.update(worksheet="Bookings", data=pd.concat([df_b, new_b], ignore_index=True))
        st.success("จองเรียบร้อย!")

elif st.session_state.page == "Admin":
    st.subheader("📊 หลังบ้าน")
    df_b = get_data("Bookings")
    st.dataframe(df_b, use_container_width=True)
