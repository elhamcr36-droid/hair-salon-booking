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
        .price-card {
            background-color: #ffffff !important; padding: 18px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 12px;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.08); color: #000000 !important;
        }
        .summary-card {
            background-color: #f0f2f6; padding: 20px; border-radius: 15px; text-align: center;
            border: 1px solid #ddd; margin-bottom: 10px; color: #000;
        }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. DATA ENGINE ---
def get_data(sheet_name):
    st.cache_data.clear() 
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df is None or df.empty: return pd.DataFrame()
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        for col in df.columns:
            # แก้ปัญหา Data Type และล้างช่องว่าง
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
            # บังคับรูปแบบเบอร์โทรให้มี 0 นำหน้า
            if 'phone' in col or 'username' in col:
                df[col] = df[col].apply(lambda x: '0' + x if len(x) == 9 and x.isdigit() else x)
        return df
    except:
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

# 1. หน้าแรก (Home)
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
    address = "222 ถนนเทศบาล 1 ตำบลบ่อยาง อำเภอเมืองสงขลา สงขลา 90000"
    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border: 1px solid #eee; text-align: center; color: #000; box-shadow: 0px 4px 10px rgba(0,0,0,0.05);">
            <h3 style="color: #FF4B4B; margin-bottom: 15px;">📞 ติดต่อเรา & พิกัดร้าน</h3>
            <p style="font-size: 1.1em;">🔵 <b>Facebook:</b> <a href="https://www.facebook.com/222Salon" target="_blank" style="color: #1877F2; text-decoration: none; font-weight: bold;">222Salon Songkhla</a></p>
            <p style="font-size: 1.1em;">📱 <b>เบอร์โทรศัพท์:</b> 081-222-2222</p>
            <p style="font-size: 1.1em;">💬 <b>LINE ID:</b> @222salon</p>
            <hr style="margin: 15px 0; border: 0.5px solid #eee;">
            <p style="font-size: 1em; color: #555;">📍 <b>ที่อยู่:</b> {address}</p>
            <a href="https://www.google.com/maps/search/?api=1&query={address.replace(' ', '+')}" target="_blank">
                <button style="background-color: #4285F4; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; width: auto;">
                    🗺️ เปิดใน Google Maps
                </button>
            </a>
        </div>
    """, unsafe_allow_html=True)

# 2. หน้าสมัครสมาชิก (Register)
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg"):
        nf = st.text_input("ชื่อ-นามสกุล")
        nu = st.text_input("เบอร์โทรศัพท์")
        np = st.text_input("กำหนดรหัสผ่าน", type="password")
        npc = st.text_input("ยืนยันรหัสผ่านอีกครั้ง", type="password")
        
        if st.form_submit_button("ลงทะเบียน"):
            if not nf or not nu or not np or not npc:
                st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วน")
            elif np != npc:
                st.error("❌ รหัสผ่านไม่ตรงกัน")
            else:
                df_u = get_data("Users")
                u_clean = nu.strip()
                if not df_u.empty and u_clean in df_u['phone'].values:
                    st.error("❌ เบอร์โทรศัพท์นี้ถูกใช้งานแล้ว")
                else:
                    new_u = pd.DataFrame([{"phone": u_clean, "password": np.strip(), "fullname": nf.strip(), "role": "user"}])
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                    st.success("✅ ลงทะเบียนสำเร็จ!"); time.sleep(1.5); navigate("Login")

# 3. หน้าเข้าสู่ระบบ (Login)
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์")
    p_in = st.text_input("รหัสผ่าน", type="password")
    if st.button("ตกลง", type="primary"):
        u_clean = u_in.strip()
        p_clean = p_in.strip()
        if u_clean == "admin222" and p_clean == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': u_clean, 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_clean) & (df_u['password'] == p_clean)] if not df_u.empty else pd.DataFrame()
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': user.iloc[0]['role'], 'username': u_clean, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking" if user.iloc[0]['role'] == 'user' else "Admin")
            else: st.error("❌ เบอร์โทรศัพท์หรือรหัสผ่านไม่ถูกต้อง")

# 4. หน้าจองคิวลูกค้า (Booking)
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2 = st.tabs(["🆕 จองคิว", "📋 ประวัติ"])
    df_b = get_data("Bookings")
    active_booking = df_b[(df_b['username'] == st.session_state.username) & (df_b['status'] == "รอรับบริการ")]

    with t1:
        if not active_booking.empty:
            st.warning("⚠️ คุณมีคิวที่รอรับบริการอยู่แล้ว")
            st.info("กรุณายกเลิกคิวเดิมในหน้า '📋 ประวัติ' ก่อนจองใหม่")
        else:
            with st.form("b"):
                bd = st.date_input("วันที่", min_value=datetime.now().date())
                all_times = ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"]
                booked_counts = df_b[(df_b['date'] == str(bd)) & (df_b['status'] == "รอรับบริการ")]['time'].value_counts()
                full_slots = booked_counts[booked_counts >= 2].index.tolist()
                available_times = [t for t in all_times if t not in full_slots]
                
                bt = st.selectbox("เลือกเวลา (จำกัด 2 ท่านต่อช่วงเวลา)", available_times)
                bs = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
                if st.form_submit_button("ยืนยันการจอง"):
                    if bd.weekday() == 5: st.error("❌ ร้านปิดบริการวันเสาร์")
                    elif not bt: st.error("❌ เวลานี้เต็มแล้ว กรุณาเลือกวันหรือเวลาอื่น")
                    else:
                        new_q = pd.DataFrame([{"id": str(uuid.uuid4())[:8], "username": st.session_state.username, "fullname": st.session_state.fullname, "date": str(bd), "time": bt, "service": bs, "status": "รอรับบริการ", "price": "0"}])
                        conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                        st.success("✅ จองสำเร็จ!"); time.sleep(1); st.rerun()

    with t2:
        my_qs = df_b[df_b['username'] == st.session_state.username].iloc[::-1]
        if my_qs.empty: st.info("ยังไม่มีประวัติการจอง")
        else:
            for _, r in my_qs.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"📅 {r['date']} | ⏰ {r['time']} | {r['service']}")
                    if r['status'] == "รอรับบริการ":
                        if c2.button("ยกเลิกคิว", key=f"can_{r['id']}"):
                            df_b.loc[df_b['id'] == r['id'], 'status'] = "ยกเลิกโดยลูกค้า"
                            conn.update(worksheet="Bookings", data=df_b)
                            st.success("ยกเลิกสำเร็จ!"); time.sleep(1); st.rerun()
                    else: c1.write(f"สถานะ: `{r['status']}`")

# 5. หน้าแอดมิน (Admin)
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    at1, at2 = st.tabs(["📊 สรุปยอด", "📅 จัดการคิว"])
    with at1:
        df_all = get_data("Bookings")
        if not df_all.empty:
            done = df_all[df_all['status'] == "เสร็จสิ้น"].copy()
            done['price'] = pd.to_numeric(done['price'], errors='coerce').fillna(0)
            st.metric("รายได้รวม", f"{done['price'].sum():,.0f} บ.")
            st.dataframe(done[['date', 'fullname', 'service', 'price']], use_container_width=True)
    with at2:
        df_adm = get_data("Bookings")
        active = df_adm[df_adm['status'] == "รอรับบริการ"] if not df_adm.empty else pd.DataFrame()
        if active.empty: st.info("ไม่มีคิวรอรับบริการ")
        else:
            for _, r in active.iterrows():
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    col1.write(f"👤 {r['fullname']} | ⏰ {r['time']} | {r['service']}")
                    pr = col2.number_input("ใส่ราคา", min_value=0, key=f"p{r['id']}")
                    if col2.button("✅ เสร็จสิ้น", key=f"ok{r['id']}"):
                        df_adm.loc[df_adm['id'] == r['id'], ['status', 'price']] = ["เสร็จสิ้น", str(pr)]
                        conn.update(worksheet="Bookings", data=df_adm); st.rerun()
                    if col3.button("❌ ยกเลิก", key=f"no{r['id']}"):
                        df_adm.loc[df_adm['id'] == r['id'], 'status'] = "ยกเลิกโดยร้าน"
                        conn.update(worksheet="Bookings", data=df_adm); st.rerun()

# 6. หน้าดูคิววันนี้ (บุคคลทั่วไป)
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิววันนี้")
    df_q = get_data("Bookings")
    today = datetime.now().strftime("%Y-%m-%d")
    if not df_q.empty:
        qs = df_q[(df_q['date'] == today) & (df_q['status'] == "รอรับบริการ")].sort_values('time')
        if not qs.empty: st.table(qs[['time', 'service', 'fullname']])
        else: st.info("ไม่มีคิวจองในวันนี้")
