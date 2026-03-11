import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon-Final-Fix", layout="wide", initial_sidebar_state="collapsed")

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

# --- 2. DATABASE CONNECTION & CACHE CLEARING ---
# ใช้คำสั่งเชื่อมต่อแบบระบุพารามิเตอร์เพื่อความเสถียร
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        # บังคับล้าง Cache ทุกครั้งที่เรียกใช้ เพื่อให้ข้อมูลล่าสุดจาก Sheets ปรากฏทันที
        df = conn.read(worksheet=sheet_name, ttl=0) 
        if df is None or df.empty: return pd.DataFrame()
        
        # ล้างช่องว่างที่หัวคอลัมน์และแปลงเป็นตัวพิมพ์เล็ก
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # ล้างข้อมูลในตาราง: ลบแถวที่ว่างเปล่าทั้งหมด
        df = df.dropna(how='all')
        
        # ฟังก์ชันพิเศษ: แปลงทุกอย่างให้เป็นข้อความที่ "สะอาด" (ไม่มี .0 และไม่มีช่องว่าง)
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

# เมนูหลัก
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
            # บังคับล้าง Cache การเชื่อมต่อเมื่อ Logout
            st.cache_data.clear()
            navigate("Home")
st.divider()

# --- 4. PAGE LOGIC ---

# --- หน้าเข้าสู่ระบบ (LOGIN) - แก้ไขรอบที่ 4 ---
if st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    # ใช้คีย์เฉพาะเพื่อป้องกัน Streamlit จำค่า Input ผิดพลาด
    u_input = st.text_input("เบอร์โทรศัพท์", key="login_u").strip()
    p_input = st.text_input("รหัสผ่าน", type="password", key="login_p").strip()
    
    if st.button("ตกลง", type="primary"):
        # 1. ตรวจสอบ Admin แบบ Hard-coded
        if u_input == "admin222" and p_input == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': u_input, 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            # 2. ตรวจสอบจาก Sheets ด้วยโหมดความปลอดภัยสูง
            df_u = get_data("Users")
            if not df_u.empty:
                # ตรวจสอบคอลัมน์ที่จำเป็น
                if 'phone' in df_u.columns and 'password' in df_u.columns:
                    # ค้นหาแบบ Case-insensitive และล้างค่าแปลกปลอม
                    user_match = df_u[(df_u['phone'] == u_input) & (df_u['password'] == p_input)]
                    
                    if not user_match.empty:
                        user_data = user_match.iloc[0]
                        st.session_state.update({
                            'logged_in': True, 
                            'user_role': user_data.get('role', 'user'), 
                            'username': u_input, 
                            'fullname': user_data.get('fullname', 'ลูกค้า')
                        })
                        st.success("สำเร็จ!")
                        navigate("Booking")
                    else:
                        st.error("❌ ข้อมูลไม่ถูกต้อง: โปรดเช็คเบอร์และรหัสผ่าน [รหัสแก้ไข-04]")
                        # แสดงปุ่มช่วยล้างระบบหากยังไม่ได้
                        if st.button("🔄 รีเฟรชระบบเชื่อมต่อ"):
                            st.cache_data.clear()
                            st.rerun()
                else:
                    st.error("หัวข้อคอลัมน์ใน Google Sheets ไม่ถูกต้อง (ต้องมี phone และ password)")
            else:
                st.error("ไม่สามารถดึงข้อมูลผู้ใช้งานได้")

# --- หน้าจัดการร้าน (ADMIN) - รวมฟีเจอร์ติดต่อลูกค้า ---
elif st.session_state.page == "Admin" and st.session_state.user_role == 'admin':
    st.subheader("📊 จัดการร้าน (Admin)")
    df_bookings = get_data("Bookings")
    
    if not df_bookings.empty:
        with st.expander("✅ บันทึกราคาและสถานะ", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1: sel_id = st.selectbox("เลือก ID คิว", df_bookings['id'].tolist())
            with c2: in_price = st.text_input("ราคา (บาท)", "0")
            with c3: in_status = st.selectbox("สถานะ", ["รอรับบริการ", "กำลังบริการ", "เสร็จสิ้น", "ยกเลิก"])
            if st.button("💾 บันทึกข้อมูล"):
                df_bookings.loc[df_bookings['id'] == sel_id, ['price', 'status']] = [in_price, in_status]
                conn.update(worksheet="Bookings", data=df_bookings)
                st.success("อัปเดตแล้ว!")
                st.rerun()

        st.divider()
        st.write("### 📝 รายการจองทั้งหมด")
        # แสดงปุ่มติดต่อลูกค้าทันที
        df_bookings['📞 โทร'] = "tel:" + df_bookings['username']
        df_bookings['💬 LINE'] = "https://line.me/ti/p/~" + df_bookings['username']
        
        st.dataframe(
            df_bookings[['id', 'fullname', 'date', 'time', 'service', 'status', 'price', '📞 โทร', '💬 LINE']],
            column_config={
                "📞 โทร": st.column_config.LinkColumn("โทรหา"),
                "💬 LINE": st.column_config.LinkColumn("ทัก LINE")
            },
            use_container_width=True, hide_index=True
        )
    else: st.info("ยังไม่มีข้อมูลการจอง")

# --- ส่วนอื่นๆ (สมัครสมาชิก/จองคิว/หน้าแรก) คงเดิมแต่ปรับปรุงความเสถียร ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        f_name = st.text_input("ชื่อ-นามสกุล")
        f_phone = st.text_input("เบอร์โทรศัพท์")
        f_pass = st.text_input("รหัสผ่าน", type="password")
        f_conf = st.text_input("ยืนยันรหัสผ่าน", type="password")
        if st.form_submit_button("สมัครสมาชิก"):
            if f_pass != f_conf: st.error("รหัสผ่านไม่ตรงกัน")
            elif not f_name or not f_phone: st.error("กรุณากรอกข้อมูลให้ครบ")
            else:
                df_u = get_data("Users")
                new_data = pd.DataFrame([{"phone": f_phone, "password": f_pass, "fullname": f_name, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_data], ignore_index=True))
                st.cache_data.clear() # ล้าง Cache ทันทีหลังสมัคร
                st.success("สมัครสำเร็จ! กรุณาล็อกอิน")
                navigate("Login")

elif st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("📍 222 ถนนเทศบาล 1 (ตำบลบ่อยาง)")
    st.markdown(f'<a href="https://www.google.com/maps/place/222+Tesaban+1+Alley,+Tambon+Bo+Yang,+Amphoe+Mueang+Songkhla,+Chang+Wat+Songkhla+900000" target="_blank" class="nav-button">🚩 เปิดแผนที่ร้าน</a>', unsafe_allow_html=True)

elif st.session_state.page == "Booking":
    st.subheader(f"✂️ จองคิว: คุณ {st.session_state.fullname}")
    with st.form("book"):
        d = st.date_input("วันที่", min_value=datetime.now().date())
        t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
        s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
        if st.form_submit_button("ยืนยัน"):
            df_b = get_data("Bookings")
            new_b = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(d), "time": t, "service": s, "status": "รอรับบริการ", "price": "0"}])
            conn.update(worksheet="Bookings", data=pd.concat([df_b, new_b], ignore_index=True))
            st.success("จองแล้ว!"); navigate("Home")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_q = get_data("Bookings")
    if not df_q.empty:
        today = datetime.now().strftime("%Y-%m-%d")
        st.table(df_q[df_q['date'] == today][['time', 'fullname', 'service']].sort_values('time'))
