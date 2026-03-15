import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon Songkhla", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; height: 3.2em; transition: 0.3s;}
        
        /* Card ราคาและสรุปยอด */
        .price-card {
            background-color: #ffffff !important; padding: 18px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 12px;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.08); color: #000000 !important;
        }
        .summary-card {
            background-color: #f0f2f6; padding: 20px; border-radius: 15px; text-align: center;
            border: 1px solid #ddd; margin-bottom: 10px;
        }
        
        /* Chat สไตล์ Messenger */
        [data-testid="stChatMessage"][data-testid^="stChatMessageUser"] {
            flex-direction: row-reverse !important; background-color: #0084FF !important;
            color: white !important; border-radius: 15px 15px 2px 15px !important;
            margin-left: auto !important; width: fit-content !important; max-width: 85% !important;
        }
        [data-testid="stChatMessage"][data-testid^="stChatMessageAssistant"] {
            background-color: #E4E6EB !important; color: black !important;
            border-radius: 15px 15px 15px 2px !important;
            margin-right: auto !important; width: fit-content !important; max-width: 85% !important;
        }
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

# 1. หน้าแรก
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")
    st.subheader("📋 บริการและราคา")
    # ... (แสดงราคาตามโค้ดเดิม)
    st.markdown("""
        <div style="background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #eee; text-align: center;">
            <h3>📞 ติดต่อเรา</h3>
            <p>🔵 <b>Facebook:</b> <a href="https://www.facebook.com/222Salon" target="_blank">222Salon</a></p>
            <p>📱 <b>เบอร์โทร:</b> 081-222-2222 | 💬 <b>LINE:</b> @222salon</p>
        </div>
    """, unsafe_allow_html=True)

# 2. หน้าสมัครสมาชิก
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg"):
        nf = st.text_input("ชื่อ-นามสกุล")
        nu = st.text_input("เบอร์โทรศัพท์")
        np = st.text_input("รหัสผ่าน", type="password")
        npc = st.text_input("ยืนยันรหัสผ่าน", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            if np != npc: st.error("❌ รหัสผ่านไม่ตรงกัน")
            else:
                df_u = get_data("Users")
                new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                st.success("✅ สำเร็จ!"); time.sleep(1); navigate("Login")

# 3. หน้าเข้าสู่ระบบ
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
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

# 4. หน้าแอดมิน (จัดการคิว & สรุปยอด)
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2, at3 = st.tabs(["📊 สรุปยอด", "📅 จัดการคิว", "📩 แชทลูกค้า"])
    
    with at1:
        st.subheader("📈 สรุปยอดรายได้")
        df_all = get_data("Bookings")
        if not df_all.empty:
            # กรองเฉพาะที่เสร็จสิ้น
            done_qs = df_all[df_all['status'] == "เสร็จสิ้น"].copy()
            done_qs['price'] = pd.to_numeric(done_qs['price'], errors='coerce').fillna(0)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="summary-card"><h3>💰 รายได้รวม</h3><h2>{done_qs["price"].sum():,.0f} บ.</h2></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="summary-card"><h3>👥 ลูกค้าทั้งหมด</h3><h2>{len(done_qs)} ท่าน</h2></div>', unsafe_allow_html=True)
            with c3:
                today_sum = done_qs[done_qs['date'] == datetime.now().strftime("%Y-%m-%d")]['price'].sum()
                st.markdown(f'<div class="summary-card"><h3>📅 ยอดวันนี้</h3><h2>{today_sum:,.0f} บ.</h2></div>', unsafe_allow_html=True)
            
            st.divider()
            st.write("📊 **แยกตามประเภทบริการ:**")
            st.dataframe(done_qs.groupby('service')['price'].agg(['count', 'sum']).rename(columns={'count':'จำนวนคิว','sum':'ยอดรวม'}), use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลรายได้")

    with at2:
        st.subheader("📅 คิวที่รอรับบริการ")
        df_adm = get_data("Bookings")
        # แสดงเฉพาะคิวที่ยังไม่เสร็จและไม่ถูกยกเลิก
        active = df_adm[df_adm['status'] == "รอรับบริการ"] if not df_adm.empty else pd.DataFrame()
        
        if active.empty:
            st.info("ไม่มีคิวค้างในขณะนี้")
        else:
            for _, r in active.iterrows():
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    col1.write(f"👤 **{r['fullname']}** | ⏰ {r['time']} \n {r['service']} ({r['date']})")
                    # ช่องกรอกราคา
                    pr = col2.number_input("ค่าบริการ (บาท)", min_value=0, step=10, key=f"p{r['id']}")
                    
                    # ปุ่มยืนยัน (กดแล้วสถานะเปลี่ยน ข้อมูลหายจากหน้านี้ ไปโผล่หน้าสรุปยอด)
                    if col2.button("✅ เสร็จสิ้น", key=f"ok{r['id']}", use_container_width=True):
                        df_adm.loc[df_adm['id'] == r['id'], ['status', 'price']] = ["เสร็จสิ้น", str(pr)]
                        conn.update(worksheet="Bookings", data=df_adm)
                        st.success(f"บันทึกยอด {pr} บาท เรียบร้อย!")
                        time.sleep(0.5)
                        st.rerun()
                        
                    if col3.button("❌ ยกเลิก", key=f"no{r['id']}", use_container_width=True):
                        df_adm.loc[df_adm['id'] == r['id'], 'status'] = "ยกเลิกโดยร้าน"
                        conn.update(worksheet="Bookings", data=df_adm)
                        st.rerun()
                        
    with at3:
        # ... (ส่วนแชทแอดมินตามโค้ดก่อนหน้า)
        st.subheader("📩 แชทสอบถาม")
        df_ch = get_data("Chats")
        df_u = get_data("Users")
        name_map = dict(zip(df_u['phone'], df_u['fullname']))
        if not df_ch.empty:
            for u in df_ch['username'].unique():
                with st.expander(f"👤 แชทจาก: {name_map.get(u, u)}"):
                    for _, m in df_ch[df_ch['username'] == u].iterrows():
                        with st.chat_message("assistant" if m['sender']=="user" else "user"): st.write(m['msg'])
                    with st.form(f"f{u}", clear_on_submit=True):
                        rep = st.text_input("ตอบกลับ...")
                        if st.form_submit_button("ส่ง"):
                            new_r = pd.DataFrame([{"username": u, "sender": "admin", "msg": rep, "time": datetime.now().strftime("%H:%M")}])
                            conn.update(worksheet="Chats", data=pd.concat([df_ch, new_r], ignore_index=True))
                            st.rerun()

# 5. หน้าจองคิว (ลูกค้า)
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    # ... (ส่วนจองคิวลูกค้าตามโค้ดก่อนหน้า)
    st.subheader("✂️ จองคิวบริการ")
    t_booking, t_history, t_chat = st.tabs(["🆕 จองใหม่", "📋 ประวัติ", "💬 แชท"])
    # (เพิ่ม Logic จองคิวที่นี่)
    with t_chat:
        # ส่วนแชทลูกค้า (Messenger Style)
        df_c = get_data("Chats")
        chat_box = st.container(height=300)
        with chat_box:
            if not df_c.empty:
                for _, m in df_c[df_c['username'] == st.session_state.username].iterrows():
                    with st.chat_message("user" if m['sender']=="user" else "assistant"): st.write(m['msg'])
        if prompt := st.chat_input("พิมพ์ข้อความ..."):
            new_m = pd.DataFrame([{"username": st.session_state.username, "sender": "user", "msg": prompt, "time": datetime.now().strftime("%H:%M")}])
            conn.update(worksheet="Chats", data=pd.concat([df_c, new_m], ignore_index=True))
            st.rerun()
