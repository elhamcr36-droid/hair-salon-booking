import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอและสไตล์ (UI/UX) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

SHOP_LOCATION_URL = "https://www.google.com/maps/place/222+%E0%B8%96%E0%B8%99%E0%B8%99+%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B8%9A%E0%B8%B2%E0%B8%A5+1+%E0%B8%95%E0%B8%B3%E0%B8%9A%E0%B8%A5%E0%B8%9A%E0%B9%88%E0%B8%AD%E0%B8%A2%E0%B8%B2%E0%B8%87+%E0%B8%AD%E0%B8%B3%E0%B9%80%E0%B8%A0%E0%B8%AD%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2+90000/@7.1915128,100.6007972,17z/data=!3m1!4b1!4m6!3m5!1s0x304d3323c7ad029d:0x7cfb098f4f859e4c!8m2!3d7.1915128!4d100.6007972!16s%2Fg%2F11jylj3r6y?entry=ttu&g_ep=EgoyMDI2MDMwOC4wIKXMDSoASAFQAw%3D%3D" 

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        
        .price-card {
            background-color: #ffffff !important; padding: 20px; border-radius: 15px;
            border-left: 8px solid #FF4B4B; margin-bottom: 15px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #1A1A1A !important;
        }
        
        /* Chat Bubble Styles */
        .chat-bubble {
            padding: 10px 15px; border-radius: 15px; margin-bottom: 5px;
            display: inline-block; max-width: 80%; line-height: 1.4;
        }
        .user-bubble { background-color: #E1FFC7; color: #000; border-bottom-right-radius: 2px; }
        .admin-bubble { background-color: #F0F0F0; color: #000; border-bottom-left-radius: 2px; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. ข้อมูลบริการและฟังก์ชันช่วย ---
SERVICES_DISPLAY = {
    "✂️ ตัดผมชาย": "150 - 350", "💇‍♀️ ตัดผมหญิง": "350 - 800",
    "🚿 สระ-ไดร์": "200 - 450", "🎨 ทำสีผม": "1,500 - 4,500",
    "✨ ยืดผมวอลลุ่ม": "1,000 - 5,500", "🌿 เคราติน": "1,500 - 3,500"
}
SERVICES_BASE_PRICE = {"ตัดผมชาย": 150, "ตัดผมหญิง": 350, "สระ-ไดร์": 200, "ทำสีผม": 1500, "ยืดผมวอลลุ่ม": 1000, "เคราติน": 1500}
TIME_SLOTS = [f"{h:02d}:{m}" for h in range(9, 20) for m in ["00", "30"] if "09:30" <= f"{h:02d}:{m}" <= "19:30"]

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        if 'phone' in df.columns:
            df['phone'] = df['phone'].apply(lambda x: str(x).strip().zfill(10) if x and x != "" else "")
        return df
    except:
        return pd.DataFrame()

# --- 3. ระบบนำทาง (Navigation) ---
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
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 4. หน้าแอดมิน (Admin Dashboard & Chat) ---
if st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการร้านและข้อความ")
    t_admin1, t_admin2 = st.tabs(["📈 สรุปยอด/จัดการคิว", "💬 แชทกับลูกค้า"])
    
    with t_admin1:
        df_b = get_data("Bookings")
        df_u = get_data("Users")
        if not df_b.empty:
            today_str = datetime.now().strftime("%Y-%m-%d")
            df_today = df_b[df_b['date'] == today_str]
            daily_rev = pd.to_numeric(df_today['price'], errors='coerce').sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 ยอดขายวันนี้", f"{daily_rev:,.0f} ฿")
            c2.metric("👥 ลูกค้าวันนี้", f"{len(df_today)} ท่าน")
            c3.write(f"📅 วันที่: {today_str}")
            
            df_admin = pd.merge(df_b, df_u[['username', 'fullname', 'phone']], on='username', how='left')
            for _, row in df_admin.sort_values(['date','time'], ascending=[False, True]).iterrows():
                status_color = "🟢" if row['status'] == 'เสร็จสิ้น' else "🔵"
                with st.expander(f"{status_color} {row['time']} | {row['fullname']} - {row['service']}"):
                    col_a, col_b, col_c = st.columns(3)
                    col_a.write(f"📞 {row['phone']}")
                    if row['status'] == 'รอรับบริการ':
                        if col_b.button("✅ เสร็จสิ้น", key=f"ok_{row['id']}"):
                            df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                            conn.update(worksheet="Bookings", data=df_b); st.rerun()
                    if col_c.button("🗑️ ลบคิว", key=f"del_{row['id']}"):
                        conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']]); st.rerun()

    with t_admin2:
        df_msg = get_data("Messages")
        if not df_msg.empty:
            all_users = df_msg['username'].unique()
            target_user = st.selectbox("เลือกแชทกับลูกค้า:", all_users)
            
            chat_box = df_msg[df_msg['username'] == target_user].sort_values('msg_id')
            for _, m in chat_box.iterrows():
                align = "left" if m['sender'] == "user" else "right"
                cls = "user-bubble" if m['sender'] == "user" else "admin-bubble"
                st.markdown(f"<div style='text-align: {align};'><div class='chat-bubble {cls}'><b>{m['sender']}:</b> {m['text']}</div></div>", unsafe_allow_html=True)
            
            with st.form("admin_reply_form", clear_on_submit=True):
                rep = st.text_input("พิมพ์ข้อความตอบกลับ...")
                if st.form_submit_button("ส่ง") and rep:
                    new_r = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": target_user, "sender": "admin", "text": rep, "timestamp": datetime.now().strftime("%H:%M")}])
                    conn.update(worksheet="Messages", data=pd.concat([df_msg, new_r], ignore_index=True)); st.rerun()

# --- 5. หน้าจองคิว & ติดต่อเรา (User) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 คุณ {st.session_state.get('fullname', st.session_state.username)}")
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง", "💬 ติดต่อเรา"])
    
    with t1:
        svc = st.selectbox("เลือกบริการ", list(SERVICES_BASE_PRICE.keys()))
        d = st.date_input("เลือกวันที่จอง")
        t = st.selectbox("เลือกเวลา", TIME_SLOTS)
        if st.button("ยืนยันการจอง"):
            df_b = get_data("Bookings")
            if d.weekday() == 2: st.error("❌ ร้านหยุดวันพุธ")
            else:
                new_id = str(int(datetime.now().timestamp()))
                new_r = pd.DataFrame([{"id":new_id, "username":st.session_state.username, "service":svc, "date":str(d), "time":t, "price":str(SERVICES_BASE_PRICE[svc]), "status":"รอรับบริการ"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_r], ignore_index=True)); st.success("✅ จองสำเร็จ!"); st.rerun()
    
    with t2:
        df_b = get_data("Bookings")
        st.dataframe(df_b[df_b['username'] == st.session_state.username].sort_values('date', ascending=False), use_container_width=True)

    with t3:
        st.write("### 💬 คุยกับแอดมิน")
        df_msg = get_data("Messages")
        my_msgs = df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id')
        
        for _, m in my_msgs.iterrows():
            align = "right" if m['sender'] == "user" else "left"
            cls = "user-bubble" if m['sender'] == "user" else "admin-bubble"
            st.markdown(f"<div style='text-align: {align};'><div class='chat-bubble {cls}'>{m['text']}</div></div>", unsafe_allow_html=True)
            
            if m['sender'] == "user":
                c_edit, c_del = st.columns([1, 1])
                with c_del:
                    if st.button("🗑️", key=f"msg_del_{m['msg_id']}"):
                        conn.update(worksheet="Messages", data=df_msg[df_msg['msg_id'] != m['msg_id']]); st.rerun()
                with c_edit:
                    with st.popover("📝 แก้ไข"):
                        new_txt = st.text_input("แก้ไขข้อความ", value=m['text'], key=f"edt_{m['msg_id']}")
                        if st.button("💾 บันทึก", key=f"sav_{m['msg_id']}"):
                            df_msg.loc[df_msg['msg_id'] == m['msg_id'], 'text'] = new_txt
                            conn.update(worksheet="Messages", data=df_msg); st.rerun()

        with st.form("user_msg_form", clear_on_submit=True):
            u_msg = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่งข้อความ") and u_msg:
                new_row = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "sender": "user", "text": u_msg, "timestamp": datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_row], ignore_index=True)); st.rerun()

# --- 6. หน้าอื่นๆ (Home, Register, Login, ViewQueues) ---
elif st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    c_i1, c_i2 = st.columns(2)
    c_i1.info("⏰ 09:30 - 19:30 น. (หยุดวันพุธ)")
    c_i2.link_button("📍 นำทางไปยังร้าน (GPS)", SHOP_LOCATION_URL, type="primary")
    st.subheader("📋 บริการและราคาเริ่มต้น")
    p_col1, p_col2 = st.columns(2)
    for i, (name, price) in enumerate(SERVICES_DISPLAY.items()):
        target = p_col1 if i % 2 == 0 else p_col2
        target.markdown(f'<div class="price-card"><b>{name}</b><br><span style="color:#FF4B4B">{price} บาท</span></div>', unsafe_allow_html=True)

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nu, np = st.text_input("Username"), st.text_input("Password", type="password")
        nf, nt = st.text_input("ชื่อ-นามสกุล"), st.text_input("เบอร์โทรศัพท์")
        if st.form_submit_button("สมัครสมาชิก"):
            df_u = get_data("Users")
            if nu in df_u['username'].values: st.error("❌ Username นี้มีผู้ใช้แล้ว")
            else:
                new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "phone":nt, "role":"user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True)); st.success("✅ สำเร็จ!"); navigate("Login")

elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin'}); navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if not user.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u, 'fullname':user.iloc[0]['fullname']}); navigate("Booking")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_b = get_data("Bookings")
    active = df_b[(df_b['date'] == str(datetime.now().date())) & (df_b['status'] == 'รอรับบริการ')]
    st.dataframe(active[['time', 'service']].sort_values('time'), use_container_width=True)
