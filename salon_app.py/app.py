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
        # ดึงข้อมูลแบบไม่มี Cache เพื่อให้ได้ข้อมูลล่าสุดเสมอ
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df is None or df.empty: return pd.DataFrame()
        
        # ปรับชื่อคอลัมน์ให้เป็นตัวพิมพ์เล็กและไม่มีช่องว่าง
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # ฟังก์ชันกำจัด .0 และช่องว่าง (แก้ปัญหา Login ล้มเหลว)
        def force_clean(val):
            if pd.isna(val): return ""
            s = str(val).strip()
            if s.endswith('.0'): s = s[:-2]
            return s

        return df.applymap(force_clean)
    except:
        return pd.DataFrame()

# --- 3. SESSION & NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)

# แถบเมนู
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
    st.write("📍 222 ถนนเทศบาล 1 (ตำบลบ่อยาง) จังหวัดสงขลา")
    st.markdown(f'<a href="https://www.google.com/maps/place/222+Tesaban+1+Alley,+Tambon+Bo+Yang,+Amphoe+Mueang+Songkhla,+Chang+Wat+Songkhla+900000" target="_blank" class="nav-button">🚩 นำทางด้วย Google Maps</a>', unsafe_allow_html=True)

# --- หน้าเข้าสู่ระบบ (Login) ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_input = st.text_input("เบอร์โทรศัพท์").strip()
    p_input = st.text_input("รหัสผ่าน", type="password").strip()
    
    if st.button("ตกลง", type="primary"):
        # ตรวจสอบ Admin แบบกำหนดเอง
        if u_input == "admin222" and p_input == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': u_input, 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            # ตรวจสอบจาก Sheets พร้อมล้างค่า .0
            df_u = get_data("Users")
            if not df_u.empty:
                match = df_u[(df_u['phone'] == u_input) & (df_u['password'] == p_input)]
                if not match.empty:
                    user_data = match.iloc[0]
                    st.session_state.update({
                        'logged_in': True, 
                        'user_role': user_data.get('role', 'user'), 
                        'username': u_input, 
                        'fullname': user_data.get('fullname', 'ลูกค้า')
                    })
                    st.success("สำเร็จ!")
                    navigate("Booking")
                else:
                    st.error("❌ ข้อมูลไม่ถูกต้อง โปรดตรวจสอบเบอร์โทรและรหัสผ่าน")
            else:
                st.error("ไม่สามารถโหลดข้อมูลผู้ใช้งานได้")

# --- หน้าจัดการร้าน (Admin) ---
elif st.session_state.page == "Admin" and st.session_state.user_role == 'admin':
    st.subheader("📊 จัดการร้าน (Admin)")
    df_b = get_data("Bookings")
    if not df_b.empty:
        with st.expander("✅ บันทึกราคาและสถานะ"):
            sid = st.selectbox("เลือก ID คิว", df_b['id'].tolist())
            prc = st.text_input("ราคา (บาท)", "0")
            sts = st.selectbox("สถานะ", ["รอรับบริการ", "กำลังบริการ", "เสร็จสิ้น", "ยกเลิก"])
            if st.button("💾 บันทึก"):
                df_b.loc[df_b['id'] == sid, ['price', 'status']] = [prc, sts]
                conn.update(worksheet="Bookings", data=df_b)
                st.success("บันทึกแล้ว!"); st.rerun()
        
        st.divider()
        # ปุ่มติดต่อลูกค้า
        df_b['📞 โทร'] = "tel:" + df_b['username']
        df_b['💬 LINE'] = "https://line.me/ti/p/~" + df_b['username']
        st.dataframe(
            df_b[['id', 'fullname', 'date', 'time', 'service', 'status', 'price', '📞 โทร', '💬 LINE']],
            column_config={
                "📞 โทร": st.column_config.LinkColumn("โทร"),
                "💬 LINE": st.column_config.LinkColumn("LINE")
            },
            use_container_width=True, hide_index=True
        )
    else: st.info("ยังไม่มีรายการจอง")

# --- หน้าสมัครสมาชิก ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        n = st.text_input("ชื่อ-นามสกุล")
        p = st.text_input("เบอร์โทรศัพท์")
        pw = st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"phone": p, "password": pw, "fullname": n, "role": "user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
            st.success("สมัครสำเร็จ! กรุณาล็อกอิน")
            navigate("Login")

# --- หน้าจองคิว ---
elif st.session_state.page == "Booking":
    st.subheader(f"✂️ จองคิว: คุณ {st.session_state.fullname}")
    with st.form("book"):
        d = st.date_input("วันที่", min_value=datetime.now().date())
        t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
        s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
        if st.form_submit_button("ยืนยันการจอง"):
            df_bk = get_data("Bookings")
            new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(d), "time": t, "service": s, "status": "รอรับบริการ", "price": "0"}])
            conn.update(worksheet="Bookings", data=pd.concat([df_bk, new_q], ignore_index=True))
            st.success("จองสำเร็จ!"); navigate("Home")

# --- หน้าคิววันนี้ ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิววันนี้")
    df_v = get_data("Bookings")
    if not df_v.empty:
        today = datetime.now().strftime("%Y-%m-%d")
        st.table(df_v[df_v['date'] == today][['time', 'fullname', 'service']].sort_values('time'))
    else: st.info("ไม่มีคิวในวันนี้")
