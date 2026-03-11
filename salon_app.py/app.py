import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS (ปรับปรุง UI ให้ชัดเจนและสวยงาม) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}
        
        /* การ์ดข้อมูลหน้า Home - ตัวหนังสือสีดำเข้ม */
        .price-card, .contact-box {
            background-color: #ffffff !important; padding: 20px; border-radius: 15px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #000000 !important;
            margin-bottom: 15px; text-align: center; border: 1px solid #eee;
        }
        .price-card b, .contact-box h3, .contact-box p { color: #000000 !important; }
        .price-text { color: #FF4B4B !important; font-weight: bold; font-size: 1.2rem; }
        
        /* สไตล์รายการจองคิวในหน้า Admin */
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
        # คอลัมน์มาตรฐานที่ต้องมีป้องกัน KeyError
        req = {
            "Users": ["username", "password", "fullname", "role"],
            "Bookings": ["id", "username", "service", "date", "time", "status"],
            "Messages": ["id", "username", "message", "timestamp", "status", "admin_reply"]
        }
        if df.empty: return pd.DataFrame(columns=req.get(sheet_name, []))
        df.columns = [str(c).strip() for c in df.columns]
        df = df.fillna("")
        for col in req.get(sheet_name, []):
            if col not in df.columns: df[col] = ""
        return df
    except: return pd.DataFrame()

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

# --- 3. HELPER: MESSENGER CHAT UI ---
def display_messenger(df_m, target_user):
    # กล่องแชทแบบมี Scrollbar
    chat_container = st.container(height=450, border=True)
    with chat_container:
        messages = df_m[df_m['username'] == target_user].sort_values('timestamp')
        if messages.empty:
            st.info("👋 เริ่มต้นการสนทนาได้เลย!")
        for _, m in messages.iterrows():
            # ข้อความจากลูกค้า
            with st.chat_message("user"):
                st.write(m['message'])
                st.caption(f"🕒 {m['timestamp']}")
            # ข้อความตอบกลับจากแอดมิน
            if m['admin_reply']:
                with st.chat_message("assistant", avatar="✂️"):
                    st.write(m['admin_reply'])
                    st.caption("Admin Reply")

# --- 4. PAGE: HOME ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.subheader("📋 บริการและราคา")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="price-card"><b>✂️ ตัดผมชาย</b><br><span class="price-text">150-350 บ.</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="price-card"><b>🚿 สระ-ไดร์</b><br><span class="price-text">200-450 บ.</span></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="price-card"><b>💇‍♀️ ตัดผมหญิง</b><br><span class="price-text">350-800 บ.</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="price-card"><b>🎨 ทำสีผม</b><br><span class="price-text">1,500 บ.+</span></div>', unsafe_allow_html=True)
    st.divider()
    st.subheader("📞 ติดต่อเรา")
    cc1, cc2 = st.columns(2)
    with cc1: st.markdown('<div class="contact-box"><h3>📞 โทร</h3><p>081-222-XXXX</p></div>', unsafe_allow_html=True)
    with cc2: st.markdown('<div class="contact-box"><h3>💬 Line</h3><p>@222salon</p></div>', unsafe_allow_html=True)
    st.link_button("📍 นำทางไปที่ร้าน (Google Maps)", "https://goo.gl/maps/example", type="primary", use_container_width=True)

# --- 5. PAGE: BOOKING (Customer) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👤 คุณ: {st.session_state.get('fullname', st.session_state.username)}")
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง", "💬 Messenger"])
    
    with t1:
        with st.form("bk_form"):
            svc = st.selectbox("เลือกบริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            d = st.date_input("เลือกวันที่", min_value=datetime.now().date())
            t = st.selectbox("เลือกเวลา", [f"{h:02d}:{m}" for h in range(9, 20) for m in ["00", "30"] if "09:30" <= f"{h:02d}:{m}" <= "19:00"])
            if st.form_submit_button("ยืนยันการจอง"):
                if d.weekday() == 2: st.error("ร้านหยุดทุกวันพุธครับ")
                else:
                    df_b = get_data("Bookings")
                    new_q = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "status": "รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                    st.success("จองคิวสำเร็จ!"); st.rerun()

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
        display_messenger(df_m, st.session_state.username)
        with st.form("send_msg", clear_on_submit=True):
            msg = st.text_input("พิมพ์ข้อความ...", placeholder="สอบถามบริการ/แจ้งเลื่อนคิว...")
            if st.form_submit_button("ส่ง ✈️") and msg:
                new_row = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "message": msg, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "unread", "admin_reply": ""}])
                conn.update(worksheet="Messages", data=pd.concat([df_m, new_row], ignore_index=True))
                st.rerun()

# --- 6. PAGE: ADMIN (จัดการคิว & ตอบแชทแบบเลือกห้องคุย) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการร้าน (Admin Only)")
    at1, at2 = st.tabs(["📅 จัดการคิวลูกค้า", "📩 ห้องแชท Messenger"])
    
    with at1:
        df_b = get_data("Bookings")
        df_u = get_data("Users")
        pending = df_b[df_b['status'].isin(['รอรับบริการ', ''])].sort_values(['date', 'time'])
        if not pending.empty:
            for _, row in pending.iterrows():
                u_info = df_u[df_u['username'] == row['username']]
                name = u_info.iloc[0]['fullname'] if not u_info.empty else row['username']
                c_inf, c_ok, c_del = st.columns([3, 1, 1])
                c_inf.markdown(f"<div class='booking-item'><b>คุณ {name}</b> ({row['username']})<br>📅 {row['date']} | ⏰ {row['time']}<br>✂️ {row['service']}</div>", unsafe_allow_html=True)
                if c_ok.button("✅ สำเร็จ", key=f"ok_{row['id']}"):
                    df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                    conn.update(worksheet="Bookings", data=df_b); st.rerun()
                if c_del.button("🗑️ ลบ", key=f"del_{row['id']}"):
                    df_b = df_b[df_b['id'] != row['id']]
                    conn.update(worksheet="Bookings", data=df_b); st.rerun()
        else: st.info("ไม่มีคิวรอรับบริการในขณะนี้")

    with at2:
        df_m = get_data("Messages")
        chat_users = df_m['username'].unique()
        if len(chat_users) > 0:
            selected_user = st.selectbox("เลือกแชทลูกค้าเพื่อตอบกลับ:", chat_users)
            display_messenger(df_m, selected_user)
            with st.form("admin_reply_f", clear_on_submit=True):
                ans = st.text_input("พิมพ์ข้อความตอบกลับ...")
                if st.form_submit_button("ส่งคำตอบ 📤") and ans:
                    # อัปเดตบรรทัดล่าสุดที่ยังไม่มีคำตอบ หรือสร้างข้อความใหม่
                    df_m = pd.concat([df_m, pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": selected_user, "message": "(Admin Message)", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "read", "admin_reply": ans}])], ignore_index=True)
                    conn.update(worksheet="Messages", data=df_m)
                    st.rerun()
        else: st.write("ยังไม่มีข้อความจากลูกค้า")

# --- 7. AUTHENTICATION ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u, p = st.text_input("เบอร์โทรศัพท์"), st.text_input("รหัสผ่าน", type="password")
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
            else: st.error("เบอร์โทรหรือรหัสผ่านไม่ถูกต้อง")

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg_form"):
        nu, np, nf = st.text_input("เบอร์โทรศัพท์ (ใช้เข้าระบบ)"), st.text_input("รหัสผ่าน"), st.text_input("ชื่อ-นามสกุล")
        if st.form_submit_button("สมัครสมาชิก"):
            df_u = get_data("Users")
            if nu in df_u['username'].values: st.error("เบอร์นี้เคยสมัครแล้ว")
            else:
                new_user = pd.DataFrame([{"username": nu, "password": np, "fullname": nf, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_user], ignore_index=True))
                st.success("สมัครสำเร็จ! กรุณาเข้าสู่ระบบ"); navigate("Login")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิวที่จองแล้ววันนี้")
    df_b = get_data("Bookings")
    active = df_b[(df_b['date'] == datetime.now().strftime("%Y-%m-%d")) & (df_b['status'].isin(['รอรับบริการ', '']))]
    if not active.empty: st.table(active[['time', 'service']])
    else: st.write("วันนี้ยังไม่มีคิวจอง")
