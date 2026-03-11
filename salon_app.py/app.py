import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# 📍 ลิงก์แผนที่ร้าน
SHOP_LOCATION_URL = "https://www.google.com/maps/place/222+%E0%B8%96%E0%B8%99%E0%B8%99+%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B8%9A%E0%B8%B2%E0%B8%A5+1+%E0%B8%95%E0%B8%B3%E0%B8%9A%E0%B8%A5%E0%B8%9A%E0%B9%88%E0%B8%AD%E0%B8%A2%E0%B8%B2%E0%B8%87+%E0%B8%AD%E0%B8%B3%E0%B9%80%E0%B8%A0%E0%B8%AD%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+90000/@7.1954797,100.6083957,15z/data=!4m6!3m5!1s0x304d3323c7ad029d:0x7cfb098f4f859e4c!8m2!3d7.1915128!4d100.6007972!16s%2Fg%2F11jylj3r6y?entry=ttu&g_ep=EgoyMDI2MDMwOC4wIKXMDSoASAFQAw%3D%3D" 

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}
        .stButton>button:hover {background-color: #FF4B4B; color: white;}
        
        /* 📋 Price Card */
        .price-card {
            background-color: #ffffff !important; padding: 15px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 10px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #1A1A1A !important;
        }
        .price-card b { color: #000000 !important; display: block; font-size: 1.1rem; margin-bottom: 5px; }
        .price-text { color: #FF4B4B !important; font-weight: bold; font-size: 1rem; }

        /* Dashboard Admin Metrics */
        .metric-card {
            background-color: #ffffff; padding: 20px; border-radius: 15px;
            border: 2px solid #FF4B4B; text-align: center; color: #1A1A1A !important; font-weight: bold;
        }

        /* 📞 Contact Box - ปรับปรุงสีตัวหนังสือให้เข้มชัดเจน */
        .contact-box {
            text-align: center; 
            background-color: #ffffff !important; 
            padding: 20px; 
            border-radius: 15px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1);
            min-height: 150px;
            color: #1A1A1A !important; /* บังคับสีตัวหนังสือเข้ม */
        }
        .contact-box h3 { color: #FF4B4B !important; margin-bottom: 10px; font-size: 1.2rem; }
        .contact-box p { color: #333333 !important; font-weight: 500; font-size: 1rem; line-height: 1.4; }

        /* รายการคิว */
        .booking-item {
            background-color: #ffffff; color: #333; padding: 15px;
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
        if df.empty:
            cols = {
                "Users": ["username", "password", "fullname", "role"],
                "Bookings": ["id", "username", "service", "date", "time", "status"],
                "Messages": ["id", "username", "message", "timestamp", "status"]
            }
            return pd.DataFrame(columns=cols.get(sheet_name, []))
        df.columns = [str(c).strip() for c in df.columns]
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        for col in ['username', 'phone']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(x).strip().zfill(10) if x and str(x).isdigit() else str(x))
        return df
    except: return pd.DataFrame()

# --- 2. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

# --- TOP MENU BAR ---
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
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (หยุดทุกวันพุธ)")
    
    st.subheader("📋 รายการบริการและราคา")
    services = {
        "✂️ ตัดผมชาย": "150 - 350 บาท", 
        "💇‍♀️ ตัดผมหญิง": "350 - 800 บาท", 
        "🚿 สระ-ไดร์": "200 - 450 บาท", 
        "🎨 ทำสีผม": "1,500 - 4,500 บาท", 
        "✨ ยืดวอลลุ่ม/ดัดผม": "1,000 - 3,500 บาท",
        "🌿 ทรีทเม้นท์": "500 - 1,500 บาท"
    }
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span class="price-text">{price}</span></div>', unsafe_allow_html=True)
    
    st.divider()

    st.subheader("📞 ช่องทางการติดต่อ")
    c1, c2, c3 = st.columns(3)
    # ใช้ HTML เพื่อบังคับสีตัวหนังสือให้เข้มตลอดเวลา
    with c1:
        st.markdown("""<div class='contact-box'><h3>📞 โทรศัพท์</h3><p>081-222-XXXX</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class='contact-box'><h3>💬 โซเชียล</h3><p>Line: @222salon<br>FB: 222 Salon</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class='contact-box'><h3>📍 ที่ตั้ง</h3><p>ย่านสุขุมวิท กรุงเทพฯ</p></div>""", unsafe_allow_html=True)

    st.write("")
    st.link_button("📍 นำทางไปที่ร้าน (Google Maps)", SHOP_LOCATION_URL, type="primary", use_container_width=True)

# --- 4. PAGE: BOOKING ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.get('fullname', st.session_state.username)}")
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติ/ยกเลิกคิว", "💬 ส่งข้อความหาแอดมิน"])
    
    with t1:
        with st.form("booking_form"):
            svc = st.selectbox("เลือกบริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            d = st.date_input("เลือกวันที่จอง", min_value=datetime.now().date())
            t = st.selectbox("เลือกเวลา", [f"{h:02d}:{m}" for h in range(9, 20) for m in ["00", "30"] if "09:30" <= f"{h:02d}:{m}" <= "19:00"])
            submit = st.form_submit_button("ยืนยันการจองคิว")
            if submit:
                df_b = get_data("Bookings")
                booked_count = len(df_b[(df_b['date'] == str(d)) & (df_b['time'] == t) & (df_b['status'] == 'รอรับบริการ')])
                if d.weekday() == 2: st.error("ขออภัย ร้านหยุดทุกวันพุธครับ")
                elif booked_count >= 2: st.error("เวลานี้เต็มแล้ว กรุณาเลือกเวลาอื่น")
                else:
                    new_id = str(int(datetime.now().timestamp()))
                    new_q = pd.DataFrame([{"id": new_id, "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "status": "รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                    st.success("จองคิวสำเร็จ!"); st.rerun()

    with t2:
        df_b = get_data("Bookings")
        my_q = df_b[df_b['username'] == st.session_state.username].sort_values(['date', 'time'], ascending=False)
        if not my_q.empty:
            for _, row in my_q.iterrows():
                with st.container():
                    c_info, c_btn = st.columns([4, 1])
                    c_info.markdown(f"<div class='booking-item'><b>{row['date']} | {row['time']}</b><br>{row['service']} ({row['status']})</div>", unsafe_allow_html=True)
                    if row['status'] == 'รอรับบริการ':
                        if c_btn.button("❌ ยกเลิก", key=f"can_{row['id']}"):
                            df_b.loc[df_b['id'] == row['id'], 'status'] = 'ยกเลิกโดยลูกค้า'
                            conn.update(worksheet="Bookings", data=df_b)
                            st.toast("ยกเลิกคิวแล้ว"); st.rerun()
        else: st.write("ไม่มีประวัติการจอง")

    with t3:
        with st.form("msg_form"):
            msg_text = st.text_area("สอบถามเรื่องใด พิมพ์ไว้ได้เลยครับ")
            if st.form_submit_button("ส่งข้อความ"):
                if msg_text:
                    df_m = get_data("Messages")
                    new_m = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "message": msg_text, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "ยังไม่ได้อ่าน"}])
                    conn.update(worksheet="Messages", data=pd.concat([df_m, new_m], ignore_index=True))
                    st.success("ส่งข้อความถึงแอดมินแล้ว")
                else: st.warning("กรุณาพิมพ์ข้อความ")

# --- 5. PAGE: ADMIN ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการสำหรับเจ้าของร้าน")
    adm_t1, adm_t2 = st.tabs(["📅 จัดการคิว", "📩 ข้อความลูกค้า"])
    with adm_t1:
        df_b = get_data("Bookings")
        if not df_b.empty:
            today_str = datetime.now().strftime("%Y-%m-%d")
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='metric-card'>👥 ลูกค้าวันนี้<br>{len(df_b[df_b['date'] == today_str])} ท่าน</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-card'>📅 วันนี้<br>{today_str}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='metric-card'>⏳ คิวรอ<br>{len(df_b[df_b['status'] == 'รอรับบริการ'])} คิว</div>", unsafe_allow_html=True)
            st.divider()
            pending_q = df_b[df_b['status'] == 'รอรับบริการ'].sort_values(['date', 'time'])
            for _, row in pending_q.iterrows():
                col_i, col_b1, col_b2 = st.columns([3, 1, 1])
                col_i.markdown(f"<div class='booking-item'><b>{row['date']} | {row['time']}</b><br>คุณ: {row['username']} | {row['service']}</div>", unsafe_allow_html=True)
                if col_b1.button("✅ เสร็จ", key=f"d_{row['id']}"):
                    df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                    conn.update(worksheet="Bookings", data=df_b); st.rerun()
                if col_b2.button("🗑️ ลบ", key=f"del_{row['id']}"):
                    df_b = df_b[df_b['id'] != row['id']]
                    conn.update(worksheet="Bookings", data=df_b); st.rerun()
    with adm_t2:
        df_m = get_data("Messages")
        unread = df_m[df_m['status'] == 'ยังไม่ได้อ่าน']
        if not unread.empty:
            for _, m in unread.iterrows():
                with st.chat_message("user"):
                    st.write(f"จาก: {m['username']} ({m['timestamp']})")
                    st.write(m['message'])
                    if st.button("อ่านแล้ว", key=f"r_{m['id']}"):
                        df_m.loc[df_m['id'] == m['id'], 'status'] = 'อ่านแล้ว'
                        conn.update(worksheet="Messages", data=df_m); st.rerun()
        else: st.write("ไม่มีข้อความใหม่")

# --- 6. AUTH ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u = st.text_input("Username (เบอร์โทร)")
    p = st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'Admin'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            u_c = u.zfill(10) if u.isdigit() else u
            user = df_u[(df_u['username'] == u_c) & (df_u['password'] == p)]
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_c, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nu = st.text_input("เบอร์โทร")
        np = st.text_input("รหัสผ่าน", type="password")
        nf = st.text_input("ชื่อ-นามสกุล")
        if st.form_submit_button("ยืนยัน"):
            df_u = get_data("Users")
            nu_c = nu.zfill(10) if nu.isdigit() else nu
            if nu_c in df_u['username'].values: st.error("เบอร์นี้มีในระบบแล้ว")
            else:
                new_user = pd.DataFrame([{"username": nu_c, "password": np, "fullname": nf, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_user], ignore_index=True))
                st.success("สมัครสำเร็จ!"); navigate("Login")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิวที่จองแล้วของวันนี้")
    df_b = get_data("Bookings")
    today_str = datetime.now().strftime("%Y-%m-%d")
    active_q = df_b[(df_b['date'] == today_str) & (df_b['status'] == 'รอรับบริการ')]
    if not active_q.empty:
        st.dataframe(active_q[['time', 'service']].sort_values('time'), use_container_width=True)
    else: st.write("ยังไม่มีคนจองคิววันนี้")

