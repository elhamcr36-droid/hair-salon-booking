import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon-Ultimate-Final", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; height: 3.2em;}
        .price-card {
            background-color: #ffffff !important; padding: 18px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 12px; color: #000000 !important;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.08);
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        # ดึงข้อมูลสดใหม่เสมอเพื่อป้องกัน Cache ค้าง
        df = conn.read(worksheet=sheet_name, ttl="0s")
        if df is None or df.empty: return pd.DataFrame()
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        # ทำความสะอาดข้อมูลเบื้องต้น: ลบช่องว่างส่วนเกินในทุก Cell
        df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)
        return df
    except Exception as e:
        return pd.DataFrame()

# --- 3. SESSION & NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)

# แถบเมนูหลัก
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
            navigate("Home")
st.divider()

# --- 4. PAGE LOGIC ---

# --- หน้าเข้าสู่ระบบ (LOGIN) - ปรับปรุงการเทียบข้อมูลให้แม่นยำที่สุด ---
if st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_input = st.text_input("เบอร์โทรศัพท์", placeholder="เช่น 0817354210").strip()
    p_input = st.text_input("รหัสผ่าน", type="password").strip()
    
    if st.button("ตกลง", type="primary"):
        # เช็ค Admin
        if u_input == "admin222" and p_input == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': u_input, 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            if not df_u.empty:
                # แปลงทุกอย่างเป็น String และจัดการฟอร์แมตตัวเลขจาก Sheets
                df_u['phone'] = df_u['phone'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                df_u['password'] = df_u['password'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                
                # ตรวจสอบการจับคู่
                match = df_u[(df_u['phone'] == u_input) & (df_u['password'] == p_input)]
                
                if not match.empty:
                    user_info = match.iloc[0]
                    st.session_state.update({
                        'logged_in': True, 
                        'user_role': user_info['role'], 
                        'username': u_input, 
                        'fullname': user_info['fullname']
                    })
                    st.success(f"เข้าสู่ระบบสำเร็จ! ยินดีต้อนรับคุณ {user_info['fullname']}")
                    navigate("Booking")
                else:
                    st.error("❌ เบอร์โทรหรือรหัสผ่านไม่ถูกต้อง [รหัส 03]")
            else:
                st.error("ไม่พบฐานข้อมูลผู้ใช้งาน")

# --- หน้าสมัครสมาชิก (REGISTER) ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg_form"):
        nf = st.text_input("ชื่อ-นามสกุล")
        nu = st.text_input("เบอร์โทรศัพท์")
        np = st.text_input("รหัสผ่าน", type="password")
        npc = st.text_input("ยืนยันรหัสผ่าน", type="password")
        
        if st.form_submit_button("ลงทะเบียน"):
            if not nf or not nu or not np:
                st.error("กรุณากรอกข้อมูลให้ครบทุกช่อง")
            elif np != npc:
                st.error("❌ รหัสผ่านไม่ตรงกัน")
            else:
                df_u = get_data("Users")
                new_u = pd.DataFrame([{"phone": str(nu).strip(), "password": str(np).strip(), "fullname": nf, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                st.success("✅ ลงทะเบียนสำเร็จ!")
                navigate("Login")

# --- หน้าจัดการร้าน (ADMIN) ---
elif st.session_state.page == "Admin" and st.session_state.user_role == 'admin':
    st.subheader("📊 จัดการร้าน (Admin)")
    df_bookings = get_data("Bookings")
    
    if not df_bookings.empty:
        with st.expander("✅ บันทึกราคาและสถานะ"):
            col1, col2, col3 = st.columns(3)
            with col1:
                sel_id = st.selectbox("เลือก ID คิว", df_bookings['id'].tolist())
            with col2:
                in_price = st.text_input("ค่าบริการ (บาท)", "0")
            with col3:
                in_status = st.selectbox("สถานะ", ["รอรับบริการ", "กำลังบริการ", "เสร็จสิ้น", "ยกเลิก"])
            
            if st.button("💾 บันทึก"):
                df_bookings.loc[df_bookings['id'] == sel_id, ['price', 'status']] = [in_price, in_status]
                conn.update(worksheet="Bookings", data=df_bookings)
                st.success("อัปเดตข้อมูลแล้ว")
                st.rerun()

        st.divider()
        st.write("### 📋 รายการจอง")
        df_display = df_bookings.copy()
        # ทำความสะอาดเบอร์โทรสำหรับปุ่มติดต่อลูกค้า
        df_display['phone_clean'] = df_display['username'].astype(str).str.replace(r'\.0$', '', regex=True)
        df_display['📞 โทร'] = "tel:" + df_display['phone_clean']
        df_display['💬 LINE'] = "https://line.me/ti/p/~" + df_display['phone_clean']
        
        st.dataframe(
            df_display[['id', 'fullname', 'date', 'time', 'service', 'status', 'price', '📞 โทร', '💬 LINE']],
            column_config={
                "📞 โทร": st.column_config.LinkColumn(),
                "💬 LINE": st.column_config.LinkColumn()
            },
            use_container_width=True, hide_index=True
        )
    else: st.info("ยังไม่มีข้อมูลการจอง")

# --- หน้าแรก และ หน้าจองคิว ---
elif st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("📍 พิกัด: 222 ถนนเทศบาล 1 (ตำบลบ่อยาง)")
    st.markdown(f'<a href="http://googleusercontent.com/maps.google.com/9" target="_blank" class="nav-button">🚩 เปิดแผนที่ร้าน</a>', unsafe_allow_html=True)

elif st.session_state.page == "Booking":
    st.subheader(f"✂️ จองคิว: คุณ {st.session_state.fullname}")
    with st.form("b_form"):
        b_d = st.date_input("เลือกวันที่", min_value=datetime.now().date())
        b_t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
        b_s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
        if st.form_submit_button("ยืนยันการจอง"):
            df_all = get_data("Bookings")
            new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(b_d), "time": b_t, "service": b_s, "status": "รอรับบริการ", "price": "0"}])
            conn.update(worksheet="Bookings", data=pd.concat([df_all, new_q], ignore_index=True))
            st.success("จองสำเร็จ!"); navigate("Home")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_q = get_data("Bookings")
    if not df_q.empty:
        today = datetime.now().strftime("%Y-%m-%d")
        st.table(df_q[df_q['date'] == today][['time', 'fullname', 'service']].sort_values('time'))
    else: st.info("ไม่มีคิวในวันนี้")
