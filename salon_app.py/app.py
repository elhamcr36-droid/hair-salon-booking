import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Barber & Salon Online", layout="wide", initial_sidebar_state="collapsed")

# --- ลิงก์ GPS ร้าน (เปลี่ยนเป็นลิงก์ร้านคุณ) ---
SHOP_LOCATION_URL = "https://maps.google.com" 

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
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- ข้อมูลพื้นฐาน ---
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

# --- แถบเมนูหลัก ---
m1, m2, m3, m4, m5 = st.columns(5)
with m1: 
    if st.button("🏠 หน้าแรก"): navigate("Home")
with m2: 
    if st.button("📅 คิวว่างวันนี้"): navigate("ViewQueues")

if not st.session_state.logged_in:
    with m4: 
        if st.button("📝 สมัครสมาชิก"): navigate("Register")
    with m5: 
        if st.button("🔑 เข้าสู่ระบบ"): navigate("Login")
else:
    role = st.session_state.get('user_role')
    with m3: 
        if st.button("📊 หลังบ้าน" if role == 'admin' else "✂️ จองคิว"): navigate("Admin" if role == 'admin' else "Booking")
    with m5: 
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 1. หน้าแรก ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    c_info1, c_info2 = st.columns(2)
    c_info1.info("⏰ 09:30 - 19:30 (หยุดทุกวันพุธ)")
    c_info2.link_button("📍 นำทางด้วย GPS (Google Maps)", SHOP_LOCATION_URL, type="primary")
    
    p_col1, p_col2 = st.columns(2)
    for i, (name, price) in enumerate(SERVICES_DISPLAY.items()):
        target = p_col1 if i % 2 == 0 else p_col2
        target.markdown(f'<div class="price-card"><div class="service-name">{name}</div><div class="price-range">{price} บาท</div></div>', unsafe_allow_html=True)

# --- 2. หน้าแอดมิน (เห็นเบอร์โทรและชื่อจริง) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการหลังบ้าน")
    df_b = get_data("Bookings")
    df_u = get_data("Users")
    
    if not df_b.empty:
        # รวมข้อมูลเพื่อดึงชื่อจริงและเบอร์โทรมาแสดงเฉพาะหน้า Admin
        df_admin = pd.merge(df_b, df_u[['username', 'fullname', 'phone']], on='username', how='left')
        
        # หัวตาราง
        h = st.columns([1, 1.5, 1.2, 1.5, 1, 1, 1.2, 0.6])
        header_labels = ["เวลา", "ชื่อลูกค้า", "เบอร์โทร", "บริการ", "วันที่", "สถานะ", "การยืนยัน", "ลบ"]
        for i, label in enumerate(header_labels): h[i].write(f"**{label}**")
        
        for _, row in df_admin.sort_values(['date','time'], ascending=[False, True]).iterrows():
            r = st.columns([1, 1.5, 1.2, 1.5, 1, 1, 1.2, 0.6])
            r[0].write(row['time'])
            r[1].write(row['fullname']) # แสดงชื่อจริง
            r[2].write(row['phone'])    # แสดงเบอร์โทร (เฉพาะ Admin เห็น)
            r[3].write(row['service'])
            r[4].write(row['date'])
            r[5].write("🔵 รอ" if row['status'] == 'รอรับบริการ' else "✅ เสร็จ")
            
            if row['status'] == 'รอรับบริการ':
                if r[6].button("เสร็จสิ้น", key=f"d_{row['id']}"):
                    df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                    conn.update(worksheet="Bookings", data=df_b)
                    st.rerun()
            else: r[6].write("-")
            
            if r[7].button("🗑️", key=f"del_{row['id']}"):
                df_b = df_b[df_b['id'] != row['id']]
                conn.update(worksheet="Bookings", data=df_b)
                st.rerun()

# --- 3. หน้าสมัครสมาชิก (บังคับใส่เบอร์โทร) ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg_form"):
        nu = st.text_input("Username (ใช้เข้าสู่ระบบ)")
        np = st.text_input("Password", type="password")
        nf = st.text_input("ชื่อ - นามสกุล")
        nt = st.text_input("เบอร์โทรศัพท์ (จำเป็นต้องใส่)")
        
        if st.form_submit_button("สมัครสมาชิก"):
            if not all([nu, np, nf, nt]):
                st.error("❌ กรุณากรอกข้อมูลให้ครบทุกช่อง")
            elif len(nt) < 9:
                st.error("❌ กรุณากรอกเบอร์โทรศัพท์ให้ถูกต้อง")
            else:
                df_u = get_data("Users")
                if nu in df_u['username'].values:
                    st.error("❌ ชื่อผู้ใช้นี้ถูกใช้งานแล้ว")
                else:
                    new_user = pd.DataFrame([{"username": nu, "password": np, "fullname": nf, "phone": nt, "role": "user"}])
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_user], ignore_index=True))
                    st.success("✅ สมัครสำเร็จ! กรุณาไปที่หน้า 'เข้าสู่ระบบ'")

# --- 4. หน้าจองคิวลูกค้า (ไม่แสดงเบอร์โทร) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.username}")
    t1, t2 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง"])
    
    with t1:
        svc = st.selectbox("เลือกบริการ", list(SERVICES_BASE_PRICE.keys()))
        d = st.date_input("วันที่จอง")
        t = st.selectbox("เลือกเวลา", TIME_SLOTS)
        
        if d.weekday() == 2: st.warning("⚠️ ร้านหยุดทุกวันพุธ")
        else:
            if st.button("ยืนยันการจองคิว"):
                df_b = get_data("Bookings")
                # เช็คคิวชนเฉพาะคิวที่สถานะ 'รอรับบริการ'
                is_taken = df_b[(df_b['date'] == str(d)) & (df_b['time'] == t) & (df_b['status'] == 'รอรับบริการ')]
                if not is_taken.empty:
                    st.error("❌ เวลานี้มีคนจองแล้ว")
                else:
                    new_id = str(int(datetime.now().timestamp()))
                    new_row = pd.DataFrame([{"id": new_id, "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "price": str(SERVICES_BASE_PRICE[svc]), "status": "รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_row], ignore_index=True))
                    st.success("✅ จองคิวสำเร็จ!")
                    st.rerun()
    with t2:
        df_b = get_data("Bookings")
        my_q = df_b[df_b['username'] == st.session_state.username]
        st.write("**รายการจองของคุณ (เฉพาะคิวที่ยังไม่ถูกลบ)**")
        h_q = st.columns([2, 2, 2, 1])
        for i, txt in enumerate(["บริการ/เวลา", "วันที่", "สถานะ", "จัดการ"]): h_q[i].write(f"**{txt}**")
        
        for _, row in my_q.iterrows():
            r_q = st.columns([2, 2, 2, 1])
            r_q[0].write(f"{row['service']} ({row['time']})")
            r_q[1].write(row['date'])
            r_q[2].write(row['status'])
            if r_q[3].button("ยกเลิก", key=f"c_{row['id']}"):
                df_b = df_b[df_b['id'] != row['id']]
                conn.update(worksheet="Bookings", data=df_b)
                st.rerun()

# --- 5. หน้าเข้าสู่ระบบ ---
elif st.session_state.page == "Login":
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("ตกลง"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            check = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not check.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u})
                navigate("Booking")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

# --- 6. หน้าดูคิวว่างวันนี้ ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิวที่จองไว้แล้ววันนี้")
    df_b = get_data("Bookings")
    today = str(datetime.now().date())
    active_q = df_b[(df_b['date'] == today) & (df_b['status'] == 'รอรับบริการ')]
    if active_q.empty:
        st.write("ยังไม่มีการจองในวันนี้ สามารถจองได้เลย!")
    else:
        st.dataframe(active_q[['time', 'service']].sort_values('time'), use_container_width=True)
