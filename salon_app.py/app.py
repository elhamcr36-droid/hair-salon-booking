import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอและสไตล์ (UI/UX) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# ข้อมูลการติดต่อร้าน
SHOP_LOCATION_URL = "https://www.google.com/maps/place/222+%E0%B8%96%E0%B8%99%E0%B8%99+%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B8%9A%E0%B8%B2%E0%B8%A5+1+%E0%B8%95%E0%B8%B3%E0%B8%9A%E0%B8%A5%E0%B8%9A%E0%B9%88%E0%B8%AD%E0%B8%A2%E0%B8%B2%E0%B8%87+%E0%B8%AD%E0%B8%B3%E0%B9%80%E0%B8%A0%E0%B8%AD%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+90000/@7.1915128,100.6007972,17z/data=!3m1!4b1!4m6!3m5!1s0x304d3323c7ad029d:0x7cfb098f4f859e4c!8m2!3d7.1915128!4d100.6007972!16s%2Fg%2F11jylj3r6y?entry=ttu&g_ep=EgoyMDI2MDMwOC4wIKXMDSoASAFQAw%3D%3D" 
LINE_ID = "222Salon"
LINE_URL = f"https://line.me/ti/p/~{LINE_ID}"
FB_URL = "https://www.facebook.com/222Salon" 
SHOP_TEL = "0875644928"

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        .price-card {
            background-color: #ffffff !important; padding: 15px; border-radius: 12px;
            border-left: 5px solid #FF4B4B; margin-bottom: 10px;
            box-shadow: 1px 2px 8px rgba(0,0,0,0.1); color: #1A1A1A !important;
            min-height: 100px;
        }
        .chat-bubble {
            padding: 10px 15px; border-radius: 15px; margin-bottom: 5px;
            display: inline-block; max-width: 80%; line-height: 1.4;
        }
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
    
    # ส่วนข้อมูลการติดต่อ
    st.markdown("### 📞 ติดต่อเรา")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.info(f"⏰ 09:30 - 19:30 น.\n(หยุดวันพุธ)")
    with c2: st.link_button("📍 แผนที่ร้าน (GPS)", SHOP_LOCATION_URL, type="primary")
    with c3: st.link_button(f"🔵 Facebook: 222Salon", FB_URL)
    with c4: st.link_button(f"🟢 Line: {LINE_ID}", LINE_URL)
    st.markdown(f"**📱 โทรจอง:** [**{SHOP_TEL}**](tel:{SHOP_TEL})")
    
    st.divider()
    
    # --- รายการราคาและบริการทั้งหมด ---
    st.subheader("📋 ราคาและบริการทั้งหมด")
    
    services = {
        "✂️ งานตัดผม": {
            "ตัดผมชาย (Men's Cut)": "150 - 300",
            "ตัดผมหญิง (Women's Cut)": "300 - 600",
            "ตัดผมเด็ก": "100 - 150",
            "โกนหนวด/แต่งเครา": "80 - 150"
        },
        "🚿 งานสระไดร์/สปา": {
            "สระ-ไดร์ (Wash & Blow)": "150 - 350",
            "สระ-เซ็ต/ม้วนลอน": "250 - 450",
            "ดีท็อกซ์หนังศีรษะ": "500 - 900",
            "อบไอน้ำบำรุงผม": "300 - 600"
        },
        "🎨 งานเคมี (สี/ยืด/ดัด)": {
            "ทำสีผม (Hair Color)": "1,500 - 4,500",
            "ฟอกสีผม (Bleaching)": "1,000 - 2,500",
            "ยืดผมถาวร/วอลลุ่ม": "1,500 - 5,500",
            "ดัดผมดิจิตอล": "2,000 - 4,500",
            "เคราตินทรีทเม้นท์": "1,500 - 3,500"
        }
    }

    for category, items in services.items():
        st.markdown(f"#### {category}")
        cols = st.columns(2)
        for i, (name, price) in enumerate(items.items()):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="price-card">
                    <div style="font-weight: bold; font-size: 1.1em;">{name}</div>
                    <div style="color: #FF4B4B; font-size: 1.2em; font-weight: bold;">{price} ฿</div>
                </div>
                """, unsafe_allow_html=True)

# --- 5. หน้าแอดมิน (Admin) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการร้านและข้อความ")
    t_admin1, t_admin2 = st.tabs(["📈 จัดการคิว", "💬 แชทกับลูกค้า"])
    
    with t_admin1:
        df_b = get_data("Bookings")
        if not df_b.empty:
            for _, row in df_b.iterrows():
                with st.expander(f"⏰ {row['time']} | {row['service']}"):
                    if st.button("🗑️ ลบคิว", key=f"del_{row['id']}"):
                        conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']]); st.rerun()

    with t_admin2:
        df_msg = get_data("Messages")
        user_map = get_user_map()
        if not df_msg.empty:
            u_options = {u: f"{user_map.get(u, u)} (@{u})" for u in df_msg['username'].unique()}
            target_user = st.selectbox("เลือกแชทกับลูกค้า:", options=list(u_options.keys()), format_func=lambda x: u_options[x])
            chat_box = df_msg[df_msg['username'] == target_user].sort_values('msg_id')
            for _, m in chat_box.iterrows():
                align = "left" if m['sender'] == "user" else "right"
                cls = "user-bubble" if m['sender'] == "user" else "admin-bubble"
                d_name = user_map.get(target_user, target_user) if m['sender'] == "user" else "แอดมิน"
                st.markdown(f"<div style='text-align: {align};'><div class='chat-bubble {cls}'><b>{d_name}:</b> {m['text']}</div></div>", unsafe_allow_html=True)
            with st.form("admin_reply", clear_on_submit=True):
                rep = st.text_input("พิมพ์ข้อความ...")
                if st.form_submit_button("ส่ง"):
                    new_r = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": target_user, "sender": "admin", "text": rep, "timestamp": datetime.now().strftime("%H:%M")}])
                    conn.update(worksheet="Messages", data=pd.concat([df_msg, new_r], ignore_index=True)); st.rerun()

# --- 6. หน้าจองคิว & แชท (User) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 คุณ {st.session_state.get('fullname', '')}")
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง", "💬 ติดต่อเรา"])
    
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
                with st.popover("📝 จัดการข้อความ"):
                    new_txt = st.text_input("แก้ไข", value=m['text'], key=f"edt_{m['msg_id']}")
                    if st.button("💾 บันทึก", key=f"sav_{m['msg_id']}"):
                        df_msg.loc[df_msg['msg_id'] == m['msg_id'], 'text'] = new_txt
                        conn.update(worksheet="Messages", data=df_msg); st.rerun()
                    if st.button("🗑️ ลบ", key=f"del_{m['msg_id']}", type="primary"):
                        conn.update(worksheet="Messages", data=df_msg[df_msg['msg_id'] != m['msg_id']]); st.rerun()
        with st.form("u_send", clear_on_submit=True):
            u_msg = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง"):
                row = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "sender": "user", "text": u_msg, "timestamp": datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, row], ignore_index=True)); st.rerun()

# --- ส่วน Login / Register / ViewQueues (คงเดิมจากโค้ดก่อนหน้า) ---
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
