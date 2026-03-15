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
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    # ล้าง Cache ทุกครั้งเพื่อให้ได้ข้อมูลที่อัปเดตจาก Google Sheets จริงๆ
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

if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")

elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิก")
    with st.form("reg_form"):
        nf = st.text_input("ชื่อ-นามสกุล")
        nu = st.text_input("เบอร์โทรศัพท์")
        np = st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            df_u = get_data("Users")
            if not df_u.empty and nu in df_u['phone'].values:
                st.error("❌ เบอร์นี้ถูกใช้งานแล้ว")
            else:
                new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
                conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                st.success("✅ สำเร็จ!"); navigate("Login")

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
            b_t = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"])
            b_s = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            
            if st.form_submit_button("ยืนยันการจอง"):
                if b_d.weekday() == 5: 
                    st.error("❌ ร้านหยุดทุกวันเสาร์")
                else:
                    df_all = get_data("Bookings")
                    
                    # 1. เงื่อนไข: ต้องยกเลิกคิวเดิมที่มีสถานะ "รอรับบริการ" ก่อน
                    active_queue = df_all[(df_all['username'] == st.session_state.username) & 
                                         (df_all['status'] == "รอรับบริการ")]
                    
                    # 2. เงื่อนไข: ลูกค้าจองได้วันละ 1 ครั้ง (เฉพาะที่ทำเสร็จแล้วหรือรอรับบริการในวันนั้น)
                    user_today = df_all[(df_all['username'] == st.session_state.username) & 
                                        (df_all['date'] == str(b_d)) & 
                                        (df_all['status'].isin(["เสร็จสิ้น", "รอรับบริการ"]))]
                    
                    # 3. เงื่อนไข: จำกัด 2 คนต่อรอบเวลา
                    time_slot_count = df_all[(df_all['date'] == str(b_d)) & 
                                             (df_all['time'] == b_t) & 
                                             (df_all['status'] == "รอรับบริการ")]

                    if not active_queue.empty:
                        st.warning("⚠️ คุณยังมีคิวค้างอยู่ กรุณายกเลิกคิวเดิมก่อนถึงจะจองใหม่ได้ครับ")
                    elif not user_today.empty:
                        st.warning(f"❌ คุณได้ใช้สิทธิ์จองของวันที่ {b_d} ไปแล้ว (จำกัด 1 ครั้ง/วัน)")
                    elif len(time_slot_count) >= 2:
                        st.error(f"❌ เวลา {b_t} เต็มแล้ว (รับได้ 2 ท่าน) กรุณาเลือกเวลาอื่นที่ห่างจากคิวเดิม 1 ชม.")
                    else:
                        new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(b_d), "time": b_t, "service": b_s, "status": "รอรับบริการ", "price": "0"}])
                        conn.update(worksheet="Bookings", data=pd.concat([df_all, new_q], ignore_index=True))
                        st.success("✅ จองสำเร็จ!"); st.balloons()
                        time.sleep(1); st.rerun()
    
    with t2:
        df_history = get_data("Bookings")
        if not df_history.empty:
            my_qs = df_history[df_history['username'] == st.session_state.username]
            for _, r in my_qs.iloc[::-1].iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(f"📅 {r['date']} | ⏰ {r['time']} | {r['service']}")
                        st.markdown(f"**สถานะ: {r['status']}**")
                    with c2:
                        # ปุ่มยกเลิกเพื่อให้จองคิวใหม่ได้ตามเงื่อนไข
                        if r['status'] == "รอรับบริการ":
                            if st.button("❌ ยกเลิก", key=f"u_can_{r['id']}"):
                                df_history.loc[df_history['id'] == r['id'], 'status'] = "ยกเลิกโดยลูกค้า"
                                conn.update(worksheet="Bookings", data=df_history)
                                st.rerun()

elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2, at3 = st.tabs(["📊 สรุปยอด", "📅 จัดการคิว", "📩 แชทลูกค้า"])
    with at2:
        df_admin = get_data("Bookings")
        active_qs = df_admin[df_admin['status'] == "รอรับบริการ"].copy()
        if active_qs.empty:
            st.info("ไม่มีคิวรอรับบริการ")
        else:
            for _, row in active_qs.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    with c1:
                        st.write(f"👤 **{row['fullname']}**")
                        st.write(f"📅 {row['date']} | ⏰ {row['time']} | {row['service']}")
                    with c2:
                        p_input = st.number_input(f"ราคา", min_value=0, step=50, key=f"p_{row['id']}")
                        if st.button("✅ เสร็จสิ้น", key=f"d_{row['id']}", type="primary"):
                            df_admin.loc[df_admin['id'] == row['id'], ['status', 'price']] = ["เสร็จสิ้น", str(p_input)]
                            conn.update(worksheet="Bookings", data=df_admin)
                            st.rerun()
                    with c3:
                        if st.button("❌ ยกเลิก", key=f"a_can_{row['id']}"):
                            df_admin.loc[df_admin['id'] == row['id'], 'status'] = "ยกเลิกโดยร้าน"
                            conn.update(worksheet="Bookings", data=df_admin)
                            st.rerun()
