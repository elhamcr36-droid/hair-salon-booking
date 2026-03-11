import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS (หน้าตาสวยงาม ตัวหนังสือดำชัดเจน) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}
        
        /* สไตล์การ์ดราคาหน้าแรก */
        .price-card {
            background-color: #ffffff !important; padding: 15px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 10px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #000000 !important;
        }
        .price-card b { color: #000000 !important; display: block; font-size: 1.1rem; }
        .price-text { color: #FF4B4B !important; font-weight: bold; }
        
        /* กล่องติดต่อหน้าแรก */
        .contact-box {
            text-align: center; background-color: #ffffff !important; padding: 20px; 
            border-radius: 15px; box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #000000 !important;
            border: 1px solid #eee; height: 100%;
        }
        
        /* รายการคิว Admin */
        .booking-item {
            background-color: #ffffff; color: #000000; padding: 15px;
            border-radius: 10px; margin-bottom: 10px; border: 1px solid #ddd;
        }
    </style>
""", unsafe_allow_html=True)

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl="0s")
        df = df.dropna(how='all')
        # ล้างชื่อหัวตารางให้เป็นตัวเล็กและไม่มีช่องว่าง
        df.columns = [str(c).strip().lower() for c in df.columns]
        # แปลงข้อมูลทุกช่องให้เป็นข้อความ (String) ป้องกันปัญหาเลข 0 หาย หรือมีจุดทศนิยม .0
        for col in df.columns:
            df[col] = df[col].astype(str).replace(r'\.0$', '', regex=True).replace('nan', '')
        return df
    except:
        return pd.DataFrame()

# --- 2. NAVIGATION & SESSION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)

# แถบเมนูหลักด้านบน
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
    services = {
        "✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", 
        "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", 
        "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"
    }
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
    st.link_button("📍 นำทางไปที่ร้าน (Google Maps)", "https://goo.gl/maps/example", type="primary", use_container_width=True)

# --- หน้า Login (แก้บัคเปรียบเทียบเบอร์โทร) ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    with st.container(border=True):
        u_in = st.text_input("เบอร์โทรศัพท์", placeholder="กรอกเบอร์ที่ใช้สมัคร").strip()
        p_in = st.text_input("รหัสผ่าน", type="password").strip()
        
        if st.button("Login", type="primary"):
            if u_in == "admin222" and p_in == "222":
                st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'Admin'})
                navigate("Admin")
            else:
                df_u = get_data("Users")
                if not df_u.empty:
                    # ค้นหาโดยเช็คค่าแบบ String (ป้องกันเลข 0 หาย)
                    user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)]
                    if not user.empty:
                        st.session_state.update({
                            'logged_in': True, 
                            'user_role': user.iloc[0]['role'], 
                            'username': u_in, 
                            'fullname': user.iloc[0]['fullname']
                        })
                        navigate("Booking")
                    else: st.error("❌ เบอร์โทรหรือรหัสผ่านไม่ถูกต้อง")
                else: st.error("ไม่พบข้อมูลในระบบ")

# --- หน้าสมัครสมาชิก ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg"):
        nu, np, nf = st.text_input("เบอร์โทรศัพท์"), st.text_input("รหัสผ่าน"), st.text_input("ชื่อ-นามสกุล")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            new_data = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_data], ignore_index=True))
            st.success("สมัครสำเร็จ!"); navigate("Login")

# --- หน้า Booking & Messenger (ลูกค้า) ---
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 Messenger"])
    
    with t1:
        with st.form("bk"):
            svc = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม"])
            d = st.date_input("วันที่", min_value=datetime.now().date())
            t = st.selectbox("เวลา", ["09:30", "10:30", "13:00", "15:00", "17:00"])
            if st.form_submit_button("ยืนยันการจอง"):
                df_b = get_data("Bookings")
                new_q = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "status": "รอรับบริการ"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True)); st.success("จองสำเร็จ!"); st.rerun()

    with t3:
        st.subheader("💬 ห้องแชทส่วนตัว (แก้ไข/ลบได้)")
        df_m = get_data("Messages")
        chat_box = st.container(height=400, border=True)
        with chat_box:
            msgs = df_m[df_m['username'] == st.session_state.username].sort_values('id')
            for _, m in msgs.iterrows():
                cm, ce, cd = st.columns([4, 0.6, 0.6])
                with cm:
                    with st.chat_message("user"):
                        st.write(m['message'])
                        st.caption(f"🕒 {m['timestamp']} {m.get('status','')}")
                if ce.button("✏️", key=f"e_{m['id']}"):
                    new_txt = st.text_input("แก้ไข:", value=m['message'], key=f"in_{m['id']}")
                    if st.button("บันทึก", key=f"sv_{m['id']}"):
                        df_m.loc[df_m['id'] == m['id'], 'message'] = new_txt
                        df_m.loc[df_m['id'] == m['id'], 'status'] = "(แก้ไขแล้ว)"
                        conn.update(worksheet="Messages", data=df_m); st.rerun()
                if cd.button("🗑️", key=f"d_{m['id']}"):
                    df_m = df_m[df_m['id'] != m['id']]
                    conn.update(worksheet="Messages", data=df_m); st.rerun()
                if m['admin_reply']:
                    with st.chat_message("assistant", avatar="✂️"): st.write(m['admin_reply'])

        with st.form("send", clear_on_submit=True):
            m_in = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง"):
                new_m = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "message": m_in, "timestamp": datetime.now().strftime("%H:%M"), "status": "", "admin_reply": ""}])
                conn.update(worksheet="Messages", data=pd.concat([df_m, new_m], ignore_index=True)); st.rerun()

# --- หน้า Admin (จัดการคิว & ตอบแชท) ---
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2 = st.tabs(["📅 คิววันนี้", "📩 แชทลูกค้า"])
    with at1:
        df_b = get_data("Bookings")
        pending = df_b[df_b['status'].isin(['รอรับบริการ', ''])]
        for _, row in pending.iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"<div class='booking-item'><b>คุณ {row['username']}</b><br>{row['date']} {row['time']} | {row['service']}</div>", unsafe_allow_html=True)
            if c2.button("✅ เสร็จ", key=f"ok_{row['id']}"):
                df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                conn.update(worksheet="Bookings", data=df_b); st.rerun()
            if c3.button("🗑️ ลบ", key=f"del_{row['id']}"):
                df_b = df_b[df_b['id'] != row['id']]
                conn.update(worksheet="Bookings", data=df_b); st.rerun()

    with at2:
        df_m = get_data("Messages")
        u_list = df_m['username'].unique()
        if len(u_list) > 0:
            sel_u = st.selectbox("เลือกห้องแชท:", u_list)
            for _, m in df_m[df_m['username'] == sel_u].iterrows():
                with st.chat_message("user"): st.write(m['message'])
                if m['admin_reply']:
                    with st.chat_message("assistant", avatar="✂️"): st.write(m['admin_reply'])
            with st.form("admin_rep"):
                ans = st.text_input("ตอบกลับลูกค้า:")
                if st.form_submit_button("ส่งคำตอบ"):
                    df_m.loc[df_m[df_m['username'] == sel_u].index[-1], 'admin_reply'] = ans
                    conn.update(worksheet="Messages", data=df_m); st.rerun()

# --- หน้า ViewQueues ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_b = get_data("Bookings")
    active = df_b[(df_b['date'] == datetime.now().strftime("%Y-%m-%d"))]
    st.table(active[['time', 'service']]) if not active.empty else st.write("ยังไม่มีคิว")
