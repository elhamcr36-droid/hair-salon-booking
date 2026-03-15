import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time
import hashlib

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
        /* ปรับแต่ง Chat Bubble */
        [data-testid="stChatMessage"][data-testid^="stChatMessageUser"] {
            flex-direction: row-reverse !important; background-color: #0084FF !important;
            color: white !important; border-radius: 15px 15px 2px 15px !important;
        }
        [data-testid="stChatMessage"][data-testid^="stChatMessageAssistant"] {
            background-color: #E4E6EB !important; color: black !important;
            border-radius: 15px 15px 15px 2px !important;
        }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. DATA ENGINE ---
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df is None or df.empty: return pd.DataFrame()
        
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        for col in df.columns:
            # จัดการเลข .0 และช่องว่าง
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
            # ตรวจสอบเบอร์โทรศัพท์ (ถ้าเริ่มด้วย 8 หรือ 9 ให้เติม 0)
            if 'phone' in col or 'username' in col:
                df[col] = df[col].apply(lambda x: '0' + x if len(x) == 9 and x.isdigit() else x)
        return df
    except Exception as e:
        return pd.DataFrame()

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
    if role == 'admin':
        with m_cols[2]: 
            if st.button("📊 จัดการร้าน"): navigate("Admin")
    else:
        with m_cols[2]: 
            if st.button("✂️ จองคิว"): navigate("Booking")
    with m_cols[4]:
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")
st.divider()

# --- 4. PAGE LOGIC ---

# 1. หน้าแรก
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")
    
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+" }
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span style="float:right; color:#FF4B4B;">{price}</span></div>', unsafe_allow_html=True)

    st.divider()
    
    # ส่วนติดต่อและพิกัดร้าน
    shop_addr = "222 ถนนเทศบาล 1 ตำบลบ่อยาง อำเภอเมืองสงขลา สงขลา 90000"
    st.markdown(f"""
        <div class="contact-section">
            <h3 style="color: #FF4B4B; margin-bottom: 15px;">📞 ติดต่อเรา & พิกัดร้าน</h3>
            <p style="font-size: 1.1em;">🔵 <b>Facebook:</b> <a href="https://www.facebook.com/222Salon" target="_blank" style="color: #1877F2; text-decoration: none; font-weight: bold;">222Salon</a></p>
            <p style="font-size: 1.1em;">📱 <b>เบอร์โทรศัพท์:</b> 082-222-2222</p>
            <p style="font-size: 1.1em;">💬 <b>LINE ID:</b> 222Salon</p>
            <hr style="margin: 15px 0; border: 0.5px solid #eee;">
            <p style="font-size: 1em; color: #555;">📍 <b>ที่อยู่:</b> {shop_addr}</p>
        </div>
    """, unsafe_allow_html=True)
    
    maps_url = f"https://www.google.com/maps/search/?api=1&query={shop_addr.replace(' ', '+')}"
    st.link_button("🗺️ เปิดใน Google Maps", maps_url, use_container_width=True)

# 2. หน้าสมัครสมาชิก
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg"):
        nf = st.text_input("ชื่อ-นามสกุล")
        nu = st.text_input("เบอร์โทรศัพท์")
        np = st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            if not nf or not nu or not np: st.error("❌ กรุณากรอกข้อมูลให้ครบ")
            else:
                df_u = get_data("Users")
                u_clean = nu.strip()
                if len(u_clean) == 9: u_clean = "0" + u_clean
                
                if not df_u.empty and u_clean in df_u['phone'].values:
                    st.error("❌ เบอร์โทรนี้มีในระบบแล้ว")
                else:
                    hashed_pw = hash_pass(np.strip())
                    new_u = pd.DataFrame([{"phone": u_clean, "password": hashed_pw, "fullname": nf.strip(), "role": "user"}])
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                    st.success("✅ ลงทะเบียนสำเร็จ!"); time.sleep(1); navigate("Login")

# 3. หน้าเข้าสู่ระบบ
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์")
    p_in = st.text_input("รหัสผ่าน", type="password")
    if st.button("ตกลง", type="primary"):
        u_clean = u_in.strip()
        if len(u_clean) == 9: u_clean = "0" + u_clean
        p_raw = p_in.strip()
        p_hashed = hash_pass(p_raw)
        
        if u_clean == "admin222" and p_raw == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': u_clean, 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            if not df_u.empty:
                # ตรวจสอบทั้งรหัสธรรมดาและ Hashed
                user = df_u[(df_u['phone'] == u_clean) & ((df_u['password'] == p_raw) | (df_u['password'] == p_hashed))]
                if not user.empty:
                    st.session_state.update({'logged_in': True, 'user_role': user.iloc[0]['role'], 'username': u_clean, 'fullname': user.iloc[0]['fullname']})
                    navigate("Booking" if user.iloc[0]['role'] == 'user' else "Admin")
                else: st.error("❌ ข้อมูลไม่ถูกต้อง")
            else: st.error("❌ ไม่พบข้อมูลผู้ใช้")

# 4. หน้าจองคิว
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติ", "💬 แชทสอบถาม"])
    df_b = get_data("Bookings")
    
    with t1:
        active_booking = df_b[(df_b['username'] == st.session_state.username) & (df_b['status'] == "รอรับบริการ")]
        if not active_booking.empty:
            st.warning("⚠️ คุณมีคิวที่รอรับบริการอยู่")
        else:
            with st.form("b"):
                bd = st.date_input("เลือกวันที่", min_value=datetime.now().date())
                all_times = ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"]
                # กรองเวลาที่ถูกจองแล้ว
                booked = df_b[(df_b['date'] == str(bd)) & (df_b['status'] == "รอรับบริการ")]['time'].tolist()
                avail = [t for t in all_times if t not in booked]
                
                bt = st.selectbox("เวลา", avail if avail else ["เต็ม"])
                bs = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
                if st.form_submit_button("ยืนยัน") and avail:
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
                c1.write(f"📅 {r['date']} | ⏰ {r['time']} | {r['service']} | {r['status']}")
                if r['status'] == "รอรับบริการ":
                    if c2.button("ยกเลิก", key=f"can_{r['id']}"):
                        df_b.loc[df_b['id'] == r['id'], 'status'] = "ยกเลิกโดยลูกค้า"
                        conn.update(worksheet="Bookings", data=df_b); st.rerun()

    with t3:
        df_c = get_data("Chats")
        with st.container(height=300):
            if not df_c.empty:
                for _, m in df_c[df_c['username'] == st.session_state.username].iterrows():
                    with st.chat_message("user" if m['sender']=="user" else "assistant"): st.write(m['msg'])
        if p := st.chat_input("พิมพ์ข้อความ..."):
            new_m = pd.DataFrame([{"username": st.session_state.username, "sender": "user", "msg": p, "time": datetime.now().strftime("%H:%M")}])
            conn.update(worksheet="Chats", data=pd.concat([df_c, new_m], ignore_index=True)); st.rerun()

# 5. หน้าแอดมิน
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2, at3 = st.tabs(["📊 สรุปยอด", "📅 จัดการคิว", "📩 แชทลูกค้า"])
    df_adm = get_data("Bookings")
    
    with at1:
        if not df_adm.empty:
            done = df_adm[df_adm['status'] == "เสร็จสิ้น"].copy()
            done['price'] = pd.to_numeric(done['price'], errors='coerce').fillna(0)
            st.metric("รายได้รวม", f"{done['price'].sum():,.0f} บ.")
            st.dataframe(done, use_container_width=True)

    with at2:
        active = df_adm[df_adm['status'] == "รอรับบริการ"] if not df_adm.empty else pd.DataFrame()
        for _, r in active.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"👤 {r['fullname']} | ⏰ {r['time']} | {r['service']}")
                pr = col2.number_input("ราคา", min_value=0, key=f"p{r['id']}")
                if col2.button("✅ เสร็จ", key=f"ok{r['id']}"):
                    df_adm.loc[df_adm['id'] == r['id'], ['status', 'price']] = ["เสร็จสิ้น", str(pr)]
                    conn.update(worksheet="Bookings", data=df_adm); st.rerun()
                if col3.button("❌ ยกเลิก", key=f"no{r['id']}"):
                    df_adm.loc[df_adm['id'] == r['id'], 'status'] = "ยกเลิกโดยร้าน"
                    conn.update(worksheet="Bookings", data=df_adm); st.rerun()

    with at3:
        df_ch = get_data("Chats")
        if not df_ch.empty:
            for u in df_ch['username'].unique():
                with st.expander(f"📩 แชทจาก: {u}"):
                    for _, m in df_ch[df_ch['username'] == u].iterrows():
                        with st.chat_message("assistant" if m['sender']=="user" else "user"): st.write(m['msg'])
                    with st.form(f"rep_{u}", clear_on_submit=True):
                        rep = st.text_input("ตอบกลับ...")
                        if st.form_submit_button("ส่ง") and rep:
                            new_r = pd.DataFrame([{"username": u, "sender": "admin", "msg": rep, "time": datetime.now().strftime("%H:%M")}])
                            conn.update(worksheet="Chats", data=pd.concat([df_ch, new_r], ignore_index=True)); st.rerun()

# 6. หน้าดูคิววันนี้
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิววันนี้")
    df_q = get_data("Bookings")
    today = datetime.now().strftime("%Y-%m-%d")
    if not df_q.empty:
        qs = df_q[(df_q['date'] == today) & (df_q['status'] == "รอรับบริการ")].sort_values('time')
        if not qs.empty: st.table(qs[['time', 'service', 'fullname']])
        else: st.info("ไม่มีคิวจองในวันนี้")
