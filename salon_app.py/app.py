import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time
import hashlib
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon Songkhla", layout="wide", initial_sidebar_state="collapsed")

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

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
        .contact-section {
            background-color: #ffffff; padding: 25px; border-radius: 15px; 
            border: 1px solid #eee; text-align: center; color: #000; 
            box-shadow: 0px 4px 10px rgba(0,0,0,0.05); margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATABASE ENGINE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    default_cols = {
        "Users": ["phone", "password", "fullname", "role"],
        "Bookings": ["id", "username", "fullname", "date", "time", "service", "status", "price"],
        "Chats": ["username", "sender", "msg", "time"]
    }
    try:
        # ดึงข้อมูลและล้างค่า format
        df = conn.read(worksheet=sheet_name, ttl=0).astype(str)
        if df is None or df.empty:
            return pd.DataFrame(columns=default_cols.get(sheet_name, []))
        
        df.columns = [str(c).strip().lower() for c in df.columns]
        for col in df.columns:
            df[col] = df[col].str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
            if 'phone' in col or 'username' in col:
                df[col] = df[col].apply(lambda x: '0' + x if (len(x) == 9 and x.isdigit()) else x)
        return df
    except Exception:
        return pd.DataFrame(columns=default_cols.get(sheet_name, []))

# --- 3. NAVIGATION & SESSION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

# Auto Refresh 
if st.session_state.page in ["ViewQueues", "Admin", "Booking"]:
    st_autorefresh(interval=60000, key="datarefresh")

# --- 4. NAVIGATION BAR ---
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
    with m_cols[2]:
        btn_label = "📊 จัดการร้าน" if role == 'admin' else "✂️ จองคิว"
        if st.button(btn_label): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]:
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")
st.divider()

# --- 5. PAGES ---

# --- 5.1 HOME ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")
    
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+" }
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span style="float:right; color:#FF4B4B;">{price}</span></div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="contact-section">
            <h3 style="color: #FF4B4B;">📞 ติดต่อเรา</h3>
            <p>🔵 Facebook: 222Salon | 📱 โทร: 082-222-2222</p>
            <p>📍 ที่อยู่: 222 ถนนเทศบาล 1 ตำบลบ่อยาง อำเภอเมืองสงขลา</p>
        </div>
    """, unsafe_allow_html=True)

# --- 5.2 REGISTER ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg_form"):
        nf = st.text_input("ชื่อ-นามสกุล")
        nu = st.text_input("เบอร์โทรศัพท์")
        np = st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            df_u = get_data("Users")
            u_clean = nu.strip()
            if len(u_clean) == 9: u_clean = "0" + u_clean
            if u_clean in df_u['phone'].values:
                st.error("❌ เบอร์โทรนี้มีในระบบแล้ว")
            elif not nf or not nu or not np:
                st.warning("กรุณากรอกข้อมูลให้ครบ")
            else:
                new_u = pd.DataFrame([{"phone": u_clean, "password": hash_pass(np), "fullname": nf, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                st.success("✅ สมัครสำเร็จ!"); time.sleep(1); navigate("Login")

# --- 5.3 LOGIN ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์")
    p_in = st.text_input("รหัสผ่าน", type="password")
    if st.button("ตกลง", type="primary"):
        u_clean = u_in.strip()
        if len(u_clean) == 9: u_clean = "0" + u_clean
        if u_clean == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'admin222', 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_clean) & ((df_u['password'] == hash_pass(p_in)) | (df_u['password'] == p_in))]
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': user.iloc[0]['role'], 'username': u_clean, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking" if user.iloc[0]['role'] == 'user' else "Admin")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

# --- 5.4 USER BOOKING & CHAT ---
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติการจอง", "💬 แชทสอบถาม"])
    df_b = get_data("Bookings")
    
    with t1:
        active = df_b[(df_b['username'] == st.session_state.username) & (df_b['status'] == "รอรับบริการ")]
        if not active.empty:
            st.warning("⚠️ คุณยังมีคิวที่รอรับบริการอยู่")
        else:
            with st.form("booking_form"):
                bd = st.date_input("เลือกวันที่", min_value=datetime.now().date())
                all_times = ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"]
                booked = df_b[(df_b['date'] == str(bd)) & (df_b['status'] == "รอรับบริการ")]['time'].tolist()
                avail = [t for t in all_times if t not in booked]
                bt = st.selectbox("เวลา", avail if avail else ["เต็ม"])
                bs = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
                if st.form_submit_button("ยืนยันการจอง") and avail:
                    if bd.weekday() == 5: st.error("❌ ร้านปิดวันเสาร์")
                    else:
                        new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(bd), "time": bt, "service": bs, "status": "รอรับบริการ", "price": "0"}])
                        conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                        st.success("✅ จองสำเร็จ!"); time.sleep(1); st.rerun()

    with t2:
        my_qs = df_b[df_b['username'] == st.session_state.username].iloc[::-1]
        for _, r in my_qs.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"📅 {r['date']} | ⏰ {r['time']} | {r['service']} | **{r['status']}**")
                if r['status'] == "รอรับบริการ" and c2.button("ยกเลิก", key=f"can_{r['id']}"):
                    df_b.loc[df_b['id'] == r['id'], 'status'] = "ยกเลิกโดยลูกค้า"
                    conn.update(worksheet="Bookings", data=df_b); st.rerun()

    with t3:
        df_c = get_data("Chats")
        with st.container(height=300):
            for _, m in df_c[df_c['username'] == st.session_state.username].iterrows():
                with st.chat_message("user" if m['sender']=="user" else "assistant"): st.write(m['msg'])
        if p := st.chat_input("พิมพ์ข้อความ..."):
            new_m = pd.DataFrame([{"username": st.session_state.username, "sender": "user", "msg": p, "time": datetime.now().strftime("%H:%M")}])
            conn.update(worksheet="Chats", data=pd.concat([df_c, new_m], ignore_index=True)); st.rerun()

# --- 5.5 ADMIN PANEL ---
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2, at3 = st.tabs(["📊 สถิติรายได้", "📅 จัดการคิวลูกค้า", "📩 แชทกับลูกค้า"])
    df_adm = get_data("Bookings")
    
    with at1:
        done = df_adm[df_adm['status'] == "เสร็จสิ้น"].copy()
        done['price'] = pd.to_numeric(done['price'], errors='coerce').fillna(0)
        st.metric("รายได้รวมทั้งหมด", f"{done['price'].sum():,.0f} บาท")
        st.dataframe(done, use_container_width=True)

    with at2:
        active = df_adm[df_adm['status'] == "รอรับบริการ"]
        for _, r in active.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"👤 {r['fullname']} | ⏰ {r['time']} | {r['service']}")
                pr = col2.number_input("ใส่ราคา (บาท)", min_value=0, key=f"p_{r['id']}")
                if col2.button("✅ เสร็จสิ้น", key=f"ok_{r['id']}"):
                    df_adm.loc[df_adm['id'] == r['id'], ['status', 'price']] = ["เสร็จสิ้น", str(pr)]
                    conn.update(worksheet="Bookings", data=df_adm); st.rerun()
                if col3.button("❌ ยกเลิกคิว", key=f"no_{r['id']}"):
                    df_adm.loc[df_adm['id'] == r['id'], 'status'] = "ยกเลิกโดยร้าน"
                    conn.update(worksheet="Bookings", data=df_adm); st.rerun()

    with at3:
        df_ch = get_data("Chats")
        for u in df_ch['username'].unique():
            with st.expander(f"📩 ข้อความจาก: {u}"):
                for _, m in df_ch[df_ch['username'] == u].iterrows():
                    with st.chat_message("assistant" if m['sender']=="user" else "user"): st.write(m['msg'])
                with st.form(f"rep_{u}", clear_on_submit=True):
                    rep = st.text_input("ตอบกลับลูกค้า...")
                    if st.form_submit_button("ส่งข้อความ") and rep:
                        new_r = pd.DataFrame([{"username": u, "sender": "admin", "msg": rep, "time": datetime.now().strftime("%H:%M")}])
                        conn.update(worksheet="Chats", data=pd.concat([df_ch, new_r], ignore_index=True)); st.rerun()

# --- 5.6 VIEW TODAY'S QUEUES ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิวรอรับบริการวันนี้")
    df_q = get_data("Bookings")
    today = datetime.now().strftime("%Y-%m-%d")
    qs = df_q[(df_q['date'] == today) & (df_q['status'] == "รอรับบริการ")].sort_values('time')
    if not qs.empty:
        st.table(qs[['time', 'service', 'fullname']])
    else:
        st.info("ไม่มีรายการจองสำหรับวันนี้")
