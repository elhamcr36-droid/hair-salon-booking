import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="222-Salon-Final",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- STYLE ----------------
st.markdown("""
<style>

[data-testid="stSidebar"] {display:none;}

.main-header{
text-align:center;
color:#FF4B4B;
font-weight:bold;
margin-bottom:20px;
}

.stButton>button{
width:100%;
border-radius:10px;
font-weight:bold;
height:3.2em;
}

/* กล่องบริการ */
.price-card{
background:#ffffff;
padding:18px;
border-radius:12px;
border-left:6px solid #FF4B4B;
margin-bottom:12px;
box-shadow:2px 4px 12px rgba(0,0,0,0.08);
color:#000000 !important;
font-size:18px;
}

.price-card b{
color:#000000 !important;
}

.price-text{
float:right;
color:#FF4B4B;
font-weight:bold;
}

/* กล่องติดต่อ */
.contact-section{
background:#ffffff;
padding:30px;
border-radius:15px;
text-align:center;
box-shadow:0px 4px 15px rgba(0,0,0,0.1);
border:1px solid #eeeeee;
color:#000000 !important;
}

.contact-section p{
color:#000000 !important;
font-size:18px;
}

.contact-section h3{
color:#FF4B4B !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- CONNECTION ----------------
conn = st.connection("gsheets", type=GSheetsConnection)

# ---------------- FUNCTIONS ----------------
def get_data(sheet):

    try:
        df = conn.read(worksheet=sheet, ttl=0)

        if df is None or df.empty:
            return pd.DataFrame()

        df = df.dropna(how="all")
        df.columns = [str(c).strip().lower() for c in df.columns]

        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace("nan","")

        return df

    except:
        return pd.DataFrame()


def get_new_msg_count():

    df = get_data("Messages")

    if 'admin_reply' not in df.columns:
        df['admin_reply'] = ""

    if not df.empty:
        unreplied = df[df['admin_reply']==""]

        return len(unreplied)

    return 0


# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page="Home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False


def navigate(p):
    st.session_state.page=p
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

    role = st.session_state.get("user_role")

    with m_cols[2]:

        if role=="admin":

            new = get_new_msg_count()

            lbl=f"📊 จัดการร้าน {'🔴' if new>0 else ''}"

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
if st.session_state.page=="Home":

    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")

    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 (หยุดวันเสาร์)")

    st.subheader("📋 บริการและราคา")

    services={
    "✂️ ตัดผมชาย":"150-350 บ.",
    "💇‍♀️ ตัดผมหญิง":"350-800 บ.",
    "🚿 สระ-ไดร์":"200-450 บ.",
    "🎨 ทำสีผม":"1500 บ.+",
    "✨ ยืด/ดัด":"1000 บ.+",
    "🌿 ทรีทเม้นท์":"500 บ.+"
    }

    p1,p2=st.columns(2)

    for i,(name,price) in enumerate(services.items()):

        target=p1 if i%2==0 else p2

        target.markdown(
        f"<div class='price-card'><b>{name}</b><span class='price-text'>{price}</span></div>",
        unsafe_allow_html=True)

    st.divider()

    map_link="https://www.google.com/maps/search/?api=1&query=222+Tesaban+1+Alley+Songkhla"

    st.markdown(f"""
    <div class="contact-section">

    <h3>📞 ติดต่อเรา</h3>

    <p>📱 081-222-2222</p>
    <p>💬 LINE : @222salon</p>
    <p>🔵 Facebook : 222 Salon</p>

    <a href="{map_link}" target="_blank"
    style="background:#FF4B4B;color:white;padding:12px 30px;border-radius:10px;text-decoration:none;font-weight:bold;">
    📍 ดูพิกัดร้านใน Google Maps
    </a>

    </div>
    """,unsafe_allow_html=True)

# ---------------- VIEW QUEUE ----------------
elif st.session_state.page=="ViewQueues":

    st.subheader("📅 รายการคิววันนี้")

    df=get_data("Bookings")

    today=datetime.now().strftime("%Y-%m-%d")

    if not df.empty:

        active=df[(df['date']==today)&(df['status']=="รอรับบริการ")]

        if not active.empty:

            st.write(f"🔔 มี {len(active)} คิว")

            st.table(active[['time','service','fullname']].sort_values("time"))

        else:

            st.info("ยังไม่มีคิววันนี้")

    else:

        st.info("ไม่มีข้อมูลการจอง")
