import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon-Complete", layout="wide", initial_sidebar_state="collapsed")

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
        .price-text { float: right; color: #FF4B4B; font-weight: bold; }
        .contact-section { 
            background-color: #ffffff; padding: 30px; border-radius: 15px; text-align: center; 
            box-shadow: 0px 4px 15px rgba(0,0,0,0.1); border: 1px solid #eeeeee;
        }
        .chat-msg { padding: 12px; border-radius: 15px; margin-bottom: 10px; max-width: 80%; }
        .user-msg { background-color: #E3F2FD; margin-left: auto; text-align: right; border-bottom-right-radius: 2px; }
        .admin-msg { background-color: #F5F5F5; margin-right: auto; text-align: left; border-bottom-left-radius: 2px; }
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
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
            if 'phone' in col or 'username' in col:
                df[col] = df[col].apply(lambda x: '0' + x if len(x) == 9 and x.isdigit() else x)
        return df
    except:
        return pd.DataFrame()

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

# --- 3. PAGE LOGIC ---

# 1. หน้าแรก (กลับมาครบแล้ว!)
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000", caption="222-Salon ยินดีต้อนรับครับ")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")
    
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"}
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span class="price-text">{price}</span></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("""
        <div class="contact-section">
            <h3 style="color: #FF4B4B; margin-top: 0;">📞 ติดต่อเรา & พิกัดร้าน</h3>
            <p><b>📱 เบอร์โทรศัพท์:</b> 081-222-2222</p>
            <p><b>💬 LINE ID:</b> @222salon</p>
            <p><b>📍 พิกัด:</b> 222 ถนนเทศบาล 1 ซอย 2 (หลังตลาดสดเทศบาล)</p>
            <p style="color: #666; font-size: 0.9em;">(สามารถจอดรถได้ที่หน้าร้านหรือลานจอดรถตลาดครับ)</p>
        </div>
    """, unsafe_allow_html=True)

# 2. หน้าสมัครสมาชิก
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg_form"):
        nf = st.text_input("ชื่อ-นามสกุล")
        nu = st.text_input("เบอร์โทรศัพท์ (ใช้เข้าสู่ระบบ)")
        np = st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            df_u = get_data("Users")
            if not df_u.empty and nu in df_u['phone'].values:
                st.error("❌ เบอร์โทรนี้ถูกใช้งานแล้ว")
            else:
                new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                st.success("✅ สมัครสมาชิกสำเร็จ!"); time.sleep(1); navigate("Login")

# 3. หน้าเข้าสู่ระบบ
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์").strip()
    p_in = st.text_input("รหัสผ่าน", type="password").strip()
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
            else:
                st.error("❌ ข้อมูลไม่ถูกต้อง")

# 4. หน้าดูคิววันนี้
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิววันนี้")
    df_v = get_data("Bookings")
    t_str = datetime.now().strftime("%Y-%m-%d")
    if not df_v.empty:
        today_qs = df_v[(df_v['date'] == t_str) & (df_v['status'] == "รอรับบริการ")].sort_values('time')
        if not today_qs.empty:
            st.write(f"🔔 วันนี้มีคิวรอรับบริการ {len(today_qs)} ท่าน")
            st.table(today_qs[['time', 'service', 'fullname']])
        else:
            st.info("วันนี้ยังไม่มีคิวจอง")
    else:
        st.info("ไม่มีข้อมูล")

# 5. หน้าจองคิว / ประวัติ / แชท
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิวของฉัน", "💬 แชทกับร้าน"])
    
    with t1:
        with st.form("b_form"):
            b_d = st.date_input("วันที่ต้องการ", min_value=datetime.now().date())
            b_t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"])
            b_s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยันการจอง"):
                df_all = get_data("Bookings")
                active = df_all[(df_all['username'] == st.session_state.username) & (df_all['status'] == "รอรับบริการ")]
                user_today = df_all[(df_all['username'] == st.session_state.username) & (df_all['date'] == str(b_d)) & (df_all['status'] == "เสร็จสิ้น")]
                slot_count = df_all[(df_all['date'] == str(b_d)) & (df_all['time'] == b_t) & (df_all['status'] == "รอรับบริการ")]

                if b_d.weekday() == 5: st.error("❌ ร้านหยุดวันเสาร์")
                elif not active.empty: st.warning("⚠️ ต้องยกเลิกคิวเดิมก่อนถึงจะจองใหม่ได้")
                elif not user_today.empty: st.warning("❌ คุณจองครบสิทธิ์วันละ 1 ครั้งแล้ว")
                elif len(slot_count) >= 2: st.error("❌ เวลานี้เต็มแล้ว (2 ท่าน) กรุณาเลือกเวลาอื่นที่ห่างไป 1 ชม.")
                else:
                    new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(b_d), "time": b_t, "service": b_s, "status": "รอรับบริการ", "price": "0"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_all, new_q], ignore_index=True))
                    st.success("✅ จองสำเร็จ!"); st.balloons(); time.sleep(1); st.rerun()

    with t2:
        df_h = get_data("Bookings")
        my_qs = df_h[df_h['username'] == st.session_state.username].iloc[::-1] if not df_h.empty else pd.DataFrame()
        for _, r in my_qs.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"📅 {r['date']} | ⏰ {r['time']} | {r['service']} \n **สถานะ: {r['status']}**")
                if r['status'] == "รอรับบริการ" and c2.button("❌ ยกเลิก", key=r['id']):
                    df_h.loc[df_h['id'] == r['id'], 'status'] = "ยกเลิกโดยลูกค้า"
                    conn.update(worksheet="Bookings", data=df_h); st.rerun()

    with t3:
        st.subheader("💬 แชทสอบถาม")
        df_c = get_data("Chats")
        chat_box = st.container(height=300)
        if not df_c.empty:
            my_m = df_c[df_c['username'] == st.session_state.username]
            for _, m in my_m.iterrows():
                cls = "user-msg" if m['sender'] == "user" else "admin-msg"
                chat_box.markdown(f'<div class="chat-msg {cls}">{m['msg']}</div>', unsafe_allow_html=True)
        with st.form("chat_f", clear_on_submit=True):
            msg = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง") and msg:
                new_m = pd.DataFrame([{"username": st.session_state.username, "sender": "user", "msg": msg, "time": datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Chats", data=pd.concat([df_c, new_m], ignore_index=True)); st.rerun()

# 6. หน้าแอดมิน
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2, at3 = st.tabs(["📊 สรุปยอด", "📅 จัดการคิว", "📩 แชทลูกค้า"])
    with at2:
        df_adm = get_data("Bookings")
        active = df_adm[df_adm['status'] == "รอรับบริการ"] if not df_adm.empty else pd.DataFrame()
        for _, r in active.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"👤 {r['fullname']} \n ⏰ {r['time']} | {r['service']}")
                pr = col2.number_input("ราคา", min_value=0, key=f"ad_p{r['id']}")
                if col2.button("✅ เสร็จสิ้น", key=f"ok{r['id']}"):
                    df_adm.loc[df_adm['id'] == r['id'], ['status', 'price']] = ["เสร็จสิ้น", str(pr)]
                    conn.update(worksheet="Bookings", data=df_adm); st.rerun()
                if col3.button("❌ ยกเลิก", key=f"no{r['id']}"):
                    df_adm.loc[df_adm['id'] == r['id'], 'status'] = "ยกเลิกโดยร้าน"
                    conn.update(worksheet="Bookings", data=df_adm); st.rerun()
    with at3:
        df_ch_adm = get_data("Chats")
        if not df_ch_adm.empty:
            for u in df_ch_adm['username'].unique():
                with st.expander(f"ข้อความจาก: {u}"):
                    for _, m in df_ch_adm[df_ch_adm['username'] == u].iterrows():
                        style = "user-msg" if m['sender'] == "user" else "admin-msg"
                        st.markdown(f'<div class="chat-msg {style}">{m['msg']}</div>', unsafe_allow_html=True)
                    with st.form(f"rep_{u}"):
                        reply = st.text_input("พิมพ์ตอบกลับ...")
                        if st.form_submit_button("ส่ง"):
                            new_r = pd.DataFrame([{"username": u, "sender": "admin", "msg": reply, "time": datetime.now().strftime("%H:%M")}])
                            conn.update(worksheet="Chats", data=pd.concat([df_ch_adm, new_r], ignore_index=True)); st.rerun()
