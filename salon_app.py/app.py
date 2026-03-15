import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon-Total", layout="wide", initial_sidebar_state="collapsed")

# CSS สำหรับ Messenger Style และส่วนติดต่อให้ตัวหนังสือสีดำชัดเจน
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 20px; font-weight: bold; height: 3.2em;}
        .price-card {
            background-color: #ffffff !important; padding: 18px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 12px;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.08); color: #000000 !important;
        }
        .contact-section-black { 
            background-color: #ffffff; padding: 30px; border-radius: 15px; text-align: center; 
            box-shadow: 0px 4px 15px rgba(0,0,0,0.1); border: 1px solid #eeeeee;
            color: #000000 !important;
        }
        /* บังคับสีใน Chat Message ให้เป็นสีดำ */
        [data-testid="stChatMessage"] { color: #000000 !important; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    st.cache_data.clear() 
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df is None or df.empty: return pd.DataFrame()
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace('nan', '')
        return df
    except:
        return pd.DataFrame()

# --- 2. NAVIGATION LOGIC ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon @สงขลา</h1>", unsafe_allow_html=True)

# แถบเมนูหลัก (Navbar)
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
    if st.session_state.get('user_role') == 'admin':
        with m_cols[2]:
            if st.button("📊 จัดการร้าน"): navigate("Admin")
    else:
        with m_cols[2]:
            if st.button("💬 แชท/จองคิว"): navigate("Booking")
    with m_cols[4]:
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")
st.divider()

# --- 3. PAGE LOGIC ---

# 🏠 หน้าแรก
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"}
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span style="float:right; color:#FF4B4B;">{price}</span></div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("""
        <div class="contact-section-black">
            <h3>📞 ติดต่อเรา & พิกัดร้าน</h3>
            <p>📱 <b>เบอร์โทรศัพท์:</b> 081-222-2222 | 💬 <b>LINE:</b> @222salon</p>
            <p>📍 ต.บ่อยาง อ.เมืองสงขลา จ.สงขลา (ใกล้เทศบาล 1)</p>
        </div>
    """, unsafe_allow_html=True)

# 📅 ดูคิวรวมวันนี้
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิวรอรับบริการวันนี้")
    df_q = get_data("Bookings")
    today = datetime.now().strftime("%Y-%m-%d")
    if not df_q.empty:
        today_qs = df_q[(df_q['date'] == today) & (df_q['status'] == "รอรับบริการ")].sort_values('time')
        if not today_qs.empty:
            st.table(today_qs[['time', 'service', 'fullname']])
        else: st.info("ยังไม่มีคิวจองในวันนี้")
    else: st.info("ไม่มีข้อมูล")

# 📝 สมัครสมาชิก
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg"):
        nf, nu, np = st.text_input("ชื่อ-นามสกุล"), st.text_input("เบอร์โทรศัพท์"), st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ตกลง"):
            df_u = get_data("Users")
            if not df_u.empty and nu in df_u['phone'].values: st.error("❌ เบอร์โทรนี้สมัครแล้ว")
            else:
                new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                st.success("สมัครสำเร็จ!"); time.sleep(1); navigate("Login")

# 🔑 เข้าสู่ระบบ
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in, p_in = st.text_input("เบอร์โทรศัพท์"), st.text_input("รหัสผ่าน", type="password")
    if st.button("ตกลง"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': u_in, 'fullname': 'Admin'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)] if not df_u.empty else pd.DataFrame()
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("❌ เบอร์โทรหรือรหัสผ่านไม่ถูกต้อง")

# 💬 หน้าลูกค้า (Messenger Style)
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิว", "💬 Messenger"])
    
    with t1:
        with st.form("b_form"):
            b_d = st.date_input("วันที่", min_value=datetime.now().date())
            b_t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"])
            b_s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยันการจอง"):
                df_all = get_data("Bookings")
                new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(b_d), "time": b_t, "service": b_s, "status": "รอรับบริการ", "price": "0"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_all, new_q], ignore_index=True))
                st.success("จองสำเร็จ!"); time.sleep(1); st.rerun()

    with t2:
        df_h = get_data("Bookings")
        if not df_h.empty:
            my = df_h[df_h['username'] == st.session_state.username].iloc[::-1]
            for _, r in my.iterrows():
                with st.container(border=True):
                    st.write(f"📅 {r['date']} | ⏰ {r['time']} | **{r['service']}** | สถานะ: {r['status']}")
                    if r['status'] == "รอรับบริการ":
                        if st.button("❌ ยกเลิก", key=r['id']):
                            df_h.loc[df_h['id'] == r['id'], 'status'] = "ยกเลิกโดยลูกค้า"
                            conn.update(worksheet="Bookings", data=df_h); st.rerun()

    with t3:
        st.subheader("💬 สนทนากับร้าน")
        df_msg = get_data("Messages")
        chat_box = st.container(height=450)
        with chat_box:
            if not df_msg.empty:
                my_m = df_msg[df_msg['username'] == st.session_state.username]
                for _, m in my_m.iterrows():
                    with st.chat_message("user"):
                        st.write(m['message'])
                    if m.get('admin_reply'):
                        with st.chat_message("assistant", avatar="✂️"):
                            st.write(m['admin_reply'])
        
        if prompt := st.chat_input("ถามร้านค้าที่นี่..."):
            new_m = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "message": prompt, "timestamp": datetime.now().strftime("%d/%m %H:%M"), "admin_reply": ""}])
            conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m], ignore_index=True))
            st.rerun()

# 📊 หน้าแอดมิน (Messenger Reply Style)
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2, at3 = st.tabs(["📊 สรุปยอด", "📅 จัดการคิว", "📩 ตอบแชท"])
    
    with at2:
        df_adm_q = get_data("Bookings")
        wait = df_adm_q[df_adm_q['status'] == "รอรับบริการ"] if not df_adm_q.empty else pd.DataFrame()
        for _, r in wait.iterrows():
            with st.container(border=True):
                st.write(f"👤 {r['fullname']} | ⏰ {r['time']} | {r['date']}")
                pr = st.number_input("ยอดเงิน", min_value=0, key=f"p{r['id']}")
                c1, c2 = st.columns(2)
                if c1.button("✅ เสร็จสิ้น", key=f"ok{r['id']}"):
                    df_adm_q.loc[df_adm_q['id'] == r['id'], ['status', 'price']] = ["เสร็จสิ้น", str(pr)]
                    conn.update(worksheet="Bookings", data=df_adm_q); st.rerun()
                if c2.button("❌ ยกเลิก", key=f"no{r['id']}"):
                    df_adm_q.loc[df_adm_q['id'] == r['id'], 'status'] = "ยกเลิกโดยร้าน"
                    conn.update(worksheet="Bookings", data=df_adm_q); st.rerun()

    with at3:
        st.subheader("📩 จัดการข้อความลูกค้า")
        df_adm_msg = get_data("Messages")
        if not df_adm_msg.empty:
            users_in_chat = df_adm_msg['username'].unique()
            for user_phone in users_in_chat:
                with st.expander(f"💬 แชทจาก: {user_phone}"):
                    user_history = df_adm_msg[df_adm_msg['username'] == user_phone]
                    for idx, msg in user_history.iterrows():
                        st.write(f"**ลูกค้า:** {msg['message']}")
                        if msg['admin_reply']:
                            st.info(f"**แอดมิน:** {msg['admin_reply']}")
                        else:
                            with st.form(key=f"rep_{msg['id']}", clear_on_submit=True):
                                ans = st.text_input("พิมพ์คำตอบ...")
                                if st.form_submit_button("ส่งคำตอบ"):
                                    df_adm_msg.at[idx, 'admin_reply'] = ans
                                    conn.update(worksheet="Messages", data=df_adm_msg)
                                    st.success("ส่งข้อความแล้ว!"); time.sleep(0.5); st.rerun()
