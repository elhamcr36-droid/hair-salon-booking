import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Barber & Salon Online", layout="wide", initial_sidebar_state="collapsed")

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
        /* ปุ่มยกเลิกสีแดงพิเศษ */
        .stButton>button[kind="secondary"] {background-color: #ff4b4b; color: white; border: none;}
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- ข้อมูลเวลาเปิดร้าน (09:30 - 19:30 ทุก 30 นาที) ---
TIME_SLOTS = []
for h in range(9, 20):
    for m in ["00", "30"]:
        t = f"{h:02d}:{m}"
        if "09:30" <= t <= "19:30": TIME_SLOTS.append(t)

# --- ข้อมูลบริการ ---
SERVICES_DISPLAY = {
    "✂️ ตัดผมชาย (Men's Haircut)": "150 - 350",
    "💇‍♀️ ตัดผมหญิง (Women's Haircut)": "350 - 800",
    "🚿 สระ-ไดร์ (Wash & Blow Dry)": "200 - 450",
    "🎨 ทำสีผม (Hair Color)": "1,500 - 4,500",
    "✨ ยืดผมวอลลุ่ม (Magic Volume)": "2,000 - 5,500",
    "🌿 เคราตินทรีทเม้นท์ (Keratin)": "1,500 - 3,500"
}
SERVICES_BASE_PRICE = {"ตัดผมชาย": 150, "ตัดผมหญิง": 350, "สระ-ไดร์": 200, "ทำสีผม": 1500, "ยืดผมวอลลุ่ม": 2000, "เคราตินทรีทเม้นท์": 1500}

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

if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ Barber & Salon Online</h1>", unsafe_allow_html=True)
# --- แถบเมนู ---
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

# --- 1. หน้าจองคิว (ปรับปรุงปุ่มยกเลิกแบบรายบรรทัด) ---
if st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.username}")
    tab1, tab2 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง"])
    
    with tab1:
        svc = st.selectbox("เลือกบริการ", list(SERVICES_BASE_PRICE.keys()))
        d = st.date_input("เลือกวันที่")
        t = st.selectbox("เลือกเวลา", TIME_SLOTS)
        
        if d.weekday() == 2:
            st.warning("⚠️ ร้านหยุดทุกวันพุธ กรุณาเลือกวันอื่น")
        else:
            if st.button("ยืนยันจองคิว"):
                df_b = get_data("Bookings")
                # กันคิวชน (เช็คเฉพาะคิวที่รอรับบริการ)
                is_taken = df_b[(df_b['date'] == str(d)) & (df_b['time'] == t) & (df_b['status'] == 'รอรับบริการ')]
                if not is_taken.empty:
                    st.error("❌ เวลานี้มีคนจองแล้ว")
                else:
                    new_b = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "price": str(SERVICES_BASE_PRICE[svc]), "status": "รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_b], ignore_index=True))
                    st.success("จองคิวสำเร็จ!")
                    st.rerun()

    with tab2:
        df_b = get_data("Bookings")
        my_q = df_b[df_b['username'] == st.session_state.username]
        
        if my_q.empty:
            st.info("คุณยังไม่มีรายการจอง")
        else:
            # สร้างหัวตาราง
            h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([2, 2, 2, 2, 1.5])
            h_col1.write("**บริการ**")
            h_col2.write("**วันที่**")
            h_col3.write("**เวลา**")
            h_col4.write("**สถานะ**")
            h_col5.write("**จัดการ**")
            
            # แสดงข้อมูลทีละแถวพร้อมปุ่มกด
            for _, row in my_q.iterrows():
                r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([2, 2, 2, 2, 1.5])
                r_col1.write(row['service'])
                r_col2.write(row['date'])
                r_col3.write(row['time'])
                r_col4.write(f"🟢 {row['status']}" if row['status'] == "รอรับบริการ" else row['status'])
                
                # ปุ่มยกเลิกรายบรรทัด
                if r_col5.button("ยกเลิก", key=f"btn_{row['id']}"):
                    df_all = get_data("Bookings")
                    # ลบแถวนี้ออกทันที
                    df_all = df_all[df_all['id'] != row['id']]
                    conn.update(worksheet="Bookings", data=df_all)
                    st.toast(f"ลบคิว {row['service']} เรียบร้อย!")
                    st.rerun()

# --- หน้าอื่นๆ (Home, ViewQueues, Admin) คงเดิมแต่ปรับให้ข้อมูลสะอาด ---
elif st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ 09:30 - 19:30 น. (หยุดทุกวันพุธ)")
    p_col1, p_col2 = st.columns(2)
    for i, (name, price) in enumerate(SERVICES_DISPLAY.items()):
        target_col = p_col1 if i % 2 == 0 else p_col2
        with target_col:
            st.markdown(f'<div class="price-card"><div class="service-name">{name}</div><div class="price-range">{price} บาท</div></div>', unsafe_allow_html=True)

elif st.session_state.page == "Admin":
    st.subheader("📊 หลังบ้าน (Admin)")
    df_b = get_data("Bookings")
    st.dataframe(df_b, use_container_width=True)
    
    tid = st.text_input("ใส่ ID งานที่เสร็จแล้ว")
    if st.button("✅ ยืนยันให้บริการเสร็จ"):
        df_b.loc[df_b['id'] == tid, 'status'] = 'เสร็จสิ้น'
        conn.update(worksheet="Bookings", data=df_b)
        st.rerun()

elif st.session_state.page == "Login":
    # ... (ส่วน Login เหมือนเดิม)
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
                st.session_state.update({'logged_in':True, 'user_role':check.iloc[0]['role'], 'username':u})
                navigate("Booking")
            else: st.error("ผิดพลาด")

elif st.session_state.page == "Register":
    # ... (ส่วน Register เหมือนเดิม)
    with st.form("reg"):
        nu, np, nt = st.text_input("ชื่อ"), st.text_input("รหัส", type="password"), st.text_input("เบอร์")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "phone":nt, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
            st.success("สำเร็จ!")

elif st.session_state.page == "ViewQueues":
    df_b = get_data("Bookings")
    today = str(datetime.now().date())
    st.dataframe(df_b[(df_b['date'] == today) & (df_b['status'] == 'รอรับบริการ')][['time', 'service']])
