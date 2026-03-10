import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอและสไตล์ ---
st.set_page_config(page_title="222-Salon", layout="wide", initial_sidebar_state="collapsed")

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
        .history-card {
            background-color: #f8f9fa; padding: 15px; border-radius: 10px;
            border-left: 5px solid #dee2e6; margin-bottom: 15px;
            box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
        }
        .status-done { color: #28a745; font-weight: bold; }
        .status-wait { color: #FF4B4B; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. ฟังก์ชันดึงข้อมูล (ป้องกัน Quota & KeyError) ---
def get_data(sheet_name):
    try:
        # ttl=5 เพื่อป้องกัน Google บล็อก (Error 429)
        df = conn.read(worksheet=sheet_name, ttl=5)
        if df is None or df.empty:
            cols = {
                "Users": ['username', 'password', 'fullname', 'phone', 'role'],
                "Bookings": ['id', 'username', 'service', 'date', 'time', 'status']
            }
            return pd.DataFrame(columns=cols.get(sheet_name, []))
        
        # ล้างช่องว่างที่หัวคอลัมน์อัตโนมัติ (แก้ปัญหา 'username ')
        df.columns = [str(c).strip() for c in df.columns] 
        df = df.fillna("").map(lambda x: str(x).replace('.0', '') if isinstance(x, (float, int)) else str(x))
        return df
    except Exception:
        return pd.DataFrame()

# --- 3. ระบบนำทาง (ปุ่มไม่ค้างแน่นอน) ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def navigate(p):
    st.session_state.page = p
    st.rerun()

st.markdown("<h1 class='main-header'>✂️ 222-Salon Online</h1>", unsafe_allow_html=True)

# แถวปุ่มเมนูหลัก
m_cols = st.columns(5)
with m_cols[0]: 
    if st.button("🏠 หน้าแรก"): navigate("Home")
with m_cols[1]: 
    if st.button("📅 คิววันนี้"): navigate("ViewQueues")

# ตรรกะแสดงปุ่มตามสถานะการ Login
if not st.session_state.logged_in:
    with m_cols[3]: 
        if st.button("📝 สมัครสมาชิก"): navigate("Register")
    with m_cols[4]: 
        if st.button("🔑 เข้าสู่ระบบ"): navigate("Login")
else:
    role = st.session_state.get('user_role')
    with m_cols[2]: 
        # แอดมินจะเห็นเมนูหลังบ้าน ลูกค้าเห็นเมนูจองคิว
        label = "📊 หลังบ้าน" if role == 'admin' else "✂️ จองคิว"
        page_target = "Admin" if role == 'admin' else "Booking"
        if st.button(label): navigate(page_target)
    with m_cols[4]: 
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            navigate("Home")

st.divider()

# --- 4. หน้า ADMIN (จัดการแล้วหายทันที) ---
if st.session_state.page == "Admin":
    st.subheader("📊 ระบบจัดการคิว (แอดมิน)")
    df_b = get_data("Bookings")
    
    # กรองแสดงเฉพาะคิวที่ยังไม่เสร็จ
    pending = df_b[df_b['status'] == "รอรับบริการ"] if not df_b.empty else pd.DataFrame()
    
    if not pending.empty:
        for _, row in pending.sort_values(['date', 'time']).iterrows():
            with st.container():
                c_txt, c_ok, c_del = st.columns([3, 1, 1])
                with c_txt:
                    st.write(f"👤 **ลูกค้า:** {row['username']} | ✂️ **{row['service']}**")
                    st.write(f"📅 {row['date']} เวลา {row['time']} น.")
                
                if c_ok.button("✅ เสร็จสิ้น", key=f"ok_{row['id']}"):
                    df_b.loc[df_b['id'] == row['id'], 'status'] = "เสร็จสิ้น"
                    conn.update(worksheet="Bookings", data=df_b)
                    st.toast("อัปเดตสถานะสำเร็จ!"); st.rerun()
                
                if c_del.button("🗑️ ลบ", key=f"adm_del_{row['id']}", type="primary"):
                    conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']])
                    st.toast("ลบคิวเรียบร้อย"); st.rerun()
            st.markdown("---")
    else:
        st.info("✨ ไม่มีคิวรอดำเนินการในขณะนี้")

# --- 5. หน้า BOOKING (ประวัติครบถ้วน + ยกเลิกได้) ---
elif st.session_state.page == "Booking":
    st.subheader(f"👋 สวัสดีคุณ {st.session_state.fullname}")
    t1, t2 = st.tabs(["🆕 จองคิวใหม่", "📋 ประวัติการจอง"])
    
    df_b = get_data("Bookings")
    
    with t1:
        d = st.date_input("เลือกวันที่จอง", min_value=datetime.now().date())
        # เช็คกฎ 1 คน 1 วัน
        already = not df_b[(df_b['username'] == st.session_state.username) & (df_b['date'] == str(d))].empty
        
        if already:
            st.warning(f"⚠️ คุณมีการจองวันที่ {d} อยู่แล้ว (จำกัด 1 ครั้ง/วัน)")
        else:
            # เช็คจำนวนพนักงาน 2 คนต่อช่วงเวลา
            all_slots = [f"{h:02d}:00" for h in range(10, 20)]
            valid_slots = []
            for slot in all_slots:
                count = len(df_b[(df_b['date'] == str(d)) & (df_b['time'] == slot)])
                if count < 2: valid_slots.append(f"{slot} (ว่าง {2-count})")
            
            if not valid_slots: st.error("❌ ขออภัย วันนี้คิวเต็มทุกช่วงเวลา")
            else:
                svc = st.selectbox("เลือกบริการ", ["ตัดผมชาย", "ตัดผมหญิง", "สระ-ไดร์", "ทำสีผม", "ยืดผม"])
                t_input = st.selectbox("เลือกเวลา", valid_slots)
                if st.button("✅ ยืนยันการจองคิว"):
                    new_id = str(int(datetime.now().timestamp()))
                    new_row = pd.DataFrame([{"id":new_id, "username":st.session_state.username, "service":svc, "date":str(d), "time":t_input.split(" ")[0], "status":"รอรับบริการ"}])
                    conn.update(worksheet="Bookings", data=pd.concat([df_b, new_row]))
                    st.success("จองคิวสำเร็จแล้ว!"); st.rerun()

    with t2:
        st.write("### ประวัติการจองทั้งหมดของคุณ")
        if not df_b.empty:
            # ดึงประวัติของ User นี้ (เรียงจากล่าสุด)
            my_history = df_b[df_b['username'] == st.session_state.username].sort_values(['date', 'time'], ascending=False)
            
            if not my_history.empty:
                for _, row in my_history.iterrows():
                    is_wait = row['status'] == "รอรับบริการ"
                    st_cls = "status-wait" if is_wait else "status-done"
                    
                    st.markdown(f"""
                    <div class="history-card">
                        <b>📅 วันที่:</b> {row['date']} | <b>⏰ เวลา:</b> {row['time']}<br>
                        <b>✂️ บริการ:</b> {row['service']} | <b>สถานะ:</b> <span class="{st_cls}">{row['status']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # ปุ่มยกเลิก: จะแสดงเฉพาะคิวที่ยัง "รอรับบริการ" เท่านั้น
                    if is_wait:
                        if st.button(f"❌ ยกเลิกคิว {row['date']} ({row['time']})", key=f"user_can_{row['id']}", type="primary"):
                            conn.update(worksheet="Bookings", data=df_b[df_b['id'] != row['id']])
                            st.rerun()
                    st.markdown("---")
            else:
                st.info("คุณยังไม่มีประวัติการจอง")

# --- 6. หน้าอื่นๆ (Login, Register, Home, View) ---
elif st.session_state.page == "Login":
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("เข้าสู่ระบบ"):
        df_u = get_data("Users")
        user = df_u[(df_u['username'] == u) & (df_u['password'] == p)]
        if u == "admin222" and p == "222":
            st.session_state.update({'logged_in':True, 'user_role':'admin', 'username':'Admin', 'fullname':'แอดมิน'})
            navigate("Admin")
        elif not user.empty:
            st.session_state.update({'logged_in':True, 'user_role':'user', 'username':u, 'fullname':user.iloc[0]['fullname']})
            navigate("Booking")
        else: st.error("ข้อมูลไม่ถูกต้อง")

elif st.session_state.page == "Register":
    with st.form("reg"):
        nu, np, nf, nt = st.text_input("Username"), st.text_input("Password"), st.text_input("ชื่อจริง"), st.text_input("เบอร์โทร")
        if st.form_submit_button("สมัครสมาชิก"):
            df_u = get_data("Users")
            new_u = pd.DataFrame([{"username":nu, "password":np, "fullname":nf, "phone":nt, "role":"user"}])
            conn.update(worksheet="Users", data=pd.concat([df_u, new_u]))
            navigate("Login")

elif st.session_state.page == "Home":
    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.write("💈 ยินดีต้อนรับสู่ 222-Salon - บริการตัดผมมืออาชีพ")

elif st.session_state.page == "ViewQueues":
    st.subheader("📅 ตารางคิววันนี้")
    st.dataframe(get_data("Bookings"), use_container_width=True)
