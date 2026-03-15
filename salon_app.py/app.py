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
        # ใช้ ttl=10 เพื่อป้องกันการยิง API ถี่เกินไปจนโดน Google Block
        df = conn.read(worksheet=sheet_name, ttl=10).astype(str)
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

def safe_update(sheet_name, df):
    """ฟังก์ชันอัปเดตข้อมูลแบบปลอดภัยเพื่อเลี่ยง Error API"""
    try:
        clean_df = df.fillna("").astype(str)
        conn.update(worksheet=sheet_name, data=clean_df)
        return True
    except Exception as e:
        st.error(f"❌ บันทึกไม่สำเร็จ: โปรดตรวจสอบการแชร์สิทธิ์ (Share) ไฟล์ Google Sheets")
        return False

# --- 3. NAVIGATION & SESSION ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# เก็บจำนวนข้อมูลเพื่อทำระบบจุดแจ้งเตือน
if 'last_booking_count' not in st.session_state: st.session_state.last_booking_count = 0
if 'last_chat_count' not in st.session_state: st.session_state.last_chat_count = 0

def navigate(p):
    st.session_state.page = p
    st.rerun()

# Auto Refresh ทุก 60 วินาที
if st.session_state.page in ["ViewQueues", "Admin", "Booking"]:
    st_autorefresh(interval=60000, key="datarefresh")

# --- 4. NOTIFICATION CHECK ---
df_bookings_all = get_data("Bookings")
df_chats_all = get_data("Chats")

current_b_count = len(df_bookings_all[df_bookings_all['status'] == "รอรับบริการ"])
current_c_count = len(df_chats_all)

has_new_booking = current_b_count > st.session_state.last_booking_count
has_new_chat = current_c_count > st.session_state.last_chat_count

# --- 5. NAVIGATION BAR ---
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
        dot = " 🔴" if (role == 'admin' and (has_new_booking or has_new_chat)) else ""
        btn_label = f"📊 จัดการร้าน{dot}" if role == 'admin' else "✂️ จองคิว"
        if st.button(btn_label): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]:
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")
st.divider()

# --- 6. PAGES ---

# --- 6.1 HOME (หน้าแรก) ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")
    
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+" }
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span style="float:right; color:#FF4B4B;">{price}</span></div>', unsafe_allow_html=True)
    
    # ส่วนที่เพิ่มกลับมา: ติดต่อเรา & GPS
    st.markdown("""
        <div class="contact-section">
            <h3 style="color: #FF4B4B;">📞 ติดต่อเรา</h3>
            <p style="font-size: 1.1em;"><b>🔵 Facebook:</b> 222Salon Songkhla</p>
            <p style="font-size: 1.1em;"><b>📱 โทร:</b> 082-222-2222</p>
            <p style="font-size: 1.1em;"><b>📍 ที่อยู่:</b> 222 ถนนเทศบาล 1 ตำบลบ่อยาง อำเภอเมืองสงขลา</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    mc1, mc2, mc3 = st.columns([1, 2, 1])
    with mc2:
        st.link_button("📍 นำทางด้วย Google Maps (GPS)", "https://maps.google.com", use_container_width=True)

# --- 6.2 REGISTER ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg_form"):
        nf, nu = st.text_input("ชื่อ-นามสกุล"), st.text_input("เบอร์โทรศัพท์")
        np = st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            df_u = get_data("Users")
            u_clean = nu.strip()
            if len(u_clean) == 9: u_clean = "0" + u_clean
            if u_clean in df_u['phone'].values: st.error("❌ เบอร์โทรนี้มีในระบบแล้ว")
            elif not nf or not nu or not np: st.warning("กรุณากรอกข้อมูลให้ครบ")
            else:
                new_u = pd.DataFrame([{"phone": u_clean, "password": hash_pass(np), "fullname": nf, "role": "user"}])
                if safe_update("Users", pd.concat([df_u, new_u], ignore_index=True)):
                    st.success("✅ สมัครสำเร็จ!"); time.sleep(1); navigate("Login")

# --- 6.3 LOGIN ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in, p_in = st.text_input("เบอร์โทรศัพท์"), st.text_input("รหัสผ่าน", type="password")
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

# --- 6.4 BOOKING & CHAT ---
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติการจอง", "💬 แชทสอบถาม"])
    with t1:
        active = df_bookings_all[(df_bookings_all['username'] == st.session_state.username) & (df_bookings_all['status'] == "รอรับบริการ")]
        if not active.empty: st.warning("⚠️ คุณยังมีคิวที่รอรับบริการอยู่")
        else:
            with st.form("booking_form"):
                bd = st.date_input("เลือกวันที่", min_value=datetime.now().date())
                all_times = ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"]
                booked = df_bookings_all[(df_bookings_all['date'] == str(bd)) & (df_bookings_all['status'] == "รอรับบริการ")]['time'].tolist()
                avail = [t for t in all_times if t not in booked]
                bt = st.selectbox("เวลา", avail if avail else ["เต็ม"])
                bs = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
                if st.form_submit_button("ยืนยันการจอง") and avail:
                    if bd.weekday() == 5: st.error("❌ ร้านปิดวันเสาร์")
                    else:
                        new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(bd), "time": bt, "service": bs, "status": "รอรับบริการ", "price": "0"}])
                        if safe_update("Bookings", pd.concat([df_bookings_all, new_q], ignore_index=True)):
                            st.success("✅ จองสำเร็จ!"); time.sleep(1); st.rerun()
    with t2:
        my_qs = df_bookings_all[df_bookings_all['username'] == st.session_state.username].iloc[::-1]
        for _, r in my_qs.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"📅 {r['date']} | ⏰ {r['time']} | {r['service']} | **{r['status']}**")
                if r['status'] == "รอรับบริการ" and c2.button("ยกเลิก", key=f"can_{r['id']}"):
                    df_bookings_all.loc[df_bookings_all['id'] == r['id'], 'status'] = "ยกเลิกโดยลูกค้า"
                    safe_update("Bookings", df_bookings_all); st.rerun()
    with t3:
        with st.container(height=300):
            for _, m in df_chats_all[df_chats_all['username'] == st.session_state.username].iterrows():
                with st.chat_message("user" if m['sender']=="user" else "assistant"): st.write(m['msg'])
        if p := st.chat_input("พิมพ์ข้อความ..."):
            new_m = pd.DataFrame([{"username": st.session_state.username, "sender": "user", "msg": p, "time": datetime.now().strftime("%H:%M")}])
            if safe_update("Chats", pd.concat([df_chats_all, new_m], ignore_index=True)): st.rerun()

# --- 6.5 ADMIN PANEL ---
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2, at3 = st.tabs(["📊 สถิติ", "📅 จัดการคิว" + (" 🔴" if has_new_booking else ""), "📩 แชท" + (" 🔴" if has_new_chat else "")])
    
    with at1:
        done = df_bookings_all[df_bookings_all['status'] == "เสร็จสิ้น"].copy()
        done['price'] = pd.to_numeric(done['price'], errors='coerce').fillna(0)
        st.metric("รายได้รวม", f"{done['price'].sum():,.0f} บาท")
        st.dataframe(done, use_container_width=True)

    with at2:
        st.session_state.last_booking_count = current_b_count # ล้างแจ้งเตือน
        active = df_bookings_all[df_bookings_all['status'] == "รอรับบริการ"]
        for _, r in active.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"👤 {r['fullname']} | ⏰ {r['time']} | {r['service']}")
                pr = col2.number_input("ราคา", min_value=0, key=f"p_{r['id']}")
                if col2.button("✅ เสร็จ", key=f"ok_{r['id']}"):
                    df_bookings_all.loc[df_bookings_all['id'] == r['id'], ['status', 'price']] = ["เสร็จสิ้น", str(pr)]
                    safe_update("Bookings", df_bookings_all); st.rerun()
                if col3.button("❌ ยกเลิก", key=f"no_{r['id']}"):
                    df_bookings_all.loc[df_bookings_all['id'] == r['id'], 'status'] = "ยกเลิกโดยร้าน"
                    safe_update("Bookings", df_bookings_all); st.rerun()

    with at3:
        st.session_state.last_chat_count = current_c_count # ล้างแจ้งเตือน
        for u in df_chats_all['username'].unique():
            with st.expander(f"📩 ข้อความจาก: {u}"):
                for _, m in df_chats_all[df_chats_all['username'] == u].iterrows():
                    with st.chat_message("assistant" if m['sender']=="user" else "user"): st.write(m['msg'])
                with st.form(f"rep_{u}", clear_on_submit=True):
                    rep = st.text_input("ตอบกลับ...")
                    if st.form_submit_button("ส่ง") and rep:
                        new_r = pd.DataFrame([{"username": u, "sender": "admin", "msg": rep, "time": datetime.now().strftime("%H:%M")}])
                        if safe_update("Chats", pd.concat([df_chats_all, new_r], ignore_index=True)): st.rerun()

# --- 6.6 VIEW QUEUES ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิวรอรับบริการวันนี้")
    today = datetime.now().strftime("%Y-%m-%d")
    qs = df_bookings_all[(df_bookings_all['date'] == today) & (df_bookings_all['status'] == "รอรับบริการ")].sort_values('time')
    if not qs.empty: st.table(qs[['time', 'service', 'fullname']])
    else: st.info("ไม่มีรายการจองสำหรับวันนี้")
