import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon Songkhla", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; height: 3.2em; transition: 0.3s;}
        .price-card {
            background-color: #ffffff !important; padding: 18px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 12px;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.08); color: #000000 !important;
        }
        /* Messenger Style Chat */
        [data-testid="stChatMessage"][data-testid^="stChatMessageUser"] {
            flex-direction: row-reverse !important; background-color: #0084FF !important;
            color: white !important; border-radius: 15px 15px 2px 15px !important;
            margin-left: auto !important; width: fit-content !important; max-width: 85% !important;
        }
        [data-testid="stChatMessage"][data-testid^="stChatMessageAssistant"] {
            background-color: #E4E6EB !important; color: black !important;
            border-radius: 15px 15px 15px 2px !important;
            margin-right: auto !important; width: fit-content !important; max-width: 85% !important;
        }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. DATA ENGINE ---
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df is None or df.empty: return pd.DataFrame()
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
            if 'phone' in col or 'username' in col:
                df[col] = df[col].apply(lambda x: '0' + x if len(x) == 9 and x.isdigit() else x)
        return df
    except:
        return pd.DataFrame()

# --- 3. NAVIGATION & NOTIFICATION LOGIC ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# ดึงข้อมูลมาเช็คสถานะการแจ้งเตือน
df_b_now = get_data("Bookings")
df_c_now = get_data("Chats")

# เช็คจุดแดงคิว
show_q_dot = False
if 'last_b_count' in st.session_state:
    if len(df_b_now) > st.session_state.last_b_count:
        show_q_dot = True
else:
    st.session_state.last_b_count = len(df_b_now)

# เช็คจุดแดงแชท
show_c_dot = False
if not df_c_now.empty and df_c_now.iloc[-1]['sender'] == 'user':
    show_c_dot = True

# รีเฟรชอัตโนมัติทุก 30 วินาที
if st.session_state.logged_in:
    st_autorefresh(interval=30000, key="nav_refresh")

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon @สงขลา</h1>", unsafe_allow_html=True)
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
    if role == 'admin':
        with m_cols[2]:
            admin_btn_label = "📊 จัดการร้าน 🔴" if (show_q_dot or show_c_dot) else "📊 จัดการร้าน"
            if st.button(admin_btn_label): navigate("Admin")
    else:
        with m_cols[2]: 
            if st.button("✂️ จองคิว"): navigate("Booking")
    with m_cols[4]:
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")
st.divider()

# --- 4. PAGE CONTENT ---

if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+" }
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span style="float:right; color:#FF4B4B;">{price}</span></div>', unsafe_allow_html=True)

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg"):
        nf, nu, np = st.text_input("ชื่อ-นามสกุล"), st.text_input("เบอร์โทรศัพท์"), st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"phone": nu.strip(), "password": np.strip(), "fullname": nf.strip(), "role": "user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
            st.success("✅ สมัครสำเร็จ!"); time.sleep(1); navigate("Login")

elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in, p_in = st.text_input("เบอร์โทรศัพท์"), st.text_input("รหัสผ่าน", type="password")
    if st.button("ตกลง", type="primary"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': u_in, 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_in.strip()) & (df_u['password'] == p_in.strip())] if not df_u.empty else pd.DataFrame()
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': user.iloc[0]['role'], 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")

elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 แชทสอบถาม"])
    with t1:
        with st.form("b"):
            bd = st.date_input("วันที่", min_value=datetime.now().date())
            bt = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"])
            bs = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยัน"):
                new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(bd), "time": bt, "service": bs, "status": "รอรับบริการ", "price": "0"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_b_now, new_q], ignore_index=True))
                st.success("✅ จองสำเร็จ!"); time.sleep(1); st.rerun()
    with t2:
        for _, r in df_b_now[df_b_now['username'] == st.session_state.username].iloc[::-1].iterrows():
            st.write(f"📅 {r['date']} | ⏰ {r['time']} | {r['service']} | `{r['status']}`")
    with t3:
        for _, m in df_c_now[df_c_now['username'] == st.session_state.username].iterrows():
            with st.chat_message("user" if m['sender']=="user" else "assistant"): st.write(m['msg'])
        if p := st.chat_input("ถามร้าน..."):
            new_m = pd.DataFrame([{"username": st.session_state.username, "sender": "user", "msg": p, "time": datetime.now().strftime("%H:%M")}])
            conn.update(worksheet="Chats", data=pd.concat([df_c_now, new_m], ignore_index=True)); st.rerun()

elif st.session_state.page == "Admin" and st.session_state.logged_in:
    # กำหนดหัวข้อ Tab แบบมีจุดแดงแยกกัน
    tab_q_label = "📅 จัดการคิว 🔴" if show_q_dot else "📅 จัดการคิว"
    tab_c_label = "📩 แชทลูกค้า 🔴" if show_c_dot else "📩 แชทลูกค้า"
    
    at1, at2, at3 = st.tabs(["📊 สรุปยอด", tab_q_label, tab_c_label])
    
    with at1:
        done = df_b_now[df_b_now['status'] == "เสร็จสิ้น"].copy()
        done['price'] = pd.to_numeric(done['price'], errors='coerce').fillna(0)
        st.metric("รายได้รวม", f"{done['price'].sum():,.0f} บ.")
        st.dataframe(done, use_container_width=True)

    with at2:
        # เมื่อกดเข้า Tab คิว ให้รีเซ็ตจุดแดงคิว
        st.session_state.last_b_count = len(df_b_now)
        active = df_b_now[df_b_now['status'] == "รอรับบริการ"]
        for _, r in active.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 {r['fullname']} | ⏰ {r['time']} | {r['service']}")
                pr = c2.number_input("ราคา", min_value=0, key=f"p{r['id']}")
                if c2.button("✅ เสร็จ", key=f"ok{r['id']}"):
                    df_b_now.loc[df_b_now['id'] == r['id'], ['status', 'price']] = ["เสร็จสิ้น", str(pr)]
                    conn.update(worksheet="Bookings", data=df_b_now); st.rerun()

    with at3:
        for u in df_c_now['username'].unique():
            user_chat = df_c_now[df_c_now['username'] == u]
            chat_title = f"📩 จาก: {u} 🔴" if user_chat.iloc[-1]['sender'] == 'user' else f"📩 จาก: {u}"
            with st.expander(chat_title):
                for _, m in user_chat.iterrows():
                    with st.chat_message("assistant" if m['sender']=="user" else "user"): st.write(m['msg'])
                with st.form(f"rep_{u}", clear_on_submit=True):
                    rep = st.text_input("ตอบกลับ...")
                    if st.form_submit_button("ส่ง") and rep:
                        new_r = pd.DataFrame([{"username": u, "sender": "admin", "msg": rep, "time": datetime.now().strftime("%H:%M")}])
                        conn.update(worksheet="Chats", data=pd.concat([df_c_now, new_r], ignore_index=True)); st.rerun()

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    today = datetime.now().strftime("%Y-%m-%d")
    qs = df_b_now[(df_b_now['date'] == today) & (df_b_now['status'] == "รอรับบริการ")].sort_values('time')
    st.table(qs[['time', 'service', 'fullname']]) if not qs.empty else st.info("ไม่มีคิว")
