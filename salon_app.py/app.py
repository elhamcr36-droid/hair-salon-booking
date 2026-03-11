import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS (เน้นอ่านง่าย สบายตา) ---
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
        }
    </style>
""", unsafe_allow_html=True)

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl="0s")
        df = df.dropna(how='all')
        # ล้างหัวตารางให้เป็นตัวเล็กและตัดช่องว่าง
        df.columns = [str(c).strip().lower() for c in df.columns]
        # แปลงข้อมูลทุกช่องให้เป็น String และจัดการเลข 0 ที่อาจหายไป
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

# เมนูหลัก
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
        if st.button("🚪 ออก"):
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
    st.subheader("📞 ติดต่อเรา")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='contact-box'><h3>📞 โทร</h3><p>081-222-XXXX</p></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='contact-box'><h3>💬 Line</h3><p>@222salon</p></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='contact-box'><h3>📍 ที่ตั้ง</h3><p>ย่านสุขุมวิท กทม.</p></div>", unsafe_allow_html=True)

# --- หน้า Login (Fix บัคข้อมูล) ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    with st.container(border=True):
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
                    st.session_state.update({
                        'logged_in': True, 'user_role': user.iloc[0]['role'], 
                        'username': u_in, 'fullname': user.iloc[0]['fullname']
                    })
                    navigate("Booking")
                else:
                    st.error("❌ ไม่พบข้อมูล (ตรวจสอบเบอร์โทรและรหัสผ่าน)")

# --- หน้าสมัครสมาชิก ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nu, np, nf = st.text_input("เบอร์โทร"), st.text_input("รหัสผ่าน"), st.text_input("ชื่อ-นามสกุล")
        if st.form_submit_button("ยืนยัน"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
            st.success("สมัครสำเร็จ!"); navigate("Login")

# --- หน้า Booking & Messenger (สำคัญ: แก้ไขการแสดงผลข้อความ) ---
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 Messenger"])
    
    with t3:
        st.subheader("💬 ห้องแชทส่วนตัว")
        df_m = get_data("Messages")
        
        chat_box = st.container(height=400, border=True)
        with chat_box:
            # กรองข้อความของคนนั้นโดยเฉพาะ
            my_msgs = df_m[df_m['username'] == st.session_state.username]
            if my_msgs.empty:
                st.write("ยังไม่มีข้อความ... เริ่มคุยกับเราได้ที่นี่")
            else:
                for _, m in my_msgs.iterrows():
                    # แสดงข้อความลูกค้า
                    col_msg, col_act = st.columns([5, 1])
                    with col_msg:
                        with st.chat_message("user"):
                            st.write(m['message'])
                            st.caption(f"🕒 {m['timestamp']} {m.get('status', '')}")
                    # ปุ่มลบข้อความ
                    if col_act.button("🗑️", key=f"del_{m['id']}"):
                        df_m = df_m[df_m['id'] != m['id']]
                        conn.update(worksheet="Messages", data=df_m)
                        st.rerun()
                    # แสดงคำตอบจากแอดมิน
                    if m.get('admin_reply'):
                        with st.chat_message("assistant", avatar="✂️"):
                            st.write(m['admin_reply'])

        with st.form("send_msg", clear_on_submit=True):
            m_input = st.text_input("พิมพ์ข้อความที่นี่...")
            if st.form_submit_button("ส่ง"):
                if m_input:
                    new_m = pd.DataFrame([{
                        "id": str(int(datetime.now().timestamp())),
                        "username": st.session_state.username,
                        "message": m_input,
                        "timestamp": datetime.now().strftime("%H:%M"),
                        "status": "", "admin_reply": ""
                    }])
                    conn.update(worksheet="Messages", data=pd.concat([df_m, new_m], ignore_index=True))
                    st.rerun()

# --- หน้า Admin ---
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    df_m = get_data("Messages")
    st.subheader("📩 จัดการแชทลูกค้า")
    users = df_m['username'].unique()
    if len(users) > 0:
        sel_u = st.selectbox("เลือกลูกค้า:", users)
        for _, m in df_m[df_m['username'] == sel_u].iterrows():
            st.info(f"ลูกค้า: {m['message']}")
            if m['admin_reply']: st.success(f"แอดมิน: {m['admin_reply']}")
        with st.form("reply"):
            ans = st.text_input("ตอบกลับ:")
            if st.form_submit_button("ส่ง"):
                df_m.loc[df_m[df_m['username'] == sel_u].index[-1], 'admin_reply'] = ans
                conn.update(worksheet="Messages", data=df_m); st.rerun()

# --- หน้า ViewQueues ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิวจองวันนี้")
    df_b = get_data("Bookings")
    st.table(df_b[df_b['date'] == datetime.now().strftime("%Y-%m-%d")][['time', 'service']])
