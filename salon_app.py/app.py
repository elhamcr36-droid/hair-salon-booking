import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# ปรับแต่ง CSS เพื่อความสวยงามและซ่อน Sidebar
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

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl="0s")
        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')
            if 'phone' in col:
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

# เมนูบาร์ด้านบน
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
            navigate("Home")

st.divider()

# --- 3. PAGE LOGIC ---

# --- หน้าแรก (Home) ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (หยุดทุกวันพุธ)")
    
    st.subheader("📋 บริการและราคา")
    services = {
        "✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", 
        "🚿 สระ-ไดร์": "200-450 บ.", "🎨 ทำสีผม": "1,500 บ.+", 
        "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+"
    }
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span class="price-text">{price}</span></div>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📞 ติดต่อเรา & แผนที่")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='contact-box'><h3>📞 โทร</h3><p>081-222-2222</p></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='contact-box'><h3>💬 Line</h3><p>@222salon</p></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='contact-box'><h3>📍 ที่ตั้ง</h3><p>222 ซอย.พิรม สงขลา</p></div>", unsafe_allow_html=True)

# --- หน้าสมัครสมาชิก (Register) ---
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg_form"):
        nu = st.text_input("เบอร์โทรศัพท์ (ใช้เป็น Username)").strip()
        nf = st.text_input("ชื่อ-นามสกุล").strip()
        np = st.text_input("รหัสผ่าน", type="password").strip()
        np_confirm = st.text_input("ยืนยันรหัสผ่านอีกครั้ง", type="password").strip()
        if st.form_submit_button("ลงทะเบียน"):
            if not nu or not nf or not np:
                st.error("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
            elif np != np_confirm:
                st.error("❌ รหัสผ่านไม่ตรงกัน")
            else:
                df_u = get_data("Users")
                if not df_u.empty and nu in df_u['phone'].values:
                    st.error("⚠️ เบอร์โทรนี้เคยลงทะเบียนไว้แล้ว")
                else:
                    new_user = pd.DataFrame([{"phone": nu, "password": np, "fullname": nf, "role": "user"}])
                    conn.update(worksheet="Users", data=pd.concat([df_u, new_user], ignore_index=True))
                    st.success("✅ สมัครสมาชิกสำเร็จ!"); time.sleep(1.5); navigate("Login")

# --- หน้าเข้าสู่ระบบ (Login) ---
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์").strip()
    p_in = st.text_input("รหัสผ่าน", type="password").strip()
    if st.button("ตกลง", type="primary"):
        if u_in == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'admin', 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            df_u = get_data("Users")
            user = df_u[(df_u['phone'] == u_in) & (df_u['password'] == p_in)]
            if not user.empty:
                st.session_state.update({'logged_in': True, 'user_role': 'user', 'username': u_in, 'fullname': user.iloc[0]['fullname']})
                navigate("Booking")
            else:
                st.error("❌ เบอร์โทรหรือรหัสผ่านไม่ถูกต้อง")

# --- หน้าจองคิว (Booking) พร้อมระบบกันจองซ้ำ ---
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2 = st.tabs(["🆕 จองคิว", "📋 ประวัติคิวของคุณ"])
    with t1:
        with st.form("booking_form"):
            b_date = st.date_input("เลือกวันที่จอง", min_value=datetime.now().date())
            b_time = st.selectbox("เลือกเวลา", ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
            b_service = st.selectbox("เลือกบริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
            
            if st.form_submit_button("ยืนยันการจอง"):
                df_b = get_data("Bookings")
                today_str = str(b_date)
                
                # ระบบตรวจสอบการจองซ้ำ
                if not df_b.empty:
                    # 1. กันจองซ้ำวันเดียวกัน (ถ้ายังมีสถานะ "รอรับบริการ")
                    user_duplicate = df_b[(df_b['username'] == st.session_state.username) & 
                                         (df_b['date'] == today_str) & 
                                         (df_b['status'] == "รอรับบริการ")]
                    
                    # 2. กันช่วงเวลาเต็ม (จำกัด 2 ท่านต่อช่วงเวลา)
                    time_slot_full = df_b[(df_b['date'] == today_str) & 
                                         (df_b['time'] == b_time) & 
                                         (df_b['status'] == "รอรับบริการ")]
                    
                    if not user_duplicate.empty:
                        st.error(f"⚠️ คุณมีการจองในวันที่ {today_str} อยู่แล้ว")
                    elif len(time_slot_full) >= 2:
                        st.error(f"⚠️ ขออภัย เวลา {b_time} ของวันที่ {today_str} เต็มแล้ว (รับ 2 ท่านต่อช่วงเวลา)")
                    else:
                        new_q = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "fullname": st.session_state.fullname, "date": today_str, "time": b_time, "service": b_service, "status": "รอรับบริการ", "price": "0"}])
                        conn.update(worksheet="Bookings", data=pd.concat([df_b, new_q], ignore_index=True))
                        st.success("✅ จองสำเร็จแล้ว!"); time.sleep(1); st.rerun()
                else:
                    new_q = pd.DataFrame([{"id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "fullname": st.session_state.fullname, "date": today_str, "time": b_time, "service": b_service, "status": "รอรับบริการ", "price": "0"}])
                    conn.update(worksheet="Bookings", data=new_q)
                    st.success("✅ จองสำเร็จแล้ว!"); time.sleep(1); st.rerun()
    with t2:
        df_b = get_data("Bookings")
        if not df_b.empty:
            my_qs = df_b[df_b['username'] == st.session_state.username].sort_values('date', ascending=False)
            for _, row in my_qs.iterrows():
                with st.container(border=True):
                    st.write(f"**{row['service']}** | 📅 {row['date']} ⏰ {row['time']}")
                    st.write(f"สถานะ: `{row['status']}`" + (f" | ราคา: {row['price']} บาท" if row['status'] == "รับบริการเสร็จสิ้น" else ""))
                    if row['status'] == "รอรับบริการ" and st.button("❌ ยกเลิกคิวนี้", key=f"del_{row['id']}"):
                        conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']]); st.rerun()

# --- หน้า Admin (สำหรับเจ้าของร้าน) ---
elif st.session_state.page == "Admin" and st.session_state.logged_in:
    df_b = get_data("Bookings")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # สรุปยอด
    if not df_b.empty:
        today_data = df_b[df_b['date'] == today_str]
        income = pd.to_numeric(today_data[today_data['status'] == "รับบริการเสร็จสิ้น"]['price'], errors='coerce').sum()
        wait_q = len(today_data[today_data['status'] == "รอรับบริการ"])
    else: income, wait_q = 0, 0
    
    c1, c2 = st.columns(2)
    c1.markdown(f"<div class='summary-box'><h3>📅 คิวรอวันนี้</h3><h2>{wait_q} คิว</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='summary-box' style='background:#28a745;'><h3>💰 ยอดเงินวันนี้</h3><h2>{income:,.2f} บาท</h2></div>", unsafe_allow_html=True)
    
    st.subheader("📋 จัดการคิวลูกค้า (วันนี้)")
    if not df_b.empty:
        pending = df_b[(df_b['status'] == "รอรับบริการ") & (df_b['date'] == today_str)].sort_values('time')
        for _, row in pending.iterrows():
            with st.container(border=True):
                col_i, col_p, col_b = st.columns([2, 1, 1])
                col_i.write(f"👤 **{row['fullname']}**\n{row['service']} | ⏰ {row['time']}")
                price_val = col_p.number_input("ค่าบริการ", min_value=0, key=f"pr_{row['id']}")
                if col_b.button("✅ เสร็จงาน", key=f"ok_{row['id']}"):
                    df_b.loc[df_b['id'] == row['id'], 'status'] = "รับบริการเสร็จสิ้น"
                    df_b.loc[df_b['id'] == row['id'], 'price'] = str(price_val)
                    conn.update(worksheet="Bookings", data=df_b); st.rerun()

# --- หน้าดูตารางคิวรวม (ViewQueues) ---
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 ตารางการจองวันนี้")
    df_b = get_data("Bookings")
    today_str = datetime.now().strftime("%Y-%m-%d")
    if not df_b.empty:
        active = df_b[(df_b['date'] == today_str) & (df_b['status'] == "รอรับบริการ")].sort_values('time')
        if not active.empty:
            # ซ่อนชื่อบางส่วนเพื่อความเป็นส่วนตัว
            active['customer'] = active['fullname'].apply(lambda x: x[:3] + "..." if len(x) > 3 else x)
            st.table(active[['time', 'service', 'customer']])
        else:
            st.info("ยังไม่มีคิวจองในวันนี้")
    else:
        st.write("ไม่มีข้อมูลการจอง")
