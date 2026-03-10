import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอและสไตล์ (UI/UX) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# 📍 เปลี่ยนลิงก์ GPS ร้านคุณที่นี่
SHOP_LOCATION_URL = "https://www.google.com/maps/place/222+%E0%B8%96%E0%B8%99%E0%B8%99+%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B8%9A%E0%B8%B2%E0%B8%A5+1+%E0%B8%95%E0%B8%B3%E0%B8%9A%E0%B8%A5%E0%B8%9A%E0%B9%88%E0%B8%AD%E0%B8%A2%E0%B8%B2%E0%B8%87+%E0%B8%AD%E0%B8%B3%E0%B9%80%E0%B8%A0%E0%B8%AD%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+90000/@7.1915128,100.6007972,17z/data=!3m1!4b1!4m6!3m5!1s0x304d3323c7ad029d:0x7cfb098f4f859e4c!8m2!3d7.1915128!4d100.6007972!16s%2Fg%2F11jylj3r6y?entry=ttu&g_ep=EgoyMDI2MDMwOC4wIKXMDSoASAFQAw%3D%3D" 

st.markdown("""
    <style>
        /* ซ่อน Sidebar และปรับแต่งปุ่ม */
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}
        .stButton>button:hover {background-color: #FF4B4B; color: white; border-color: #FF4B4B;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        
        /* แก้ไข Price Card ให้เห็นตัวหนังสือชัดเจน (Fix Invisible Text) */
        .price-card {
            background-color: #ffffff !important; 
            padding: 20px; 
            border-radius: 15px;
            border-left: 8px solid #FF4B4B; 
            margin-bottom: 15px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1);
            color: #1A1A1A !important; /* บังคับสีตัวอักษรเข้ม */
        }
        .price-card b {
            color: #000000 !important;
            font-size: 1.2rem;
            display: block;
            margin-bottom: 5px;
        }
        .price-text {
            color: #FF4B4B !important;
            font-weight: bold;
            font-size: 1.1rem;
        }

        /* สไตล์ Dashboard สำหรับแอดมิน */
        .metric-container {
            background-color: #ffffff; padding: 25px; border-radius: 20px;
            border: 2px solid #FF4B4B; text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .metric-title { font-size: 18px; color: #555 !important; font-weight: bold; }
        .metric-value { font-size: 38px; color: #FF4B4B !important; font-weight: 900; }
    </style>
""", unsafe_allow_html=True)

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. ข้อมูลบริการและเวลา ---
SERVICES_DISPLAY = {
    "✂️ ตัดผมชาย": "150 - 350", "💇‍♀️ ตัดผมหญิง": "350 - 800",
    "🚿 สระ-ไดร์": "200 - 450", "🎨 ทำสีผม": "1,500 - 4,500",
    "✨ ยืดผมวอลลุ่ม": "1,000 - 5,500", "🌿 เคราติน": "1,500 - 3,500"
}
SERVICES_BASE_PRICE = {"ตัดผมชาย": 150, "ตัดผมหญิง": 350, "สระ-ไดร์": 200, "ทำสีผม": 1500, "ยืดผมวอลลุ่ม": 1000, "เคราติน": 1500}
TIME_SLOTS = [f"{h:02d}:{m}" for h in range(9, 20) for m in ["00", "30"] if "09:30" <= f"{h:02d}:{m}" <= "19:30"]

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        
        # ล้างข้อมูลเบื้องต้น (จัดการเลข .0)
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        
        # 📍 แก้ไขเบอร์โทรศัพท์ (Fix Leading Zero)
        if 'phone' in df.columns:
            df['phone'] = df['phone'].apply(lambda x: str(x).strip().zfill(10) if x and x != "" else "")
            
        return df
    except: 
        return pd.DataFrame()

# --- 3. ระบบนำทาง (Navigation) ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon Online</h1>", unsafe_allow_html=True)
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
    with m_cols[2]: 
        if st.button("📊 หลังบ้าน" if role == 'admin' else "✂️ จองคิว"): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 4. หน้าแอดมิน (Admin Dashboard) ---
if st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการร้านและสรุปยอดรายวัน")
    df_b = get_data("Bookings")
    df_u = get_data("Users")
    
    if not df_b.empty:
        today_str = datetime.now().strftime("%Y-%m-%d")
        df_today = df_b[df_b['date'] == today_str]
        
        daily_rev = pd.to_numeric(df_today['price'], errors='coerce').sum()
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-container'><div class='metric-title'>💰 ยอดขายวันนี้</div><div class='metric-value'>{daily_rev:,.0f} ฿</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-container'><div class='metric-title'>👥 ลูกค้าวันนี้</div><div class='metric-value'>{len(df_today)} ท่าน</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-container'><div class='metric-title'>📅 วันที่</div><div class='metric-value'>{today_str}</div></div>", unsafe_allow_html=True)
        
        st.divider()
        # รวมข้อมูลจองกับข้อมูลลูกค้าเพื่อดูชื่อจริงและเบอร์โทร
        df_admin = pd.merge(df_b, df_u[['username', 'fullname', 'phone']], on='username', how='left')
        
        for _, row in df_admin.sort_values(['date','time'], ascending=[False, True]).iterrows():
            status_color = "🟢" if row['status'] == 'เสร็จสิ้น' else "🔵"
            with st.expander(f"{status_color} ⏰ {row['time']} | {row['fullname']} - {row['service']}"):
                col_a, col_b, col_c = st.columns(3)
                col_a.markdown(f"📞 **เบอร์โทร:** {row['phone']}")
                col_b.write(f"📅 วันที่: {row['date']}")
                
                if row['status'] == 'รอรับบริการ':
                    if col_c.button("✅ เสร็จสิ้นคิวนี้", key=f"ok_{row['id']}"):
                        df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                        conn.update(worksheet="Bookings", data=df_b)
                        st.rerun()
                if st.button("🗑️ ลบคิวนี้", key=f"del_{row['id']}"):
                    conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']])
                    st.rerun()

# --- 5. หน้าจองคิว (Booking) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.get('fullname', st.session_state.username)}")
    t1, t2 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง"])
    
    with t1:
        svc = st.selectbox("เลือกบริการ", list(SERVICES_BASE_PRICE.keys()))
        d = st.date_input("เลือกวันที่จอง")
        t = st.selectbox("เลือกเวลา", TIME_SLOTS)
        
        if d.weekday() == 2: 
            st.error("⚠️ ร้านหยุดทุกวันพุธครับ")
        elif st.button("ยืนยันการจอง"):
            df_b = get_data("Bookings")
            user_booked = df_b[(df_b['username'] == st.session_state.username) & (df_b['date'] == str(d)) & (df_b['status'] == 'รอรับบริการ')]
            booked_now = len(df_b[(df_b['date'] == str(d)) & (df_b['time'] == t) & (df_b['status'] == 'รอรับบริการ')])
            
            if not user_booked.empty:
                st.error(f"❌ คุณมีคิวจองในวันที่ {d} อยู่แล้ว (จำกัด 1 คิว/วัน)")
            elif booked_now >= 2:
                st.error(f"❌ เวลานี้ ({t}) เต็มแล้ว (พนักงาน 2 ท่าน)")
            else:
                new_id = str(int(datetime.now().timestamp()))
                new_r = pd.DataFrame([{"id":new_id, "username":st.session_state.username, "service":svc, "date":str(d), "time":t, "price":str(SERVICES_BASE_PRICE[svc]), "status":"รอรับบริการ"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_r], ignore_index=True))
                st.success("✅ จองคิวสำเร็จ!")
                st.rerun()
    with t2:
        df_b = get_data("Bookings")
        my_q = df_b[df_b['username'] == st.session_state.username].sort_values('date', ascending=False)
        st.dataframe(my_q[['date', 'time', 'service', 'status']], use_container_width=True)

# --- 6. หน้าแรก (Home) ---
elif st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    c_i1, c_i2 = st.columns(2)
    c_i1.info("⏰ 09:30 - 19:30 น. (หยุดวันพุธ)")
    c_i2.link_button("📍 นำทางไปยังร้าน (GPS)", SHOP_LOCATION_URL, type="primary")
    
    st.subheader("📋 บริการและราคาเริ่มต้น")
    p_col1, p_col2 = st.columns(2)
    for i, (name, price) in enumerate(SERVICES_DISPLAY.items()):
        target = p_col1 if i % 2 == 0 else p_col2
        target.markdown(f'''
            <div class="price-card">
                <b>{name}</b>
                <span class="price-text">{price} บาท</span>
            </div>
        ''', unsafe_allow_html=True)

# --- 7. หน้าสมัครสมาชิกและล็อกอิน ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nu, np = st.text_input("Username"), st.text_input("Password", type="password")
        nf, nt = st.text_input("ชื่อ-นามสกุล"), st.text_input("เบอร์โทรศัพท์")
        if st.form_submit_button("สมัครสมาชิก"):
            if nu and np and nf and nt:
                df_u = get_data("Users")
                if nu in df_u['username'].values: st.error("❌ Username นี้มีผู้ใช้แล้ว")
                else:
                    new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "phone":nt, "role":"user"}])
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                    st.success("✅ สมัครสำเร็จ! กรุณาเข้าสู่ระบบ")
            else: st.warning("⚠️ กรุณากรอกข้อมูลให้ครบ")

elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin'}); navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not user.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u, 'fullname':user.iloc[0]['fullname']}); navigate("Booking")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้ (จำกัดช่วงละ 2 ท่าน)")
    df_b = get_data("Bookings")
    active = df_b[(df_b['date'] == str(datetime.now().date())) & (df_b['status'] == 'รอรับบริการ')]
    st.dataframe(active[['time', 'service']].sort_values('time'), use_container_width=True)

