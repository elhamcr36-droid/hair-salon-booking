import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & UI STYLE ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# ข้อมูลติดต่อ (ดึงมาจากโค้ดชุดแรกของคุณ)
SHOP_TEL = "0875644928"
FACEBOOK_URL = "https://www.facebook.com/share/18Yv8zGNoG/?mibextid=wwXIfr" # ลิงก์จากโค้ดแรก
LINE_URL = "https://line.me/ti/p/yourid" # แก้ไขเป็นลิงก์ Line ของคุณ
MAP_URL = "https://maps.app.goo.gl/rDEn5k35LwP2f1t17" # ลิงก์จากโค้ดแรก

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        
        /* สไตล์ตารางราคา */
        .price-card {
            background-color: #ffffff; padding: 15px; border-radius: 12px;
            border-left: 5px solid #FF4B4B; margin-bottom: 10px; color: #1A1A1A;
            box-shadow: 1px 2px 8px rgba(0,0,0,0.1);
        }
        
        /* สไตล์ Social Buttons */
        .social-container { display: flex; justify-content: center; gap: 15px; margin-bottom: 20px; }
        .social-btn {
            padding: 10px 20px; border-radius: 30px; color: white !important;
            text-decoration: none; font-weight: bold; font-size: 14px;
            transition: 0.3s; display: inline-flex; align-items: center;
        }
        .fb-color { background-color: #1877F2; }
        .line-color { background-color: #00B900; }
        .gps-color { background-color: #EA4335; }
        
        /* แชทสไตล์ (ตัวอักษรชัดเจน) */
        .chat-container { background-color: #f0f2f5; padding: 15px; border-radius: 15px; margin-bottom: 20px; }
        .bubble { padding: 10px 15px; border-radius: 15px; margin-bottom: 8px; max-width: 75%; font-size: 16px; clear: both; display: block; }
        .user-msg { background-color: #0084FF; color: white !important; float: right; border-bottom-right-radius: 2px; }
        .admin-msg { background-color: #E4E6EB; color: black !important; float: left; border-bottom-left-radius: 2px; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. CORE DATA FUNCTIONS ---
def get_data(sheet_name, ttl_val=1):
    try:
        df = conn.read(worksheet=sheet_name, ttl=ttl_val)
        if df is None or df.empty:
            cols = {"Users": ['username', 'password', 'fullname', 'phone', 'role'],
                    "Bookings": ['id', 'username', 'service', 'date', 'time', 'status'],
                    "Messages": ['msg_id', 'username', 'sender', 'text', 'timestamp']}
            return pd.DataFrame(columns=cols.get(sheet_name, []))
        df.columns = [str(c).strip() for c in df.columns] 
        return df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
    except: return pd.DataFrame()

# --- 3. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon Online</h1>", unsafe_allow_html=True)

# Menu Bar
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
        lbl = "📊 หลังบ้าน" if role == 'admin' else "✂️ จองคิว"
        if st.button(lbl): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 4. PAGE: HOME (ใส่ Social + ราคา กลับมาตามโค้ดแรก) ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000", caption="222-Salon ยินดีต้อนรับ")
    
    # Social Media Buttons (เพิ่มกลับมาตามคำขอ)
    st.markdown(f"""
        <div class="social-container">
            <a href="{FACEBOOK_URL}" target="_blank" class="social-btn fb-color">🔵 Facebook</a>
            <a href="{LINE_URL}" target="_blank" class="social-btn line-color">🟢 Line</a>
            <a href="{MAP_URL}" target="_blank" class="social-btn gps-color">🔴 GPS แผนที่</a>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.info(f"📞 **เบอร์โทรติดต่อ:** {SHOP_TEL}")
    with c2:
        st.success("🕒 **เวลาทำการ:** 10:00 - 20:00 น. (เปิดทุกวัน)")

    st.write("### 💇‍♂️ เมนูบริการและราคา")
    prices = [
        ["ตัดผมชาย (Men's Cut)", "100 - 150 บาท"],
        ["ตัดผมหญิง (Women's Cut)", "200 - 350 บาท"],
        ["สระ-ไดร์ (Wash & Blow dry)", "100 - 150 บาท"],
        ["ทำสีผม (Hair Color)", "เริ่มต้น 500 บาท"],
        ["ยืดผม/ดัดผม (Perm & Straighten)", "เริ่มต้น 800 บาท"]
    ]
    for p in prices:
        st.markdown(f'<div class="price-card"><b>{p[0]}</b> <span style="float:right;">{p[1]}</span></div>', unsafe_allow_html=True)

# --- 5. PAGE: BOOKING & HISTORY (ครบถ้วน ไม่หาย) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.fullname}")
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง", "💬 แชทสอบถาม"])
    
    df_b = get_data("Bookings", ttl_val=0)
    
    with t1:
        d = st.date_input("เลือกวันที่จอง", min_value=datetime.now().date())
        # Logic ป้องกันจองซ้ำ
        if not df_b[(df_b['username'] == st.session_state.username) & (df_b['date'] == str(d))].empty:
            st.warning("⚠️ คุณมีการจองวันนี้อยู่แล้ว")
        else:
            slots = [f"{h:02d}:00" for h in range(10, 20)]
            valid = [s for s in slots if len(df_b[(df_b['date'] == str(d)) & (df_b['time'] == s)]) < 2]
            if not valid: st.error("❌ คิวเต็ม")
            else:
                svc = st.selectbox("เลือกบริการ", [p[0] for p in prices])
                tm = st.selectbox("เลือกเวลา", valid)
                if st.button("✅ ยืนยันการจอง"):
                    new_r = pd.DataFrame([{"id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "service":svc, "date":str(d), "time":tm, "status":"รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_r])); st.success("จองคิวสำเร็จ!"); st.rerun()

    with t2:
        my_q = df_b[df_b['username'] == st.session_state.username].sort_values(['date', 'time'], ascending=False)
        if my_q.empty: st.info("ยังไม่มีประวัติการจอง")
        else:
            for _, r in my_q.iterrows():
                st_cls = "status-wait" if r['status'] == "รอรับบริการ" else "status-done"
                st.markdown(f'<div class="price-card">📅 {r["date"]} | ⏰ {r["time"]} | {r["service"]} | <b>{r["status"]}</b></div>', unsafe_allow_html=True)
                if r['status'] == "รอรับบริการ":
                    if st.button(f"❌ ยกเลิกคิว {r['date']}", key=f"c_{r['id']}", type="primary"):
                        conn.update(worksheet="Bookings", data=df_b[df_b['id'] != r['id']]); st.rerun()

    with t3:
        df_msg = get_data("Messages", ttl_val=0)
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for _, m in df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id').iterrows():
            cls = "user-msg" if m['sender'] == "user" else "admin-msg"
            st.markdown(f'<div class="bubble {cls}">{m["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        with st.form("chat", clear_on_submit=True):
            um = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง") and um:
                new_m = pd.DataFrame([{"msg_id":str(int(datetime.now().timestamp())), "username":st.session_state.username, "sender":"user", "text":um, "timestamp":datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m])); st.rerun()

# --- 6. PAGE: VIEW QUEUES (ตารางคิวรวม) ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    st.dataframe(get_data("Bookings", ttl_val=0), use_container_width=True)

# --- 7. AUTH PAGES (Login/Register) ---
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
            else: st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

elif st.session_state.page == "Register":
    with st.form("reg"):
        nu, np, nf, nt = st.text_input("User"), st.text_input("Pass"), st.text_input("ชื่อจริง"), st.text_input("เบอร์โทร")
        if st.form_submit_button("สมัครสมาชิก"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "phone":nt, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u])); navigate("Login")

# --- 8. PAGE: ADMIN (จัดการคิว) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบแอดมิน")
    df_b = get_data("Bookings", ttl_val=0)
    pending = df_b[df_b['status'] == "รอรับบริการ"]
    if not pending.empty:
        for _, r in pending.sort_values(['date', 'time']).iterrows():
            c1, c2 = st.columns([4, 1])
            c1.write(f"👤 {r['username']} | {r['service']} | {r['date']} ({r['time']})")
            if c2.button("✅ เสร็จสิ้น", key=f"adm_{r['id']}"):
                df_b.loc[df_b['id'] == r['id'], 'status'] = "เสร็จสิ้น"
                conn.update(worksheet="Bookings", data=df_b); st.rerun()
    else: st.info("ไม่มีคิวค้าง")
