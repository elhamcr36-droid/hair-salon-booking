import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & UI STYLE ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

SHOP_TEL = "0875644928"

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        
        /* สไตล์แชท: แก้ไขตัวอักษรมองไม่เห็น */
        .chat-container { background-color: #f0f2f5; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
        .bubble { padding: 12px 18px; border-radius: 18px; margin-bottom: 10px; max-width: 80%; font-size: 16px; clear: both; display: block; line-height: 1.4; }
        .user-msg { background-color: #0084FF; color: #FFFFFF !important; float: right; border-bottom-right-radius: 2px; box-shadow: 1px 1px 5px rgba(0,0,0,0.1); }
        .admin-msg { background-color: #E4E6EB; color: #000000 !important; float: left; border-bottom-left-radius: 2px; box-shadow: 1px 1px 5px rgba(0,0,0,0.05); }
        .timestamp { font-size: 10px; opacity: 0.7; display: block; margin-top: 5px; color: inherit; }
        
        /* สไตล์ประวัติการจอง */
        .history-card { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #dee2e6; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); color: #000; }
        .status-wait { color: #FF4B4B; font-weight: bold; }
        .status-done { color: #28a745; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. CORE DATA FUNCTIONS ---
def get_data(sheet_name, ttl_val=2):
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

# --- 3. NAVIGATION SYSTEM (Fixed: No Stuck Buttons) ---
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
        btn_label = "📊 หลังบ้าน" if role == 'admin' else "✂️ จองคิว"
        if st.button(btn_label): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 4. PAGE: ADMIN (Manage & Chat) ---
if st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการหลังบ้าน")
    t1, t2 = st.tabs(["📉 จัดการคิว", "💬 แชทลูกค้า"])
    
    with t1:
        df_b = get_data("Bookings", ttl_val=0) # ttl=0 ให้แอดมินเห็นข้อมูลสดใหม่เสมอ
        pending = df_b[df_b['status'] == "รอรับบริการ"] if not df_b.empty else pd.DataFrame()
        if not pending.empty:
            for _, row in pending.sort_values(['date', 'time']).iterrows():
                with st.container():
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.write(f"👤 **{row['username']}** | ✂️ {row['service']} | 📅 {row['date']} ({row['time']})")
                    if c2.button("✅ เสร็จ", key=f"ok_{row['id']}"):
                        df_b.loc[df_b['id'] == row['id'], 'status'] = "เสร็จสิ้น"
                        conn.update(worksheet="Bookings", data=df_b); st.rerun()
                    if c3.button("🗑️ ลบ", key=f"del_{row['id']}", type="primary"):
                        conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']]); st.rerun()
                st.markdown("---")
        else: st.info("✨ ไม่มีคิวรอรับบริการ")

    with t2:
        df_msg = get_data("Messages", ttl_val=0)
        if not df_msg.empty:
            u_list = df_msg['username'].unique()
            target = st.selectbox("เลือกแชทลูกค้า", u_list)
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for _, m in df_msg[df_msg['username'] == target].sort_values('msg_id').iterrows():
                cls = "user-msg" if m['sender'] == "user" else "admin-msg"
                st.markdown(f'<div class="bubble {cls}">{m["text"]}<span class="timestamp">{m["timestamp"]}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            with st.form("admin_reply", clear_on_submit=True):
                rep = st.text_input("ตอบกลับ...")
                if st.form_submit_button("ส่ง") and rep:
                    new_m = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": target, "sender": "admin", "text": rep, "timestamp": datetime.now().strftime("%H:%M")}])
                    conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- 5. PAGE: BOOKING & HISTORY & CHAT ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.fullname}")
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง", "💬 แชทติดต่อร้าน"])
    
    df_b = get_data("Bookings", ttl_val=0)
    
    with t1:
        d = st.date_input("เลือกวันที่", min_value=datetime.now().date())
        if not df_b[(df_b['username'] == st.session_state.username) & (df_b['date'] == str(d))].empty:
            st.warning("⚠️ คุณมีการจองวันนี้แล้ว")
        else:
            slots = [f"{h:02d}:00" for h in range(10, 20)]
            valid = [s for s in slots if len(df_b[(df_b['date'] == str(d)) & (df_b['time'] == s)]) < 2]
            if not valid: st.error("❌ คิวเต็ม")
            else:
                svc = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืดผม"])
                time_sel = st.selectbox("เวลา", valid)
                if st.button("✅ ยืนยันการจอง"):
                    new_id = str(int(datetime.now().timestamp()))
                    new_row = pd.DataFrame([{"id":new_id, "username":st.session_state.username, "service":svc, "date":str(d), "time":time_sel, "status":"รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_row])); st.success("จองสำเร็จ!"); st.rerun()

    with t2:
        my_q = df_b[df_b['username'] == st.session_state.username].sort_values(['date', 'time'], ascending=False)
        if my_q.empty: st.info("ไม่มีประวัติการจอง")
        else:
            for _, r in my_q.iterrows():
                cls = "status-wait" if r['status'] == "รอรับบริการ" else "status-done"
                st.markdown(f'<div class="history-card">📅 {r["date"]} | ⏰ {r["time"]} | {r["service"]} | <span class="{cls}">{r["status"]}</span></div>', unsafe_allow_html=True)
                if r['status'] == "รอรับบริการ":
                    if st.button(f"❌ ยกเลิกคิว {r['date']}", key=f"can_{r['id']}", type="primary"):
                        conn.update(worksheet="Bookings", data=df_b[df_b['id'] != r['id']]); st.rerun()

    with t3:
        df_msg = get_data("Messages", ttl_val=0)
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        my_chat = df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id')
        for _, m in my_chat.iterrows():
            cls = "user-msg" if m['sender'] == "user" else "admin-msg"
            st.markdown(f'<div class="bubble {cls}">{m["text"]}<span class="timestamp">{m["timestamp"]}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        with st.form("user_chat", clear_on_submit=True):
            um = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง") and um:
                new_m = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "sender": "user", "text": um, "timestamp": datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- 6. AUTH & OTHER PAGES ---
elif st.session_state.page == "Login":
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
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
        nu, np, nf, nt = st.text_input("User"), st.text_input("Pass"), st.text_input("ชื่อจริง"), st.text_input("โทร")
        if st.form_submit_button("สมัครสมาชิก"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "phone":nt, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u])); navigate("Login")

elif st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.subheader("💈 222-Salon ยินดีต้อนรับ")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    st.dataframe(get_data("Bookings", ttl_val=0), use_container_width=True)
