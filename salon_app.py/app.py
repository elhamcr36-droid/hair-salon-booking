import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon-Total", layout="wide", initial_sidebar_state="collapsed")

# บังคับ CSS สำหรับ Messenger UI, ตัวหนังสือสีดำ และจุดแดงแจ้งเตือน
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 20px; font-weight: bold; height: 3.2em;}
        .price-card {
            background-color: #ffffff !important; padding: 18px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 12px;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.08); color: #000000 !important;
        }
        .contact-section-black { 
            background-color: #ffffff; padding: 30px; border-radius: 15px; text-align: center; 
            box-shadow: 0px 4px 15px rgba(0,0,0,0.1); border: 1px solid #eeeeee;
            color: #000000 !important;
        }
        /* บังคับสีข้อความแชทเป็นสีดำ */
        [data-testid="stChatMessage"] { color: #000000 !important; border-radius: 15px; }
        .stChatMessage:nth-child(even) { background-color: #f0f2f6; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 🛠️ FIX LOGIN & DATA ENGINE: ปรับปรุงการดึงข้อมูล ---
def get_data(sheet_name):
    st.cache_data.clear() 
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df is None or df.empty: return pd.DataFrame()
        
        df = df.dropna(how='all') # ลบแถวที่ว่างเปล่าออก
        df.columns = [str(c).strip().lower() for c in df.columns] # หัวตารางตัวเล็กและตัดช่องว่าง
        
        # บังคับข้อมูลทุกช่องเป็น String เพื่อแก้ปัญหารหัสผ่านและเบอร์โทร (Plain Text Logic)
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace('nan', '')
            
        return df
    except:
        return pd.DataFrame()

# --- 2. NOTIFICATION ENGINE (ตรวจหาแชทใหม่) ---
df_msg_check = get_data("Messages")
new_msg_count = 0
unreplied_users = []
if not df_msg_check.empty:
    unreplied_df = df_msg_check[df_msg_check['admin_reply'] == ""]
    new_msg_count = len(unreplied_df)
    unreplied_users = unreplied_df['username'].unique().tolist()

# --- 3. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

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
    # แสดงจุดแดงแจ้งเตือนที่ปุ่มเมนูสำหรับ Admin
    label = f"📊 จัดการร้าน {'🔴' if new_msg_count > 0 else ''}" if role == 'admin' else "💬 แชท/จองคิว"
    with m_cols[2]:
        if st.button(label): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]:
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")
st.divider()

# --- 4. PAGE CONTENT ---

# 🔑 หน้าเข้าสู่ระบบ (Fix Logic: เปรียบเทียบข้อมูลแบบ String)
if st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์", placeholder="08xxxxxxxx").strip()
    p_in = st.text_input("รหัสผ่าน", type="password").strip()
    
    if st.button("ตกลง"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': u_in, 'fullname': 'Admin'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            # ค้นหาโดยบังคับ String ทั้งคู่ ป้องกันปัญหาเลข 0 หาย
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)] if not df_u.empty else pd.DataFrame()
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง ตรวจสอบเบอร์โทรและรหัสผ่านอีกครั้ง")

# 📝 หน้าสมัครสมาชิก
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg"):
        nf, nu, np = st.text_input("ชื่อ-นามสกุล"), st.text_input("เบอร์โทร"), st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ตกลง"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"phone": nu.strip(), "password": np.strip(), "fullname": nf.strip(), "role": "user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
            st.success("ลงทะเบียนสำเร็จ!"); time.sleep(1); navigate("Login")

# 💬 หน้าลูกค้า (Messenger & Booking)
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิว", "💬 Messenger"])
    with t1:
        with st.form("b_form"):
            d = st.date_input("วันที่", min_value=datetime.now().date())
            t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"])
            s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยันการจอง"):
                if d.weekday() == 5: st.error("❌ ร้านหยุดทุกวันเสาร์")
                else:
                    df_b = get_data("Bookings")
                    new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(d), "time": t, "service": s, "status": "รอรับบริการ", "price": "0"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                    st.success("จองสำเร็จ!"); time.sleep(1); st.rerun()
    with t3:
        st.subheader("💬 สนทนากับร้าน")
        df_msg = get_data("Messages")
        with st.container(height=400):
            if not df_msg.empty:
                my_m = df_msg[df_msg['username'] == st.session_state.username]
                for _, m in my_m.iterrows():
                    with st.chat_message("user"): st.write(m['message'])
                    if m.get('admin_reply'):
                        with st.chat_message("assistant", avatar="✂️"): st.write(m['admin_reply'])
        if prompt := st.chat_input("ถามร้านค้า..."):
            new_m = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "message": prompt, "timestamp": datetime.now().strftime("%H:%M"), "admin_reply": ""}])
            conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m], ignore_index=True)); st.rerun()

# 📊 หน้า Admin (จัดการคิว + ตอบแชทรายคนพร้อมจุดแดง)
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2, at3 = st.tabs(["📊 สรุปยอด", "📅 คิวลูกค้า", f"📩 ตอบแชท ({new_msg_count})"])
    with at3:
        df_adm_msg = get_data("Messages")
        if not df_adm_msg.empty:
            for u in df_adm_msg['username'].unique():
                is_new = u in unreplied_users
                with st.expander(f"👤 {u} {'🔴' if is_new else ''}"):
                    u_hist = df_adm_msg[df_adm_msg['username'] == u]
                    for idx, msg in u_hist.iterrows():
                        st.write(f"**ลูกค้า:** {msg['message']}")
                        if msg['admin_reply']: st.info(f"**แอดมิน:** {msg['admin_reply']}")
                        else:
                            with st.form(key=f"rep_{msg['id']}"):
                                ans = st.text_input("พิมพ์ตอบกลับ...")
                                if st.form_submit_button("ส่ง"):
                                    df_adm_msg.at[idx, 'admin_reply'] = ans
                                    conn.update(worksheet="Messages", data=df_adm_msg); st.rerun()

# 🏠 หน้าแรก
elif st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")
    st.markdown("""<div class="contact-section-black"><h3>📞 ติดต่อเรา</h3><p>📱 <b>เบอร์โทร:</b> 081-222-2222 | 📍 ต.บ่อยาง อ.เมืองสงขลา</p></div>""", unsafe_allow_html=True)
