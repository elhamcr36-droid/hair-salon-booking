import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time
import hashlib
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon Songkhla", layout="wide", initial_sidebar_state="collapsed")

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; height: 3.2em; transition: 0.3s;}
        
        /* จุดแจ้งเตือนสีแดงกะพริบ */
        .nav-container { position: relative; width: 100%; }
        .badge {
            position: absolute; top: -5px; right: 5px;
            height: 14px; width: 14px;
            background-color: #FF0000; border-radius: 50%;
            border: 2px solid white; display: inline-block;
            z-index: 100; animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(255, 0, 0, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
        }

        .price-card {
            background-color: #ffffff !important; padding: 18px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 12px;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.08); color: #000000 !important;
        }
        .contact-section {
            background-color: #ffffff; padding: 25px; border-radius: 15px; 
            border: 1px solid #eee; text-align: center; color: #000; 
            box-shadow: 0px 4px 10px rgba(0,0,0,0.05); margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. DATA ENGINE ---
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df is None or df.empty: return pd.DataFrame()
        df.columns = [str(c).strip().lower() for c in df.columns]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
            if 'phone' in col or 'username' in col:
                df[col] = df[col].apply(lambda x: '0' + x if len(x) == 9 and x.isdigit() else x)
        return df
    except:
        return pd.DataFrame()

def check_notifications():
    """เช็คว่ามีคิวรอรับบริการ หรือแชทล่าสุดที่ลูกค้าส่งมาหรือไม่"""
    has_notif = False
    df_b = get_data("Bookings")
    if not df_b.empty and any(df_b['status'] == "รอรับบริการ"):
        has_notif = True
    df_c = get_data("Chats")
    if not df_c.empty and df_c.iloc[-1]['sender'] == "user":
        has_notif = True
    return has_notif

# --- 3. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

# ตั้งค่า Refresh ทุก 30 วินาทีในหน้าสำคัญ
if st.session_state.page in ["ViewQueues", "Admin", "Booking"]:
    st_autorefresh(interval=30000, key="data_refresh_check")

st.markdown("<h1 class='main-header'>✂️ 222-Salon @สงขลา</h1>", unsafe_allow_html=True)

# เมนู Navigation Bar
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
    if role == 'admin':
        with m_cols[2]:
            st.markdown('<div class="nav-container">', unsafe_allow_html=True)
            if check_notifications():
                st.markdown('<span class="badge"></span>', unsafe_allow_html=True)
            if st.button("📊 จัดการร้าน"): navigate("Admin")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        with m_cols[2]: 
            if st.button("✂️ จองคิว"): navigate("Booking")
    with m_cols[4]:
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")
st.divider()

# --- 4. PAGE LOGIC ---

# หน้าแรก
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")
    
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+" }
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span style="float:right; color:#FF4B4B;">{price}</span></div>', unsafe_allow_html=True)

    shop_addr = "222 ถนนเทศบาล 1 ตำบลบ่อยาง อำเภอเมืองสงขลา สงขลา 90000"
    st.markdown(f'<div class="contact-section"><b>📍 พิกัดร้าน:</b> {shop_addr}<br>📞 ติดต่อ: 082-222-2222</div>', unsafe_allow_html=True)

# หน้าสมัครสมาชิก
elif st.session_state.page == "Register":
    st.subheader("📝 ลงทะเบียนสมาชิก")
    with st.form("reg_form"):
        name = st.text_input("ชื่อ-นามสกุล")
        phone = st.text_input("เบอร์โทรศัพท์ (10 หลัก)")
        pwd = st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ยืนยันการสมัคร"):
            if name and phone and pwd:
                df_u = get_data("Users")
                u_clean = '0' + phone.strip() if (len(phone.strip()) == 9 and phone.strip().isdigit()) else phone.strip()
                if not df_u.empty and u_clean in df_u['phone'].values:
                    st.error("เบอร์นี้เคยลงทะเบียนแล้ว")
                else:
                    new_user = pd.DataFrame([{"phone": u_clean, "password": hash_pass(pwd), "fullname": name, "role": "user"}])
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_user], ignore_index=True))
                    st.success("สมัครสมาชิกสำเร็จ!"); time.sleep(1); navigate("Login")

# หน้าเข้าสู่ระบบ
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์")
    p_in = st.text_input("รหัสผ่าน", type="password")
    if st.button("Login", type="primary"):
        u_clean = '0' + u_in.strip() if len(u_in.strip()) == 9 else u_in.strip()
        if u_clean == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': u_clean, 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            if not df_u.empty:
                user = df_u[(df_u['phone'] == u_clean) & (df_u['password'] == hash_pass(p_in))]
                if not user.empty:
                    st.session_state.update({'logged_in': True, 'user_role': user.iloc[0]['role'], 'username': u_clean, 'fullname': user.iloc[0]['fullname']})
                    navigate("Booking" if user.iloc[0]['role'] == 'user' else "Admin")
                else: st.error("เบอร์โทรหรือรหัสผ่านผิด")

# หน้าจองคิว (ลูกค้า)
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง", "💬 แชทกับร้าน"])
    df_b = get_data("Bookings")
    
    with t1:
        if not df_b.empty and not df_b[(df_b['username'] == st.session_state.username) & (df_b['status'] == "รอรับบริการ")].empty:
            st.warning("คุณยังมีคิวที่ค้างอยู่ในระบบ")
        else:
            with st.form("book_form"):
                d = st.date_input("วันที่", min_value=datetime.now().date())
                t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"])
                s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
                if st.form_submit_button("ยืนยันการจอง"):
                    if d.weekday() == 5: st.error("ร้านหยุดวันเสาร์ครับ")
                    else:
                        new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(d), "time": t, "service": s, "status": "รอรับบริการ", "price": "0"}])
                        conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                        st.success("จองคิวสำเร็จ!"); st.rerun()

    with t2:
        st.dataframe(df_b[df_b['username'] == st.session_state.username].iloc[::-1], use_container_width=True)

    with t3:
        df_c = get_data("Chats")
        chat_box = st.container(height=300)
        with chat_box:
            if not df_c.empty:
                for _, m in df_c[df_c['username'] == st.session_state.username].iterrows():
                    with st.chat_message(m['sender']): st.write(m['msg'])
        if msg := st.chat_input("พิมพ์ข้อความ..."):
            new_msg = pd.DataFrame([{"username": st.session_state.username, "sender": "user", "msg": msg, "time": datetime.now().strftime("%H:%M")}])
            conn.update(worksheet="Chats", data=pd.concat([df_c, new_msg], ignore_index=True)); st.rerun()

# หน้าแอดมิน
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2, at3 = st.tabs(["📊 สรุปรายได้", "📅 จัดการคิว", "📩 ข้อความลูกค้า"])
    df_adm = get_data("Bookings")
    
    with at1:
        done = df_adm[df_adm['status'] == "เสร็จสิ้น"] if not df_adm.empty else pd.DataFrame()
        total = pd.to_numeric(done['price'], errors='coerce').sum() if not done.empty else 0
        st.metric("รายได้รวมทั้งหมด", f"{total:,.0f} บาท")
        st.dataframe(done, use_container_width=True)

    with at2:
        waiting = df_adm[df_adm['status'] == "รอรับบริการ"] if not df_adm.empty else pd.DataFrame()
        for _, r in waiting.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"👤 {r['fullname']} | ⏰ {r['time']} | {r['service']}")
                price = c2.number_input("ราคา", min_value=0, key=f"p_{r['id']}")
                if c2.button("✅ เสร็จสิ้น", key=f"ok_{r['id']}"):
                    df_adm.loc[df_adm['id'] == r['id'], ['status', 'price']] = ["เสร็จสิ้น", str(price)]
                    conn.update(worksheet="Bookings", data=df_adm); st.rerun()
                if c3.button("❌ ยกเลิก", key=f"no_{r['id']}"):
                    df_adm.loc[df_adm['id'] == r['id'], 'status'] = "ยกเลิกโดยร้าน"
                    conn.update(worksheet="Bookings", data=df_adm); st.rerun()

    with at3:
        df_ch = get_data("Chats")
        if not df_ch.empty:
            for u in df_ch['username'].unique():
                with st.expander(f"📩 แชทจาก: {u} (คลิกเพื่อตอบ)"):
                    for _, m in df_ch[df_ch['username'] == u].iterrows():
                        st.write(f"**{m['sender']}**: {m['msg']}")
                    with st.form(f"reply_{u}", clear_on_submit=True):
                        rep = st.text_input("ข้อความตอบกลับ")
                        if st.form_submit_button("ส่ง"):
                            new_r = pd.DataFrame([{"username": u, "sender": "assistant", "msg": rep, "time": datetime.now().strftime("%H:%M")}])
                            conn.update(worksheet="Chats", data=pd.concat([df_ch, new_r], ignore_index=True)); st.rerun()

# หน้าดูคิวรวมวันนี้
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิววันนี้")
    df_q = get_data("Bookings")
    today = datetime.now().strftime("%Y-%m-%d")
    if not df_q.empty:
        qs = df_q[(df_q['date'] == today) & (df_q['status'] == "รอรับบริการ")].sort_values('time')
        if not qs.empty: st.table(qs[['time', 'service', 'fullname']])
        else: st.info("ยังไม่มีคิวที่จองในวันนี้")
