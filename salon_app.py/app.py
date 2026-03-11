import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. SETTINGS & CSS (หน้าตาแอป) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 8px; font-weight: bold; transition: 0.2s;}
        
        /* การ์ดบริการและติดต่อ - ตัวหนังสือดำชัดเจน */
        .price-card, .contact-box {
            background-color: #ffffff !important; padding: 20px; border-radius: 15px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #000000 !important;
            margin-bottom: 15px; text-align: center; border: 1px solid #eee;
        }
        .price-card b, .contact-box h3, .contact-box p { color: #000000 !important; }
        .price-text { color: #FF4B4B !important; font-weight: bold; font-size: 1.2rem; }
        
        /* รายการจองคิว Admin */
        .booking-item {
            background-color: #ffffff; color: #000000; padding: 12px;
            border-radius: 10px; margin-bottom: 8px; border-left: 5px solid #FF4B4B;
            box-shadow: 1px 2px 5px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl="0s")
        df = df.dropna(how='all')
        req = {
            "Users": ["username", "password", "fullname", "role"],
            "Bookings": ["id", "username", "service", "date", "time", "status"],
            "Messages": ["id", "username", "message", "timestamp", "status", "admin_reply"]
        }
        if df.empty: return pd.DataFrame(columns=req.get(sheet_name, []))
        df.columns = [str(c).strip() for c in df.columns]
        df = df.fillna("")
        for col in req.get(sheet_name, []):
            if col not in df.columns: df[col] = ""
        return df
    except: return pd.DataFrame()

# --- 2. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)
m_cols = st.columns(5)
with m_cols[0]:
    if st.button("🏠 หน้าแรก"): navigate("Home")
with m_cols[1]:
    if st.button("📅 คิววันนี้"): navigate("ViewQueues")

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
        if st.button("🚪 ออก"):
            st.session_state.clear()
            navigate("Home")

st.divider()

# --- 3. HELPER: MESSENGER UI (EDIT & DELETE) ---
def display_messenger_pro(df_m, target_user, is_admin=False):
    chat_box = st.container(height=500, border=True)
    with chat_box:
        messages = df_m[df_m['username'] == target_user].sort_values('timestamp')
        if messages.empty: st.info("👋 เริ่มการสนทนาได้เลย")
        
        for _, m in messages.iterrows():
            # [ลูกค้ารับส่ง]
            c_m, c_e, c_d = st.columns([4, 0.6, 0.6])
            with c_m:
                with st.chat_message("user"):
                    st.write(m['message'])
                    st.caption(f"🕒 {m['timestamp']} {m.get('status','')}")
            
            # ลูกค้าลบ/แก้ของตัวเอง
            if not is_admin and st.session_state.username == m['username']:
                if c_e.button("✏️", key=f"ed_{m['id']}"):
                    new = st.text_input("แก้ข้อความ:", value=m['message'], key=f"in_{m['id']}")
                    if st.button("บันทึก", key=f"sv_{m['id']}"):
                        df_m.loc[df_m['id'] == m['id'], 'message'] = new
                        df_m.loc[df_m['id'] == m['id'], 'status'] = "(แก้ไขแล้ว)"
                        conn.update(worksheet="Messages", data=df_m); st.rerun()
                if c_d.button("🗑️", key=f"dl_{m['id']}"):
                    df_m = df_m[df_m['id'] != m['id']]
                    conn.update(worksheet="Messages", data=df_m); st.rerun()

            # [แอดมินตอบกลับ]
            if m['admin_reply']:
                ca_m, ca_e, ca_d = st.columns([4, 0.6, 0.6])
                with ca_m:
                    with st.chat_message("assistant", avatar="✂️"):
                        st.write(m['admin_reply'])
                        st.caption("Admin Reply")
                
                # แอดมินลบ/แก้คำตอบตัวเอง
                if is_admin:
                    if ca_e.button("✏️", key=f"aed_{m['id']}"):
                        new_r = st.text_input("แก้คำตอบ:", value=m['admin_reply'], key=f"ain_{m['id']}")
                        if st.button("บันทึก", key=f"asv_{m['id']}"):
                            df_m.loc[df_m['id'] == m['id'], 'admin_reply'] = new_r
                            conn.update(worksheet="Messages", data=df_m); st.rerun()
                    if ca_d.button("🗑️", key=f"adl_{m['id']}"):
                        df_m.loc[df_m['id'] == m['id'], 'admin_reply'] = ""
                        conn.update(worksheet="Messages", data=df_m); st.rerun()

# --- 4. PAGE: HOME ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.subheader("📋 บริการและราคา")
    c1, c2 = st.columns(2)
    with c1: st.markdown('<div class="price-card"><b>✂️ ตัดผมชาย</b><br><span class="price-text">150-350 บ.</span></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="price-card"><b>💇‍♀️ ตัดผมหญิง</b><br><span class="price-text">350-800 บ.</span></div>', unsafe_allow_html=True)
    st.divider()
    st.subheader("📞 ติดต่อเรา")
    cc1, cc2 = st.columns(2)
    with cc1: st.markdown('<div class="contact-box"><h3>📞 โทร</h3><p>081-222-XXXX</p></div>', unsafe_allow_html=True)
    with cc2: st.markdown('<div class="contact-box"><h3>💬 Line</h3><p>@222salon</p></div>', unsafe_allow_html=True)

# --- 5. PAGE: BOOKING (Customer) ---
elif st.session_state.page == "Booking":
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 Messenger"])
    with t3:
        st.subheader("💬 คุยกับแอดมิน")
        df_m = get_data("Messages")
        display_messenger_pro(df_m, st.session_state.username)
        with st.form("send_msg", clear_on_submit=True):
            m_in = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง ✈️") and m_in:
                new = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "message": m_in, "timestamp": datetime.now().strftime("%H:%M"), "status": "", "admin_reply": ""}])
                conn.update(worksheet="Messages", data=pd.concat([df_m, new], ignore_index=True)); st.rerun()
    # (ส่วนจองคิวและประวัติคงเดิมตามเวอร์ชันก่อนหน้า)
    with t1:
        with st.form("bk"):
            svc = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม"])
            d = st.date_input("วันที่", min_value=datetime.now().date())
            t = st.selectbox("เวลา", ["09:30", "10:30", "13:00", "15:00", "17:00"])
            if st.form_submit_button("จองคิว"):
                df_b = get_data("Bookings")
                new_b = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "service": svc, "date": str(d), "time": t, "status": "รอรับบริการ"}])
                conn.update(worksheet="Bookings", data=pd.concat([df_b, new_b], ignore_index=True)); st.success("จองแล้ว!"); st.rerun()

# --- 6. PAGE: ADMIN (จัดการคิว + แชท) ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบแอดมิน")
    at1, at2 = st.tabs(["📅 คิวลูกค้า", "📩 Messenger แชท"])
    
    with at1:
        df_b = get_data("Bookings")
        pending = df_b[df_b['status'].isin(['รอรับบริการ', ''])]
        for _, row in pending.iterrows():
            c_i, c_o, c_d = st.columns([3, 1, 1])
            c_i.markdown(f"<div class='booking-item'><b>คุณ {row['username']}</b><br>{row['date']} {row['time']} | {row['service']}</div>", unsafe_allow_html=True)
            if c_o.button("✅ เสร็จ", key=f"ok_{row['id']}"):
                df_b.loc[df_b['id'] == row['id'], 'status'] = 'เสร็จสิ้น'
                conn.update(worksheet="Bookings", data=df_b); st.rerun()
            if c_d.button("🗑️ ลบ", key=f"dl_{row['id']}"):
                df_b = df_b[df_b['id'] != row['id']]
                conn.update(worksheet="Bookings", data=df_b); st.rerun()

    with at2:
        df_m = get_data("Messages")
        users = df_m['username'].unique()
        if len(users) > 0:
            sel_u = st.selectbox("เลือกแชทลูกค้า:", users)
            display_messenger_pro(df_m, sel_u, is_admin=True)
            with st.form("rep_f", clear_on_submit=True):
                ans = st.text_input("ตอบกลับ...")
                if st.form_submit_button("ส่งตอบกลับ"):
                    df_m.loc[df_m[df_m['username'] == sel_u].index[-1], 'admin_reply'] = ans
                    conn.update(worksheet="Messages", data=df_m); st.rerun()

# --- 7. AUTH ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u, p = st.text_input("เบอร์โทร"), st.text_input("รหัสผ่าน", type="password")
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
            else: st.error("ข้อมูลผิด")

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nu, np, nf = st.text_input("เบอร์"), st.text_input("รหัส"), st.text_input("ชื่อ")
        if st.form_submit_button("สมัคร"):
            df_u = get_data("Users")
            conn.update(worksheet="Users", data=pd.concat([df_u, pd.DataFrame([{"username": nu, "password": np, "fullname": nf, "role": "user"}])], ignore_index=True))
            st.success("สำเร็จ"); navigate("Login")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 คิววันนี้")
    df_b = get_data("Bookings")
    active = df_b[(df_b['date'] == datetime.now().strftime("%Y-%m-%d")) & (df_b['status'].isin(['รอรับบริการ', '']))]
    st.table(active[['time', 'service']]) if not active.empty else st.write("ไม่มีคิว")
