import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon-Fixed", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; height: 3.2em; transition: 0.3s;}
        
        /* การ์ดบริการ */
        .price-card {
            background-color: #ffffff !important; padding: 18px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 12px;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.08); color: #000000 !important;
        }
        .price-text { float: right; color: #FF4B4B; font-weight: bold; }
        
        /* ข้อมูลติดต่อสีดำ */
        .contact-section-black { 
            background-color: #ffffff; padding: 30px; border-radius: 15px; text-align: center; 
            box-shadow: 0px 4px 15px rgba(0,0,0,0.1); border: 1px solid #eeeeee;
            color: #000000 !important;
        }
        .contact-section-black h3, .contact-section-black p { color: #000000 !important; }
        .map-link { color: #0000EE !important; text-decoration: underline; font-weight: bold; }
        
        /* ส่วนแชท (บังคับตัวหนังสือสีดำ) */
        .chat-msg { padding: 12px; border-radius: 15px; margin-bottom: 10px; max-width: 85%; line-height: 1.4; }
        .user-msg { background-color: #E3F2FD; margin-left: auto; text-align: right; color: #000000 !important; border: 1px solid #BBDEFB; }
        .admin-msg { background-color: #F5F5F5; margin-right: auto; text-align: left; color: #000000 !important; border: 1px solid #E0E0E0; }
        .msg-meta { font-size: 0.75em; color: #666; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    st.cache_data.clear() 
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df is None or df.empty: return pd.DataFrame()
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace('nan', '')
        return df
    except Exception as e:
        return pd.DataFrame()

# --- 2. NAVIGATION ---
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
    if st.session_state.get('user_role') == 'admin':
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

# --- 3. PAGE LOGIC ---

# 🏠 หน้าแรก
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"}
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span class="price-text">{price}</span></div>', unsafe_allow_html=True)
    
    st.divider()
    google_maps_url = "https://www.google.com/maps/search/?api=1&query=222+ถนนเทศบาล+1+ตำบลบ่อยาง+อำเภอเมืองสงขลา+สงขลา+90000"
    st.markdown(f"""
        <div class="contact-section-black">
            <h3>📞 ติดต่อเรา & พิกัดร้าน</h3>
            <p>📱 <b>เบอร์โทรศัพท์:</b> 081-222-2222</p>
            <p>💬 <b>LINE ID:</b> @222salon</p>
            <p>📍 <b>พิกัด:</b> <a class="map-link" href="{google_maps_url}" target="_blank">222 ถนนเทศบาล 1 ตำบลบ่อยาง อำเภอเมืองสงขลา สงขลา 90000</a></p>
            <p style="font-size: 0.85em; color: #555 !important;">(คลิกพิกัดเพื่อเปิด GPS นำทาง | จอดรถได้ที่หน้าร้านครับ)</p>
        </div>
    """, unsafe_allow_html=True)

# 📅 หน้าคิววันนี้
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิวรอรับบริการวันนี้")
    df_q = get_data("Bookings")
    today = datetime.now().strftime("%Y-%m-%d")
    if not df_q.empty:
        today_qs = df_q[(df_q['date'] == today) & (df_q['status'] == "รอรับบริการ")].sort_values('time')
        if not today_qs.empty:
            st.table(today_qs[['time', 'service', 'fullname']])
        else: st.info("ยังไม่มีคิวในวันนี้")
    else: st.info("ไม่มีข้อมูล")

# 📝 สมัครสมาชิก
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nf = st.text_input("ชื่อ-นามสกุล")
        nu = st.text_input("เบอร์โทรศัพท์")
        np = st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            df_u = get_data("Users")
            if not df_u.empty and nu in df_u['phone'].values: st.error("❌ เบอร์โทรนี้สมัครแล้ว")
            else:
                new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                st.success("✅ สมัครสำเร็จ!"); time.sleep(1); navigate("Login")

# 🔑 เข้าสู่ระบบ
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์")
    p_in = st.text_input("รหัสผ่าน", type="password")
    if st.button("ตกลง", type="primary"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': u_in, 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)] if not df_u.empty else pd.DataFrame()
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("❌ เบอร์โทรหรือรหัสผ่านไม่ถูกต้อง")

# ✂️ หน้าลูกค้า (จอง/ประวัติ/แชท)
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิว", "💬 แชทสอบถาม"])
    
    with t1:
        with st.form("b_form"):
            b_d = st.date_input("วันที่", min_value=datetime.now().date())
            b_t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"])
            b_s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยัน"):
                df_all = get_data("Bookings")
                active = df_all[(df_all['username'] == st.session_state.username) & (df_all['status'] == "รอรับบริการ")]
                if b_d.weekday() == 5: st.error("❌ หยุดทุกวันเสาร์")
                elif not active.empty: st.warning("⚠️ คุณมีคิวที่ยังไม่ได้รับบริการ")
                else:
                    new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(b_d), "time": b_t, "service": b_s, "status": "รอรับบริการ", "price": "0"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_all, new_q], ignore_index=True))
                    st.success("✅ จองสำเร็จ!"); time.sleep(1); st.rerun()

    with t2:
        df_h = get_data("Bookings")
        if not df_h.empty:
            my = df_h[df_h['username'] == st.session_state.username].iloc[::-1]
            for _, r in my.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"📅 {r['date']} | ⏰ {r['time']} \n **{r['service']}** | สถานะ: {r['status']}")
                    if r['status'] == "รอรับบริการ" and c2.button("❌ ยกเลิก", key=r['id']):
                        df_h.loc[df_h['id'] == r['id'], 'status'] = "ยกเลิกโดยลูกค้า"
                        conn.update(worksheet="Bookings", data=df_h); st.rerun()

    with t3:
        st.subheader("💬 สนทนากับร้าน")
        df_msg = get_data("Messages") 
        box = st.container(height=350, border=True)
        if not df_msg.empty:
            my_m = df_msg[df_msg['username'] == st.session_state.username]
            for _, m in my_m.iterrows():
                if m['message']:
                    box.markdown(f'<div class="chat-msg user-msg">{m["message"]}<div class="msg-meta">{m.get("timestamp", "")}</div></div>', unsafe_allow_html=True)
                if m.get('admin_reply'):
                    box.markdown(f'<div class="chat-msg admin-msg"><b>ร้านตอบกลับ:</b><br>{m["admin_reply"]}</div>', unsafe_allow_html=True)
        
        with st.form("chat_f", clear_on_submit=True):
            txt = st.text_input("ถามร้านค้า...")
            if st.form_submit_button("ส่ง") and txt:
                new_m = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "message": txt, "timestamp": datetime.now().strftime("%d/%m %H:%M"), "admin_reply": ""}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m], ignore_index=True))
                st.rerun()

# 📊 หน้าแอดมิน
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2, at3 = st.tabs(["📊 สรุปยอด", "📅 คิวลูกค้า", "📩 แชท"])
    
    with at2:
        df_a = get_data("Bookings")
        wait = df_a[df_a['status'] == "รอรับบริการ"] if not df_a.empty else pd.DataFrame()
        for _, r in wait.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"👤 {r['fullname']} | ⏰ {r['time']} \n {r['date']} | {r['service']}")
                pr = col2.number_input("ราคา", min_value=0, key=f"p{r['id']}")
                if col2.button("✅ เสร็จ", key=f"ok{r['id']}"):
                    df_a.loc[df_a['id'] == r['id'], ['status', 'price']] = ["เสร็จสิ้น", str(pr)]
                    conn.update(worksheet="Bookings", data=df_a); st.rerun()
                if col3.button("❌ ยก", key=f"no{r['id']}"):
                    df_a.loc[df_a['id'] == r['id'], 'status'] = "ยกเลิกโดยร้าน"
                    conn.update(worksheet="Bookings", data=df_a); st.rerun()
    
    with at3:
        st.subheader("📩 ตอบแชท")
        df_ch = get_data("Messages")
        if not df_ch.empty:
            for idx, m in df_ch.iterrows():
                if not m['admin_reply']:
                    with st.expander(f"แชทจากคุณ: {m['username']}"):
                        st.write(f"💬: {m['message']}")
                        with st.form(key=f"rep_{m['id']}"):
                            ans = st.text_input("ตอบ...")
                            if st.form_submit_button("ส่ง"):
                                df_ch.at[idx, 'admin_reply'] = ans
                                conn.update(worksheet="Messages", data=df_ch); st.rerun()
