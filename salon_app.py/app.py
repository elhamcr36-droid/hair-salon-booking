import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon-Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; height: 3.2em; transition: 0.3s;}
        .price-card {
            background-color: #ffffff !important; padding: 18px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 12px;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.08); color: #000000 !important;
        }
        .price-card b { color: #000000 !important; display: block; font-size: 1.1rem;}
        .price-text { color: #FF4B4B !important; font-weight: bold;}
        .contact-box {
            text-align: center; background-color: #ffffff !important; padding: 20px; 
            border-radius: 15px; box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #000000 !important;
            border: 1px solid #eee; height: 100%;
        }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        # ดึงข้อมูลจาก Sheets แบบ Real-time
        df = conn.read(worksheet=sheet_name, ttl="0s")
        if df is None or df.empty:
            return pd.DataFrame()
        
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        for col in df.columns:
            # แปลงข้อมูลเป็น String และจัดการเลข .0 ที่อาจเกิดจาก Format ของ Sheets
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
            
            # แก้ปัญหาเบอร์โทรเลข 0 หาย (ถ้ามี 9 หลัก ให้เติม 0 ข้างหน้า)
            if 'phone' in col or 'username' in col:
                df[col] = df[col].apply(lambda x: '0' + x if len(x) == 9 and x.isdigit() else x)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# --- 2. SESSION & NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)

m_cols = st.columns(5)
with m_cols[0]:
    if st.button("🏠 หน้าแรก"): navigate("Home")
with m_cols[1]:
    if st.button("📅 คิววันนี้"): navigate("ViewQueues")

if not st.session_state.logged_in:
    with m_cols[3]: 
        if st.button("📝 สมัคร"): navigate("Register")
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

# --- 3. PAGE LOGIC ---

# --- HOME PAGE ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (หยุดทุกวันพุธ)")
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"}
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span class="price-text">{price}</span></div>', unsafe_allow_html=True)
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='contact-box'><h3>📞 โทร</h3><p>081-222-2222</p></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='contact-box'><h3>💬 Line</h3><p>@222salon</p></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='contact-box'><h3>📍 ที่ตั้ง</h3><p>222 ซอย.พิรม สงขลา.</p></div>", unsafe_allow_html=True)

# --- LOGIN PAGE ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์").strip()
    p_in = st.text_input("รหัสผ่าน", type="password").strip()
    
    if st.button("ตกลง", type="primary"):
        # แอดมินล็อกอินแบบ Hardcode (ใช้เบอร์พิเศษ หรือกำหนดในระบบ)
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'admin222', 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            if not df_u.empty:
                # ตรวจสอบเบอร์และรหัส
                user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)]
                if not user.empty:
                    st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                    navigate("Booking")
                else: 
                    st.error("❌ เบอร์โทรศัพท์หรือรหัสผ่านไม่ถูกต้อง")
            else: 
                st.error("❌ ไม่พบข้อมูลผู้ใช้งานในระบบ")

# --- REGISTER PAGE ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg_form"):
        nf = st.text_input("ชื่อ-นามสกุล")
        nu = st.text_input("เบอร์โทรศัพท์")
        np = st.text_input("รหัสผ่าน", type="password")
        np_confirm = st.text_input("ยืนยันรหัสผ่าน", type="password")
        
        if st.form_submit_button("ลงทะเบียน"):
            if not (nu and np and nf and np_confirm):
                st.warning("⚠️ กรุณากรอกข้อมูลให้ครบทุกช่อง")
            elif np != np_confirm:
                st.error("❌ รหัสผ่านไม่ตรงกัน")
            else:
                df_u = get_data("Users")
                if not df_u.empty and nu in df_u['phone'].values:
                    st.error("❌ เบอร์โทรศัพท์นี้มีในระบบแล้ว")
                else:
                    new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                    st.success("✅ สมัครสมาชิกสำเร็จ!"); navigate("Login")

# --- USER BOOKING PAGE ---
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิว"])
    with t1:
        with st.form("booking_form"):
            b_date = st.date_input("เลือกวันที่")
            b_time = st.selectbox("เลือกเวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            b_service = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยันการจอง"):
                df_b = get_data("Bookings")
                new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(b_date), "time": b_time, "service": b_service, "status": "รอรับบริการ", "price": "0"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                st.success("✅ จองคิวสำเร็จ!"); st.rerun()
    with t2:
        df_b = get_data("Bookings")
        if not df_b.empty:
            my_qs = df_b[df_b['username'] == st.session_state.username]
            if not my_qs.empty:
                for _, row in my_qs.iterrows():
                    with st.container(border=True):
                        st.write(f"**{row['service']}** | 📅 {row['date']} ⏰ {row['time']}")
                        st.write(f"สถานะ: `{row['status']}`" + (f" | ราคา: **{row['price']} บ.**" if row['status'] == "เสร็จสิ้น" else ""))
            else: st.write("คุณยังไม่มีประวัติการจอง")

# --- ADMIN PAGE ---
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    df_b = get_data("Bookings")
    
    # --- 📊 สรุปยอดขาย (Dashboard) ---
    if not df_b.empty:
        # ป้องกัน Error หากคอลัมน์ price ไม่มี
        if 'price' not in df_b.columns: df_b['price'] = "0"
        df_b['price'] = pd.to_numeric(df_b['price'], errors='coerce').fillna(0)
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        done_today = df_b[(df_b['status'] == "เสร็จสิ้น") & (df_b['date'] == today_str)]
        done_all = df_b[df_b['status'] == "เสร็จสิ้น"]
        
        st.subheader("📊 รายงานยอดขาย")
        c1, c2, c3 = st.columns(3)
        c1.metric("เสร็จสิ้นวันนี้", f"{len(done_today)} คิว")
        c2.metric("รายได้วันนี้", f"{done_today['price'].sum():,.0f} บ.")
        c3.metric("รายได้รวมทั้งหมด", f"{done_all['price'].sum():,.0f} บ.")
        st.divider()

    st.subheader("📅 จัดการคิวลูกค้า")
    if not df_b.empty:
        # เรียงคิว ล่าสุดขึ้นก่อน
        df_view = df_b.sort_values(['date', 'time'], ascending=[False, True])
        for _, row in df_view.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 **{row['fullname']}** ({row['username']})")
                col1.write(f"✂️ {row['service']} | 📅 {row['date']} ⏰ {row['time']}")
                col1.write(f"สถานะปัจจุบัน: `{row['status']}`")
                
                if row['status'] == "รอรับบริการ":
                    with col2.popover("✅ จบงาน"):
                        p_in = st.number_input("ยอดเงินที่ชำระ (บาท)", min_value=0, step=50, key=f"p_{row['id']}")
                        if st.button("ยืนยันบันทึกยอด", key=f"b_{row['id']}"):
                            df_b.loc[df_b['id'] == row['id'], 'status'] = "เสร็จสิ้น"
                            df_b.loc[df_b['id'] == row['id'], 'price'] = str(p_in)
                            conn.update(worksheet="Bookings", data=df_b)
                            st.success("บันทึกยอดสำเร็จ!"); st.rerun()
                    if col2.button("❌ ยกเลิก", key=f"can_{row['id']}"):
                        df_b.loc[df_b['id'] == row['id'], 'status'] = "ยกเลิก"
                        conn.update(worksheet="Bookings", data=df_b)
                        st.rerun()

# --- VIEW QUEUES (PUBLIC) ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิววันนี้")
    df_b = get_data("Bookings")
    today = datetime.now().strftime("%Y-%m-%d")
    if not df_b.empty:
        active = df_b[(df_b['date'] == today) & (df_b['status'] == "รอรับบริการ")]
        if not active.empty:
            st.dataframe(active[['time', 'service', 'fullname']].sort_values('time'), use_container_width=True, hide_index=True)
        else: st.info("วันนี้ยังไม่มีคิวที่กำลังรอรับบริการ")
    else: st.write("ยังไม่มีข้อมูลการจองในระบบ")
