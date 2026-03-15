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

# ---------------- DATA FUNCTIONS ----------------
def get_data(sheet_name):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)

        if df is None or df.empty:
            return pd.DataFrame()

        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]

        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan', '')

            if 'phone' in col or 'username' in col:
                df[col] = df[col].apply(lambda x: '0'+x if len(x)==9 and x.isdigit() else x)

        return df

    except:
        return pd.DataFrame()


def get_new_msg_count():

    df_m = get_data("Messages")

    if 'admin_reply' not in df_m.columns:
        df_m['admin_reply'] = ""

    if not df_m.empty:
        unreplied = df_m[df_m['admin_reply'] == ""]
        return len(unreplied)

    return 0


# ---------------- SESSION ----------------
if 'page' not in st.session_state:
    st.session_state.page = "Home"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


def navigate(p):
    st.session_state.page = p
    st.rerun()


# ---------------- MENU ----------------
st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)

m_cols = st.columns(5)

with m_cols[0]:
    if st.button("🏠 หน้าแรก"):
        navigate("Home")

with m_cols[1]:
    if st.button("📅 คิววันนี้"):
        navigate("ViewQueues")

if not st.session_state.logged_in:

    with m_cols[3]:
        if st.button("📝 สมัครสมาชิก"):
            navigate("Register")

    with m_cols[4]:
        if st.button("🔑 เข้าสู่ระบบ"):
            navigate("Login")

else:

    role = st.session_state.get('user_role')

    with m_cols[2]:

        if role == 'admin':

            new_msgs = get_new_msg_count()

            lbl = f"📊 จัดการร้าน {'🔴' if new_msgs > 0 else ''}"

            if st.button(lbl):
                navigate("Admin")

        else:

            if st.button("✂️ จองคิว"):
                navigate("Booking")

    with m_cols[4]:

        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")

st.divider()

# ---------------- HOME ----------------
if st.session_state.page == "Home":

    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")

    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (⚠️ หยุดทุกวันเสาร์)")

    st.subheader("📋 บริการและราคา")

    services = {
        "✂️ ตัดผมชาย": "150-350 บ.",
        "💇‍♀️ ตัดผมหญิง": "350-800 บ.",
        "🚿 สระ-ไดร์": "200-450 บ.",
        "🎨 ทำสีผม": "1,500 บ.+",
        "✨ ยืด/ดัด": "1,000 บ.+",
        "🌿 ทรีทเม้นท์": "500 บ.+"
    }

    p1, p2 = st.columns(2)

    for i, (name, price) in enumerate(services.items()):
        target = p1 if i % 2 == 0 else p2

        target.markdown(
            f'<div class="price-card"><b>{name}</b><span class="price-text">{price}</span></div>',
            unsafe_allow_html=True
        )

# ---------------- VIEW QUEUES ----------------
elif st.session_state.page == "ViewQueues":

    st.subheader("📅 รายการคิววันนี้ (Real-time)")

    placeholder = st.empty()

    df_today = get_data("Bookings")

    today_str = datetime.now().strftime("%Y-%m-%d")

    with placeholder.container():

        if not df_today.empty:

            active = df_today[
                (df_today['date'] == today_str) &
                (df_today['status'] == "รอรับบริการ")
            ]

            if not active.empty:

                st.write(f"🔔 มีคิวรอรับบริการทั้งหมด {len(active)} คิว")

                st.table(
                    active[['time', 'service', 'fullname']].sort_values('time')
                )

            else:

                st.info(f"✨ ยังไม่มีการจองในวันนี้ ({today_str})")

        else:

            st.info("📅 ยังไม่มีข้อมูลการจอง")

    time.sleep(30)
    st.rerun()


# ---------------- REGISTER ----------------
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

                    new_u = pd.DataFrame([{
                        "phone": nu,
                        "password": np,
                        "fullname": nf,
                        "role": "user"
                    }])

                    conn.update(
                        worksheet="Users",
                        data=pd.concat([df_u, new_u], ignore_index=True)
                    )

                    st.success("✅ สำเร็จ!")
                    navigate("Login")

            else:

                st.error("❌ ข้อมูลไม่ถูกต้อง")


# ---------------- LOGIN ----------------
elif st.session_state.page == "Login":

    st.subheader("🔑 เข้าสู่ระบบ")

    u_in = st.text_input("เบอร์โทรศัพท์").strip()
    p_in = st.text_input("รหัสผ่าน", type="password").strip()

    if st.button("ตกลง", type="primary"):

        if u_in == "admin222" and p_in == "222":

            st.session_state.update({
                'logged_in': True,
                'user_role': 'admin',
                'username': u_in,
                'fullname': 'ผู้ดูแลระบบ'
            })

            navigate("Admin")

        else:

            df_u = get_data("Users")

            user = df_u[
                (df_u['phone'] == u_in) &
                (df_u['password'] == p_in)
            ] if not df_u.empty else pd.DataFrame()

            if not user.empty:

                st.session_state.update({
                    'logged_in': True,
                    'user_role': 'user',
                    'username': u_in,
                    'fullname': user.iloc[0]['fullname']
                })

                navigate("Booking")

            else:

                st.error("❌ ข้อมูลไม่ถูกต้อง")
