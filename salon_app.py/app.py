import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import time
import hashlib
from supabase import create_client, Client

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="222-Salon Songkhla", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# CSS Custom Styling
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main-header {text-align: center; color: #FF4B4B; font-weight: bold; margin-bottom: 5px;}
        .sub-header {text-align: center; color: #666; margin-bottom: 20px;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}
        .price-card {
            background-color: #ffffff; padding: 15px; border-radius: 12px;
            border-left: 6px solid #FF4B4B; margin-bottom: 12px;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.05); color: #111;
        }
        .nav-btn { margin-bottom: 10px; }
        .notification-dot { color: #FF4B4B; font-size: 12px; vertical-align: top; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HELPERS & NOTIFICATIONS ---
def navigate(p):
    st.session_state.page = p
    st.rerun()

def get_admin_notifications():
    # เช็คคิวใหม่ และ แชทใหม่ (ที่แอดมินยังไม่ได้ตอบ)
    new_bookings = supabase.table("bookings").select("id").eq("status", "รอรับบริการ").execute()
    new_chats = supabase.table("chats").select("id").eq("sender", "user").execute() 
    # หมายเหตุ: ในระบบจริงอาจเพิ่มคอลัมน์ 'is_read' แต่ในที่นี้เช็คจากสถานะเบื้องต้น
    return len(new_bookings.data) > 0 or len(new_chats.data) > 0

# --- 3. NAVIGATION LOGIC ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

st.markdown("<h1 class='main-header'>✂️ 222-Salon @สงขลา</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Professional Hair Design & Care</p>", unsafe_allow_html=True)

m_cols = st.columns([1, 1, 1, 1, 1])
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
        has_notif = "🔴" if get_admin_notifications() else ""
        with m_cols[2]:
            if st.button(f"📊 จัดการร้าน {has_notif}"): navigate("Admin")
    else:
        with m_cols[2]:
            if st.button("✂️ จองคิว"): navigate("Booking")
    with m_cols[4]:
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")
st.divider()

# --- 4. PAGES ---

# 1. หน้าแรก (Home)
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000", caption="บรรยากาศร้านที่เป็นกันเอง")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.info("⏰ **เวลาทำการ:** 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")
    with c2:
        st.markdown("[📍 ดูแผนที่ Google Maps](https://maps.google.com)", unsafe_allow_html=True) # เปลี่ยน Link จริงที่นี่

    services = {"✂️ ตัดผมชาย": "150-350 บ.", "💇‍♀️ ตัดผมหญิง": "350-800 บ.", "🚿 สระ-ไดร์": "200-450 บ.", 
                "🎨 ทำสีผม": "1,500 บ.+", "✨ ยืด/ดัด": "1,000 บ.+", "🌿 ทรีทเม้นท์": "500 บ.+" }
    
    st.subheader("ราคาค่าบริการ")
    p1, p2 = st.columns(2)
    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2
        target.markdown(f'<div class="price-card"><b>{name}</b><span style="float:right; color:#FF4B4B;">{price}</span></div>', unsafe_allow_html=True)

# 2. หน้าสมัครสมาชิก
elif st.session_state.page == "Register":
    st.subheader("📝 สมัครสมาชิกใหม่")
    with st.form("reg"):
        nf = st.text_input("ชื่อ-นามสกุล")
        nu = st.text_input("เบอร์โทรศัพท์ (10 หลัก)")
        np = st.text_input("รหัสผ่าน", type="password")
        if st.form_submit_button("ลงทะเบียน"):
            u_clean = nu.strip().replace("-", "")
            if len(u_clean) == 9: u_clean = "0" + u_clean
            
            if len(u_clean) != 10:
                st.error("❌ กรุณากรอกเบอร์โทรศัพท์ให้ถูกต้อง")
            else:
                check = supabase.table("users").select("phone").eq("phone", u_clean).execute()
                if check.data:
                    st.error("❌ เบอร์โทรนี้มีในระบบแล้ว")
                else:
                    supabase.table("users").insert({
                        "phone": u_clean, "password": hash_pass(np), "fullname": nf.strip(), "role": "user"
                    }).execute()
                    st.success("✅ ลงทะเบียนสำเร็จ!"); time.sleep(1); navigate("Login")

# 3. หน้าเข้าสู่ระบบ
elif st.session_state.page == "Login":
    st.subheader("🔑 เข้าสู่ระบบ")
    u_in = st.text_input("เบอร์โทรศัพท์ / Username")
    p_in = st.text_input("รหัสผ่าน", type="password")
    if st.button("ตกลง", type="primary"):
        u_clean = u_in.strip()
        if u_clean == "admin222" and p_in == "222":
            st.session_state.update({'logged_in': True, 'user_role': 'admin', 'username': 'admin', 'fullname': 'ผู้ดูแลระบบ'})
            navigate("Admin")
        else:
            if len(u_clean) == 9: u_clean = "0" + u_clean
            user = supabase.table("users").select("*").eq("phone", u_clean).execute()
            if user.data and user.data[0]['password'] == hash_pass(p_in):
                u_data = user.data[0]
                st.session_state.update({'logged_in': True, 'user_role': u_data['role'], 'username': u_clean, 'fullname': u_data['fullname']})
                navigate("Booking" if u_data['role'] == 'user' else "Admin")
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")

# 4. หน้าจองคิว (Booking)
elif st.session_state.page == "Booking" and st.session_state.logged_in:
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง", "💬 แชทสอบถาม"])
    
    with t1:
        # Check Active Booking
        active = supabase.table("bookings").select("*").eq("username", st.session_state.username).eq("status", "รอรับบริการ").execute()
        if active.data:
            st.warning("⚠️ คุณมีคิวที่รอรับบริการอยู่ ไม่สามารถจองเพิ่มได้")
        else:
            with st.form("b"):
                bd = st.date_input("เลือกวันที่", min_value=datetime.now().date())
                all_times = ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"]
                
                # Smart Filter: กรองเวลาที่จองไปแล้ว
                booked_res = supabase.table("bookings").select("time").eq("date", str(bd)).not_.eq("status", "ยกเลิกโดยลูกค้า").execute()
                booked = [r['time'] for r in booked_res.data]
                avail = [t for t in all_times if t not in booked]
                
                bt = st.selectbox("เลือกเวลา", avail if (avail and bd.weekday() != 5) else ["เต็ม/ร้านหยุด"])
                bs = st.selectbox("เลือกบริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืด/ดัด", "ทรีทเม้นท์"])
                
                if st.form_submit_button("ยืนยันการจอง"):
                    if bd.weekday() == 5: st.error("❌ ร้านปิดวันเสาร์ กรุณาเลือกวันอื่น")
                    elif not avail: st.error("❌ ขออภัย คิวเต็มแล้ว")
                    else:
                        supabase.table("bookings").insert({
                            "id": str(uuid.uuid4())[:8], "username": st.session_state.username, 
                            "fullname": st.session_state.fullname, "date": str(bd), 
                            "time": bt, "service": bs, "status": "รอรับบริการ", "price": 0
                        }).execute()
                        st.success("✅ จองสำเร็จ!"); time.sleep(1); st.rerun()

    with t2:
        res = supabase.table("bookings").select("*").eq("username", st.session_state.username).order("created_at", desc=True).execute()
        for r in res.data:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                status_color = "🔵" if r['status'] == "รอรับบริการ" else "✅" if r['status'] == "เสร็จสิ้น" else "⚪"
                c1.write(f"{status_color} **{r['date']}** เวลา **{r['time']}**")
                c1.caption(f"บริการ: {r['service']} | สถานะ: {r['status']}")
                if r['status'] == "รอรับบริการ":
                    if c2.button("ยกเลิก", key=f"can_{r['id']}"):
                        supabase.table("bookings").update({"status": "ยกเลิกโดยลูกค้า"}).eq("id", r['id']).execute()
                        st.rerun()

    with t3:
        chats = supabase.table("chats").select("*").eq("username", st.session_state.username).order("created_at").execute()
        with st.container(height=300):
            for m in chats.data:
                with st.chat_message("user" if m['sender']=="user" else "assistant"): st.write(m['msg'])
        if p := st.chat_input("สอบถามร้านค้า..."):
            supabase.table("chats").insert({"username": st.session_state.username, "sender": "user", "msg": p}).execute()
            st.rerun()

# 5. หน้าแอดมิน (Admin Panel)
elif st.session_state.page == "Admin" and st.session_state.user_role == 'admin':
    at1, at2, at3 = st.tabs(["📊 Dashboard รายได้", "📅 จัดการคิวลูกค้า", "📩 ตอบแชท"])
    
    with at1:
        res = supabase.table("bookings").select("price, service").eq("status", "เสร็จสิ้น").execute()
        if res.data:
            df_done = pd.DataFrame(res.data)
            st.metric("รายได้รวมทั้งหมด", f"{df_done['price'].sum():,.0f} บาท")
            st.subheader("แยกตามบริการ")
            st.bar_chart(df_done.groupby('service')['price'].sum())
        else: st.info("ยังไม่มีข้อมูลรายได้")

    with at2:
        res = supabase.table("bookings").select("*").eq("status", "รอรับบริการ").order("date").order("time").execute()
        st.subheader(f"คิวรอรับบริการ ({len(res.data)})")
        for r in res.data:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"👤 {r['fullname']}\n📅 {r['date']} | ⏰ {r['time']}\n✂️ {r['service']}")
                pr = col2.number_input("ราคาจริง (บาท)", min_value=0, step=50, key=f"p{r['id']}")
                if col2.button("✅ ปิดงาน", key=f"ok{r['id']}"):
                    supabase.table("bookings").update({"status": "เสร็จสิ้น", "price": pr}).eq("id", r['id']).execute()
                    st.rerun()
                if col3.button("❌ ยกเลิกคิว", key=f"no{r['id']}"):
                    supabase.table("bookings").update({"status": "ยกเลิกโดยร้าน"}).eq("id", r['id']).execute()
                    st.rerun()

    with at3:
        # ดึงแชทแยกตาม User
        chat_data = supabase.table("chats").select("username").execute()
        unique_users = sorted(list(set([d['username'] for d in chat_data.data])))
        for u in unique_users:
            with st.expander(f"📩 แชทจากลูกค้าเบอร์: {u}"):
                msgs = supabase.table("chats").select("*").eq("username", u).order("created_at").execute()
                for m in msgs.data:
                    with st.chat_message("assistant" if m['sender']=="user" else "user"): st.write(m['msg'])
                with st.form(f"rep_{u}", clear_on_submit=True):
                    rep = st.text_input("ตอบกลับ...")
                    if st.form_submit_button("ส่งข้อความ"):
                        supabase.table("chats").insert({"username": u, "sender": "admin", "msg": rep}).execute()
                        st.rerun()

# 6. หน้าดูคิววันนี้ (Public)
elif st.session_state.page == "ViewQueues":
    st.subheader("📅 รายการคิววันนี้")
    today = datetime.now().date()
    res = supabase.table("bookings").select("time, service, fullname").eq("date", str(today)).eq("status", "รอรับบริการ").order("time").execute()
    if res.data:
        df_today = pd.DataFrame(res.data)
        df_today.columns = ['เวลา', 'บริการ', 'ชื่อลูกค้า']
        st.table(df_today)
    else:
        st.info(f"ไม่มีคิวจองในวันนี้ ({today})")
