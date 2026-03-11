import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

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
        .price-card b { color: #000000 !important; display: block; font-size: 1.1rem;}
        .price-text { color: #FF4B4B !important; font-weight: bold;}
        .summary-box {
            text-align: center; background: #FF4B4B; color: white; padding: 15px;
            border-radius: 10px; margin-bottom: 20px; box-shadow: 2px 4px 8px rgba(0,0,0,0.1);
        }
        .contact-box {
            text-align: center; background-color: #ffffff !important; padding: 20px; 
            border-radius: 15px; box-shadow: 2px 4px 10px rgba(0,0,0,0.1); color: #000000 !important;
            border: 1px solid #eee; height: 100%;
        }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- ฟังก์ชันดึงข้อมูล (ใช้ Cache 60 วินาที เพื่อป้องกัน Error 429) ---
@st.cache_data(ttl=60)
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name)
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
            if 'phone' in col or 'username' in col:
                df[col] = df[col].apply(lambda x: '0' + x if len(x) == 9 and x.isdigit() else x)
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูล {sheet_name} ได้: {e}")
        return pd.DataFrame()

# --- 2. NAVIGATION & SESSION ---
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
        if st.button("📝 สมัคร"): navigate("Register")
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
            st.cache_data.clear() # ล้าง Cache เมื่อ Logout
            navigate("Home")

st.divider()

# --- 3. PAGE LOGIC ---

# --- หน้าแรก (Home) ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (หยุดทุกวันพุธ)")
    
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"}
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span class="price-text">{price}</span></div>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📞 ติดต่อเรา & แผนที่")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='contact-box'><h3>📞 โทร</h3><p>081-222-2222</p></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='contact-box'><h3>💬 Line</h3><p>@222salon</p></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='contact-box'><h3>📍 ที่ตั้ง</h3><p>222 ซอย.พิรม สงขลา.</p></div>", unsafe_allow_html=True)
    
    st.link_button("📍 นำทางด้วย Google Maps (GPS)", "https://www.google.com/maps/search/?api=1&query=Songkhla", type="primary", use_container_width=True)

# --- สมัครสมาชิก ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg_form"):
        nu, nf = st.text_input("เบอร์โทรศัพท์ (สิบลัก)").strip(), st.text_input("ชื่อ-นามสกุล").strip()
        np, npc = st.text_input("รหัสผ่าน", type="password"), st.text_input("ยืนยันรหัส", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            if np != npc: st.error("❌ รหัสผ่านไม่ตรงกัน")
            elif not nu or not nf or not np: st.error("⚠️ กรุณากรอกข้อมูลให้ครบ")
            else:
                df_u = get_data("Users")
                if not df_u.empty and nu in df_u['phone'].values: st.error("⚠️ เบอร์นี้เคยลงทะเบียนแล้ว")
                else:
                    new_u = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}]).astype(str)
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True))
                    st.cache_data.clear()
                    st.success("✅ ลงทะเบียนสำเร็จ!"); time.sleep(1); navigate("Login")

# --- เข้าสู่ระบบ ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์").strip()
    p_in = st.text_input("รหัสผ่าน", type="password").strip()
    if st.button("ตกลง", type="primary"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'admin', 'fullname': 'แอดมิน'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)]
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else: st.error("❌ เบอร์โทรหรือรหัสผ่านไม่ถูกต้อง")

# --- หน้าจองคิว (พร้อมระบบกันจองซ้ำ) ---
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิวของคุณ"])
    with t1:
        with st.form("booking_form"):
            b_date = st.date_input("วันที่", min_value=datetime.now().date())
            b_time = st.selectbox("เวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            b_service = st.selectbox("บริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            if st.form_submit_button("ยืนยันการจอง"):
                df_b = get_data("Bookings")
                d_str = str(b_date)
                
                # เช็คการจองซ้ำ
                dup = df_b[(df_b['username'] == st.session_state.username) & (df_b['date'] == d_str) & (df_b['status'] == "รอรับบริการ")]
                full = df_b[(df_b['date'] == d_str) & (df_b['time'] == b_time) & (df_b['status'] == "รอรับบริการ")]
                
                if not dup.empty: st.error("⚠️ คุณจองวันนี้ไว้แล้ว")
                elif len(full) >= 2: st.error("⚠️ เวลานี้เต็มแล้ว (รับ 2 ท่านต่อช่วงเวลา)")
                else:
                    new_q = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "fullname": st.session_state.fullname, "date": d_str, "time": b_time, "service": b_service, "status": "รอรับบริการ", "price": "0"}]).astype(str)
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                    st.cache_data.clear() # ล้าง Cache เพื่อให้เห็นคิวที่เพิ่มทันที
                    st.success("✅ จองคิวสำเร็จ!"); time.sleep(1); st.rerun()
    with t2:
        df_b = get_data("Bookings")
        if not df_b.empty:
            my = df_b[df_b['username'] == st.session_state.username].sort_values('date', ascending=False)
            for _, r in my.iterrows():
                with st.container(border=True):
                    st.write(f"**{r['service']}** | 📅 {r['date']} ⏰ {r['time']}")
                    st.write(f"สถานะ: `{r['status']}`" + (f" | ราคา: {r['price']} บาท" if r['status'] == "รับบริการเสร็จสิ้น" else ""))

# --- หน้า Admin (จัดการยอดเงินและคิว) ---
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    df_b = get_data("Bookings")
    t_str = datetime.now().strftime("%Y-%m-%d")
    
    if not df_b.empty:
        today_df = df_b[df_b['date'] == t_str]
        income = pd.to_numeric(today_df[today_df['status'] == "รับบริการเสร็จสิ้น"]['price'], errors='coerce').sum()
        wait_q = len(today_df[today_df['status'] == "รอรับบริการ"])
        
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='summary-box'><h3>📅 คิวรอวันนี้</h3><h2>{wait_q} คิว</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='summary-box' style='background:#28a745;'><h3>💰 ยอดเงินวันนี้</h3><h2>{income:,.0f} บาท</h2></div>", unsafe_allow_html=True)
        
        st.subheader("📋 จัดการคิวรอรับบริการ")
        pend = today_df[today_df['status'] == "รอรับบริการ"].sort_values('time')
        for _, r in pend.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"👤 **{r['fullname']}** | {r['service']} | ⏰ {r['time']}")
                p_val = col2.number_input("ราคาเก็บจริง", min_value=0, key=f"p_{r['id']}")
                if col3.button("✅ จบงาน", key=f"f_{r['id']}"):
                    df_b.loc[df_b['id'] == r['id'], ['status', 'price']] = ["รับบริการเสร็จสิ้น", str(p_val)]
                    conn.update(worksheet="Bookings", data=df_b.astype(str))
                    st.cache_data.clear()
                    st.rerun()

# --- หน้าคิววันนี้ (สำหรับบุคคลทั่วไป) ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 ตารางการจองวันนี้")
    df_b = get_data("Bookings")
    t_str = datetime.now().strftime("%Y-%m-%d")
    if not df_b.empty:
        active = df_b[(df_b['date'] == t_str) & (df_b['status'] == "รอรับบริการ")].sort_values('time')
        if not active.empty: st.table(active[['time', 'service', 'fullname']])
        else: st.info("ไม่มีคิวจองในขณะนี้")
