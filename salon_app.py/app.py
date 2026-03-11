import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold;}
        .price-card {
            background-color: #ffffff !important; padding: 15px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 10px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #1A1A1A !important;
        }
        .contact-box {
            text-align: center; background-color: #ffffff !important; padding: 20px; 
            border-radius: 15px; box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #1A1A1A !important;
        }
        .reply-box {
            background-color: #f0f2f6; padding: 10px; border-radius: 10px; 
            border-left: 5px solid #FF4B4B; margin-top: 5px; color: #333;
        }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl="0s")
        df = df.dropna(how='all')
        if df.empty: return pd.DataFrame()
        df.columns = [str(c).strip() for c in df.columns]
        df = df.fillna("")
        return df
    except: return pd.DataFrame()

# --- 2. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

# --- TOP MENU BAR ---
st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)
m_cols = st.columns(5)
with m_cols[0]: 
    if st.button("🏠 หน้าแรก"): navigate("Home")
if not st.session_state.logged_in:
    with m_cols[3]: 
        if st.button("📝 สมัคร"): navigate("Register")
    with m_cols[4]: 
        if st.button("🔑 เข้าสู่ระบบ"): navigate("Login")
else:
    role = st.session_state.get('user_role')
    with m_cols[2]: 
        lbl = "📊 จัดการ" if role == 'admin' else "✂️ จองคิว"
        if st.button(lbl): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")

st.divider()

# --- 3. PAGE: HOME ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.subheader("📞 ช่องทางการติดต่อ")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='contact-box'><h3>📞 โทร</h3><p>081-222-XXXX</p></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='contact-box'><h3>💬 Line</h3><p>@222salon</p></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='contact-box'><h3>📍 พิกัด</h3><p>กรุงเทพฯ</p></div>", unsafe_allow_html=True)

# --- 4. PAGE: BOOKING (Customer Chat) ---
elif st.session_state.page == "Booking":
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 แชทกับแอดมิน"])
    
    with t3:
        st.subheader("💬 กล่องข้อความของคุณ")
        df_m = get_data("Messages")
        if not df_m.empty:
            my_msgs = df_m[df_m['username'] == st.session_state.username].sort_values('timestamp', ascending=False)
            for _, m in my_msgs.iterrows():
                with st.chat_message("user"):
                    st.write(m['message'])
                    st.caption(f"ส่งเมื่อ: {m['timestamp']}")
                if m['admin_reply']:
                    with st.chat_message("assistant", avatar="✂️"):
                        st.write(f"**แอดมินตอบ:** {m['admin_reply']}")
        
        st.divider()
        with st.form("customer_msg"):
            new_msg = st.text_input("พิมพ์ข้อความสอบถาม...")
            if st.form_submit_button("ส่ง"):
                if new_msg:
                    df_m = get_data("Messages")
                    # สร้าง DataFrame ใหม่ที่มีคอลัมน์ admin_reply ว่างไว้
                    row = pd.DataFrame([{
                        "id": str(int(datetime.now().timestamp())),
                        "username": st.session_state.username,
                        "message": new_msg,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "status": "ยังไม่ได้อ่าน",
                        "admin_reply": ""
                    }])
                    conn.update(worksheet="Messages", data=pd.concat([df_m, row], ignore_index=True))
                    st.success("ส่งแล้ว!"); st.rerun()

# --- 5. PAGE: ADMIN (Admin Reply) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการร้าน")
    adm_t1, adm_t2 = st.tabs(["📅 คิวลูกค้า", "📩 ตอบแชทลูกค้า"])
    
    with adm_t2:
        df_m = get_data("Messages")
        if not df_m.empty:
            unread = df_m[df_m['admin_reply'] == ""].sort_values('timestamp')
            if not unread.empty:
                for _, m in unread.iterrows():
                    with st.expander(f"✉️ จากคุณ {m['username']} - {m['timestamp']}"):
                        st.write(f"**ลูกค้า:** {m['message']}")
                        reply_txt = st.text_area("พิมพ์ข้อความตอบกลับ", key=f"re_{m['id']}")
                        if st.button("ส่งคำตอบ", key=f"btn_{m['id']}"):
                            df_m.loc[df_m['id'] == m['id'], 'admin_reply'] = reply_txt
                            df_m.loc[df_m['id'] == m['id'], 'status'] = 'ตอบแล้ว'
                            conn.update(worksheet="Messages", data=df_m)
                            st.success("ส่งคำตอบแล้ว!"); st.rerun()
            else: st.write("ไม่มีข้อความค้างตอบ")
        
        if st.checkbox("ดูประวัติการแชททั้งหมด"):
            st.dataframe(df_m, use_container_width=True)

# --- 6. AUTHENTICATION (Login/Register) ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u = st.text_input("เบอร์โทร")
    p = st.text_input("รหัสผ่าน", type="password")
    if st.button("ตกลง"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'Admin'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nu, np, nf = st.text_input("เบersโทร"), st.text_input("รหัส"), st.text_input("ชื่อ")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            new_user = pd.DataFrame([{"username": nu, "password": np, "fullname": nf, "role": "user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_user], ignore_index=True))
            st.success("สมัครสำเร็จ!"); navigate("Login")
