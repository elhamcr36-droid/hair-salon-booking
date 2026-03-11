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
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; height: 3.2em; transition: 0.2s;}
        .stButton>button:hover {border: 2px solid #FF4B4B; color: #FF4B4B;}
        .price-card {
            background-color: #ffffff !important; padding: 18px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 12px;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.08); color: #000000 !important;
        }
        .price-card b { color: #000000 !important; display: block; font-size: 1.15rem; margin-bottom: 5px;}
        .price-text { color: #FF4B4B !important; font-weight: bold; font-size: 1.1rem;}
        .status-badge { padding: 4px 10px; border-radius: 15px; font-size: 0.85rem; font-weight: bold; background: #eee; }
    </style>
""", unsafe_allow_html=True)

# เชื่อมต่อ Google Sheets
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

# แถบเมนูหลัก (Top Navigation)
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

# --- หน้าแรก (Home) ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ เปิดบริการ: 09:30 - 19:30 น. (หยุดทุกวันพุธ)")
    
    st.subheader("📋 รายการบริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"}
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span class="price-text">{price}</span></div>', unsafe_allow_html=True)
    
    st.write("")
    st.link_button("📍 นำทางด้วย Google Maps (GPS)", "https://goo.gl/maps/xxx", type="primary", use_container_width=True)

# --- หน้า Login ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์ (Admin ใช้ admin222)").strip()
    p_in = st.text_input("รหัสผ่าน", type="password").strip()
    
    if st.button("ตกลง", type="primary"):
        # กรณี Admin
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'Admin', 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            # กรณีลูกค้า
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)]
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else:
                st.error("❌ ข้อมูลไม่ถูกต้อง ตรวจสอบเบอร์โทรหรือรหัสผ่าน")

# --- หน้าจองคิว & Messenger (ลูกค้า) ---
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติคิวของคุณ", "💬 แชทกับร้าน"])
    
    with t1:
        st.subheader("📅 เลือกวันและเวลา")
        with st.form("booking_form", clear_on_submit=True):
            b_date = st.date_input("เลือกวันที่")
            b_time = st.selectbox("เลือกเวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            b_service = st.selectbox("เลือกบริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            
            if st.form_submit_button("ยืนยันการจอง"):
                df_b = get_data("Bookings")
                # เช็ค 1 คน/1 คิว/วัน
                user_daily = df_b[(df_b['username'] == st.session_state.username) & (df_b['date'] == str(b_date))]
                # เช็ค เต็ม 2 คนต่อ slot
                slot_usage = len(df_b[(df_b['date'] == str(b_date)) & (df_b['time'] == b_time)])
                
                if not user_daily.empty:
                    st.error(f"⚠️ คุณมีคิวในวันที่ {b_date} แล้ว (จองได้วันละ 1 คิว) หากต้องการเปลี่ยนเวลา กรุณายกเลิกคิวเดิมก่อน")
                elif slot_usage >= 2:
                    st.error(f"⚠️ เวลา {b_time} ของวันที่ {b_date} เต็มแล้ว กรุณาเลือกเวลาอื่น")
                else:
                    new_q = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(b_date), "time": b_time, "service": b_service, "status": "รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                    st.success("✅ จองสำเร็จ!")
                    st.rerun()

    with t2:
        st.subheader("📋 รายการจองของคุณ")
        df_b = get_data("Bookings")
        my_q = df_b[df_b['username'] == st.session_state.username]
        if my_q.empty: st.write("ยังไม่มีประวัติการจอง")
        else:
            for _, row in my_q.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1.2])
                    c1.write(f"**{row['service']}**")
                    c1.write(f"📅 {row['date']} | ⏰ {row['time']} | <span class='status-badge'>{row['status']}</span>", unsafe_allow_html=True)
                    if c2.button("❌ ยกเลิกคิว", key=f"del_{row['id']}"):
                        df_b = df_b[df_b['id'] != row['id']]
                        conn.update(worksheet="Bookings", data=df_b)
                        st.toast("ยกเลิกคิวเรียบร้อย")
                        st.rerun()

    with t3:
        df_m = get_data("Messages")
        chat_box = st.container(height=350, border=True)
        with chat_box:
            my_msgs = df_m[df_m['username'] == st.session_state.username]
            for _, m in my_msgs.iterrows():
                with st.chat_message("user"):
                    st.write(m['message'])
                    if m.get('admin_reply'): st.info(f"Admin: {m['admin_reply']}")
        with st.form("msg_send", clear_on_submit=True):
            m_text = st.text_input("พิมพ์ข้อความแจ้งร้าน...")
            if st.form_submit_button("ส่งข้อความ"):
                new_m = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "message": m_text, "timestamp": datetime.now().strftime("%H:%M"), "admin_reply": ""}])
                conn.update(worksheet="Messages", data=pd.concat([df_m, new_m], ignore_index=True))
                st.rerun()

# --- หน้า Admin (Backend) ---
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2 = st.tabs(["📅 จัดการคิว", "📩 ตอบแชทลูกค้า"])
    with at1:
        st.subheader("📊 รายการคิวทั้งหมด")
        st.dataframe(get_data("Bookings"), use_container_width=True)
    with at2:
        df_m = get_data("Messages"); df_u = get_data("Users")
        user_map = dict(zip(df_u['phone'], df_u['fullname']))
        unique_users = [u for u in df_m['username'].unique() if u != 'Admin']
        options = {u: f"{user_map.get(u, 'ลูกค้าใหม่')} ({u})" for u in unique_users}
        if options:
            sel_u = st.selectbox("เลือกแชทลูกค้า:", options.keys(), format_func=lambda x: options[x])
            for _, m in df_m[df_m['username'] == sel_u].iterrows():
                st.write(f"👤 {m['message']}")
                if m.get('admin_reply'): st.write(f"🤖 Admin: {m['admin_reply']}")
            with st.form("admin_rep"):
                ans = st.text_input("พิมพ์คำตอบ:")
                if st.form_submit_button("ส่งคำตอบ"):
                    idx = df_m[df_m['username'] == sel_u].index[-1]
                    df_m.at[idx, 'admin_reply'] = ans
                    conn.update(worksheet="Messages", data=df_m); st.rerun()

# --- หน้า ViewQueues (Public) ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิวที่จองแล้ววันนี้")
    df_b = get_data("Bookings")
    active = df_b[df_b['date'] == datetime.now().strftime("%Y-%m-%d")]
    if not active.empty:
        st.table(active[['time', 'service', 'fullname']])
    else:
        st.write("ยังไม่มีการจองในวันนี้")

# --- หน้า Register ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg_form"):
        nu, np, nf = st.text_input("เบอร์โทรศัพท์"), st.text_input("รหัสผ่าน"), st.text_input("ชื่อ-นามสกุล")
        if st.form_submit_button("ลงทะเบียน"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
            st.success("สมัครสำเร็จ! กรุณาเข้าสู่ระบบ"); navigate("Login")
