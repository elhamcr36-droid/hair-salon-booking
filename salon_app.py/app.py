import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS (Messenger Style & High Contrast) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

SHOP_LOCATION_URL = "https://maps.google.com" 

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold;}
        
        /* 📱 Messenger Style Layout (Admin) */
        .chat-sidebar-box {
            background-color: #f0f2f5; padding: 15px; border-radius: 15px;
            height: 550px; overflow-y: auto; border: 1px solid #ddd;
        }
        .chat-window-box {
            background-color: #ffffff; border: 1px solid #ddd; border-radius: 15px;
            padding: 20px; height: 450px; overflow-y: auto;
            display: flex; flex-direction: column; gap: 10px;
        }
        
        /* 💬 Chat Bubbles */
        .bubble { padding: 10px 15px; border-radius: 18px; max-width: 75%; font-size: 14px; margin-bottom: 2px; }
        .admin-msg { align-self: flex-end; background-color: #0084FF; color: white !important; border-bottom-right-radius: 2px; }
        .user-msg { align-self: flex-start; background-color: #E4E6EB; color: #1A1A1A !important; border-bottom-left-radius: 2px; }

        /* 📋 Price Card (Fix Invisible Text) */
        .price-card {
            background-color: #ffffff !important; padding: 15px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 10px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #1A1A1A !important;
        }
        .price-card b { color: #000000 !important; display: block; font-size: 1.1rem; }
        .price-text { color: #FF4B4B !important; font-weight: bold; }

        /* Dashboard Metrics */
        .metric-card {
            background-color: #ffffff; padding: 20px; border-radius: 15px;
            border: 2px solid #FF4B4B; text-align: center; color: #1A1A1A;
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
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        # 📍 จัดการเลข 0 นำหน้าเบอร์โทร/Username
        for col in ['username', 'phone']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(x).strip().zfill(10) if x and str(x).isdigit() else str(x))
        return df
    except: return pd.DataFrame()

# --- 2. NAVIGATION & STATE ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'selected_chat' not in st.session_state: st.session_state.selected_chat = None

def navigate(p):
    st.session_state.page = p
    st.rerun()

# --- TOP MENU ---
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
        lbl = "📊 จัดการร้าน" if role == 'admin' else "✂️ จองคิว"
        if st.button(lbl): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪 ออก"):
            st.session_state.clear()
            navigate("Home")

st.divider()

# --- 3. PAGE: HOME ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ เปิด 09:30 - 19:30 น. (หยุดวันพุธ)")
    st.subheader("📋 บริการของเรา")
    services = {"✂️ ตัดผมชาย": "150-350", "💇‍♀️ ตัดผมหญิง": "350-800", "🚿 สระ-ไดร์": "200-450", "🎨 ทำสีผม": "1,500+", "✨ ยืดวอลลุ่ม": "1,000+"}
    p1, p2 = st.columns(2)
    for i, (n, p) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{n}</b><span class="price-text">{p} บาท</span></div>', unsafe_allow_html=True)
    st.link_button("📍 นำทางด้วย GPS", SHOP_LOCATION_URL, type="primary")

# --- 4. PAGE: ADMIN (Messenger Style) ---
elif st.session_state.page == "Admin":
    t_admin1, t_admin2 = st.tabs(["📉 สรุปงาน", "💬 Messenger แชทลูกค้า"])
    
    with t_admin1:
        df_b = get_data("Bookings")
        if not df_b.empty:
            today = datetime.now().strftime("%Y-%m-%d")
            df_today = df_b[df_b['date'] == today]
            c1, c2 = st.columns(2)
            c1.markdown(f"<div class='metric-card'>👥 ลูกค้าวันนี้: {len(df_today)} ท่าน</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-card'>📅 วันที่: {today}</div>", unsafe_allow_html=True)
            st.write("---")
            for _, row in df_b[df_b['status'] == 'รอรับบริการ'].iterrows():
                col_x, col_y = st.columns([4, 1])
                col_x.write(f"⏰ {row['time']} | {row['username']} - {row['service']}")
                if col_y.button("✅ เสร็จ", key=f"finish_{row['id']}"):
                    df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                    conn.update(worksheet="Bookings", data=df_b); st.rerun()

    with t_admin2:
        df_msg = get_data("Messages")
        df_users = get_data("Users")
        if not df_msg.empty:
            col_list, col_chat = st.columns([1, 2])
            with col_list:
                st.markdown("### 👥 รายชื่อลูกค้า")
                u_list = df_msg['username'].unique()
                for u in u_list:
                    user_info = df_users[df_users['username'] == u]
                    name = user_info['fullname'].iloc[0] if not user_info.empty else u
                    if st.button(f"👤 {name}", key=f"list_{u}"):
                        st.session_state.selected_chat = u
                        st.rerun()
            with col_chat:
                if st.session_state.selected_chat:
                    target = st.session_state.selected_chat
                    st.markdown(f"### 💬 คุยกับคุณ: {target}")
                    st.markdown('<div class="chat-window-box">', unsafe_allow_html=True)
                    chats = df_msg[df_msg['username'] == target].sort_values('msg_id')
                    for _, m in chats.iterrows():
                        cls = "admin-msg" if m['sender'] == "admin" else "user-msg"
                        st.markdown(f'<div class="bubble {cls}">{m["text"]}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    with st.form("admin_send", clear_on_submit=True):
                        c_in, c_btn = st.columns([4, 1])
                        txt = c_in.text_input("พิมพ์...", label_visibility="collapsed")
                        if c_btn.form_submit_button("ส่ง") and txt:
                            new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":target, "sender":"admin", "text":txt}])
                            conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m], ignore_index=True)); st.rerun()
                else: st.info("👈 เลือกรายชื่อเพื่อดูแชท")

# --- 5. PAGE: BOOKING (Customer) ---
elif st.session_state.page == "Booking":
    st.subheader(f"สวัสดีคุณ {st.session_state.fullname}")
    tb1, tb2, tb3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 แชทสอบถาม"])
    with tb1:
        svc = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม"])
        d = st.date_input("วันที่")
        t = st.selectbox("เวลา", [f"{h:02d}:00" for h in range(10, 19)])
        if st.button("ยืนยัน"):
            df_b = get_data("Bookings")
            new_q = pd.DataFrame([{"id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "service":svc, "date":str(d), "time":t, "price":"0", "status":"รอรับบริการ"}])
            conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True)); st.success("จองแล้ว!"); navigate("Booking")
    with tb3:
        df_msg = get_data("Messages")
        st.markdown('<div class="chat-window-box">', unsafe_allow_html=True)
        my_chat = df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id')
        for _, m in my_chat.iterrows():
            cls = "admin-msg" if m['sender'] == "user" else "user-msg" # user ส่งอยู่ขวา (สีฟ้า)
            st.markdown(f'<div class="bubble {cls}">{m["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        with st.form("u_msg", clear_on_submit=True):
            tx = st.text_input("ถามร้าน...")
            if st.form_submit_button("ส่ง") and tx:
                new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "sender":"user", "text":tx}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m], ignore_index=True)); st.rerun()

# --- 6. LOGIN & REGISTER ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u = st.text_input("Username (เบอร์โทร)")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin'}); navigate("Admin")
        else:
            df_u = get_data("Users")
            u_clean = u.zfill(10) if u.isdigit() else u
            user = df_u[(df_u['username'] == u_clean) & (df_u['password'] == p)]
            if not user.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u_clean, 'fullname':user.iloc[0]['fullname']}); navigate("Booking")
            else: st.error("ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nu, np, nf = st.text_input("Username (เบอร์โทร)"), st.text_input("Password"), st.text_input("ชื่อจริง")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            nu_clean = nu.zfill(10) if nu.isdigit() else nu
            new_u = pd.DataFrame([{"username":nu_clean, "password":np, "fullname":nf, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True)); navigate("Login")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิววันนี้")
    df_b = get_data("Bookings")
    active = df_b[(df_b['date'] == str(datetime.now().date())) & (df_b['status'] == 'รอรับบริการ')]
    st.dataframe(active[['time', 'service']].sort_values('time'), use_container_width=True)
