import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS (จัดตำแหน่งแชท ซ้าย-ขวา) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold;}
        
        /* ⚪ กล่องหน้าต่างแชทสีขาว */
        .chat-window-box {
            background-color: #ffffff !important;
            border: 1px solid #dddddd;
            border-radius: 15px;
            padding: 20px;
            height: 480px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 10px;
        }
        
        /* 💬 Chat Bubbles Base */
        .bubble {
            padding: 10px 16px;
            border-radius: 20px;
            max-width: 70%;
            font-size: 14px;
            line-height: 1.4;
        }

        /* 🔵 ฝั่งเราส่ง (ชิดขวา - สีฟ้า) */
        .msg-right {
            align-self: flex-end;
            background-color: #0084FF;
            color: white !important;
            border-bottom-right-radius: 4px;
        }

        /* ⚪ ฝั่งเขาส่ง (ชิดซ้าย - สีเทา) */
        .msg-left {
            align-self: flex-start;
            background-color: #F0F0F0;
            color: #1A1A1A !important;
            border-bottom-left-radius: 4px;
            border: 1px solid #E0E0E0;
        }

        /* Price Card หน้าแรก */
        .price-card {
            background-color: #ffffff !important; padding: 15px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 10px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #1A1A1A !important;
        }
        .price-card b { color: #000000 !important; display: block; }
        .price-text { color: #FF4B4B !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df = df.dropna(how='all')
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        if 'username' in df.columns:
            df['username'] = df['username'].apply(lambda x: str(x).strip().zfill(10) if x.isdigit() else str(x))
        return df
    except: return pd.DataFrame()

# --- 2. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'selected_chat' not in st.session_state: st.session_state.selected_chat = None

def navigate(p):
    st.session_state.page = p
    st.rerun()

# --- HEADER MENU ---
st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)
m_cols = st.columns(5)
with m_cols[0]: 
    if st.button("🏠"): navigate("Home")
with m_cols[1]: 
    if st.button("📅"): navigate("ViewQueues")

if not st.session_state.logged_in:
    with m_cols[3]: 
        if st.button("📝"): navigate("Register")
    with m_cols[4]: 
        if st.button("🔑"): navigate("Login")
else:
    role = st.session_state.get('user_role')
    with m_cols[2]: 
        lbl = "📊" if role == 'admin' else "✂️"
        if st.button(lbl): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪"):
            st.session_state.clear()
            navigate("Home")

st.divider()

# --- 3. PAGE: HOME ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ 09:30 - 19:30 น. (หยุดวันพุธ)")
    services = {"✂️ ตัดผมชาย": "150-350", "💇‍♀️ ตัดผมหญิง": "350-800", "🚿 สระ-ไดร์": "200-450", "🎨 ทำสีผม": "1,500+", "✨ ยืดวอลลุ่ม": "1,000+"}
    p1, p2 = st.columns(2)
    for i, (n, p) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{n}</b><span class="price-text">{p} บาท</span></div>', unsafe_allow_html=True)

# --- 4. PAGE: BOOKING (Customer Chat) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.get('fullname')}")
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 แชทสอบถาม"])
    
    with t3:
        df_msg = get_data("Messages")
        st.markdown('<div class="chat-window-box">', unsafe_allow_html=True)
        if not df_msg.empty:
            my_chat = df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id')
            for _, m in my_chat.iterrows():
                # ลูกค้าใช้แอป: ถ้า sender คือ user (เราเอง) ชิดขวา / ถ้า admin ชิดซ้าย
                side = "msg-right" if m['sender'] == "user" else "msg-left"
                st.markdown(f'<div class="bubble {side}">{m["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("u_chat", clear_on_submit=True):
            c1, c2 = st.columns([4,1])
            txt = c1.text_input("พิมพ์...", label_visibility="collapsed")
            if c2.form_submit_button("ส่ง") and txt:
                new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "sender":"user", "text":txt}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m], ignore_index=True)); st.rerun()

# --- 5. PAGE: ADMIN (Messenger Chat) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 แอดมินจัดการร้าน")
    a1, a2 = st.tabs(["📉 รายการจอง", "💬 แชทลูกค้า (Messenger)"])
    
    with a2:
        df_msg = get_data("Messages")
        if not df_msg.empty:
            col_list, col_chat = st.columns([1, 2])
            with col_list:
                st.write("รายชื่อ")
                u_list = df_msg['username'].unique()
                for u in u_list:
                    if st.button(f"👤 {u}", key=f"ad_u_{u}"):
                        st.session_state.selected_chat = u
                        st.rerun()
            with col_chat:
                if st.session_state.selected_chat:
                    target = st.session_state.selected_chat
                    st.write(f"กำลังคุยกับ: {target}")
                    st.markdown('<div class="chat-window-box">', unsafe_allow_html=True)
                    chats = df_msg[df_msg['username'] == target].sort_values('msg_id')
                    for _, m in chats.iterrows():
                        # แอดมินใช้แอป: ถ้า sender คือ admin (เราเอง) ชิดขวา / ถ้า user ชิดซ้าย
                        side = "msg-right" if m['sender'] == "admin" else "msg-left"
                        st.markdown(f'<div class="bubble {side}">{m["text"]}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    with st.form("ad_chat", clear_on_submit=True):
                        c1, c2 = st.columns([4,1])
                        rep = c1.text_input("ตอบกลับ...", label_visibility="collapsed")
                        if c2.form_submit_button("ส่ง") and rep:
                            new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":target, "sender":"admin", "text":rep}])
                            conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m], ignore_index=True)); st.rerun()
                else: st.info("👈 เลือกแชทลูกค้าด้านซ้าย")

# --- 6. LOGIN & REGISTER ---
elif st.session_state.page == "Login":
    u = st.text_input("User (เบอร์โทร)")
    p = st.text_input("Pass", type="password")
    if st.button("ตกลง"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin'}); navigate("Admin")
        else:
            df_u = get_data("Users")
            u_clean = u.zfill(10) if u.isdigit() else u
            user = df_u[(df_u['username'] == u_clean) & (df_u['password'] == p)]
            if not user.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u_clean, 'fullname':user.iloc[0]['fullname']}); navigate("Booking")

elif st.session_state.page == "Register":
    with st.form("reg"):
        nu, np, nf = st.text_input("User"), st.text_input("Pass"), st.text_input("ชื่อจริง")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            nu_clean = nu.zfill(10) if nu.isdigit() else nu
            new_u = pd.DataFrame([{"username":nu_clean, "password":np, "fullname":nf, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True)); navigate("Login")

elif st.session_state.page == "ViewQueues":
    df_b = get_data("Bookings")
    active = df_b[(df_b['date'] == str(datetime.now().date())) & (df_b['status'] == 'รอรับบริการ')]
    st.table(active[['time', 'service']])
