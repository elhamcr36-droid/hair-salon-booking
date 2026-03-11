import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

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

# --- หน้าแรก (Home) ---
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
    st.subheader("📞 ติดต่อเรา")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='contact-box'><h3>📞 โทร</h3><p>081-222-2222</p></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='contact-box'><h3>💬 Line</h3><p>@222salon</p></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='contact-box'><h3>📍 ที่ตั้ง</h3><p>222 ซอย.พิรม สงขลา.</p></div>", unsafe_allow_html=True)
    st.write("")
    st.link_button("📍 นำทางด้วย Google Maps (GPS)", "https://www.google.com/maps/place/222+%E0%B8%96%E0%B8%99%E0%B8%99+%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B8%9A%E0%B8%B2%E0%B8%A5+1+%E0%B8%95%E0%B8%B3%E0%B8%9A%E0%B8%A5%E0%B8%9A%E0%B9%88%E0%B8%AD%E0%B8%A2%E0%B8%B2%E0%B8%87+%E0%B8%AD%E0%B8%B3%E0%B9%80%E0%B8%A0%E0%B8%AD%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+90000/@7.1915128,100.5982223,17z/data=!3m1!4b1!4m6!3m5!1s0x304d3323c7ad029d:0x7cfb098f4f859e4c!8m2!3d7.1915128!4d100.6007972!16s%2Fg%2F11jylj3r6y?entry=ttu&g_ep=EgoyMDI2MDMwOC4wIKXMDSoASAFQAw%3D%3D", type="primary", use_container_width=True)

# --- หน้า Login ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์").strip()
    p_in = st.text_input("รหัสผ่าน", type="password").strip()
    if st.button("ตกลง", type="primary"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'Admin', 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)]
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

# --- หน้าจองคิว (ลูกค้า) ---
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิว", "💬 Messenger"])
    with t1:
        with st.form("booking_form"):
            b_date = st.date_input("เลือกวันที่")
            b_time = st.selectbox("เลือกเวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            b_service = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยัน"):
                df_b = get_data("Bookings")
                if not df_b[(df_b['username'] == st.session_state.username) & (df_b['date'] == str(b_date))].empty:
                    st.error("⚠️ คุณมีคิวในวันนี้แล้ว")
                elif len(df_b[(df_b['date'] == str(b_date)) & (df_b['time'] == b_time)]) >= 2:
                    st.error("⚠️ เวลานี้เต็มแล้ว (จำกัด 2 ท่าน)")
                else:
                    new_q = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(b_date), "time": b_time, "service": b_service, "status": "รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                    st.success("✅ จองสำเร็จ"); st.rerun()
    with t2:
        df_b = get_data("Bookings")
        for _, row in df_b[df_b['username'] == st.session_state.username].iterrows():
            with st.container(border=True):
                st.write(f"**{row['service']}** | 📅 {row['date']} ⏰ {row['time']} | สถานะ: `{row['status']}`")
                if row['status'] == "รอรับบริการ" and st.button("❌ ยกเลิก", key=f"u_del_{row['id']}"):
                    conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']]); st.rerun()
    with t3:
        df_m = get_data("Messages")
        chat_box = st.container(height=300, border=True)
        with chat_box:
            my_msgs = df_m[df_m['username'] == st.session_state.username]
            for _, m in my_msgs.iterrows():
                with st.chat_message("user"):
                    st.write(m['message'])
                    if m.get('admin_reply'): st.info(f"Admin: {m['admin_reply']}")
        with st.form("send", clear_on_submit=True):
            m_text = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง"):
                new_m = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "message": m_text, "timestamp": datetime.now().strftime("%H:%M"), "admin_reply": ""}])
                conn.update(worksheet="Messages", data=pd.concat([df_m, new_m], ignore_index=True)); st.rerun()

# --- หน้า Admin (จัดการสถานะคิว) ---
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2 = st.tabs(["📅 จัดการคิว", "📩 แชทลูกค้า"])
    with at1:
        st.subheader("📊 จัดการรายการคิว")
        df_b = get_data("Bookings")
        for _, row in df_b.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"👤 **{row['fullname']}** | {row['service']} | ⏰ {row['time']} ({row['date']})")
                c1.write(f"สถานะ: `{row['status']}`")
                if row['status'] == "รอรับบริการ":
                    if c2.button("✅ เสร็จสิ้น", key=f"done_{row['id']}"):
                        df_b.loc[df_b['id'] == row['id'], 'status'] = "รับบริการเสร็จสิ้น"
                        conn.update(worksheet="Bookings", data=df_b); st.rerun()
                    if c3.button("❌ ยกเลิก", key=f"adm_del_{row['id']}"):
                        df_b.loc[df_b['id'] == row['id'], 'status'] = "ถูกยกเลิกโดยร้าน"
                        conn.update(worksheet="Bookings", data=df_b); st.rerun()
    with at2:
        df_m = get_data("Messages"); df_u = get_data("Users")
        user_map = dict(zip(df_u['phone'], df_u['fullname']))
        unique_users = [u for u in df_m['username'].unique() if u != 'Admin']
        if unique_users:
            sel_u = st.selectbox("เลือกแชทลูกค้า:", unique_users, format_func=lambda x: f"{user_map.get(x, 'ลูกค้า')} ({x})")
            for _, m in df_m[df_m['username'] == sel_u].iterrows():
                st.write(f"👤 {m['message']}")
                if m.get('admin_reply'): st.info(f"🤖 Admin: {m['admin_reply']}")
            with st.form("admin_rep"):
                ans = st.text_input("ตอบกลับ:")
                if st.form_submit_button("ส่ง"):
                    idx = df_m[df_m['username'] == sel_u].index[-1]
                    df_m.at[idx, 'admin_reply'] = ans
                    conn.update(worksheet="Messages", data=df_m); st.rerun()

# --- หน้า ViewQueues (คิววันนี้) ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_b = get_data("Bookings")
    active = df_b[(df_b['date'] == datetime.now().strftime("%Y-%m-%d")) & (df_b['status'] == "รอรับบริการ")]
    if not active.empty:
        st.table(active[['time', 'service', 'fullname']])
    else:
        st.write("ยังไม่มีคิวจองสำหรับวันนี้")

# --- หน้า Register ---
elif st.session_state.page == "Register":
    with st.form("reg"):
        nu, np, nf = st.text_input("เบอร์โทร"), st.text_input("รหัสผ่าน"), st.text_input("ชื่อ-นามสกุล")
        if st.form_submit_button("ลงทะเบียน"):
            df_u = get_data("Users")
            conn.update(worksheet="Users", data=pd.concat([df_u, pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])], ignore_index=True))
            st.success("สมัครสำเร็จ!"); navigate("Login")
