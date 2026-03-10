import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอและสไตล์ (UI/UX) ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

# ข้อมูลติดต่อร้าน
SHOP_LOCATION_URL = "https://maps.google.com" 
LINE_URL = "https://line.me/ti/p/~222Salon"
FB_URL = "https://www.facebook.com/222Salon" 
SHOP_TEL = "0875644928"

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stButton>button {width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s;}
        .main-header {text-align: center; color: #FF4B4B; margin-bottom: 20px;}
        .price-card {
            background-color: #ffffff; padding: 15px; border-radius: 12px;
            border-left: 5px solid #FF4B4B; margin-bottom: 10px; color: #1A1A1A;
            box-shadow: 1px 2px 8px rgba(0,0,0,0.1);
        }
        .chat-bubble { padding: 10px 15px; border-radius: 15px; margin-bottom: 5px; display: inline-block; max-width: 85%; }
        .user-bubble { background-color: #E1FFC7; color: #000; border-bottom-right-radius: 2px; }
        .admin-bubble { background-color: #F0F0F0; color: #000; border-bottom-left-radius: 2px; }
        .status-badge { padding: 2px 8px; border-radius: 5px; font-size: 0.85em; font-weight: bold; color: white; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. ฟังก์ชันดึงข้อมูล (แก้ปัญหา Quota และชื่อคอลัมน์) ---
def get_data(sheet_name):
    try:
        # ใช้ ttl=10 เพื่อลดการ Request ไปยัง Google Sheets ป้องกัน Error 429
        df = conn.read(worksheet=sheet_name, ttl=10)
        
        if df is None or df.empty:
            # สร้าง Template เปล่าเพื่อป้องกัน KeyError เมื่อ Sheet ยังไม่มีข้อมูล
            cols = {
                "Users": ['username', 'password', 'fullname', 'phone', 'role'],
                "Bookings": ['id', 'username', 'service', 'date', 'time', 'status'],
                "Messages": ['msg_id', 'username', 'sender', 'text', 'timestamp']
            }
            return pd.DataFrame(columns=cols.get(sheet_name, []))

        df = df.dropna(how='all')
        # ลบเว้นวรรคที่อาจติดมากับหัวคอลัมน์ (เช่น 'username ' ให้เป็น 'username')
        df.columns = [str(c).strip() for c in df.columns] 
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        return df
    except Exception:
        # กรณี Quota เต็ม ให้ส่ง DataFrame เปล่าที่มีคอลัมน์พื้นฐานกลับไปเพื่อไม่ให้แอปพัง
        cols = {
            "Users": ['username', 'password', 'fullname', 'phone', 'role'],
            "Bookings": ['id', 'username', 'service', 'date', 'time', 'status'],
            "Messages": ['msg_id', 'username', 'sender', 'text', 'timestamp']
        }
        return pd.DataFrame(columns=cols.get(sheet_name, []))

def get_user_info_map():
    df_u = get_data("Users")
    if not df_u.empty and 'username' in df_u.columns:
        return df_u.set_index('username')[['fullname', 'phone']].to_dict('index')
    return {}

# --- 3. ระบบนำทาง ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon Online</h1>", unsafe_allow_html=True)
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
        if st.button("📊 หลังบ้าน" if role == 'admin' else "✂️ จองคิว"): navigate("Admin" if role == 'admin' else "Booking")
    with m_cols[4]: 
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.logged_in = False
            navigate("Home")

st.divider()

# --- 4. หน้าแรก ---
if st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    c_tel, c_map, c_fb, c_line = st.columns(4)
    with c_tel: st.info(f"📞 ติดต่อ: {SHOP_TEL}")
    with c_map: st.link_button("📍 แผนที่ร้าน", SHOP_LOCATION_URL, type="primary")
    with c_fb: st.link_button("🔵 Facebook", FB_URL)
    with c_line: st.link_button("🟢 Line", LINE_URL)
    
    st.subheader("📋 บริการและราคา")
    services = {"✂️ ตัดผม": {"ชาย": "150-300", "หญิง": "300-600"}, "🎨 เคมี": {"ทำสี": "1,500+", "ยืด": "1,500+"}}
    for cat, items in services.items():
        st.markdown(f"#### {cat}")
        cols = st.columns(2)
        for i, (n, p) in enumerate(items.items()):
            cols[i].markdown(f'<div class="price-card"><b>{n}</b><br><span style="color:#FF4B4B">{p} ฿</span></div>', unsafe_allow_html=True)

# --- 5. หน้าแอดมิน ---
elif st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการหลังบ้าน")
    t1, t2 = st.tabs(["📈 รายการคิวลูกค้า", "💬 แชทลูกค้า"])
    
    with t1:
        df_b = get_data("Bookings")
        u_info = get_user_info_map()
        if not df_b.empty:
            for _, row in df_b.sort_values(['date', 'time'], ascending=False).iterrows():
                user_data = u_info.get(row['username'], {'fullname': row['username'], 'phone': '-'})
                with st.container():
                    c_info, c_done, c_del = st.columns([3, 1, 1])
                    with c_info:
                        st.markdown(f"👤 **{user_data['fullname']}** | 📞 {user_data['phone']}")
                        st.markdown(f"✂️ {row['service']} | 📅 {row['date']} ({row['time']})")
                    with c_done:
                        if st.button("✅ เสร็จสิ้น", key=f"ok_{row['id']}"):
                            df_b.loc[df_b['id'] == row['id'], 'status'] = "เสร็จสิ้น"
                            conn.update(worksheet="Bookings", data=df_b); st.rerun()
                    with c_del:
                        if st.button("🗑️ ลบ", key=f"adm_del_{row['id']}", type="primary"):
                            conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']]); st.rerun()
                st.markdown("---")

    with t2:
        df_msg = get_data("Messages")
        u_map = get_user_info_map()
        if not df_msg.empty and 'username' in df_msg.columns:
            u_list = {u: f"{u_map.get(u, {}).get('fullname', u)} (@{u})" for u in df_msg['username'].unique() if u}
            if u_list:
                target = st.selectbox("เลือกห้องแชท:", options=list(u_list.keys()), format_func=lambda x: u_list[x])
                for _, m in df_msg[df_msg['username'] == target].sort_values('msg_id').iterrows():
                    align, cls = ("left", "user-bubble") if m['sender'] == "user" else ("right", "admin-bubble")
                    st.markdown(f"<div style='text-align: {align};'><div class='chat-bubble {cls}'>{m['text']}</div></div>", unsafe_allow_html=True)
                with st.form("admin_send", clear_on_submit=True):
                    msg = st.text_input("พิมพ์ข้อความตอบกลับ...")
                    if st.form_submit_button("ส่ง"):
                        new_m = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": target, "sender": "admin", "text": msg, "timestamp": datetime.now().strftime("%H:%M")}])
                        conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m], ignore_index=True)); st.rerun()

# --- 6. หน้าลูกค้า (เงื่อนไข 1 ครั้ง/วัน และ พนักงาน 2 คน) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.fullname}")
    t1, t2, t3 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติ/ยกเลิก", "💬 ติดต่อร้าน"])
    
    df_b = get_data("Bookings")
    
    with t1:
        st.write("### กรอกข้อมูลการจอง")
        d = st.date_input("เลือกวันที่จอง", min_value=datetime.now().date())
        svc = st.selectbox("เลือกบริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืดผม/วอลลุ่ม"])
        
        # กฎ: 1 คนต่อ 1 ครั้งต่อวัน (จะจองได้อีกครั้งก็ต่อเมื่อยกเลิกคิวเดิมในวันนั้น)
        is_booked = False
        if 'username' in df_b.columns and 'date' in df_b.columns:
            is_booked = not df_b[(df_b['username'] == st.session_state.username) & (df_b['date'] == str(d))].empty
            
        if is_booked:
            st.warning(f"⚠️ คุณมีการจองในวันที่ {d} อยู่แล้ว (จำกัด 1 ครั้งต่อวัน)")
        else:
            all_slots = [f"{h:02d}:00" for h in range(10, 20)]
            valid_slots = []
            for slot in all_slots:
                # กฎ: พนักงาน 2 คน (ห้ามจองเกิน 2 คนในเวลาเดียวกัน)
                count = len(df_b[(df_b['date'] == str(d)) & (df_b['time'] == slot)])
                if count < 2: valid_slots.append(f"{slot} (ว่าง {2-count} ที่)")
            
            if not valid_slots: st.error("❌ คิวเต็มทุกช่วงเวลาในวันนี้")
            else:
                t_input = st.selectbox("เลือกเวลาที่ว่าง", valid_slots)
                if st.button("✅ ยืนยันการจอง"):
                    new_id = str(int(datetime.now().timestamp()))
                    new_row = pd.DataFrame([{"id":new_id, "username":st.session_state.username, "service":svc, "date":str(d), "time":t_input.split(" ")[0], "status":"รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_row], ignore_index=True)); st.rerun()

    with t2:
        if 'username' in df_b.columns:
            my_q = df_b[df_b['username'] == st.session_state.username]
            if not my_q.empty:
                for _, row in my_q.iterrows():
                    st.write(f"📅 {row['date']} | ⏰ {row['time']} | {row['service']}")
                    if st.button(f"❌ ยกเลิกและลบคิวนี้", key=f"can_{row['id']}", type="primary"):
                        df_b = df_b[df_b['id'] != row['id']] # ลบออกจาก Sheet ทันที
                        conn.update(worksheet="Bookings", data=df_b); st.rerun()
                    st.markdown("---")
            else: st.info("ยังไม่มีประวัติการจอง")

    with t3:
        df_msg = get_data("Messages")
        if not df_msg.empty and 'username' in df_msg.columns:
            my_m = df_msg[df_msg['username'] == st.session_state.username].sort_values('msg_id')
            for _, m in my_m.iterrows():
                align, cls = ("right", "user-bubble") if m['sender'] == "user" else ("left", "admin-bubble")
                st.markdown(f"<div style='text-align: {align};'><div class='chat-bubble {cls}'>{m['text']}</div></div>", unsafe_allow_html=True)
        with st.form("u_msg_send", clear_on_submit=True):
            umsg = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง"):
                new_m = pd.DataFrame([{"msg_id": str(int(datetime.now().timestamp())), "username": st.session_state.username, "sender": "user", "text": umsg, "timestamp": datetime.now().strftime("%H:%M")}])
                conn.update(worksheet="Messages", data=pd.concat([df_msg, new_m], ignore_index=True)); st.rerun()

# --- 7. หน้าจัดการระบบสมาชิก ---
elif st.session_state.page == "Login":
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
        df_u = get_data("Users")
        if not df_u.empty and 'username' in df_u.columns:
            user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
            if u == "admin222" and p == "222":
                st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin', 'fullname':'แอดมิน'}); navigate("Admin")
            elif not user.empty:
                st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u, 'fullname':user.iloc[0]['fullname']}); navigate("Booking")
            else: st.error("ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Register":
    with st.form("reg_form"):
        nu, np, nf, nt = st.text_input("Username"), st.text_input("Password"), st.text_input("ชื่อจริง"), st.text_input("เบอร์โทร")
        if st.form_submit_button("สมัครสมาชิก"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "phone":nt, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u], ignore_index=True)); navigate("Login")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 ตารางคิววันนี้")
    st.dataframe(get_data("Bookings"), use_container_width=True)
