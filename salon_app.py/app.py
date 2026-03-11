import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS (ปรับปรุงสีตัวหนังสือให้ดำชัดเจน) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}
        
        /* การ์ดและกล่องข้อมูล - ปรับสีตัวหนังสือเป็นสีดำเข้ม */
        .price-card, .contact-box {
            background-color: #ffffff !important; 
            padding: 20px; 
            border-radius: 15px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1); 
            color: #000000 !important; 
            margin-bottom: 15px;
            text-align: center;
            border: 1px solid #eee;
        }
        .price-card b, .contact-box h3, .contact-box p {
            color: #000000 !important;
        }
        .price-text { color: #FF4B4B !important; font-weight: bold; font-size: 1.2rem; }
        
        /* รายการจองคิว */
        .booking-item {
            background-color: #ffffff; color: #000000; padding: 15px;
            border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #FF4B4B;
            box-shadow: 1px 2px 5px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl="0s")
        df = df.dropna(how='all')
        
        # กำหนดคอลัมน์มาตรฐานป้องกัน KeyError
        req = {
            "Users": ["username", "password", "fullname", "role"],
            "Bookings": ["id", "username", "service", "date", "time", "status"],
            "Messages": ["id", "username", "message", "timestamp", "status", "admin_reply"]
        }
        
        if df.empty:
            return pd.DataFrame(columns=req.get(sheet_name, []))
        
        df.columns = [str(c).strip() for c in df.columns]
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        
        # ตรวจสอบและซ่อมคอลัมน์ที่หายไป
        for col in req.get(sheet_name, []):
            if col not in df.columns:
                df[col] = ""
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

# --- 3. PAGE: HOME ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ เปิดบริการ 09:30 - 19:30 น. (หยุดทุกวันพุธ)")
    
    st.subheader("📋 บริการและราคา")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown('<div class="price-card"><b>✂️ ตัดผมชาย</b><br><span class="price-text">150-350 บ.</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="price-card"><b>🚿 สระ-ไดร์</b><br><span class="price-text">200-450 บ.</span></div>', unsafe_allow_html=True)
    with p2:
        st.markdown('<div class="price-card"><b>💇‍♀️ ตัดผมหญิง</b><br><span class="price-text">350-800 บ.</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="price-card"><b>🎨 ทำสีผม</b><br><span class="price-text">1,500 บ.+</span></div>', unsafe_allow_html=True)

    st.subheader("📞 ติดต่อเรา")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="contact-box"><h3>📞 โทร</h3><p>081-222-XXXX</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="contact-box"><h3>💬 Line</h3><p>@222salon</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="contact-box"><h3>📍 พิกัด</h3><p>สุขุมวิท กรุงเทพฯ</p></div>', unsafe_allow_html=True)
    st.link_button("📍 แผนที่ Google Maps", "https://goo.gl/maps/example", type="primary", use_container_width=True)

# --- 4. PAGE: BOOKING (Customer) ---
elif st.session_state.page == "Booking":
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 แชทกับร้าน"])
    
    with t1:
        with st.form("bk"):
            svc = st.selectbox("เลือกบริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            d = st.date_input("วันที่", min_value=datetime.now().date())
            t = st.selectbox("เวลา", [f"{h:02d}:{m}" for h in range(9, 20) for m in ["00", "30"] if "09:30" <= f"{h:02d}:{m}" <= "19:00"])
            if st.form_submit_button("ยืนยันการจอง"):
                if d.weekday() == 2: st.error("ร้านหยุดทุกวันพุธครับ")
                else:
                    df_b = get_data("Bookings")
                    new_q = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "status": "รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                    st.success("จองคิวเรียบร้อย!"); st.rerun()

    with t2:
        df_b = get_data("Bookings")
        my_q = df_b[df_b['username'] == st.session_state.username].sort_values(['date', 'time'], ascending=False)
        for _, row in my_q.iterrows():
            ci, cb = st.columns([4, 1])
            ci.markdown(f"<div class='booking-item'><b>{row['date']} | {row['time']}</b><br>{row['service']} ({row['status']})</div>", unsafe_allow_html=True)
            if row['status'] == 'รอรับบริการ' and cb.button("❌", key=f"c_{row['id']}"):
                df_b.loc[df_b['id'] == row['id'], 'status'] = 'ยกเลิกโดยลูกค้า'
                conn.update(worksheet="Bookings", data=df_b); st.rerun()

    with t3:
        df_m = get_data("Messages")
        for _, m in df_m[df_m['username'] == st.session_state.username].sort_values('timestamp').iterrows():
            with st.chat_message("user"): st.write(m['message'])
            if m['admin_reply']:
                with st.chat_message("assistant", avatar="✂️"): st.write(m['admin_reply'])
        with st.form("chat", clear_on_submit=True):
            msg = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง") and msg:
                new_msg = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "message": msg, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "unread", "admin_reply": ""}])
                conn.update(worksheet="Messages", data=pd.concat([df_m, new_msg], ignore_index=True))
                st.rerun()

# --- 5. PAGE: ADMIN (จัดการคิว & ตอบแชท) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการร้าน (Admin)")
    adm_t1, adm_t2 = st.tabs(["📅 คิวลูกค้าวันนี้", "📩 ข้อความจากลูกค้า"])
    
    with adm_t1:
        df_b = get_data("Bookings")
        df_u = get_data("Users")
        # กรองเฉพาะสถานะ รอรับบริการ หรือ ว่าง
        pending = df_b[df_b['status'].isin(['รอรับบริการ', ''])].sort_values(['date', 'time'])
        if not pending.empty:
            for _, row in pending.iterrows():
                u_info = df_u[df_u['username'] == row['username']]
                name = u_info.iloc[0]['fullname'] if not u_info.empty else row['username']
                
                c_inf, c_ok, c_del = st.columns([3, 1, 1])
                c_inf.markdown(f"<div class='booking-item'><b>คุณ {name}</b><br>📅 {row['date']} | ⏰ {row['time']}<br>✂️ {row['service']}</div>", unsafe_allow_html=True)
                if c_ok.button("✅ สำเร็จ", key=f"ok_{row['id']}"):
                    df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                    conn.update(worksheet="Bookings", data=df_b); st.rerun()
                if c_del.button("🗑️ ลบ", key=f"del_{row['id']}"):
                    df_b = df_b[df_b['id'] != row['id']]
                    conn.update(worksheet="Bookings", data=df_b); st.rerun()
        else: st.write("ไม่มีคิวค้างในระบบ")

    with adm_t2:
        df_m = get_data("Messages")
        unread = df_m[df_m['admin_reply'] == ""]
        for _, m in unread.iterrows():
            with st.expander(f"✉️ จาก {m['username']} - {m['timestamp']}"):
                st.write(f"ลูกค้า: {m['message']}")
                ans = st.text_area("ตอบกลับ", key=f"re_{m['id']}")
                if st.button("ส่งคำตอบ", key=f"btn_{m['id']}"):
                    df_m.loc[df_m['id'] == m['id'], 'admin_reply'] = ans
                    conn.update(worksheet="Messages", data=df_m); st.rerun()

# --- 6. AUTHENTICATION ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u, p = st.text_input("เบอร์โทร"), st.text_input("รหัสผ่าน", type="password")
    if st.button("ตกลง"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'Admin'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nu, np, nf = st.text_input("เบอร์โทร"), st.text_input("รหัสผ่าน"), st.text_input("ชื่อ-นามสกุล")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            if nu in df_u['username'].values: st.error("เบอร์นี้มีในระบบแล้ว")
            else:
                new_u = pd.DataFrame([{"username": nu, "password": np, "fullname": nf, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                st.success("สมัครสำเร็จ!"); navigate("Login")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิวที่จองแล้ววันนี้")
    df_b = get_data("Bookings")
    today = datetime.now().strftime("%Y-%m-%d")
    active = df_b[(df_b['date'] == today) & (df_b['status'].isin(['รอรับบริการ', '']))]
    if not active.empty: st.table(active[['time', 'service']])
    else: st.write("วันนี้ยังไม่มีคิวจอง")
