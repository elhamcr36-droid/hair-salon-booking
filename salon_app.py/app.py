import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอและสไตล์ (UI/UX) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# 📍 ข้อมูลติดต่อจากโค้ดชุดแรกของคุณ
SHOP_TEL = "0875644928"
FACEBOOK_URL = "https://www.facebook.com/share/18Yv8zGNoG/?mibextid=wwXIfr" 
LINE_URL = "https://line.me/ti/p/yourid" # เปลี่ยนเป็นลิงก์ Line ของคุณ
SHOP_LOCATION_URL = "https://www.google.com/maps/place/222+%E0%B8%96%E0%B8%99%E0%B8%99+%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B8%9A%E0%B8%B2%E0%B8%A5+1+%E0%B8%95%E0%B8%B3%E0%B8%9A%E0%B8%A5%E0%B8%9A%E0%B9%88%E0%B8%AD%E0%B8%A2%E0%B8%B2%E0%B8%87+%E0%B8%AD%E0%B8%B3%E0%B9%80%E0%B8%A0%E0%B8%AD%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+90000/@7.1915128,100.6007972,17z/data=!3m1!4b1!4m6!3m5!1s0x304d3323c7ad029d:0x7cfb098f4f859e4c!8m2!3d7.1915128!4d100.6007972!16s%2Fg%2F11jylj3r6y?entry=ttu&g_ep=EgoyMDI2MDMwOC4wIKXMDSoASAFQAw%3D%3D" 

st.markdown(f"""
    <style>
        /* ซ่อน Sidebar และปรับแต่งปุ่ม */
        [data-testid="stSidebar"] {{display: none;}}
        .stButton>button {{width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}}
        .stButton>button:hover {{background-color: #FF4B4B; color: white; border-color: #FF4B4B;}}
        .main-header {{text-align: center; color: #FF4B4B; margin-bottom: 20px;}}
        
        /* แก้ไข Price Card ให้เห็นตัวหนังสือชัดเจน */
        .price-card {{
            background-color: #ffffff !important; 
            padding: 20px; 
            border-radius: 15px;
            border-left: 8px solid #FF4B4B; 
            margin-bottom: 15px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1);
            color: #1A1A1A !important;
        }}
        .price-card b {{ color: #000000 !important; font-size: 1.2rem; display: block; margin-bottom: 5px; }}
        .price-text {{ color: #FF4B4B !important; font-weight: bold; font-size: 1.1rem; }}

        /* สไตล์ Social Buttons */
        .social-container {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
        .social-btn {{
            padding: 10px 20px; border-radius: 30px; color: white !important;
            text-decoration: none; font-weight: bold; font-size: 14px; text-align: center; min-width: 120px;
        }}
        .fb-color {{ background-color: #1877F2; }}
        .line-color {{ background-color: #00B900; }}
        .gps-color {{ background-color: #EA4335; }}

        /* สไตล์แชท */
        .chat-container {{ background-color: #f0f2f5; padding: 15px; border-radius: 15px; margin-bottom: 20px; }}
        .bubble {{ padding: 10px 15px; border-radius: 15px; margin-bottom: 8px; max-width: 75%; font-size: 16px; clear: both; display: block; }}
        .user-msg {{ background-color: #0084FF; color: white !important; float: right; border-bottom-right-radius: 2px; }}
        .admin-msg {{ background-color: #E4E6EB; color: black !important; float: left; border-bottom-left-radius: 2px; }}

        /* สไตล์ Dashboard สำหรับแอดมิน */
        .metric-container {{
            background-color: #ffffff; padding: 25px; border-radius: 20px;
            border: 2px solid #FF4B4B; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .metric-title {{ font-size: 18px; color: #555 !important; font-weight: bold; }}
        .metric-value {{ font-size: 38px; color: #FF4B4B !important; font-weight: 900; }}
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
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        if 'phone' in df.columns:
            df['phone'] = df['phone'].apply(lambda x: str(x).strip().zfill(10) if x and x != "" else "")
        return df
    except: return pd.DataFrame()

# --- 3. ระบบนำทาง ---
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
            st.session_state.clear()
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 4. หน้าแรก (Home) + Social Buttons ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    
    # Social & GPS Buttons จากโค้ดต้นฉบับ
    st.markdown(f"""
        <div class="social-container">
            <a href="{FACEBOOK_URL}" target="_blank" class="social-btn fb-color">🔵 Facebook</a>
            <a href="{LINE_URL}" target="_blank" class="social-btn line-color">🟢 Line</a>
            <a href="{SHOP_LOCATION_URL}" target="_blank" class="social-btn gps-color">🔴 GPS แผนที่</a>
        </div>
    """, unsafe_allow_html=True)

    c_i1, c_i2 = st.columns(2)
    c_i1.info(f"⏰ 09:30 - 19:30 น. (หยุดวันพุธ)\n\n📞 ติดต่อ: {SHOP_TEL}")
    c_i2.success("📍 ร้านตั้งอยู่ถนนเลี่ยงเมือง ใกล้แยกไฟแดง")
    
    st.subheader("📋 บริการและราคาเริ่มต้น")
    p_col1, p_col2 = st.columns(2)
    for i, (name, price) in enumerate(SERVICES_DISPLAY.items()):
        target = p_col1 if i % 2 == 0 else p_col2
        target.markdown(f'<div class="price-card"><b>{name}</b><span class="price-text">{price} บาท</span></div>', unsafe_allow_html=True)

# --- 5. หน้าแอดมิน (Admin Dashboard & Chat) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 จัดการหลังบ้าน")
    adm_t1, adm_t2 = st.tabs(["📈 สรุปยอด/จัดการคิว", "💬 ตอบแชทลูกค้า"])
    
    with adm_t1:
        df_b = get_data("Bookings")
        df_u = get_data("Users")
        if not df_b.empty:
            today_str = datetime.now().strftime("%Y-%m-%d")
            df_today = df_b[df_b['date'] == today_str]
            daily_rev = pd.to_numeric(df_today['price'], errors='coerce').sum()
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='metric-container'><div class='metric-title'>💰 ยอดวันนี้</div><div class='metric-value'>{daily_rev:,.0f}</div></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='metric-container'><div class='metric-title'>👥 ลูกค้าวันนี้</div><div class='metric-value'>{len(df_today)}</div></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='metric-container'><div class='metric-title'>📅 วันที่</div><div class='metric-value'>{today_str}</div></div>", unsafe_allow_html=True)
            
            st.divider()
            df_admin = pd.merge(df_b, df_u[['username', 'fullname', 'phone']], on='username', how='left')
            for _, row in df_admin.sort_values(['date','time'], ascending=[False, True]).iterrows():
                if row['status'] == 'รอรับบริการ':
                    with st.expander(f"🔵 ⏰ {row['time']} | {row['fullname']} - {row['service']}"):
                        col_a, col_b = st.columns([3, 1])
                        col_a.write(f"📞 โทร: {row['phone']} | วันที่: {row['date']}")
                        if col_b.button("✅ เสร็จสิ้น", key=f"ok_{row['id']}"):
                            df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                            conn.update(worksheet="Bookings", data=df_b); st.rerun()

    with adm_t2:
        df_msg = get_data("Messages")
        if not df_msg.empty:
            target_u = st.selectbox("เลือกแชทลูกค้า", df_msg['username'].unique())
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for _, m in df_msg[df_msg['username'] == target_u].sort_values('msg_id').iterrows():
                cls = "user-msg" if m['sender'] == "user" else "admin-msg"
                st.markdown(f'<div class="bubble {cls}">{m["text"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            with st.form("admin_reply", clear_on_submit=True):
                rep = st.text_input("พิมพ์ตอบกลับ...")
                if st.form_submit_button("ส่ง") and rep:
                    new_m = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": target_u, "sender": "admin", "text": rep, "timestamp": datetime.now().strftime("%H:%M")}])
                    conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- 6. หน้าจองคิว (Booking & Chat) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.get('fullname', st.session_state.username)}")
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติ", "💬 แชทสอบถาม"])
    
    with t1:
        svc = st.selectbox("เลือกบริการ", list(SERVICES_BASE_PRICE.keys()))
        d = st.date_input("เลือกวันที่")
        t = st.selectbox("เวลา", TIME_SLOTS)
        if d.weekday() == 2: st.error("⚠️ ร้านหยุดวันพุธ")
        elif st.button("ยืนยันการจอง"):
            df_b = get_data("Bookings")
            new_id = str(int(datetime.now().timestamp()))
            new_r = pd.DataFrame([{"id":new_id, "username":st.session_state.username, "service":svc, "date":str(d), "time":t, "price":str(SERVICES_BASE_PRICE[svc]), "status":"รอรับบริการ"}])
            conn.update(worksheet="Bookings", data=pd.concat([df_b, new_r])); st.success("จองสำเร็จ!"); st.rerun()
    
    with t2:
        df_b = get_data("Bookings")
        st.dataframe(df_b[df_b['username'] == st.session_state.username].sort_values('date', ascending=False), use_container_width=True)

    with t3:
        df_msg = get_data("Messages")
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        my_m = df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id')
        for _, m in my_m.iterrows():
            cls = "user-msg" if m['sender'] == "user" else "admin-msg"
            st.markdown(f'<div class="bubble {cls}">{m["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        with st.form("u_chat", clear_on_submit=True):
            um = st.text_input("ถามคำถาม...")
            if st.form_submit_button("ส่ง"):
                new_m = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "sender": "user", "text": um, "timestamp": datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- หน้า Login / Register / ViewQueues คงเดิม ---
elif st.session_state.page == "Login":
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin'}); navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not user.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u, 'fullname':user.iloc[0]['fullname']}); navigate("Booking")
            else: st.error("ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Register":
    with st.form("reg"):
        nu, np, nf, nt = st.text_input("User"), st.text_input("Pass"), st.text_input("ชื่อจริง"), st.text_input("เบอร์โทร")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "phone":nt, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u])); st.success("สมัครสำเร็จ!"); navigate("Login")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_b = get_data("Bookings")
    st.dataframe(df_b[df_b['date'] == str(datetime.now().date())][['time', 'service', 'status']], use_container_width=True)
