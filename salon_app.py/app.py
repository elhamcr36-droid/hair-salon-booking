import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon-Ultimate", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; height: 3.2em; transition: 0.3s;}
        .price-card {
            background-color: #ffffff !important; padding: 18px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 12px; color: #000000 !important;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.08);
        }
        .nav-button {
            display: block; background-color: #FF4B4B; color: white !important; 
            padding: 15px; border-radius: 12px; text-align: center; font-weight: bold;
            text-decoration: none; box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.3);
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION & DATA CLEANING ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        # ดึงข้อมูลแบบ Real-time (ttl=0)
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df is None or df.empty: return pd.DataFrame()
        
        # ล้างชื่อหัวคอลัมน์ให้สะอาด
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # ฟังก์ชันกำจัด .0 และช่องว่าง (แก้ปัญหา Login ไม่ได้)
        def clean_val(v):
            if pd.isna(v): return ""
            s = str(v).strip()
            if s.endswith('.0'): s = s[:-2]
            return s

        return df.applymap(clean_val)
    except:
        return pd.DataFrame()

# --- 3. SESSION & NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)

# เมนูบาร์
m_cols = st.columns(5)
with m_cols[0]:
    if st.button("🏠 หน้าแรก"): navigate("Home")
with m_cols[1]:
    if st.button("📅 คิววันนี้"): navigate("ViewQueues")

if not st.session_state.logged_in:
    with m_cols[3]: 
        if st.button("📝 สมัครสมาชิก"): navigate("Register")
    with m_cols[4]: 
        if st.button("🔑 เข้าสู่ระบบ"): navigate("Login")
else:
    role = st.session_state.get('user_role')
    with m_cols[2]:
        lbl = "📊 จัดการร้าน" if role == 'admin' else "✂️ จองคิว"
        if st.button(lbl): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]:
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            st.cache_data.clear()
            navigate("Home")
st.divider()

# --- 4. PAGE LOGIC ---

# --- หน้าแรก ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ เปิดบริการ 09:30 - 19:30 น. (หยุดทุกวันเสาร์)")
    
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+" }
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span style="float:right; color:#FF4B4B;">{price}</span></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("📍 พิกัดร้าน")
    st.write("222 ถนนเทศบาล 1 (ตำบลบ่อยาง) จังหวัดสงขลา")
    st.markdown(f'<a href="https://www.google.com/maps/place/222+Tesaban+1+Alley,+Tambon+Bo+Yang,+Amphoe+Mueang+Songkhla,+Chang+Wat+Songkhla+900000" target="_blank" class="nav-button">🚩 เปิด Google Maps</a>', unsafe_allow_html=True)

# --- หน้าสมัครสมาชิก (Register) ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg_form"):
        nf = st.text_input("ชื่อ-นามสกุล")
        nu = st.text_input("เบอร์โทรศัพท์ (ใช้เป็นชื่อล็อกอิน)")
        np = st.text_input("กำหนดรหัสผ่าน", type="password")
        npc = st.text_input("ยืนยันรหัสผ่านอีกครั้ง", type="password")
        
        if st.form_submit_button("ลงทะเบียน"):
            if not nf or not nu or not np:
                st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
            elif np != npc:
                st.error("❌ รหัสผ่านไม่ตรงกัน")
            else:
                df_u = get_data("Users")
                new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                st.success("✅ สมัครสำเร็จ! กรุณาล็อกอิน")
                navigate("Login")

# --- หน้าเข้าสู่ระบบ (Login) ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์").strip()
    p_in = st.text_input("รหัสผ่าน", type="password").strip()
    
    if st.button("ตกลง", type="primary"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': u_in, 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            if not df_u.empty:
                # เปรียบเทียบข้อมูลที่ถูกล้างค่าแปลกปลอมแล้ว
                match = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)]
                if not match.empty:
                    st.session_state.update({'logged_in': True, 'user_role': match.iloc[0]['role'], 'username': u_in, 'fullname': match.iloc[0]['fullname']})
                    navigate("Booking")
                else: st.error("❌ ข้อมูลไม่ถูกต้อง")

# --- หน้าจัดการร้าน (Admin) ---
elif st.session_state.page == "Admin" and st.session_state.user_role == 'admin':
    st.subheader("📊 จัดการร้าน (Admin)")
    df_b = get_data("Bookings")
    if not df_b.empty:
        with st.expander("✅ บันทึกราคาและสถานะ"):
            sid = st.selectbox("เลือก ID คิว", df_b['id'].tolist())
            prc = st.text_input("ค่าบริการ (บาท)", "0")
            sts = st.selectbox("สถานะ", ["รอรับบริการ", "กำลังบริการ", "เสร็จสิ้น", "ยกเลิก"])
            if st.button("💾 บันทึก"):
                df_b.loc[df_b['id'] == sid, ['price', 'status']] = [prc, sts]
                conn.update(worksheet="Bookings", data=df_b)
                st.success("บันทึกสำเร็จ!"); st.rerun()
        
        st.divider()
        # เพิ่มปุ่มติดต่อลูกค้า
        df_b['📞 โทร'] = "tel:" + df_b['username']
        df_b['💬 LINE'] = "https://line.me/ti/p/~" + df_b['username']
        
        st.dataframe(
            df_b[['id', 'fullname', 'date', 'time', 'service', 'status', 'price', '📞 โทร', '💬 LINE']],
            column_config={
                "📞 โทร": st.column_config.LinkColumn("โทรหา"),
                "💬 LINE": st.column_config.LinkColumn("ทัก LINE")
            },
            use_container_width=True, hide_index=True
        )
    else: st.info("ยังไม่มีข้อมูลการจอง")

# --- หน้าจองคิว (Booking) ---
elif st.session_state.page == "Booking":
    st.subheader(f"✂️ จองคิว: คุณ {st.session_state.fullname}")
    with st.form("book"):
        d = st.date_input("เลือกวันที่", min_value=datetime.now().date())
        t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
        s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
        if st.form_submit_button("ยืนยันการจอง"):
            df_all = get_data("Bookings")
            new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(d), "time": t, "service": s, "status": "รอรับบริการ", "price": "0"}])
            conn.update(worksheet="Bookings", data=pd.concat([df_all, new_q], ignore_index=True))
            st.success("จองเรียบร้อย!"); navigate("Home")

# --- หน้าคิววันนี้ (ViewQueues) ---
elif st.session_state.page == "ViewQueues":
    df_q = get_data("Bookings")
    if not df_q.empty:
        today = datetime.now().strftime("%Y-%m-%d")
        st.table(df_q[df_q['date'] == today][['time', 'fullname', 'service']].sort_values('time'))
    else: st.info("ไม่มีคิวในวันนี้")
