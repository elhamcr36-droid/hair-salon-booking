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
        .price-card {
            background-color: #ffffff; padding: 15px; border-radius: 12px;
            border-left: 5px solid #FF4B4B; margin-bottom: 10px; color: #1A1A1A;
            box-shadow: 1px 2px 8px rgba(0,0,0,0.1);
        }
        .chat-bubble { padding: 10px 15px; border-radius: 15px; margin-bottom: 5px; display: inline-block; max-width: 85%; }
        .user-bubble { background-color: #E1FFC7; color: #000; border-bottom-right-radius: 2px; }
        .admin-bubble { background-color: #F0F0F0; color: #000; border-bottom-left-radius: 2px; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. CORE DATA FUNCTIONS ---
def get_data(sheet_name):
    try:
        # ใช้ ttl=10 เพื่อป้องกัน Quota Exceeded 429
        df = conn.read(worksheet=sheet_name, ttl=10)
        if df is None or df.empty:
            cols = {
                "Users": ['username', 'password', 'fullname', 'phone', 'role'],
                "Bookings": ['id', 'username', 'service', 'date', 'time', 'status'],
                "Messages": ['msg_id', 'username', 'sender', 'text', 'timestamp']
            }
            return pd.DataFrame(columns=cols.get(sheet_name, []))
        
        # ล้างช่องว่างที่หัวคอลัมน์ (แก้ KeyError 'username ')
        df.columns = [str(c).strip() for c in df.columns] 
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        return df
    except Exception:
        # หาก Google Sheets ติด Quota ให้ส่งตารางเปล่าที่มีหัวคอลัมน์ไปก่อน แอปจะได้ไม่พัง
        cols = {"Bookings": ['id', 'username', 'service', 'date', 'time', 'status'],
                "Messages": ['msg_id', 'username', 'sender', 'text', 'timestamp'],
                "Users": ['username', 'password', 'fullname', 'phone', 'role']}
        return pd.DataFrame(columns=cols.get(sheet_name, []))

def get_user_info_map():
    df_u = get_data("Users")
    if not df_u.empty and 'username' in df_u.columns:
        return df_u.set_index('username')[['fullname', 'phone']].to_dict('index')
    return {}

# --- 3. NAVIGATION (แก้ไขปัญหาปุ่ม Login ค้าง) ---
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

# ตรวจสอบสถานะการ Login เพื่อแสดงปุ่มให้ถูกต้อง
if not st.session_state.logged_in:
    # ปุ่มสำหรับลูกค้าทั่วไป (ยังไม่ Login)
    with m_cols[3]: 
        if st.button("📝 สมัครสมาชิก"): navigate("Register")
    with m_cols[4]: 
        if st.button("🔑 เข้าสู่ระบบ"): navigate("Login")
else:
    # ปุ่มสำหรับสมาชิกที่ Login แล้ว
    role = st.session_state.get('user_role')
    with m_cols[2]: 
        if st.button("📊 หลังบ้าน" if role == 'admin' else "✂️ จองคิว"): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            navigate("Home")

st.divider()

# --- 4. PAGE: ADMIN (จัดการแล้วหายทันที) ---
if st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการหลังบ้าน")
    t1, t2 = st.tabs(["📈 คิวรอดำเนินการ", "💬 แชทลูกค้า"])
    
    with t1:
        df_b = get_data("Bookings")
        u_info = get_user_info_map()
        # แสดงเฉพาะสถานะ "รอรับบริการ"
        pending = df_b[df_b['status'] == "รอรับบริการ"] if not df_b.empty else pd.DataFrame()
        
        if not pending.empty:
            for _, row in pending.sort_values(['date', 'time']).iterrows():
                user_data = u_info.get(row['username'], {'fullname': row['username'], 'phone': '-'})
                with st.container():
                    c_txt, c_ok, c_del = st.columns([3, 1, 1])
                    with c_txt:
                        st.write(f"👤 **{user_data['fullname']}** | 📞 {user_data['phone']}")
                        st.write(f"✂️ {row['service']} | 📅 {row['date']} ({row['time']})")
                    if c_ok.button("✅ เสร็จสิ้น", key=f"ok_{row['id']}"):
                        df_b.loc[df_b['id'] == row['id'], 'status'] = "เสร็จสิ้น"
                        conn.update(worksheet="Bookings", data=df_b)
                        st.rerun()
                    if c_del.button("🗑️ ลบ", key=f"adm_del_{row['id']}", type="primary"):
                        conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']])
                        st.rerun()
                st.markdown("---")
        else:
            st.info("✨ ไม่มีคิวค้างในระบบ")

# --- 5. PAGE: BOOKING (1 ครั้ง/วัน & 2 คน/ช่วงเวลา) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.fullname}")
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 แชท"])
    
    df_b = get_data("Bookings")
    
    with t1:
        d = st.date_input("เลือกวันที่", min_value=datetime.now().date())
        svc = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืดผม"])
        
        # กฎ: 1 ครั้งต่อวัน
        booked = not df_b[(df_b['username'] == st.session_state.username) & (df_b['date'] == str(d))].empty
        
        if booked:
            st.warning(f"⚠️ คุณมีการจองวันที่ {d} แล้ว")
        else:
            all_slots = [f"{h:02d}:00" for h in range(10, 20)]
            valid_slots = []
            for slot in all_slots:
                # กฎ: พนักงาน 2 คน
                count = len(df_b[(df_b['date'] == str(d)) & (df_b['time'] == slot)])
                if count < 2: valid_slots.append(f"{slot} (ว่าง {2-count})")
            
            if not valid_slots: st.error("❌ คิวเต็ม")
            else:
                t_input = st.selectbox("เลือกเวลา", valid_slots)
                if st.button("✅ ยืนยันการจอง"):
                    new_id = str(int(datetime.now().timestamp()))
                    new_row = pd.DataFrame([{"id":new_id, "username":st.session_state.username, "service":svc, "date":str(d), "time":t_input.split(" ")[0], "status":"รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_row]))
                    st.success("จองสำเร็จ!"); st.rerun()

# --- 6. AUTH & OTHER PAGES ---
elif st.session_state.page == "Login":
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
        df_u = get_data("Users")
        user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin', 'fullname':'แอดมิน'})
            navigate("Admin")
        elif not user.empty:
            st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u, 'fullname':user.iloc[0]['fullname']})
            navigate("Booking")
        else: st.error("ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Register":
    with st.form("reg"):
        nu, np, nf, nt = st.text_input("Username"), st.text_input("Password"), st.text_input("ชื่อจริง"), st.text_input("โทร")
        if st.form_submit_button("สมัครสมาชิก"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "phone":nt, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u]))
            navigate("Login")

elif st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.write("ยินดีต้อนรับสู่ 222-Salon!")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    st.dataframe(get_data("Bookings"), use_container_width=True)
