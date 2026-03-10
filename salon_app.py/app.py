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
        /* แชทสไตล์ */
        .chat-container { background-color: #f0f2f5; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
        .bubble { padding: 12px 18px; border-radius: 18px; margin-bottom: 10px; max-width: 80%; font-size: 16px; clear: both; display: block; }
        .user-msg { background-color: #0084FF; color: #FFFFFF !important; float: right; border-bottom-right-radius: 2px; }
        .admin-msg { background-color: #E4E6EB; color: #000000 !important; float: left; border-bottom-left-radius: 2px; }
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

# --- 3. NAVIGATION SYSTEM ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon Online</h1>", unsafe_allow_html=True)

# Navigation Bar
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

# --- 4. PAGE LOGIC (เงื่อนไขแสดงผลหน้าต่างๆ) ---

# --- หน้าแรก (Home) ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000", caption="222-Salon Welcome")
    st.subheader("ยินดีต้อนรับสู่ 222-Salon")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📍 **ที่ตั้งร้าน:** ถนนเลี่ยงเมืองชัยภูมิ\n\n📞 **ติดต่อ:** {SHOP_TEL}")
    with col2:
        st.success("✅ **เปิดให้บริการ:** ทุกวัน 10:00 - 20:00 น.")
    
    st.markdown("---")
    st.write("### ✂️ อัตราค่าบริการ")
    services = [["ตัดผมชาย", "100 - 150.-"], ["ตัดผมหญิง", "200 - 350.-"], ["สระ-ไดร์", "100 - 150.-"], ["ทำสีผม", "เริ่มต้น 500.-"]]
    for s in services:
        st.markdown(f'<div class="price-card"><b>{s[0]}</b> <span style="float:right;">{s[1]}</span></div>', unsafe_allow_html=True)

# --- หน้าดูคิววันนี้ (ViewQueues) ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิวทั้งหมดในวันนี้")
    df_v = get_data("Bookings", ttl_val=0)
    if not df_v.empty:
        st.dataframe(df_v[['service', 'date', 'time', 'status']], use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลคิวจอง")

# --- หน้า ADMIN ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการหลังบ้าน")
    t1, t2 = st.tabs(["📉 คิวงาน", "💬 แชทลูกค้า"])
    # (ใส่ Logic Admin จากโค้ดก่อนหน้าได้เลย)

# --- หน้าลูกค้า (Booking) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.fullname}")
    # (ใส่ Logic Booking จากโค้ดก่อนหน้าได้เลย)

# --- หน้า Login ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("ตกลง"):
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

# --- หน้า Register ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg"):
        nu, np, nf, nt = st.text_input("Username"), st.text_input("Password"), st.text_input("ชื่อจริง"), st.text_input("เบอร์โทร")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "phone":nt, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u]))
            st.success("สมัครสำเร็จ!")
            navigate("Login")
