import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# 📍 ลิงก์แผนที่ร้าน (เปลี่ยนเป็นลิงก์จริงของคุณ)
SHOP_LOCATION_URL = "https://goo.gl/maps/example" 

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}
        .stButton>button:hover {background-color: #FF4B4B; color: white;}
        
        .price-card {
            background-color: #ffffff !important; padding: 15px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 10px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #1A1A1A !important;
        }
        .price-card b { color: #000000 !important; display: block; font-size: 1.1rem; }
        .price-text { color: #FF4B4B !important; font-weight: bold; }

        .contact-box {
            text-align: center; background-color: #ffffff !important; padding: 20px; 
            border-radius: 15px; box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #1A1A1A !important;
        }
        .contact-box h3 { color: #FF4B4B !important; }
        
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
        
        # ป้องกันกรณี Sheet ว่างเปล่า
        if df.empty:
            cols = {
                "Users": ["username", "password", "fullname", "role"],
                "Bookings": ["id", "username", "service", "date", "time", "status"],
                "Messages": ["id", "username", "message", "timestamp", "status", "admin_reply"]
            }
            return pd.DataFrame(columns=cols.get(sheet_name, []))
            
        df.columns = [str(c).strip() for c in df.columns]
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        
        # 🛡️ ป้องกัน KeyError: 'admin_reply' ถ้าใน Sheet ลืมสร้างคอลัมน์นี้
        if sheet_name == "Messages" and "admin_reply" not in df.columns:
            df["admin_reply"] = ""
            
        return df
    except:
        return pd.DataFrame()

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
        if st.button("📝 สมัคร"):
            navigate("Register")
    with m_cols[4]:
        if st.button("🔑 เข้าสู่ระบบ"):
            navigate("Login")
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
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"}
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span class="price-text">{price}</span></div>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📞 ช่องทางการติดต่อ")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='contact-box'><h3>📞 โทร</h3><p>081-222-XXXX</p></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='contact-box'><h3>💬 Line</h3><p>@222salon</p></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='contact-box'><h3>📍 ที่ตั้ง</h3><p>กรุงเทพฯ</p></div>", unsafe_allow_html=True)
    st.link_button("📍 นำทางไปที่ร้าน (Google Maps)", SHOP_LOCATION_URL, type="primary", use_container_width=True)

# --- 4. PAGE: BOOKING ---
elif st.session_state.page == "Booking":
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติ/ยกเลิก", "💬 แชทกับแอดมิน"])
    
    with t1:
        with st.form("bk"):
            svc = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            d = st.date_input("วันที่", min_value=datetime.now().date())
            t = st.selectbox("เวลา", [f"{h:02d}:{m}" for h in range(9, 20) for m in ["00", "30"] if "09:30" <= f"{h:02d}:{m}" <= "19:00"])
            if st.form_submit_button("ยืนยัน"):
                df_b = get_data("Bookings")
                if d.weekday() == 2: st.error("ร้านหยุดวันพุธ")
                else:
                    new_q = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "status": "รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                    st.success("จองคิวสำเร็จ!"); st.rerun()

    with t2:
        df_b = get_data("Bookings")
        my_q = df_b[df_b['username'] == st.session_state.username].sort_values(['date', 'time'], ascending=False)
        for _, row in my_q.iterrows():
            ci, cb = st.columns([4, 1])
            ci.markdown(f"<div class='booking-item'><b>{row['date']} | {row['time']}</b><br>{row['service']} ({row['status']})</div>", unsafe_allow_html=True)
            if row['status'] == 'รอรับบริการ':
                if cb.button("❌", key=f"c_{row['id']}"):
                    df_b.loc[df_b['id'] == row['id'], 'status'] = 'ยกเลิก'
                    conn.update(worksheet="Bookings", data=df_b); st.rerun()

    with t3:
        st.subheader("💬 สนทนากับแอดมิน")
        df_m = get_data("Messages")
        my_m = df_m[df_m['username'] == st.session_state.username].sort_values('timestamp')
        for _, m in my_m.iterrows():
            with st.chat_message("user"): st.write(m['message'])
            if m['admin_reply']:
                with st.chat_message("assistant", avatar="✂️"): st.write(m['admin_reply'])
        
        with st.form("chat", clear_on_submit=True):
            msg = st.text_input("ถามแอดมิน...")
            if st.form_submit_button("ส่ง") and msg:
                new_msg = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "message": msg, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "ยังไม่ได้อ่าน", "admin_reply": ""}])
                conn.update(worksheet="Messages", data=pd.concat([df_m, new_msg], ignore_index=True))
                st.rerun()

# --- 5. PAGE: ADMIN ---
elif st.session_state.page == "Admin":
    st.subheader("📊 จัดการร้าน (Admin)")
    at1, at2 = st.tabs(["📅 คิวลูกค้า", "📩 ตอบแชท"])
    
    with at1:
        df_b = get_data("Bookings")
        pending = df_b[df_b['status'] == 'รอรับบริการ'].sort_values(['date', 'time'])
        for _, row in pending.iterrows():
            ci, cb1, cb2 = st.columns([3, 1, 1])
            ci.markdown(f"<div class='booking-item'><b>{row['date']} {row['time']}</b><br>คุณ {row['username']} - {row['service']}</div>", unsafe_allow_html=True)
            if cb1.button("✅ เสร็จ", key=f"d_{row['id']}"):
                df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                conn.update(worksheet="Bookings", data=df_b); st.rerun()
            if cb2.button("🗑️", key=f"del_{row['id']}"):
                df_b = df_b[df_b['id'] != row['id']]
                conn.update(worksheet="Bookings", data=df_b); st.rerun()

    with at2:
        df_m = get_data("Messages")
        unread = df_m[df_m['admin_reply'] == ""]
        for _, m in unread.iterrows():
            with st.expander(f"✉️ จากคุณ {m['username']} ({m['timestamp']})"):
                st.write(f"ลูกค้า: {m['message']}")
                ans = st.text_area("พิมพ์ตอบกลับ", key=f"ans_{m['id']}")
                if st.button("ส่ง", key=f"b_{m['id']}"):
                    df_m.loc[df_m['id'] == m['id'], 'admin_reply'] = ans
                    conn.update(worksheet="Messages", data=df_m); st.rerun()

# --- 6. AUTH ---
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
            else: st.error("ไม่พบผู้ใช้หรือรหัสผ่านผิด")

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nu, np, nf = st.text_input("เบอร์โทร"), st.text_input("รหัสผ่าน"), st.text_input("ชื่อ")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username": nu, "password": np, "fullname": nf, "role": "user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
            st.success("สมัครเสร็จแล้ว!"); navigate("Login")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_b = get_data("Bookings")
    active = df_b[(df_b['date'] == datetime.now().strftime("%Y-%m-%d")) & (df_b['status'] == 'รอรับบริการ')]
    if not active.empty: st.table(active[['time', 'service']])
    else: st.write("ยังไม่มีคนจองวันนี้")
