import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอและสไตล์ (UI/UX) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# ข้อมูลร้าน
SHOP_LOCATION_URL = "https://www.google.com/maps/place/222+%E0%B8%96%E0%B8%99%E0%B8%99+%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B8%9A%E0%B8%B2%E0%B8%A5+1+%E0%B8%95%E0%B8%B3%E0%B8%9A%E0%B8%A5%E0%B8%9A%E0%B9%88%E0%B8%AD%E0%B8%A2%E0%B8%B2%E0%B8%87+%E0%B8%AD%E0%B8%B3%E0%B9%80%E0%B8%A0%E0%B8%AD%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+90000/@7.1915128,100.6007972,17z/data=!3m1!4b1!4m6!3m5!1s0x304d3323c7ad029d:0x7cfb098f4f859e4c!8m2!3d7.1915128!4d100.6007972!16s%2Fg%2F11jylj3r6y?entry=ttu&g_ep=EgoyMDI2MDMwOC4wIKXMDSoASAFQAw%3D%3D" 
LINE_ID = "222Salon"
LINE_URL = f"https://line.me/ti/p/~{LINE_ID}"
FB_URL = "https://www.facebook.com/222Salon" 
SHOP_TEL = "0875644928"

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        .price-card {
            background-color: #ffffff !important; padding: 15px; border-radius: 12px;
            border-left: 5px solid #FF4B4B; margin-bottom: 10px; color: #1A1A1A !important;
            box-shadow: 1px 2px 8px rgba(0,0,0,0.1);
        }
        .chat-bubble { padding: 10px 15px; border-radius: 15px; margin-bottom: 5px; display: inline-block; max-width: 80%; }
        .user-bubble { background-color: #E1FFC7; color: #000; border-bottom-right-radius: 2px; }
        .admin-bubble { background-color: #F0F0F0; color: #000; border-bottom-left-radius: 2px; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. ฟังก์ชันจัดการข้อมูล ---
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        return df
    except: return pd.DataFrame()

def get_user_map():
    df_u = get_data("Users")
    if not df_u.empty: return dict(zip(df_u['username'], df_u['fullname']))
    return {}

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
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 4. หน้าแรก (Home) ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.info(f"⏰ 09:30 - 19:30 น.\n(หยุดวันพุธ)")
    with c2: st.link_button("📍 แผนที่ (GPS)", SHOP_LOCATION_URL, type="primary")
    with c3: st.link_button(f"🔵 Facebook", FB_URL)
    with c4: st.link_button(f"🟢 Line", LINE_URL)
    st.markdown(f"**📱 โทรจอง:** [**{SHOP_TEL}**](tel:{SHOP_TEL})")
    
    st.divider()
    st.subheader("📋 ราคาและบริการทั้งหมด")
    services_list = {
        "✂️ งานตัดผม": {"ตัดผมชาย": "150-300", "ตัดผมหญิง": "300-600", "ตัดผมเด็ก": "100-150"},
        "🚿 งานสระ/สปา": {"สระ-ไดร์": "150-350", "ดีท็อกซ์หนังศีรษะ": "500-900", "อบไอน้ำ": "300-600"},
        "🎨 งานเคมี": {"ทำสีผม": "1,500+", "ยืดผม/วอลลุ่ม": "1,500+", "เคราติน": "1,500+"}
    }
    for cat, items in services_list.items():
        st.markdown(f"#### {cat}")
        cols = st.columns(3)
        for i, (n, p) in enumerate(items.items()):
            cols[i%3].markdown(f'<div class="price-card"><b>{n}</b><br><span style="color:#FF4B4B">{p} ฿</span></div>', unsafe_allow_html=True)

# --- 5. หน้าจองคิว (Booking) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 คุณ {st.session_state.fullname}")
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง", "💬 ติดต่อเรา"])
    
    with t1:
        st.write("### กรอกข้อมูลเพื่อจองคิว")
        df_b = get_data("Bookings")
        all_services = ["ตัดผมชาย", "ตัดผมหญิง", "ตัดผมเด็ก", "สระ-ไดร์", "ดีท็อกซ์หนังศีรษะ", "อบไอน้ำ", "ทำสีผม", "ยืดผม/วอลลุ่ม", "เคราติน"]
        svc = st.selectbox("เลือกบริการ", all_services)
        d = st.date_input("เลือกวันที่จอง", min_value=datetime.now().date())
        t = st.selectbox("เลือกเวลา", [f"{h:02d}:00" for h in range(10, 19)])
        
        if st.button("✅ ยืนยันการจองคิว"):
            new_id = str(int(datetime.now().timestamp()))
            new_row = pd.DataFrame([{"id": new_id, "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "price": "ตามตกลง", "status": "รอรับบริการ"}])
            conn.update(worksheet="Bookings", data=pd.concat([df_b, new_row], ignore_index=True))
            st.success("จองคิวสำเร็จ! แอดมินจะรีบตรวจสอบครับ")
            
    with t2:
        df_b = get_data("Bookings")
        my_b = df_b[df_b['username'] == st.session_state.username].sort_values('date', ascending=False)
        st.dataframe(my_b, use_container_width=True)

    with t3:
        st.write(f"### 💬 คุยกับแอดมิน (ในนาม: {st.session_state.fullname})")
        df_msg = get_data("Messages")
        my_msgs = df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id')
        for _, m in my_msgs.iterrows():
            align = "right" if m['sender'] == "user" else "left"
            cls = "user-bubble" if m['sender'] == "user" else "admin-bubble"
            d_name = st.session_state.fullname if m['sender'] == "user" else "แอดมิน"
            st.markdown(f"<div style='text-align: {align};'><div class='chat-bubble {cls}'><b>{d_name}:</b> {m['text']}</div></div>", unsafe_allow_html=True)
            if m['sender'] == "user":
                with st.popover("📝 จัดการ"):
                    new_txt = st.text_input("แก้ไข", value=m['text'], key=f"e_{m['msg_id']}")
                    c1, c2 = st.columns(2)
                    if c1.button("💾 บันทึก", key=f"s_{m['msg_id']}"):
                        df_msg.loc[df_msg['msg_id'] == m['msg_id'], 'text'] = new_txt
                        conn.update(worksheet="Messages", data=df_msg); st.rerun()
                    if c2.button("🗑️ ลบ", key=f"d_{m['msg_id']}", type="primary"):
                        conn.update(worksheet="Messages", data=df_msg[df_msg['msg_id'] != m['msg_id']]); st.rerun()
        with st.form("u_send", clear_on_submit=True):
            u_msg = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง"):
                new_msg = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "sender": "user", "text": u_msg, "timestamp": datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_msg], ignore_index=True)); st.rerun()

# --- ส่วนอื่นๆ (Admin / Login / Register) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 หลังบ้าน")
    t_a1, t_a2 = st.tabs(["คิวลูกค้า", "แชท"])
    with t_a1:
        df_b = get_data("Bookings")
        st.write("รายการคิวทั้งหมด")
        st.dataframe(df_b, use_container_width=True)
    with t_a2:
        df_msg = get_data("Messages")
        user_map = get_user_map()
        if not df_msg.empty:
            target = st.selectbox("เลือกแชท:", df_msg['username'].unique(), format_func=lambda x: f"{user_map.get(x, x)} (@{x})")
            for _, m in df_msg[df_msg['username'] == target].iterrows():
                st.write(f"**{user_map.get(m['username'], m['username'])}**: {m['text']}")

elif st.session_state.page == "Login":
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
        df_u = get_data("Users")
        user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin', 'fullname':'แอดมิน'}); navigate("Admin")
        elif not user.empty:
            st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u, 'fullname':user.iloc[0]['fullname']}); navigate("Booking")
        else: st.error("ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Register":
    with st.form("reg"):
        nu, np, nf = st.text_input("Username"), st.text_input("Password"), st.text_input("ชื่อ-นามสกุล")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True)); navigate("Login")

elif st.session_state.page == "ViewQueues":
    st.write("### รายการคิวจองวันนี้")
    st.dataframe(get_data("Bookings"), use_container_width=True)
