import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; height: 3.2em; transition: 0.3s;}
        .price-card {
            background-color: #ffffff !important; padding: 18px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 12px; box-shadow: 2px 4px 12px rgba(0,0,0,0.08);
        }
        .summary-box {
            text-align: center; background: #FF4B4B; color: white; padding: 15px;
            border-radius: 10px; margin-bottom: 20px; box-shadow: 2px 4px 8px rgba(0,0,0,0.1);
        }
        .chat-container {
            background-color: #f9f9f9; padding: 15px; border-radius: 15px; 
            border: 1px solid #ddd; height: 350px; overflow-y: auto; margin-bottom: 15px;
        }
        .my-msg { background-color: #DCF8C6; padding: 10px; border-radius: 15px; margin-bottom: 8px; text-align: right; margin-left: 20%; }
        .other-msg { background-color: #FFFFFF; padding: 10px; border-radius: 15px; margin-bottom: 8px; text-align: left; margin-right: 20%; border: 1px solid #eee; }
        .msg-info { font-size: 0.7rem; color: #888; display: block; margin-bottom: 2px; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- ฟังก์ชันดึงข้อมูล (ใช้ Cache 30-60 วินาที เพื่อป้องกัน Quota Error) ---
@st.cache_data(ttl=30)
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name)
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
        lbl = "📊 จัดการร้าน" if role == 'admin' else "✂️ จอง/แชท"
        if st.button(lbl): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]:
        if st.button("🚪 ออก"):
            st.session_state.clear()
            st.cache_data.clear()
            navigate("Home")

st.divider()

# --- 3. PAGE LOGIC ---

# --- หน้าแรก (Home) ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ 09:30 - 19:30 น. (หยุดทุกวันพุธ) | 📍 222 ซอย.พิรม สงขลา.")
    
    st.subheader("📋 บริการของเรา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"}
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><br><span style="color:#FF4B4B;">{price}</span></div>', unsafe_allow_html=True)
    
    st.link_button("📍 นำทางด้วย Google Maps (GPS)", "https://maps.google.com", type="primary", use_container_width=True)

# --- สมัครสมาชิก ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg_form"):
        nu, nf = st.text_input("เบอร์โทรศัพท์ (Username)"), st.text_input("ชื่อ-นามสกุล")
        np, npc = st.text_input("รหัสผ่าน", type="password"), st.text_input("ยืนยันรหัส", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            if np == npc and nu and nf:
                df_u = get_data("Users")
                if not df_u.empty and nu in df_u['phone'].values: st.error("เบอร์นี้มีในระบบแล้ว")
                else:
                    new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}]).astype(str)
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                    st.cache_data.clear()
                    st.success("สำเร็จ!"); time.sleep(1); navigate("Login")

# --- เข้าสู่ระบบ ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์")
    p_in = st.text_input("รหัสผ่าน", type="password")
    if st.button("ตกลง", type="primary"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'admin', 'fullname': 'แอดมิน'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)]
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("ข้อมูลไม่ถูกต้อง")

# --- จองคิว + แชท (สำหรับลูกค้า) ---
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    tab1, tab2, tab3 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิว", "💬 แชทกับร้าน"])
    
    with tab1:
        with st.form("book_form"):
            b_date = st.date_input("เลือกวันที่", min_value=datetime.now().date())
            b_time = st.selectbox("เลือกเวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            b_service = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยันการจอง"):
                df_b = get_data("Bookings")
                d_str = str(b_date)
                dup = df_b[(df_b['username'] == st.session_state.username) & (df_b['date'] == d_str) & (df_b['status'] == "รอรับบริการ")]
                full = df_b[(df_b['date'] == d_str) & (df_b['time'] == b_time) & (df_b['status'] == "รอรับบริการ")]
                if not dup.empty: st.error("⚠️ จองวันนี้ไปแล้ว")
                elif len(full) >= 2: st.error("⚠️ เวลานี้เต็มแล้ว")
                else:
                    new_q = pd.DataFrame([{"id": str(int(time.time())), "username": st.session_state.username, "fullname": st.session_state.fullname, "date": d_str, "time": b_time, "service": b_service, "status": "รอรับบริการ", "price": "0"}]).astype(str)
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                    st.cache_data.clear()
                    st.success("จองสำเร็จ!"); time.sleep(1); st.rerun()

    with tab2:
        df_b = get_data("Bookings")
        my_q = df_b[df_b['username'] == st.session_state.username].sort_values('date', ascending=False)
        st.dataframe(my_q[['date', 'time', 'service', 'status', 'price']], use_container_width=True)

    with tab3:
        df_c = get_data("Chats")
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        for _, m in df_c.tail(20).iterrows():
            is_me = m['username'] == st.session_state.username
            st.markdown(f"<div class='{'my-msg' if is_me else 'other-msg'}'><span class='msg-info'>{m['fullname']} ({m['time']})</span>{m['message']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        with st.form("chat_input", clear_on_submit=True):
            msg = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง"):
                if msg:
                    new_m = pd.DataFrame([{"username": st.session_state.username, "fullname": st.session_state.fullname, "message": msg, "time": datetime.now().strftime("%H:%M")}]).astype(str)
                    conn.update(worksheet="Chats", data=pd.concat([df_c, new_m], ignore_index=True))
                    st.cache_data.clear()
                    st.rerun()

# --- หน้า Admin ---
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    adm_tab1, adm_tab2 = st.tabs(["📊 จัดการคิววันนี้", "💬 แชทกับลูกค้า"])
    df_b = get_data("Bookings")
    t_str = datetime.now().strftime("%Y-%m-%d")
    
    with adm_tab1:
        today = df_b[df_b['date'] == t_str]
        income = pd.to_numeric(today[today['status'] == "รับบริการเสร็จสิ้น"]['price'], errors='coerce').sum()
        col_s1, col_s2 = st.columns(2)
        col_s1.markdown(f"<div class='summary-box'><h3>คิวรอวันนี้</h3><h2>{len(today[today['status']=='รอรับบริการ'])} คิว</h2></div>", unsafe_allow_html=True)
        col_s2.markdown(f"<div class='summary-box' style='background:#28a745;'><h3>ยอดเงินวันนี้</h3><h2>{income:,.0f} บ.</h2></div>", unsafe_allow_html=True)
        
        pend = today[today['status'] == "รอรับบริการ"].sort_values('time')
        for _, r in pend.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"👤 **{r['fullname']}** | {r['service']} | ⏰ {r['time']}")
                p_final = c2.number_input("ราคาเรียกเก็บ", min_value=0, key=f"p_{r['id']}")
                if c3.button("จบงาน", key=f"f_{r['id']}"):
                    df_b.loc[df_b['id'] == r['id'], ['status', 'price']] = ["รับบริการเสร็จสิ้น", str(p_final)]
                    conn.update(worksheet="Bookings", data=df_b.astype(str))
                    st.cache_data.clear()
                    st.rerun()

    with adm_tab2:
        df_c = get_data("Chats")
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        for _, m in df_c.tail(30).iterrows():
            is_adm = m['username'] == 'admin'
            st.markdown(f"<div class='{'my-msg' if is_adm else 'other-msg'}'><span class='msg-info'>{m['fullname']} ({m['time']})</span>{m['message']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        with st.form("adm_chat", clear_on_submit=True):
            amsg = st.text_input("ตอบลูกค้า...")
            if st.form_submit_button("ส่งในนามร้าน"):
                new_am = pd.DataFrame([{"username": "admin", "fullname": "แอดมิน (ร้าน)", "message": amsg, "time": datetime.now().strftime("%H:%M")}]).astype(str)
                conn.update(worksheet="Chats", data=pd.concat([df_c, new_am], ignore_index=True))
                st.cache_data.clear()
                st.rerun()

# --- คิววันนี้ (บุคคลทั่วไป) ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 ตารางคิววันนี้")
    df_b = get_data("Bookings")
    t_str = datetime.now().strftime("%Y-%m-%d")
    if not df_b.empty:
        active = df_b[(df_b['date'] == t_str) & (df_b['status'] == "รอรับบริการ")].sort_values('time')
        st.table(active[['time', 'service', 'fullname']])
    else: st.info("ไม่มีคิวจอง")
