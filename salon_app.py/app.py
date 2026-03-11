import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS (เน้นความชัดเจนและ UI ที่สวยงาม) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# 📍 ลิงก์แผนที่ร้าน
SHOP_LOCATION_URL = "https://maps.google.com" 

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}
        .stButton>button:hover {background-color: #FF4B4B; color: white;}
        
        /* 📋 Price Card (ปรับปรุงให้ตัวหนังสือเข้มชัดเจน) */
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
            border: 2px solid #FF4B4B; text-align: center; color: #1A1A1A; font-weight: bold;
        }

        /* กล่องรายการจองในหน้า Admin */
        .booking-item {
            background-color: #1E1E1E; color: white; padding: 15px;
            border-radius: 10px; margin-bottom: 10px; border: 1px solid #333;
        }
    </style>
""", unsafe_allow_html=True)

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        # ล้างข้อมูลเลข .0 และช่องว่าง
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        # 📍 จัดการเลข 0 นำหน้าเบอร์โทร/Username ให้ครบ 10 หลัก
        for col in ['username', 'phone']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(x).strip().zfill(10) if x and str(x).isdigit() else str(x))
        return df
    except: return pd.DataFrame()

# --- 2. NAVIGATION & SESSION STATE ---
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
    st.link_button("📍 นำทางไปที่ร้าน (GPS)", SHOP_LOCATION_URL, type="primary", use_container_width=True)

# --- 4. PAGE: BOOKING (Customer Side) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.get('fullname', st.session_state.username)}")
    t1, t2 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง"])
    
    with t1:
        with st.form("booking_form"):
            svc = st.selectbox("เลือกบริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            d = st.date_input("เลือกวันที่จอง")
            t = st.selectbox("เลือกเวลา", [f"{h:02d}:{m}" for h in range(9, 20) for m in ["00", "30"] if "09:30" <= f"{h:02d}:{m}" <= "19:00"])
            submit = st.form_submit_button("ยืนยันการจองคิว")
            
            if submit:
                df_b = get_data("Bookings")
                booked_count = len(df_b[(df_b['date'] == str(d)) & (df_b['time'] == t) & (df_b['status'] == 'รอรับบริการ')])
                
                if d.weekday() == 2: # วันพุธ
                    st.error("ขออภัย ร้านหยุดทุกวันพุธครับ")
                elif booked_count >= 2: # สมมติว่าช่างมี 2 คน
                    st.error("ขออภัย เวลานี้มีผู้จองเต็มแล้ว กรุณาเลือกเวลาอื่น")
                else:
                    new_id = str(int(datetime.now().timestamp()))
                    new_q = pd.DataFrame([{"id": new_id, "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "status": "รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                    st.success("จองคิวสำเร็จแล้ว!")
                    st.rerun()

    with t2:
        df_b = get_data("Bookings")
        my_q = df_b[df_b['username'] == st.session_state.username].sort_values(['date', 'time'], ascending=False)
        if not my_q.empty:
            st.dataframe(my_q[['date', 'time', 'service', 'status']], use_container_width=True)
        else:
            st.write("ยังไม่มีประวัติการจอง")

# --- 5. PAGE: ADMIN (Shop Owner Side) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการสำหรับเจ้าของร้าน")
    df_b = get_data("Bookings")
    
    if not df_b.empty:
        today_str = datetime.now().strftime("%Y-%m-%d")
        df_today = df_b[df_b['date'] == today_str]
        
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'>👥 ลูกค้าวันนี้<br><span style='font-size:24px; color:#FF4B4B;'>{len(df_today)}</span> ท่าน</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'>📅 วันนี้<br><span style='font-size:20px;'>{today_str}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'>⏳ คิวรอรับบริการ<br><span style='font-size:24px;'>{len(df_b[df_b['status'] == 'รอรับบริการ'])}</span> คิว</div>", unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("📌 รายการคิวที่รอรับบริการ")
        pending_q = df_b[df_b['status'] == 'รอรับบริการ'].sort_values(['date', 'time'])
        
        for _, row in pending_q.iterrows():
            with st.container():
                col_info, col_btn = st.columns([4, 1])
                col_info.markdown(f"""
                <div class='booking-item'>
                    <b>⏰ {row['date']} | {row['time']}</b><br>
                    👤 คุณ: {row['username']} | ✂️ บริการ: {row['service']}
                </div>
                """, unsafe_allow_html=True)
                if col_btn.button("✅ เสร็จสิ้น", key=f"done_{row['id']}"):
                    df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                    conn.update(worksheet="Bookings", data=df_b)
                    st.rerun()
                if col_btn.button("🗑️ ลบคิว", key=f"del_{row['id']}"):
                    df_b = df_b[df_b['id'] != row['id']]
                    conn.update(worksheet="Bookings", data=df_b)
                    st.rerun()

# --- 6. LOGIN & REGISTER ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u = st.text_input("Username (เบอร์โทรศัพท์)")
    p = st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'Admin เจ้าของร้าน'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            u_clean = u.zfill(10) if u.isdigit() else u
            user = df_u[(df_u['username'] == u_clean) & (df_u['password'] == p)]
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_clean, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else:
                st.error("Username หรือ Password ไม่ถูกต้อง")

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg_form"):
        nu = st.text_input("เบอร์โทรศัพท์ (จะใช้เป็น Username)")
        np = st.text_input("ตั้งรหัสผ่าน", type="password")
        nf = st.text_input("ชื่อ-นามสกุล")
        if st.form_submit_button("ยืนยันการสมัคร"):
            if nu and np and nf:
                df_u = get_data("Users")
                nu_clean = nu.zfill(10) if nu.isdigit() else nu
                if not df_u.empty and nu_clean in df_u['username'].values:
                    st.error("เบอร์โทรศัพท์นี้เคยสมัครสมาชิกแล้ว")
                else:
                    new_user = pd.DataFrame([{"username": nu_clean, "password": np, "fullname": nf, "role": "user"}])
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_user], ignore_index=True))
                    st.success("สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ")
                    navigate("Login")
            else:
                st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 ตารางคิวประจำวัน")
    df_b = get_data("Bookings")
    today_str = datetime.now().strftime("%Y-%m-%d")
    active_q = df_b[(df_b['date'] == today_str) & (df_b['status'] == 'รอรับบริการ')]
    if not active_q.empty:
        st.write(f"คิวว่างและคิวที่มีผู้จองแล้วของวันที่: {today_str}")
        st.dataframe(active_q[['time', 'service']].sort_values('time'), use_container_width=True)
    else:
        st.write("วันนี้ยังไม่มีการจองคิว")
