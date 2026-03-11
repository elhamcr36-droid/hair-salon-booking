import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon-Final", layout="wide", initial_sidebar_state="collapsed")

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
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl="0s")
        if df is None or df.empty: return pd.DataFrame()
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
            if 'phone' in col or 'username' in col:
                df[col] = df[col].apply(lambda x: '0' + x if len(x) == 9 and x.isdigit() else x)
        return df
    except: return pd.DataFrame()

# --- 2. SESSION & NAVIGATION ---
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
        lbl = "📊 จัดการร้าน" if role == 'admin' else "✂️ จองคิว"
        if st.button(lbl): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]:
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")
st.divider()

# --- 3. PAGE LOGIC ---

if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    # แถบเวลาเปิด-ปิด จะแสดงเฉพาะหน้าแรกเพื่อให้ลูกค้าทราบเท่านั้น
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (หยุดทุกวันพุธ)")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"}
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span class="price-text">{price}</span></div>', unsafe_allow_html=True)

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg_form"):
        nf, nu, np, npc = st.text_input("ชื่อ-นามสกุล"), st.text_input("เบอร์โทรศัพท์"), st.text_input("รหัสผ่าน", type="password"), st.text_input("ยืนยันรหัสผ่าน", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            if nu and np == npc and nf:
                df_u = get_data("Users")
                if not df_u.empty and nu in df_u['phone'].values: st.error("❌ เบอร์นี้ถูกใช้งานแล้ว")
                else:
                    new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                    st.success("✅ สำเร็จ!"); navigate("Login")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์").strip()
    p_in = st.text_input("รหัสผ่าน", type="password").strip()
    if st.button("ตกลง", type="primary"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'admin222', 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)] if not df_u.empty else pd.DataFrame()
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

# --- หน้าลูกค้า ---
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิว", "💬 แชทกับร้าน"])
    with t1:
        with st.form("b_form"):
            b_d = st.date_input("เลือกวันที่", min_value=datetime.now().date())
            b_t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            b_s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยัน"):
                df_b = get_data("Bookings")
                is_taken = df_b[(df_b['date'] == str(b_d)) & (df_b['time'] == b_t)] if not df_b.empty else pd.DataFrame()
                if is_taken.empty:
                    new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(b_d), "time": b_t, "service": b_s, "status": "รอรับบริการ", "price": "0"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                    st.success("✅ จองสำเร็จ!")
                else: st.error("❌ เวลานี้มีผู้จองแล้ว")
    with t2:
        df_b = get_data("Bookings")
        if not df_b.empty:
            my_qs = df_b[df_b['username'] == st.session_state.username]
            for _, r in my_qs.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"📅 {r['date']} | ⏰ {r['time']} | {r['service']}\nสถานะ: `{r['status']}`")
                    if r['status'] == "รอรับบริการ":
                        if c2.button("🗑️ ยกเลิก", key=f"del_{r['id']}"):
                            df_b = df_b[df_b['id'] != r['id']]
                            conn.update(worksheet="Bookings", data=df_b); st.rerun()
    with t3:
        df_m = get_data("Messages")
        chat_c = st.container(height=300)
        if not df_m.empty:
            for _, m in df_m[df_m['username'] == st.session_state.username].iterrows():
                chat_c.chat_message("user").write(m['message'])
                if m['admin_reply']: chat_c.chat_message("assistant").info(m['admin_reply'])
        with st.form("send_m", clear_on_submit=True):
            msg = st.text_input("พิมพ์ข้อความตอบโต้กับร้าน...")
            if st.form_submit_button("ส่ง") and msg:
                new_m = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "message": msg, "timestamp": datetime.now().strftime("%H:%M"), "admin_reply": ""}])
                conn.update(worksheet="Messages", data=pd.concat([df_m, new_m], ignore_index=True))
                st.rerun()

# --- หน้าแอดมิน (จัดการร้าน) ---
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2, at3 = st.tabs(["📊 สรุปยอด", "📅 จัดการคิว", "📩 แชทลูกค้า"])
    df_b = get_data("Bookings")
    with at1:
        # ลบแถบสีน้ำเงินเวลาเปิดร้านและช่องเบอร์โทรออกแล้ว
        if not df_b.empty:
            df_b['price'] = pd.to_numeric(df_b['price'], errors='coerce').fillna(0)
            st.metric("รายได้รวม", f"{df_b[df_b['status']=='เสร็จสิ้น']['price'].sum():,.0f} บ.")
    with at2:
        if not df_b.empty:
            for _, row in df_b[df_b['status'] == "รอรับบริการ"].iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    col1.write(f"👤 {row['fullname']} | ⏰ {row['time']} ({row['date']})")
                    with col2.popover("✅ เสร็จสิ้น"):
                        p = st.number_input("ราคา", key=f"p_{row['id']}")
                        if st.button("บันทึก", key=f"f_{row['id']}"):
                            df_b.loc[df_b['id']==row['id'], ['status', 'price']] = ["เสร็จสิ้น", str(p)]
                            conn.update(worksheet="Bookings", data=df_b); st.rerun()
                    if col2.button("🗑️ ลบข้อมูล", key=f"a_del_{row['id']}"):
                        df_b = df_b[df_b['id'] != row['id']]
                        conn.update(worksheet="Bookings", data=df_b); st.rerun()
    with at3:
        df_m = get_data("Messages")
        if not df_m.empty:
            sel_u = st.selectbox("เลือกแชทลูกค้าเพื่อตอบกลับ", df_m['username'].unique())
            for _, m in df_m[df_m['username'] == sel_u].iterrows():
                st.write(f"👤 {sel_u}: {m['message']}")
                if m['admin_reply']: st.caption(f"🤖 ตอบแล้ว: {m['admin_reply']}")
            with st.form("rep", clear_on_submit=True):
                ans = st.text_input("พิมพ์คำตอบส่งถึงลูกค้า...")
                if st.form_submit_button("ตอบกลับ"):
                    last_idx = df_m[df_m['username'] == sel_u].index[-1]
                    df_m.at[last_idx, 'admin_reply'] = ans
                    conn.update(worksheet="Messages", data=df_m); st.rerun()

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิววันนี้")
    df_b = get_data("Bookings")
    today = datetime.now().strftime("%Y-%m-%d")
    if not df_b.empty:
        active = df_b[(df_b['date'] == today) & (df_b['status'] == "รอรับบริการ")]
        if not active.empty:
            st.table(active[['time', 'service', 'fullname']].sort_values('time'))
        else: st.info("ยังไม่มีคิวในวันนี้")
