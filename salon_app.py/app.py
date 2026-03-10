import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Barber & Salon Online", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        .price-card {
            background-color: #ffffff; padding: 20px; border-radius: 15px;
            border-left: 8px solid #FF4B4B; margin-bottom: 15px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
        .service-name { font-weight: bold; font-size: 18px; color: #333; }
        .price-range { color: #FF4B4B; font-size: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- ข้อมูลบริการและราคา ---
SERVICES_DISPLAY = {
    "✂️ ตัดผมชาย (Men's Haircut)": "150 - 350",
    "💇‍♀️ ตัดผมหญิง (Women's Haircut)": "350 - 800",
    "🚿 สระ-ไดร์ (Wash & Blow Dry)": "200 - 450",
    "🎨 ทำสีผม (Hair Color)": "1,500 - 4,500",
    "✨ ยืดผมวอลลุ่ม (Magic Volume)": "2,000 - 5,500",
    "🌀 ดัดผมดิจิตอล (Digital Perm)": "2,500 - 6,000",
    "🌿 เคราตินทรีทเม้นท์ (Keratin)": "1,500 - 3,500",
    "❄️ สปาหนังศีรษะ (Scalp Spa)": "500 - 1,200",
    "💅 ทำสีเล็บเจล (Gel Nails)": "300 - 800",
    "💄 แต่งหน้าทำผม (Makeup & Hair)": "1,500 - 3,500"
}

SERVICES_BASE_PRICE = {
    "ตัดผมชาย": 150, "ตัดผมหญิง": 350, "สระ-ไดร์": 200, 
    "ทำสีผม": 1500, "ยืดผมวอลลุ่ม": 2000, "ดัดผมดิจิตอล": 2500,
    "เคราตินทรีทเม้นท์": 1500, "สปาหนังศีรษะ": 500, "สีเล็บเจล": 300, "แต่งหน้าทำผม": 1500
}

# สร้างรายการเวลาจอง 09:30 - 19:30 (ทุก 30 นาที)
TIME_SLOTS = []
for h in range(9, 20):
    for m in ["00", "30"]:
        t = f"{h:02d}:{m}"
        if t >= "09:30" and t <= "19:30":
            TIME_SLOTS.append(t)

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df.columns = [str(c).strip() for c in df.columns]
        def clean_val(v):
            v = str(v).strip()
            if v.endswith('.0'): v = v[:-2]
            return v
        return df.fillna("").map(clean_val)
    except:
        return pd.DataFrame()

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
        if st.button("🔑 เข้าสู่ระบบ"): navigate("Login")
else:
    role = st.session_state.get('user_role')
    target = "Admin" if role == 'admin' else "Booking"
    btn_label = "📊 หลังบ้าน" if role == 'admin' else "✂️ จองคิว"
    with c3: 
        if st.button(btn_label): navigate(target)
    with c5: 
        if st.button("🚪 ออก"):
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 1. หน้าแรก ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ เวลาเปิดร้าน: 09:30 - 19:30 น. (หยุดทุกวันพุธ)")
    st.markdown("<h2 style='text-align: center;'>💰 อัตราค่าบริการ</h2>", unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)
    items = list(SERVICES_DISPLAY.items())
    for i, (name, price) in enumerate(items):
        target_col = p_col1 if i % 2 == 0 else p_col2
        with target_col:
            st.markdown(f'<div class="price-card"><div class="service-name">{name}</div><div class="price-range">{price} บาท</div></div>', unsafe_allow_html=True)

# --- 2. หน้าคิวว่าง ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิวที่กำลังรอรับบริการวันนี้")
    df_b = get_data("Bookings")
    if not df_b.empty:
        today = str(datetime.now().date())
        active_q = df_b[(df_b['date'] == today) & (df_b['status'] == 'รอรับบริการ')]
        if not active_q.empty:
            st.dataframe(active_q[['time', 'service']].sort_values('time'), use_container_width=True)
        else: st.success("ยังไม่มีคิวจองที่รอดำเนินการ")

# --- 3. หน้า Login / 4. หน้าสมัคร ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u = st.text_input("Username").strip()
    p = st.text_input("Password", type="password").strip()
    if st.button("ตกลง"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            check = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not check.empty:
                st.session_state.update({'logged_in':True, 'user_role':check.iloc[0]['role'], 'username':u})
                navigate("Admin" if check.iloc[0]['role'] == 'admin' else "Booking")
            else: st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg"):
        nu, np, nt = st.text_input("ชื่อผู้ใช้"), st.text_input("รหัสผ่าน", type="password"), st.text_input("เบอร์โทร")
        if st.form_submit_button("สมัครสมาชิก"):
            df_u = get_data("Users")
            if nu.strip() in df_u['username'].values: st.error("ชื่อนี้มีคนใช้แล้ว")
            else:
                new_u = pd.DataFrame([{"username":nu.strip(), "password":np.strip(), "phone":nt.strip(), "role":"user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                st.success("สมัครสำเร็จ!")

# --- 5. หน้าจองคิว (เพิ่มกฎปิดวันพุธ และเวลาเปิด-ปิด) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.username}")
    tab1, tab2 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติของฉัน"])
    with tab1:
        svc = st.selectbox("เลือกบริการ", list(SERVICES_BASE_PRICE.keys()))
        d = st.date_input("เลือกวันที่จอง")
        t = st.selectbox("เลือกเวลา (09:30 - 19:30)", TIME_SLOTS)
        
        # เช็ควันพุธ (Weekday 2 คือวันพุธใน Python)
        if d.weekday() == 2:
            st.warning("⚠️ ร้านหยุดทุกวันพุธ กรุณาเลือกวันอื่นครับ")
        else:
            if st.button("ยืนยันจองคิว"):
                df_b = get_data("Bookings")
                # เช็คคิวชนเฉพาะคิวที่ยัง "รอรับบริการ"
                is_taken = df_b[(df_b['date'] == str(d)) & (df_b['time'] == t) & (df_b['status'] == 'รอรับบริการ')]
                
                if not is_taken.empty:
                    st.error("❌ เวลานี้มีคนจองแล้ว กรุณาเปลี่ยนเวลาใหม่")
                else:
                    new_b = pd.DataFrame([{"id": str(len(df_b)+1), "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "price": str(SERVICES_BASE_PRICE[svc]), "status": "รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_b], ignore_index=True))
                    st.success("จองสำเร็จ! เจอกันที่ร้านนะครับ")
                    st.balloons()
    with tab2:
        df_b = get_data("Bookings")
        my_q = df_b[df_b['username'] == st.session_state.username]
        st.dataframe(my_q[['id', 'service', 'date', 'time', 'status']], use_container_width=True)
        cid = st.text_input("ระบุ ID เพื่อยกเลิก")
        if st.button("❌ ยกเลิกคิว"):
            if cid in my_q['id'].values:
                df_b.loc[df_b['id'] == cid, 'status'] = 'ยกเลิกโดยลูกค้า'
                conn.update(worksheet="Bookings", data=df_b)
                st.rerun()

# --- 6. หน้า Admin ---
elif st.session_state.page == "Admin":
    st.subheader("📊 จัดการร้าน (Admin)")
    df_b = get_data("Bookings")
    if not df_b.empty:
        df_b['price'] = pd.to_numeric(df_b['price'], errors='coerce').fillna(0)
        active = df_b[~df_b['status'].str.contains("ยกเลิก", na=False)]
        today = str(datetime.now().date())
        m1, m2 = st.columns(2)
        m1.metric("คิวรอวันนี้", len(active[(active['date']==today) & (active['status']=='รอรับบริการ')]))
        m2.metric("ยอดขายวันนี้", f"{active[active['date']==today]['price'].sum():,.0f} บ.")
        
    st.dataframe(df_b, use_container_width=True)
    tid = st.text_input("ใส่ ID งาน")
    ca, cb = st.columns(2)
    if ca.button("✅ ยืนยันเสร็จสิ้น"):
        df_b.loc[df_b['id'] == tid, 'status'] = 'เสร็จสิ้น'
        conn.update(worksheet="Bookings", data=df_b)
        st.rerun()
    if cb.button("🗑️ ลบข้อมูล"):
        df_b = df_b[df_b['id'] != tid]
        conn.update(worksheet="Bookings", data=df_b)
        st.rerun()
