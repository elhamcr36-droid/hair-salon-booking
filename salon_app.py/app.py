import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time

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
        .contact-section { 
            background-color: #ffffff; 
            padding: 30px; 
            border-radius: 15px; 
            text-align: center; 
            box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
            border: 1px solid #eeeeee;
        }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        # ใช้ ttl=0 เพื่อให้ดึงข้อมูลใหม่ล่าสุดเสมอจาก Google Sheets
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

def get_new_msg_count():
    df_m = get_data("Messages")
    if not df_m.empty:
        # นับข้อความที่ admin_reply ยังว่างอยู่เพื่อทำแจ้งเตือน
        unreplied = df_m[df_m['admin_reply'] == ""]
        return len(unreplied)
    return 0

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
        if role == 'admin':
            # ระบบจุดแจ้งเตือนสีแดงสำหรับ Admin
            new_msgs = get_new_msg_count()
            lbl = f"📊 จัดการร้าน {'🔴' if new_msgs > 0 else ''}"
            if st.button(lbl): navigate("Admin")
        else:
            if st.button("✂️ จองคิว"): navigate("Booking")
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
    
    # พิกัดร้านพร้อมลิงก์ Google Maps
    map_link = "https://www.google.com/maps/search/?api=1&query=222+Tesaban+1+Alley+Songkhla"
    
    st.markdown(f"""
        <div class="contact-section">
            <h3 style="color: #FF4B4B; margin-top: 0;">📞 ติดต่อเรา</h3>
            <div style="color: #222222; font-size: 1.1em; padding: 10px 0;">
                <span style="margin: 0 15px;"><b>📱 เบอร์โทร:</b> 081-222-2222</span>
                <span style="margin: 0 15px;"><b>💬 LINE ID:</b> @222salon</span>
                <span style="margin: 0 15px;"><b>🔵 Facebook:</b> 222 Salon</span>
            </div>
            <div style="margin-top: 20px;">
                <a href="{map_link}" target="_blank" style="background-color: #FF4B4B; color: white; padding: 12px 30px; border-radius: 10px; text-decoration: none; font-weight: bold; box-shadow: 0px 4px 10px rgba(255, 75, 75, 0.3);">
                    📍 พิกัด: 222 ถนน เทศบาล 1 (คลิกเพื่อดูแผนที่ Google Maps)
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิววันนี้ (Real-time)")
    # ระบบ Auto-Refresh ทุก 30 วินาทีเพื่อให้ข้อมูลเป็นปัจจุบัน
    placeholder = st.empty()
    df_today = get_data("Bookings")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    with placeholder.container():
        if not df_today.empty:
            active = df_today[(df_today['date'] == today_str) & (df_today['status'] == "รอรับบริการ")]
            if not active.empty:
                st.write(f"🔔 มีคิวรอรับบริการทั้งหมด {len(active)} คิว")
                st.table(active[['time', 'service', 'fullname']].sort_values('time'))
            else:
                st.info(f"✨ ยังไม่มีการจองในวันนี้ ({today_str})")
        else:
            st.info("📅 ยังไม่มีข้อมูลการจอง")
    
    time.sleep(30)
    st.rerun()

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg_form"):
        nf = st.text_input("ชื่อ-นามสกุล")
        nu = st.text_input("เบอร์โทรศัพท์")
        np = st.text_input("รหัสผ่าน", type="password")
        npc = st.text_input("ยืนยันรหัสผ่าน", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            if nu and np == npc and nf:
                df_u = get_data("Users")
                if not df_u.empty and nu in df_u['phone'].values:
                    st.error("❌ เบอร์นี้ถูกใช้งานแล้ว")
                else:
                    new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                    st.success("✅ สำเร็จ!"); navigate("Login")
            else:
                st.error("❌ ข้อมูลไม่ถูกต้อง")

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

elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิวของฉัน", "💬 แชทกับร้าน"])
    with t1:
        with st.form("b_form"):
            b_d = st.date_input("เลือกวันที่", min_value=datetime.now().date())
            b_t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            b_s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยัน"):
                if b_d.weekday() == 5: st.error("❌ ร้านหยุดวันเสาร์")
                else:
                    df_all = get_data("Bookings")
                    new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(b_d), "time": b_t, "service": b_s, "status": "รอรับบริการ", "price": "0"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_all, new_q], ignore_index=True))
                    st.success("✅ จองสำเร็จ!"); st.balloons()
    with t2:
        df_history = get_data("Bookings")
        if not df_history.empty:
            my_qs = df_history[df_history['username'] == st.session_state.username]
            for _, r in my_qs.iterrows():
                with st.container(border=True):
                    st.write(f"📅 {r['date']} | ⏰ {r['time']} | {r['service']} | **{r['status']}**")
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

elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2, at3 = st.tabs(["📊 สรุปยอด", "📅 จัดการคิว", "📩 แชทลูกค้า"])
    with at1:
        df_b = get_data("Bookings")
        if not df_b.empty:
            df_b['price'] = pd.to_numeric(df_b['price'], errors='coerce').fillna(0)
            st.metric("รายได้รวม", f"{df_b[df_b['status']=='เสร็จสิ้น']['price'].sum():,.0f} บ.")
    with at2:
        df_admin = get_data("Bookings")
        if not df_admin.empty:
            active_qs = df_admin[df_admin['status'] == "รอรับบริการ"]
            for _, row in active_qs.iterrows():
                with st.container(border=True):
                    st.write(f"👤 {row['fullname']} | 📅 {row['date']} | {row['time']}")
                    if st.button("✅ เสร็จสิ้น", key=f"s_{row['id']}"):
                        df_admin.loc[df_admin['id']==row['id'], 'status'] = "เสร็จสิ้น"
                        conn.update(worksheet="Bookings", data=df_admin); st.rerun()
    with at3:
        df_msg_admin = get_data("Messages")
        # แจ้งเตือนข้อความใหม่ใน Tab แชท
        new_count = len(df_msg_admin[df_msg_admin['admin_reply'] == ""])
        if new_count > 0:
            st.error(f"🔔 คุณมี {new_count} ข้อความที่ยังไม่ได้ตอบ!")
            
        df_users_info = get_data("Users")
        if not df_msg_admin.empty:
            user_map = dict(zip(df_users_info['phone'], df_users_info['fullname']))
            unique_usernames = df_msg_admin['username'].unique()
            sel_u = st.selectbox("เลือกแชทลูกค้า", options=unique_usernames, 
                                 format_func=lambda x: f"{'🔴 ' if df_msg_admin[(df_msg_admin['username']==x) & (df_msg_admin['admin_reply']=='')].shape[0] > 0 else ''}👤 {user_map.get(x, x)}")
            
            user_msgs = df_msg_admin[df_msg_admin['username'] == sel_u]
            for idx, m in user_msgs.iterrows():
                with st.chat_message("user"):
                    st.write(m['message'])
                    if not m['admin_reply']:
                        with st.form(key=f"rep_{idx}", clear_on_submit=True):
                            ans = st.text_input("ตอบกลับ...")
                            if st.form_submit_button("ส่ง"):
                                df_msg_admin.at[idx, 'admin_reply'] = ans
                                conn.update(worksheet="Messages", data=df_msg_admin); st.rerun()
                if m['admin_reply']:
                    st.chat_message("assistant").info(m['admin_reply']) 
