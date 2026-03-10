import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอและสไตล์ ---
st.set_page_config(page_title="Barber & Salon Online", layout="wide", initial_sidebar_state="collapsed")

# 📍 เปลี่ยนลิงก์ GPS ร้านคุณที่นี่
SHOP_LOCATION_URL = "https://www.google.com/maps/place/222+%E0%B8%96%E0%B8%99%E0%B8%99+%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B8%9A%E0%B8%B2%E0%B8%A5+1+%E0%B8%95%E0%B8%B3%E0%B8%9A%E0%B8%A5%E0%B8%9A%E0%B9%88%E0%B8%AD%E0%B8%A2%E0%B8%B2%E0%B8%87+%E0%B8%AD%E0%B8%B3%E0%B9%80%E0%B8%A0%E0%B8%AD%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+90000/@7.1915128,100.6007972,17z/data=!3m1!4b1!4m6!3m5!1s0x304d3323c7ad029d:0x7cfb098f4f859e4c!8m2!3d7.1915128!4d100.6007972!16s%2Fg%2F11jylj3r6y?entry=ttu&g_ep=EgoyMDI2MDMwOC4wIKXMDSoASAFQAw%3D%3D" 

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        .price-card {
            background-color: #ffffff; padding: 15px; border-radius: 15px;
            border-left: 8px solid #FF4B4B; margin-bottom: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
        /* สไตล์ Dashboard หลังบ้าน */
        .metric-container {
            background-color: #ffffff; padding: 25px; border-radius: 20px;
            border: 2px solid #FF4B4B; text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .metric-title { font-size: 20px; color: #555; margin-bottom: 10px; font-weight: bold; }
        .metric-value { font-size: 40px; color: #FF4B4B; font-weight: 900; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. ข้อมูลบริการและเวลา ---
SERVICES_DISPLAY = {
    "✂️ ตัดผมชาย": "150 - 350", "💇‍♀️ ตัดผมหญิง": "350 - 800",
    "🚿 สระ-ไดร์": "200 - 450", "🎨 ทำสีผม": "1,500 - 4,500",
    "✨ ยืดผมวอลลุ่ม": "2,000 - 5,500", "🌿 เคราติน": "1,500 - 3,500"
}
SERVICES_BASE_PRICE = {"ตัดผมชาย": 150, "ตัดผมหญิง": 350, "สระ-ไดร์": 200, "ทำสีผม": 1500, "ยืดผมวอลลุ่ม": 2000, "เคราติน": 1500}
TIME_SLOTS = [f"{h:02d}:{m}" for h in range(9, 20) for m in ["00", "30"] if "09:30" <= f"{h:02d}:{m}" <= "19:30"]

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df.columns = [str(c).strip() for c in df.columns]
        def clean_val(v):
            v = str(v).strip()
            if v.endswith('.0'): v = v[:-2]
            return v
        return df.fillna("").map(clean_val)
    except: return pd.DataFrame()

# --- 3. ระบบนำทาง (Navigation) ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ Barber & Salon Online</h1>", unsafe_allow_html=True)
m1, m2, m3, m4, m5 = st.columns(5)
with m1: 
    if st.button("🏠 หน้าแรก"): navigate("Home")
with m2: 
    if st.button("📅 คิวว่างวันนี้"): navigate("ViewQueues")

if not st.session_state.logged_in:
    with m4: 
        if st.button("📝 สมัครสมาชิก"): navigate("Register")
    with m5: 
        if st.button("🔑 เข้าสู่ระบบ"): navigate("Login")
else:
    role = st.session_state.get('user_role')
    with m3: 
        if st.button("📊 หลังบ้าน" if role == 'admin' else "✂️ จองคิว"): navigate("Admin" if role == 'admin' else "Booking")
    with m5: 
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 4. หน้าแอดมิน (Admin) - Dashboard สรุปยอด ---
if st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการร้านและสรุปยอดรายวัน")
    df_b = get_data("Bookings")
    df_u = get_data("Users")
    
    if not df_b.empty:
        today_str = datetime.now().strftime("%Y-%m-%d")
        df_today = df_b[df_b['date'] == today_str]
        
        # คำนวณยอดและจำนวนลูกค้า
        daily_rev = pd.to_numeric(df_today['price'], errors='coerce').sum()
        daily_cust = len(df_today)
        
        # แสดงผล Dashboard แบบชัดเจน
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            st.markdown(f"<div class='metric-container'><div class='metric-title'>💰 ยอดขายวันนี้</div><div class='metric-value'>{daily_rev:,.0f} ฿</div></div>", unsafe_allow_html=True)
        with c_m2:
            st.markdown(f"<div class='metric-container'><div class='metric-title'>👥 ลูกค้าวันนี้</div><div class='metric-value'>{daily_cust} ท่าน</div></div>", unsafe_allow_html=True)
        with c_m3:
            st.markdown(f"<div class='metric-container'><div class='metric-title'>📅 วันที่</div><div class='metric-value'>{today_str}</div></div>", unsafe_allow_html=True)
        
        st.divider()
        
        # ตารางแสดงข้อมูลลูกค้า (แอดมินเห็นชื่อจริงและเบอร์โทร)
        df_admin = pd.merge(df_b, df_u[['username', 'fullname', 'phone']], on='username', how='left')
        h = st.columns([1, 1.5, 1.2, 1.3, 1, 1, 1, 0.6])
        for i, lbl in enumerate(["เวลา", "ชื่อลูกค้า", "เบอร์โทร", "บริการ", "วันที่", "สถานะ", "ยืนยัน", "ลบ"]):
            h[i].write(f"**{lbl}**")
        
        for _, row in df_admin.sort_values(['date','time'], ascending=[False, True]).iterrows():
            r = st.columns([1, 1.5, 1.2, 1.3, 1, 1, 1, 0.6])
            r[0].write(row['time'])
            r[1].write(row['fullname'])
            r[2].write(row['phone'])
            r[3].write(row['service'])
            r[4].write(row['date'])
            r[5].write("🔵 รอ" if row['status'] == 'รอรับบริการ' else "✅ เสร็จ")
            
            if row['status'] == 'รอรับบริการ':
                if r[6].button("เสร็จสิ้น", key=f"ok_{row['id']}"):
                    df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                    conn.update(worksheet="Bookings", data=df_b)
                    st.rerun()
            else: r[6].write("-")
            
            if r[7].button("🗑️", key=f"del_{row['id']}"):
                conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']])
                st.rerun()

# --- 5. หน้าจองคิว (Booking) - เงื่อนไขพนักงาน 2 คน และ 1 ครั้ง/วัน ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.username}")
    t1, t2 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติ"])
    with t1:
        svc = st.selectbox("เลือกบริการ", list(SERVICES_BASE_PRICE.keys()))
        d, t = st.date_input("วันที่จอง"), st.selectbox("เลือกเวลา", TIME_SLOTS)
        
        if d.weekday() == 2: st.error("⚠️ ร้านหยุดวันพุธ")
        elif st.button("ยืนยันการจอง"):
            df_b = get_data("Bookings")
            # 🛡️ เงื่อนไข 1: 1 คน จองได้แค่ 1 ครั้งต่อวัน
            user_booked = df_b[(df_b['username'] == st.session_state.username) & (df_b['date'] == str(d)) & (df_b['status'] == 'รอรับบริการ')]
            # 🛡️ เงื่อนไข 2: ล็อก 2 คนต่อหนึ่งช่วงเวลา (พนักงาน 2 คน)
            booked_now = len(df_b[(df_b['date'] == str(d)) & (df_b['time'] == t) & (df_b['status'] == 'รอรับบริการ')])
            
            if not user_booked.empty:
                st.error(f"❌ คุณได้จองคิววันที่ {d} ไปแล้ว (จำกัด 1 ท่านต่อวัน)")
            elif booked_now >= 2:
                st.error(f"❌ เวลานี้ ({t}) เต็มโควตาพนักงาน 2 ท่านแล้ว")
            else:
                new_id = str(int(datetime.now().timestamp()))
                new_r = pd.DataFrame([{"id":new_id, "username":st.session_state.username, "service":svc, "date":str(d), "time":t, "price":str(SERVICES_BASE_PRICE[svc]), "status":"รอรับบริการ"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_r], ignore_index=True))
                st.success("✅ จองสำเร็จ!")
                st.rerun()
    with t2:
        df_b = get_data("Bookings")
        my = df_b[df_b['username'] == st.session_state.username]
        for _, r in my.iterrows():
            st.write(f"📅 {r['date']} | ⏰ {r['time']} | {r['service']} | {r['status']}")

# --- ส่วนอื่นๆ (Home, Register, Login, ViewQueues) ---
elif st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    c_i1, c_i2 = st.columns(2)
    c_i1.info("⏰ 09:30 - 19:30 น. (หยุดวันพุธ)")
    c_i2.link_button("📍 นำทางไปยังร้าน (GPS)", SHOP_LOCATION_URL, type="primary")
    p_col1, p_col2 = st.columns(2)
    for i, (name, price) in enumerate(SERVICES_DISPLAY.items()):
        target = p_col1 if i % 2 == 0 else p_col2
        target.markdown(f'<div class="price-card"><b>{name}</b><br><span style="color:#FF4B4B;">{price} บาท</span></div>', unsafe_allow_html=True)

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nu, np = st.text_input("Username"), st.text_input("Password", type="password")
        nf, nt = st.text_input("ชื่อ-นามสกุล"), st.text_input("เบอร์โทรศัพท์ (จำเป็น)")
        if st.form_submit_button("สมัครสมาชิก"):
            if not all([nu, np, nf, nt]): st.error("❌ กรุณากรอกข้อมูลให้ครบ")
            else:
                df_u = get_data("Users")
                if nu in df_u['username'].values: st.error("❌ Username นี้มีคนใช้แล้ว")
                else:
                    new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "phone":nt, "role":"user"}])
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                    st.success("✅ สมัครสำเร็จ!")

elif st.session_state.page == "Login":
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin'}); navigate("Admin")
        else:
            df_u = get_data("Users")
            check = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not check.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u}); navigate("Booking")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิววันนี้ (จำกัด 2 ท่านต่อช่วงเวลา)")
    df_b = get_data("Bookings")
    active = df_b[(df_b['date'] == str(datetime.now().date())) & (df_b['status'] == 'รอรับบริการ')]
    st.dataframe(active[['time', 'service']].sort_values('time'), use_container_width=True)

