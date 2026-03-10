import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & UI STYLE ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

SHOP_TEL = "0875644928"
FACEBOOK_URL = "https://www.facebook.com/yourpage" # เปลี่ยนเป็นลิงก์ของคุณ
LINE_URL = "https://line.me/ti/p/yourid"         # เปลี่ยนเป็นลิงก์ของคุณ
MAP_URL = "https://goo.gl/maps/yourlocation"    # เปลี่ยนเป็นลิงก์ GPS ของคุณ

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        .price-card {
            background-color: #ffffff; padding: 15px; border-radius: 12px;
            border-left: 5px solid #FF4B4B; margin-bottom: 10px; color: #1A1A1A;
            box-shadow: 1px 2px 8px rgba(0,0,0,0.1);
        }
        /* แชทสไตล์ */
        .chat-container { background-color: #f0f2f5; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
        .bubble { padding: 12px 18px; border-radius: 18px; margin-bottom: 10px; max-width: 80%; font-size: 16px; clear: both; display: block; }
        .user-msg { background-color: #0084FF; color: #FFFFFF !important; float: right; border-bottom-right-radius: 2px; }
        .admin-msg { background-color: #E4E6EB; color: #000000 !important; float: left; border-bottom-left-radius: 2px; }
        /* ปุ่ม Social */
        .social-btn { display: inline-block; padding: 10px 20px; border-radius: 8px; color: white; text-decoration: none; font-weight: bold; margin-right: 10px; text-align: center; }
        .fb-color { background-color: #1877F2; }
        .line-color { background-color: #00B900; }
        .gps-color { background-color: #EA4335; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. CORE DATA FUNCTIONS ---
def get_data(sheet_name, ttl_val=1):
    try:
        df = conn.read(worksheet=sheet_name, ttl=ttl_val)
        if df is None or df.empty:
            cols = {"Users": ['username', 'password', 'fullname', 'phone', 'role'],
                    "Bookings": ['id', 'username', 'service', 'date', 'time', 'status'],
                    "Messages": ['msg_id', 'username', 'sender', 'text', 'timestamp']}
            return pd.DataFrame(columns=cols.get(sheet_name, []))
        df.columns = [str(c).strip() for c in df.columns] 
        return df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
    except:
        return pd.DataFrame()

# --- 3. NAVIGATION SYSTEM ---
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
        label = "📊 หลังบ้าน" if role == 'admin' else "✂️ จองคิว"
        if st.button(label): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 4. PAGE LOGIC ---

# --- หน้าแรก (Home) + เพิ่ม Social & GPS กลับมา ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    
    st.subheader("💈 ยินดีต้อนรับสู่ 222-Salon")
    
    # ส่วนของปุ่ม Social Media & GPS
    st.markdown(f"""
        <div style="margin-bottom: 25px;">
            <a href="{FACEBOOK_URL}" target="_blank" class="social-btn fb-color">📘 Facebook</a>
            <a href="{LINE_URL}" target="_blank" class="social-btn line-color">💬 Line</a>
            <a href="{MAP_URL}" target="_blank" class="social-btn gps-color">📍 Google Maps (GPS)</a>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📞 **ติดต่อจองคิว:** {SHOP_TEL}\n\n📍 **พิกัด:** ร้านตั้งอยู่บนถนนเลี่ยงเมือง ใกล้แยกไฟแดง")
    with col2:
        st.success("✅ **เวลาทำการ:** 10:00 - 20:00 น. (เปิดทุกวัน)")
    
    st.write("### ✂️ เมนูและอัตราค่าบริการ")
    services = [["ตัดผมชาย", "100 - 150.-"], ["ตัดผมหญิง", "200 - 350.-"], ["สระ-ไดร์", "100 - 150.-"], ["ทำสีผม", "เริ่มต้น 500.-"]]
    for s in services:
        st.markdown(f'<div class="price-card"><b>{s[0]}</b> <span style="float:right;">{s[1]}</span></div>', unsafe_allow_html=True)

# --- หน้าดูคิว (ViewQueues) ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_v = get_data("Bookings", ttl_val=0)
    if not df_v.empty:
        st.dataframe(df_v[['service', 'date', 'time', 'status']], use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลคิวจอง")

# --- หน้า ADMIN (จัดการงาน + แชท) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 จัดการหลังบ้าน")
    t1, t2 = st.tabs(["📉 คิวงาน", "💬 แชทลูกค้า"])
    
    with t1:
        df_b = get_data("Bookings", ttl_val=0)
        pending = df_b[df_b['status'] == "รอรับบริการ"] if not df_b.empty else pd.DataFrame()
        if not pending.empty:
            for _, r in pending.sort_values(['date', 'time']).iterrows():
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"👤 {r['username']} | {r['service']} | {r['date']} ({r['time']})")
                if c2.button("✅ เสร็จ", key=f"ok_{r['id']}"):
                    df_b.loc[df_b['id'] == r['id'], 'status'] = "เสร็จสิ้น"
                    conn.update(worksheet="Bookings", data=df_b); st.rerun()
                if c3.button("🗑️ ลบ", key=f"del_{r['id']}", type="primary"):
                    conn.update(worksheet="Bookings", data=df_b[df_b['id'] != r['id']]); st.rerun()
        else: st.info("ไม่มีงานค้าง")
        
    with t2:
        df_msg = get_data("Messages", ttl_val=0)
        if not df_msg.empty:
            target = st.selectbox("เลือกแชทลูกค้า", df_msg['username'].unique())
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for _, m in df_msg[df_msg['username'] == target].sort_values('msg_id').iterrows():
                cls = "user-msg" if m['sender'] == "user" else "admin-msg"
                st.markdown(f'<div class="bubble {cls}">{m["text"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            with st.form("admin_chat", clear_on_submit=True):
                rep = st.text_input("ตอบกลับ...")
                if st.form_submit_button("ส่ง") and rep:
                    new_m = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": target, "sender": "admin", "text": rep, "timestamp": datetime.now().strftime("%H:%M")}])
                    conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- หน้าลูกค้า (Booking) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.fullname}")
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติ", "💬 แชท"])
    
    df_b = get_data("Bookings", ttl_val=0)
    
    with t1:
        d = st.date_input("เลือกวันที่", min_value=datetime.now().date())
        if not df_b[(df_b['username'] == st.session_state.username) & (df_b['date'] == str(d))].empty:
            st.warning("คุณมีการจองวันนี้แล้ว")
        else:
            slots = [f"{h:02d}:00" for h in range(10, 20)]
            valid = [s for s in slots if len(df_b[(df_b['date'] == str(d)) & (df_b['time'] == s)]) < 2]
            if not valid: st.error("คิวเต็ม")
            else:
                svc = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืดผม"])
                time_sel = st.selectbox("เวลา", valid)
                if st.button("✅ ยืนยันการจอง"):
                    new_row = pd.DataFrame([{"id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "service":svc, "date":str(d), "time":time_sel, "status":"รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_row])); st.success("จองแล้ว!"); st.rerun()

    with t2:
        my_q = df_b[df_b['username'] == st.session_state.username].sort_values(['date', 'time'], ascending=False)
        for _, r in my_q.iterrows():
            st.markdown(f'<div class="price-card">📅 {r["date"]} | {r["time"]} | {r["status"]}</div>', unsafe_allow_html=True)

    with t3:
        df_msg = get_data("Messages", ttl_val=0)
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for _, m in df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id').iterrows():
            cls = "user-msg" if m['sender'] == "user" else "admin-msg"
            st.markdown(f'<div class="bubble {cls}">{m["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        with st.form("u_chat", clear_on_submit=True):
            um = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง") and um:
                new_m = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "sender": "user", "text": um, "timestamp": datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- LOGIN / REGISTER ---
elif st.session_state.page == "Login":
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Login"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin', 'fullname':'แอดมิน'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not user.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u, 'fullname':user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Register":
    with st.form("reg"):
        nu, np, nf, nt = st.text_input("User"), st.text_input("Pass"), st.text_input("ชื่อ"), st.text_input("โทร")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "phone":nt, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u])); navigate("Login")
