import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold;}
        .price-card {
            background-color: #ffffff !important; padding: 15px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 10px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #000000 !important;
        }
        .price-card b { color: #000000 !important; display: block; font-size: 1.1rem; }
        .price-text { color: #FF4B4B !important; font-weight: bold; }
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
        df = conn.read(worksheet=sheet_name, ttl="0s")
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
            if 'phone' in col or 'username' in col:
                df[col] = df[col].apply(lambda x: '0' + x if len(x) == 9 and x.isdigit() else x)
        return df
    except:
        return pd.DataFrame()

# --- 2. NAVIGATION ---
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
        lbl = "📊 จัดการ" if role == 'admin' else "✂️ จองคิว"
        if st.button(lbl): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]:
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")

st.divider()

# --- 3. PAGE LOGIC ---

# --- หน้าแรก (Home) ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (หยุดทุกวันพุธ)")
    st.subheader("📋 รายการบริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"}
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span class="price-text">{price}</span></div>', unsafe_allow_html=True)
    st.divider()
    st.subheader("📞 ช่องทางการติดต่อ")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='contact-box'><h3>📞 โทร</h3><p>081-222-XXXX</p></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='contact-box'><h3>💬 Line</h3><p>@222salon</p></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='contact-box'><h3>📍 ที่ตั้ง</h3><p>ย่านสุขุมวิท กทม.</p></div>", unsafe_allow_html=True)
    st.write("")
    st.link_button("📍 นำทางด้วย Google Maps (GPS)", "https://goo.gl/maps/xxx", type="primary", use_container_width=True)

# --- หน้า Login ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์").strip()
    p_in = st.text_input("รหัสผ่าน", type="password").strip()
    if st.button("Login", type="primary"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'Admin'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)]
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': user.iloc[0]['role'], 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

# --- หน้าจองคิว & Messenger (ลูกค้า) ---
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 Messenger"])
    
    with t1: # ส่วนของการจองคิวที่เพิ่มกลับมา
        st.subheader("📅 จองคิวบริการ")
        with st.form("booking_form"):
            b_date = st.date_input("เลือกวันที่")
            b_time = st.selectbox("เลือกเวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            b_service = st.selectbox("เลือกบริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยันการจอง"):
                df_b = get_data("Bookings")
                new_b = pd.DataFrame([{"username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(b_date), "time": b_time, "service": b_service, "status": "รอรับบริการ"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_b], ignore_index=True))
                st.success("จองคิวสำเร็จ!")

    with t2:
        df_b = get_data("Bookings")
        st.dataframe(df_b[df_b['username'] == st.session_state.username])

    with t3: # Messenger
        st.subheader("💬 Messenger")
        df_m = get_data("Messages")
        chat_box = st.container(height=300, border=True)
        with chat_box:
            my_msgs = df_m[df_m['username'] == st.session_state.username]
            for _, m in my_msgs.iterrows():
                with st.chat_message("user"):
                    st.write(m['message'])
                    if m['admin_reply']: st.info(f"Admin: {m['admin_reply']}")
        with st.form("send_msg", clear_on_submit=True):
            m_text = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง"):
                new_m = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "message": m_text, "timestamp": datetime.now().strftime("%H:%M"), "admin_reply": ""}])
                conn.update(worksheet="Messages", data=pd.concat([df_m, new_m], ignore_index=True))
                st.rerun()

# --- หน้า Admin ---
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2 = st.tabs(["📅 คิวลูกค้า", "📩 แชทลูกค้า"])
    with at1:
        st.dataframe(get_data("Bookings"), use_container_width=True)
    with at2:
        df_m = get_data("Messages")
        df_u = get_data("Users")
        user_map = dict(zip(df_u['phone'], df_u['fullname']))
        unique_users = [u for u in df_m['username'].unique() if u != 'Admin']
        options = {u: f"{user_map.get(u, 'ลูกค้าใหม่')} ({u})" for u in unique_users}
        if options:
            sel_u = st.selectbox("เลือกแชทลูกค้า:", options.keys(), format_func=lambda x: options[x])
            for _, m in df_m[df_m['username'] == sel_u].iterrows():
                st.write(f"👤 {m['message']}")
                if m['admin_reply']: st.write(f"🤖 {m['admin_reply']}")
            with st.form("rep"):
                ans = st.text_input("ตอบกลับ:")
                if st.form_submit_button("ส่ง"):
                    idx = df_m[df_m['username'] == sel_u].index[-1]
                    df_m.at[idx, 'admin_reply'] = ans
                    conn.update(worksheet="Messages", data=df_m); st.rerun()

# --- หน้า ViewQueues (สำหรับบุคคลทั่วไป) ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_b = get_data("Bookings")
    st.table(df_b[df_b['date'] == datetime.now().strftime("%Y-%m-%d")][['time', 'service']])

# --- หน้า Register ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nu, np, nf = st.text_input("เบอร์โทร"), st.text_input("รหัสผ่าน"), st.text_input("ชื่อ-นามสกุล")
        if st.form_submit_button("ยืนยัน"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
            st.success("สมัครสำเร็จ!"); navigate("Login")
