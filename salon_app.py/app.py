import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & UI STYLE ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

SHOP_LOCATION_URL = "https://maps.google.com" 
LINE_URL = "https://line.me/ti/p/~222Salon"
FB_URL = "https://www.facebook.com/222Salon" 
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
        .status-badge { padding: 2px 8px; border-radius: 5px; font-size: 0.85em; font-weight: bold; color: white; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. CORE DATA FUNCTIONS ---
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=5) # ลด TTL เหลือ 5 เพื่อให้อัปเดตไวขึ้น
        if df is None or df.empty:
            cols = {
                "Users": ['username', 'password', 'fullname', 'phone', 'role'],
                "Bookings": ['id', 'username', 'service', 'date', 'time', 'status'],
                "Messages": ['msg_id', 'username', 'sender', 'text', 'timestamp']
            }
            return pd.DataFrame(columns=cols.get(sheet_name, []))
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns] 
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        return df
    except Exception:
        return pd.DataFrame()

def get_user_info_map():
    df_u = get_data("Users")
    if not df_u.empty and 'username' in df_u.columns:
        return df_u.set_index('username')[['fullname', 'phone']].to_dict('index')
    return {}

# --- 3. NAVIGATION ---
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
        if st.button("📝 สมัคร"): navigate("Register")
    with m_cols[4]: 
        if st.button("🔑 เข้าระบบ"): navigate("Login")
else:
    role = st.session_state.get('user_role')
    with m_cols[2]: 
        if st.button("📊 หลังบ้าน" if role == 'admin' else "✂️ จองคิว"): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 4. ADMIN PAGE (อัปเดต: กดแล้วหายทันที) ---
if st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการหลังบ้าน")
    t1, t2 = st.tabs(["📈 คิวที่รอดำเนินการ", "💬 แชทลูกค้า"])
    
    with t1:
        df_b = get_data("Bookings")
        u_info = get_user_info_map()
        
        # กรองเอาเฉพาะคิวที่สถานะเป็น "รอรับบริการ" เท่านั้นมาโชว์
        pending_queues = df_b[df_b['status'] == "รอรับบริการ"] if not df_b.empty else pd.DataFrame()
        
        if not pending_queues.empty:
            for _, row in pending_queues.sort_values(['date', 'time']).iterrows():
                user_data = u_info.get(row['username'], {'fullname': row['username'], 'phone': '-'})
                
                with st.container():
                    c_info, c_done, c_del = st.columns([3, 1, 1])
                    with c_info:
                        st.markdown(f"👤 **{user_data['fullname']}** | 📞 {user_data['phone']}")
                        st.markdown(f"✂️ {row['service']} | 📅 {row['date']} ({row['time']})")
                    
                    with c_done:
                        # เมื่อกด "เสร็จสิ้น" จะอัปเดตสถานะใน Sheet ทำให้หลุดจาก Filter และหายไปจากหน้าจอ
                        if st.button("✅ เสร็จสิ้น", key=f"ok_{row['id']}"):
                            df_b.loc[df_b['id'] == row['id'], 'status'] = "เสร็จสิ้น"
                            conn.update(worksheet="Bookings", data=df_b)
                            st.toast(f"จัดการคิว {user_data['fullname']} เรียบร้อย!")
                            st.rerun() # สั่งรีเฟรชหน้าจอเพื่อให้รายการหายไป
                            
                    with c_del:
                        # เมื่อกด "ลบ" จะลบแถวออกจาก Sheet ทันที
                        if st.button("🗑️ ลบ", key=f"adm_del_{row['id']}", type="primary"):
                            df_updated = df_b[df_b['id'] != row['id']]
                            conn.update(worksheet="Bookings", data=df_updated)
                            st.toast("ลบคิวเรียบร้อยแล้ว")
                            st.rerun()
                st.markdown("---")
        else:
            st.info("✨ ไม่มีคิวรอดำเนินการในขณะนี้")

# --- 5. BOOKING PAGE (Rules: 1/day, 2/staff) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.fullname}")
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติ/ยกเลิก", "💬 ติดต่อร้าน"])
    
    df_b = get_data("Bookings")
    
    with t1:
        d = st.date_input("เลือกวันที่", min_value=datetime.now().date())
        svc = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืดผม"])
        
        is_booked = False
        if not df_b.empty and 'username' in df_b.columns:
            is_booked = not df_b[(df_b['username'] == st.session_state.username) & (df_b['date'] == str(d))].empty
            
        if is_booked:
            st.warning(f"⚠️ คุณมีการจองวันที่ {d} อยู่แล้ว")
        else:
            all_slots = [f"{h:02d}:00" for h in range(10, 20)]
            valid_slots = []
            for slot in all_slots:
                count = len(df_b[(df_b['date'] == str(d)) & (df_b['time'] == slot)])
                if count < 2: valid_slots.append(f"{slot} (ว่าง {2-count})")
            
            if not valid_slots: st.error("❌ คิวเต็ม")
            else:
                t_input = st.selectbox("เลือกเวลา", valid_slots)
                if st.button("✅ ยืนยันการจอง"):
                    new_id = str(int(datetime.now().timestamp()))
                    new_row = pd.DataFrame([{"id":new_id, "username":st.session_state.username, "service":svc, "date":str(d), "time":t_input.split(" ")[0], "status":"รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_row], ignore_index=True))
                    st.success("จองคิวสำเร็จ!")
                    st.rerun()

# --- ส่วนอื่นๆ (Home, Login, Register) ---
elif st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.subheader("📋 บริการและราคา")
    st.info(f"📍 สนใจจองคิว ติดต่อ: {SHOP_TEL} หรือสมัครสมาชิกเพื่อจองออนไลน์")

elif st.session_state.page == "Login":
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
        df_u = get_data("Users")
        if not df_u.empty:
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
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
            navigate("Login")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    st.dataframe(get_data("Bookings"), use_container_width=True)
