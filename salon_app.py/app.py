import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Barber & Salon Online", layout="wide", initial_sidebar_state="collapsed")

# --- ลิงก์ GPS ร้าน (เปลี่ยนลิงก์ในฟันหนูนี้เป็นลิงก์ร้านคุณ) ---
SHOP_LOCATION_URL = "https://www.google.com/maps/search/?api=1&query=13.7468,100.5342" 

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        .price-card {
            background-color: #ffffff; padding: 15px; border-radius: 15px;
            border-left: 8px solid #FF4B4B; margin-bottom: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
        .service-name { font-weight: bold; font-size: 16px; color: #333; }
        .price-range { color: #FF4B4B; font-size: 18px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- ข้อมูลบริการและเวลา ---
SERVICES_DISPLAY = {
    "✂️ ตัดผมชาย": "150 - 350", "💇‍♀️ ตัดผมหญิง": "350 - 800",
    "🚿 สระ-ไดร์": "200 - 450", "🎨 ทำสีผม": "1,500 - 4,500",
    "✨ ยืดผมวอลลุ่ม": "2,000 - 5,500", "🌿 เคราติน": "1,500 - 3,500"
}
SERVICES_BASE_PRICE = {"ตัดผมชาย": 150, "ตัดผมหญิง": 350, "สระ-ไดร์": 200, "ทำสีผม": 1500, "ยืดผมวอลลุ่ม": 2000, "เคราติน": 1500}

TIME_SLOTS = [f"{h:02d}:{m}" for h in range(9, 20) for m in ["00", "30"] if "09:30" <= f"{h:02d}:{m}" <= "19:30"]

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df.columns = [str(c).strip() for c in df.columns]
        def clean_val(v):
            v = str(v).strip()
            if v.endswith('.0'): v = v[:-2]
            return v
        return df.fillna("").map(clean_val)
    except: return pd.DataFrame()

# --- ระบบ Navigation ---
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
        if st.button("🔑 Login"): navigate("Login")
else:
    role = st.session_state.get('user_role')
    with c3: 
        if st.button("📊 หลังบ้าน" if role == 'admin' else "✂️ จองคิว"): navigate("Admin" if role == 'admin' else "Booking")
    with c5: 
        if st.button("🚪 ออก"):
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 1. หน้าแรก (มีปุ่ม GPS) ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    col_i1, col_i2 = st.columns(2)
    col_i1.info("⏰ 09:30 - 19:30 น. (หยุดทุกวันพุธ)")
    col_i2.link_button("📍 นำทางไปยังร้าน (Google Maps)", SHOP_LOCATION_URL, type="primary")
    
    p_col1, p_col2 = st.columns(2)
    for i, (name, price) in enumerate(SERVICES_DISPLAY.items()):
        target = p_col1 if i % 2 == 0 else p_col2
        target.markdown(f'<div class="price-card"><div class="service-name">{name}</div><div class="price-range">{price} บาท</div></div>', unsafe_allow_html=True)

# --- 2. หน้าแอดมิน (ปุ่มอยู่หลัง Status) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการร้าน")
    df_b = get_data("Bookings")
    if not df_b.empty:
        df_b['price'] = pd.to_numeric(df_b['price'], errors='coerce').fillna(0)
        df_b['dt'] = pd.to_datetime(df_b['date'])
        today = str(datetime.now().date())
        # Dashboard
        m1, m2, m3 = st.columns(3)
        m1.metric("คิวรอวันนี้", len(df_b[(df_b['date']==today) & (df_b['status']=='รอรับบริการ')]))
        m2.metric("ยอดวันนี้", f"{df_b[df_b['date']==today]['price'].sum():,.0f} บ.")
        m3.metric("ยอดเดือนนี้", f"{df_b[df_b['dt'].dt.month == datetime.now().month]['price'].sum():,.0f} บ.")
        
        st.divider()
        # ตารางแบบมีปุ่ม
        h = st.columns([1, 1.5, 1.5, 1, 1, 1.5, 0.8])
        cols = ["เวลา", "ลูกค้า", "บริการ", "วันที่", "สถานะ", "จัดการงาน", "ลบ"]
        for i, head in enumerate(cols): h[i].write(f"**{head}**")
        
        for _, row in df_b.sort_values(['date','time'], ascending=[False, True]).iterrows():
            r = st.columns([1, 1.5, 1.5, 1, 1, 1.5, 0.8])
            r[0].write(row['time'])
            r[1].write(row['username'])
            r[2].write(row['service'])
            r[3].write(row['date'])
            r[4].write("🔵 รอ" if row['status'] == 'รอรับบริการ' else "✅ เสร็จ")
            if row['status'] == 'รอรับบริการ':
                if r[5].button("เสร็จสิ้น", key=f"d_{row['id']}"):
                    df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                    conn.update(worksheet="Bookings", data=df_b.drop(columns=['dt']))
                    st.rerun()
            else: r[5].write("-")
            if r[6].button("🗑️", key=f"del_{row['id']}"):
                conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']].drop(columns=['dt']))
                st.rerun()

# --- 3. หน้าจองคิวลูกค้า (ปุ่มยกเลิกหลัง Status) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 คุณ {st.session_state.username}")
    t1, t2 = st.tabs(["🆕 จองคิว", "📋 ประวัติ"])
    with t1:
        svc = st.selectbox("บริการ", list(SERVICES_BASE_PRICE.keys()))
        d = st.date_input("วันที่")
        t = st.selectbox("เวลา", TIME_SLOTS)
        if d.weekday() == 2: st.error("ร้านปิดวันพุธ")
        elif st.button("ยืนยันการจอง"):
            df_b = get_data("Bookings")
            if not df_b[(df_b['date']==str(d)) & (df_b['time']==t) & (df_b['status']=='รอรับบริการ')].empty:
                st.error("เวลานี้มีคนจองแล้ว")
            else:
                new = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "price": str(SERVICES_BASE_PRICE[svc]), "status": "รอรับบริการ"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new], ignore_index=True))
                st.success("จองสำเร็จ!")
                st.rerun()
    with t2:
        df_b = get_data("Bookings")
        my = df_b[df_b['username'] == st.session_state.username]
        h = st.columns([2, 2, 2, 1.5])
        for i, head in enumerate(["บริการ/เวลา", "วันที่", "สถานะ", "การจัดการ"]): h[i].write(f"**{head}**")
        for _, row in my.iterrows():
            r = st.columns([2, 2, 2, 1.5])
            r[0].write(f"{row['service']} ({row['time']})")
            r[1].write(row['date'])
            r[2].write(row['status'])
            if r[3].button("ยกเลิก", key=f"c_{row['id']}"):
                conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']])
                st.rerun()

# --- หน้า Login, Register, ViewQueues ---
elif st.session_state.page == "Login":
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            check = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not check.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u})
                navigate("Booking")
            else: st.error("ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Register":
    with st.form("reg"):
        nu, np, nt = st.text_input("ชื่อ"), st.text_input("รหัส"), st.text_input("เบอร์")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            if nu in df_u['username'].values: st.error("มีชื่อนี้แล้ว")
            else:
                conn.update(worksheet="Users", data=pd.concat([df_u, pd.DataFrame([{"username":nu,"password":np,"phone":nt,"role":"user"}])], ignore_index=True))
                st.success("สมัครสำเร็จ!")

elif st.session_state.page == "ViewQueues":
    df_b = get_data("Bookings")
    active = df_b[(df_b['date'] == str(datetime.now().date())) & (df_b['status'] == 'รอรับบริการ')]
    st.subheader("📅 คิววันนี้")
    st.dataframe(active[['time', 'service']].sort_values('time'), use_container_width=True)
