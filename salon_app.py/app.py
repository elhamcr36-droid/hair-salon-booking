import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import streamlit.components.v1 as components

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
        .price-text { float: right; color: #FF4B4B; font-weight: bold; }
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
        if st.button("📝 สมัครสมาชิก"): navigate("Register")
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
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")
    
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"}
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span class="price-text">{price}</span></div>', unsafe_allow_html=True)

    st.divider()
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("📞 ติดต่อเรา")
        st.write("📱 **เบอร์โทร:** 081-222-2222")
        st.write("💬 **LINE ID:** @222salon")
        st.write("🔵 **Facebook:** 222 Salon")
   with c2:
        st.subheader("📍 พิกัดร้าน")
        # ลิงก์ที่แปลงเป็นรูปแบบ Embed สำหรับ 222 ถนน เทศบาล 1
        map_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3875.52354504543!2d100.523186!3d13.75!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x30e29930f3c5f95f%3A0x63345472856f4d2a!2zMjIyIOC4luC4meC4meC5gOC4l-C4qOC4muC4suC4pSAx!5e0!3m2!1sth!2sth!4v1710170000000!5m2!1sth!2sth"
        
        components.html(
            f'<iframe src="{map_url}" width="100%" height="230" style="border:0; border-radius:15px;" allowfullscreen="" loading="lazy"></iframe>', 
            height=240
        )

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
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': u_in, 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)] if not df_u.empty else pd.DataFrame()
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิวของฉัน", "💬 แชทกับร้าน"])
    with t1:
        with st.form("b_form"):
            b_d = st.date_input("เลือกวันที่", min_value=datetime.now().date())
            b_t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            b_s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยัน"):
                if b_d.weekday() == 5: 
                    st.error("❌ ร้านหยุดวันเสาร์ กรุณาเลือกวันอื่นครับ")
                else:
                    df_all = get_data("Bookings")
                    is_time_taken = df_all[(df_all['date'] == str(b_d)) & (df_all['time'] == b_t) & (df_all['status'] != 'ยกเลิก')] if not df_all.empty else pd.DataFrame()
                    is_user_booked = df_all[(df_all['date'] == str(b_d)) & (df_all['username'] == st.session_state.username) & (df_all['status'] == 'รอรับบริการ')] if not df_all.empty else pd.DataFrame()

                    if not is_time_taken.empty:
                        st.error(f"❌ เวลา {b_t} ของวันที่ {b_d} มีผู้จองแล้วครับ")
                    elif not is_user_booked.empty:
                        st.warning(f"⚠️ คุณมีคิวที่รอรับบริการในวันที่ {b_d} อยู่แล้วครับ")
                    else:
                        new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(b_d), "time": b_t, "service": b_s, "status": "รอรับบริการ", "price": "0"}])
                        conn.update(worksheet="Bookings", data=pd.concat([df_all, new_q], ignore_index=True))
                        st.success("✅ จองสำเร็จ!")
                        st.balloons()
    with t2:
        st.subheader("📋 ประวัติการจองของคุณ")
        df_history = get_data("Bookings")
        if not df_history.empty:
            my_qs = df_history[df_history['username'] == st.session_state.username]
            if my_qs.empty: st.info("ยังไม่มีประวัติการจอง")
            else:
                for _, r in my_qs.iterrows():
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        c1.write(f"📅 {r['date']} | ⏰ {r['time']} | {r['service']} \nสถานะ: **{r['status']}**")
                        if r['status'] == "รอรับบริการ" and c2.button("🗑️ ยกเลิก", key=f"del_u_{r['id']}"):
                            df_updated = df_history[df_history['id'] != r['id']]
                            conn.update(worksheet="Bookings", data=df_updated); st.rerun()
    with t3:
        df_m = get_data("Messages")
        chat_c = st.container(height=300)
        if not df_m.empty:
            user_chat = df_m[df_m['username'] == st.session_state.username]
            for _, m in user_chat.iterrows():
                chat_c.chat_message("user").write(m['message'])
                if m['admin_reply']: chat_c.chat_message("assistant").info(m['admin_reply'])
        with st.form("send_m", clear_on_submit=True):
            msg = st.text_input("พิมพ์ข้อความถึงร้าน...")
            if st.form_submit_button("ส่ง") and msg:
                new_m = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "message": msg, "timestamp": datetime.now().strftime("%H:%M"), "admin_reply": ""}])
                conn.update(worksheet="Messages", data=pd.concat([df_m, new_m], ignore_index=True))
                st.rerun()

elif st.session_state.page == "Admin" and st.session_state.logged_in and st.session_state.user_role == 'admin':
    at1, at2, at3 = st.tabs(["📊 สรุปยอด", "📅 จัดการคิว", "📩 แชทลูกค้า"])
    with at1:
        df_b = get_data("Bookings")
        if not df_b.empty:
            df_b['price'] = pd.to_numeric(df_b['price'], errors='coerce').fillna(0)
            st.metric("รายได้รวมทั้งหมด", f"{df_b[df_b['status']=='เสร็จสิ้น']['price'].sum():,.0f} บ.")
            st.dataframe(df_b[df_b['status']=='เสร็จสิ้น'][['date', 'fullname', 'service', 'price']])
    with at2:
        st.subheader("📅 รายการคิวลูกค้าทั้งหมด")
        df_admin = get_data("Bookings")
        if not df_admin.empty:
            active_qs = df_admin[df_admin['status'] == "รอรับบริการ"]
            if active_qs.empty: st.info("ไม่มีคิวรอรับบริการ")
            else:
                for _, row in active_qs.iterrows():
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        col1.write(f"👤 **{row['fullname']}** ({row['username']}) \n📅 {row['date']} | ⏰ {row['time']} | ✂️ {row['service']}")
                        b_col1, b_col2 = col2.columns(2)
                        with b_col1.popover("✅"):
                            p = st.number_input("ราคา", key=f"p_{row['id']}", min_value=0, step=50)
                            if st.button("ตกลง", key=f"s_{row['id']}"):
                                df_admin.loc[df_admin['id']==row['id'], ['status', 'price']] = ["เสร็จสิ้น", str(p)]
                                conn.update(worksheet="Bookings", data=df_admin); st.rerun()
                        if b_col2.button("🗑️", key=f"d_{row['id']}"):
                            df_admin = df_admin[df_admin['id'] != row['id']]
                            conn.update(worksheet="Bookings", data=df_admin); st.rerun()
    with at3:
        # --- ส่วนที่แก้ไข: แสดงชื่อลูกค้าในหน้าแชทแอดมิน ---
        df_msg_admin = get_data("Messages")
        df_users_info = get_data("Users") 

        if not df_msg_admin.empty and not df_users_info.empty:
            # สร้างแมพ เบอร์โทร -> ชื่อ
            user_map = dict(zip(df_users_info['phone'], df_users_info['fullname']))
            unique_usernames = df_msg_admin['username'].unique()
            
            # ฟังก์ชันช่วยจัดรูปแบบการแสดงผลใน Dropdown
            def format_user_label(phone):
                name = user_map.get(phone, "ไม่พบชื่อในระบบ")
                return f"👤 {name} ({phone})"

            sel_u = st.selectbox("เลือกแชทลูกค้า", options=unique_usernames, format_func=format_user_label)
            
            st.markdown(f"### 💬 แชทกับคุณ {user_map.get(sel_u, 'ไม่ทราบชื่อ')}")
            user_msgs = df_msg_admin[df_msg_admin['username'] == sel_u]
            
            for idx, m in user_msgs.iterrows():
                with st.chat_message("user"):
                    st.write(m['message'])
                    st.caption(f"ส่งเมื่อ: {m.get('timestamp', '')}")
                
                if m['admin_reply']: 
                    with st.chat_message("assistant"):
                        st.info(m['admin_reply'])
                
                with st.expander("ตอบกลับข้อความนี้"):
                    with st.form(key=f"rep_{idx}", clear_on_submit=True):
                        ans = st.text_input("พิมพ์ข้อความตอบกลับ...")
                        if st.form_submit_button("ส่งคำตอบ"):
                            df_msg_admin.at[idx, 'admin_reply'] = ans
                            conn.update(worksheet="Messages", data=df_msg_admin)
                            st.success("ส่งคำตอบแล้ว!")
                            st.rerun()

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิววันนี้")
    df_today = get_data("Bookings")
    today_str = datetime.now().strftime("%Y-%m-%d")
    if not df_today.empty:
        active = df_today[(df_today['date'] == today_str) & (df_today['status'] == "รอรับบริการ")]
        if not active.empty:
            st.table(active[['time', 'service', 'fullname']].sort_values('time'))
        else: st.info(f"ไม่มีการจองในวันนี้ ({today_str})")









