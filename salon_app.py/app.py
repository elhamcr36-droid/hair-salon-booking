import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. Configuration & Style ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# ข้อมูลติดต่อร้าน
SHOP_LOCATION_URL = "https://maps.google.com" 
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
            border-left: 5px solid #FF4B4B; margin-bottom: 10px; color: #1A1A1A !important;
            box-shadow: 1px 2px 8px rgba(0,0,0,0.1); min-height: 80px;
        }
        .chat-bubble { padding: 10px 15px; border-radius: 15px; margin-bottom: 5px; display: inline-block; max-width: 80%; }
        .user-bubble { background-color: #E1FFC7; color: #000; border-bottom-right-radius: 2px; }
        .admin-bubble { background-color: #F0F0F0; color: #000; border-bottom-left-radius: 2px; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. Data Helper Functions ---
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

# --- 3. Navigation Logic ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon </h1>", unsafe_allow_html=True)
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

# --- 4. Page: Home (ราคาและบริการทั้งหมด) ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.info(f"⏰ 09:30 - 19:30 น.\n(หยุดวันพุธ)")
    with c2: st.link_button("📍 แผนที่ (GPS)", SHOP_LOCATION_URL, type="primary")
    with c3: st.link_button(f"🔵 Facebook", FB_URL)
    with c4: st.link_button(f"🟢 Line", LINE_URL)
    st.markdown(f"**📱 โทรจอง/สอบถาม:** [**{SHOP_TEL}**](tel:{SHOP_TEL})")
    
    st.divider()
    st.subheader("📋 ราคาและบริการทั้งหมด (Price List)")
    
    services_list = {
        "✂️ งานตัดผม": {"ตัดผมชาย (Men)": "150-300", "ตัดผมหญิง (Women)": "300-600", "ตัดผมเด็ก": "100-150"},
        "🚿 งานสระ/สปา": {"สระ-ไดร์": "150-350", "ดีท็อกซ์หนังศีรษะ": "500-900", "อบไอน้ำ": "300-600"},
        "🎨 งานเคมี": {"ทำสีผม": "1,500+", "ยืดผม/วอลลุ่ม": "1,500+", "เคราติน": "1,500+"}
    }
    for cat, items in services_list.items():
        st.markdown(f"#### {cat}")
        cols = st.columns(3)
        for i, (n, p) in enumerate(items.items()):
            cols[i%3].markdown(f'<div class="price-card"><b>{n}</b><br><span style="color:#FF4B4B">{p} ฿</span></div>', unsafe_allow_html=True)

# --- 5. Page: Admin (หลังบ้าน & แชท) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการหลังบ้าน")
    t_a1, t_a2 = st.tabs(["📈 จัดการคิว", "💬 แชทกับลูกค้า"])
    
    with t_a1:
        df_b = get_data("Bookings")
        if not df_b.empty:
            st.write("รายการจองทั้งหมด")
            st.dataframe(df_b.sort_values(['date', 'time'], ascending=False), use_container_width=True)
            for _, row in df_b.iterrows():
                if st.button(f"🗑️ ลบคิว: {row['service']} ({row['date']})", key=f"del_b_{row['id']}"):
                    conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']]); st.rerun()

    with t_a2:
        df_msg = get_data("Messages")
        user_map = get_user_map()
        if not df_msg.empty:
            u_list = df_msg['username'].unique()
            u_options = {u: f"{user_map.get(u, u)} (@{u})" for u in u_list}
            target = st.selectbox("เลือกแชทกับลูกค้า:", options=list(u_options.keys()), format_func=lambda x: u_options[x])
            
            for _, m in df_msg[df_msg['username'] == target].sort_values('msg_id').iterrows():
                align = "left" if m['sender'] == "user" else "right"
                cls = "user-bubble" if m['sender'] == "user" else "admin-bubble"
                d_name = user_map.get(target, target) if m['sender'] == "user" else "แอดมิน"
                st.markdown(f"<div style='text-align: {align};'><div class='chat-bubble {cls}'><b>{d_name}:</b> {m['text']}</div></div>", unsafe_allow_html=True)
            
            with st.form("admin_reply", clear_on_submit=True):
                rep = st.text_input("พิมพ์ข้อความตอบกลับ...")
                if st.form_submit_button("ส่ง"):
                    new_r = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": target, "sender": "admin", "text": rep, "timestamp": datetime.now().strftime("%H:%M")}])
                    conn.update(worksheet="Messages", data=pd.concat([df_msg, new_r], ignore_index=True)); st.rerun()

# --- 6. Page: Booking (จองคิว & แชทลูกค้า) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.fullname}")
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง", "💬 ติดต่อแอดมิน"])
    
    with t1:
        st.write("### กรอกข้อมูลการจอง")
        all_svcs = ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืดผม/วอลลุ่ม", "เคราติน"]
        svc = st.selectbox("บริการที่ต้องการ", all_svcs)
        d = st.date_input("วันที่", min_value=datetime.now().date())
        t = st.selectbox("เวลา", [f"{h:02d}:00" for h in range(10, 19)])
        if st.button("✅ ยืนยันจองคิว"):
            df_b = get_data("Bookings")
            new_id = str(int(datetime.now().timestamp()))
            new_row = pd.DataFrame([{"id":new_id, "username":st.session_state.username, "service":svc, "date":str(d), "time":t, "price":"-", "status":"รอรับบริการ"}])
            conn.update(worksheet="Bookings", data=pd.concat([df_b, new_row], ignore_index=True))
            st.success("จองคิวสำเร็จแล้ว!"); st.rerun()

    with t2:
        df_b = get_data("Bookings")
        st.dataframe(df_b[df_b['username'] == st.session_state.username], use_container_width=True)

    with t3:
        st.write(f"### 💬 แชท (ในนาม: {st.session_state.fullname})")
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
                    c1, c2 = st.columns(2)
                    if c1.button("💾 บันทึก", key=f"s_{m['msg_id']}"):
                        df_msg.loc[df_msg['msg_id'] == m['msg_id'], 'text'] = new_txt
                        conn.update(worksheet="Messages", data=df_msg); st.rerun()
                    if c2.button("🗑️ ลบ", key=f"d_{m['msg_id']}", type="primary"):
                        conn.update(worksheet="Messages", data=df_msg[df_msg['msg_id'] != m['msg_id']]); st.rerun()
        with st.form("u_msg", clear_on_submit=True):
            u_msg = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง"):
                new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "sender":"user", "text":u_msg, "timestamp":datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m], ignore_index=True)); st.rerun()

# --- 7. Login & Register ---
elif st.session_state.page == "Login":
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
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
        nu, np, nf = st.text_input("Username"), st.text_input("Password"), st.text_input("ชื่อ-นามสกุลจริง")
        if st.form_submit_button("สมัครสมาชิก"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True)); navigate("Login")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    st.dataframe(get_data("Bookings"), use_container_width=True)

