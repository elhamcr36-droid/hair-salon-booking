import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import streamlit.components.v1 as components

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon-Final", layout="wide", initial_sidebar_state="collapsed")

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
        .price-text { float: right; color: #FF4B4B; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl="0s")
        if df is None or df.empty: return pd.DataFrame()
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
            if 'phone' in col or 'username' in col:
                df[col] = df[col].apply(lambda x: '0' + x if len(x) == 9 and x.isdigit() else x)
        return df
    except: return pd.DataFrame()

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

# --- 3. PAGE LOGIC ---

if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")
    
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"}
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span class="price-text">{price}</span></div>', unsafe_allow_html=True)

    st.divider()
    c1, c2 = st.columns([1, 1])
    
    # ส่วนติดต่อเรา (คอลัมน์ซ้าย)
    with c1:
        st.subheader("📞 ติดต่อเรา")
        st.write("📱 **เบอร์โทร:** 081-222-2222")
        st.write("💬 **LINE ID:** @222salon")
        st.write("🔵 **Facebook:** 222 Salon")
    
    # ส่วนพิกัดร้าน (คอลัมน์ขวา - แก้ไขย่อหน้าและปุ่มลิงก์)
    with c2:
        st.subheader("📍 พิกัดร้าน")
        # ลิงก์ปักหมุดตรง 222 Tesaban 1 Alley, บ่อยาง, สงขลา
        maps_link = "https://www.google.com/maps/search/?api=1&query=7.191512,100.596200"
        
        # รูปภาพประกอบหน้าพิกัด
        st.image("https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f?w=400")
        
        # ปุ่มกดเปิดแผนที่นำทาง
        st.markdown(f'''
            <a href="{maps_link}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #FF4B4B; color: white; padding: 15px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 16px; box-shadow: 2px 4px 8px rgba(0,0,0,0.2);">
                    🚀 กดเปิด Google Maps (นำทางมาที่ร้าน)
                </div>
            </a>
            <p style="text-align: center; font-size: 13px; color: gray; margin-top: 8px;">
                🏠 222 ถนนเทศบาล 1 ต.บ่อยาง อ.เมืองสงขลา
            </p>
        ''', unsafe_allow_html=True)

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg_form"):
        nf, nu, np, npc = st.text_input("ชื่อ-นามสกุล"), st.text_input("เบอร์โทรศัพท์"), st.text_input("รหัสผ่าน", type="password"), st.text_input("ยืนยันรหัสผ่าน", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            if nu and np == npc and nf:
                df_u = get_data("Users")
                if not df_u.empty and nu in df_u['phone'].values: st.error("❌ เบอร์นี้ถูกใช้งานแล้ว")
                else:
                    new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                    st.success("✅ สำเร็จ!"); navigate("Login")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

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
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)] if not df_u.empty else pd.DataFrame()
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิวของฉัน", "💬 แชทกับร้าน"])
    with t1:
        with st.form("b_form"):
            b_d = st.date_input("เลือกวันที่", min_value=datetime.now().date())
            b_t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            b_s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยัน"):
                if b_d.weekday() == 5: 
                    st.error("❌ ร้านหยุดวันเสาร์ กรุณาเลือกวันอื่นครับ")
                else:
                    df_all = get_data("Bookings")
                    is_time_taken = df_all[(df_all['date'] == str(b_d)) & (df_all['time'] == b_t) & (df_all['status'] != 'ยกเลิก')] if not df_all.empty else pd.DataFrame()
                    if not is_time_taken.empty: st.error(f"❌ เวลา {b_t} มีผู้จองแล้วครับ")
                    else:
                        new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(b_d), "time": b_t, "service": b_s, "status": "รอรับบริการ", "price": "0"}])
                        conn.update(worksheet="Bookings", data=pd.concat([df_all, new_q], ignore_index=True))
                        st.success("✅ จองสำเร็จ!"); st.balloons()
    with t2:
        df_history = get_data("Bookings")
        if not df_history.empty:
            my_qs = df_history[df_history['username'] == st.session_state.username]
            for _, r in my_qs.iterrows():
                with st.container(border=True):
                    st.write(f"📅 {r['date']} | ⏰ {r['time']} | {r['service']} | **{r['status']}**")
    with t3:
        st.info("ระบบแชทกำลังเชื่อมต่อ...")

elif st.session_state.page == "Admin" and st.session_state.user_role == 'admin':
    st.subheader("📅 จัดการคิวลูกค้า")
    df_admin = get_data("Bookings")
    if not df_admin.empty:
        active_qs = df_admin[df_admin['status'] == "รอรับบริการ"]
        st.dataframe(active_qs)

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิววันนี้")
    df_today = get_data("Bookings")
    today_str = datetime.now().strftime("%Y-%m-%d")
    if not df_today.empty:
        active = df_today[(df_today['date'] == today_str) & (df_today['status'] == "รอรับบริการ")]
        if not active.empty: st.table(active[['time', 'service', 'fullname']].sort_values('time'))
        else: st.info("ไม่มีการจองในวันนี้")
