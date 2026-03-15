import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time

--- CONFIG ---

st.set_page_config(page_title="222-Salon-Final", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""

""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

---------------- FUNCTIONS ----------------

def get_data(sheet_name):
try:
df = conn.read(worksheet=sheet_name, ttl=0)

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.dropna(how='all')
    df.columns = [str(c).strip().lower() for c in df.columns]

    for col in df.columns:
        df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan','')

        if 'phone' in col or 'username' in col:
            df[col] = df[col].apply(lambda x: '0'+x if len(x)==9 and x.isdigit() else x)

    return df

except:
    return pd.DataFrame()

def get_new_msg_count():
df = get_data("Messages")

if not df.empty:
    return len(df[df['admin_reply']==""])

return 0

def get_new_booking_count():
df = get_data("Bookings")

if not df.empty:
    return len(df[df['status']=="รอรับบริการ"])

return 0
---------------- SESSION ----------------

if 'page' not in st.session_state:
st.session_state.page = "Home"

if 'logged_in' not in st.session_state:
st.session_state.logged_in = False

def navigate(p):
st.session_state.page = p
st.rerun()

---------------- MENU ----------------

st.markdown("✂️ 222-Salon", unsafe_allow_html=True)

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

    if role == "admin":

        new_msg = get_new_msg_count()
        new_book = get_new_booking_count()

        alert = "🔴" if new_msg > 0 or new_book > 0 else ""

        if st.button(f"📊 จัดการร้าน {alert}"):
            navigate("Admin")

    else:

        if st.button("✂️ จองคิว"):
            navigate("Booking")

with m_cols[4]:
    if st.button("🚪 ออกจากระบบ"):
        st.session_state.clear()
        navigate("Home")

st.divider()

---------------- HOME ----------------

if st.session_state.page == "Home":

st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")

st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (หยุดทุกวันเสาร์)")

st.subheader("📋 บริการและราคา")

services = {
    "✂️ ตัดผมชาย": "150-350",
    "💇‍♀️ ตัดผมหญิง": "350-800",
    "🚿 สระ-ไดร์": "200-450",
    "🎨 ทำสีผม": "1500+",
    "✨ ยืด/ดัด": "1000+",
    "🌿 ทรีทเม้นท์": "500+"
}

p1, p2 = st.columns(2)

for i, (name, price) in enumerate(services.items()):
    target = p1 if i % 2 == 0 else p2
    target.markdown(f"<div class='price-card'><b>{name}</b><span class='price-text'>{price} บ.</span></div>", unsafe_allow_html=True)

st.divider()

map_link = "https://www.google.com/maps/search/?api=1&query=222+Tesaban+1+Alley+Songkhla"

st.markdown(f"""
<div class="contact-section">
<h3>📞 ติดต่อเรา</h3>
📱 081-222-2222 | LINE : @222salon | Facebook : 222 Salon
<br><br>
<a href="{map_link}" target="_blank">📍 ดูแผนที่ร้าน</a>
</div>
""", unsafe_allow_html=True)
---------------- VIEW QUEUE ----------------

elif st.session_state.page == "ViewQueues":

st.subheader("📅 รายการคิววันนี้")

placeholder = st.empty()

df_today = get_data("Bookings")
today = datetime.now().strftime("%Y-%m-%d")

with placeholder.container():

    if not df_today.empty:

        active = df_today[(df_today['date'] == today) & (df_today['status'] == "รอรับบริการ")]

        if not active.empty:

            st.write(f"🔔 มีคิวทั้งหมด {len(active)} คิว")

            st.table(active[['time','service','fullname']].sort_values('time'))

        else:

            st.info("ยังไม่มีคิววันนี้")

time.sleep(30)
st.rerun()
---------------- REGISTER ----------------

elif st.session_state.page == "Register":

st.subheader("สมัครสมาชิก")

with st.form("reg"):

    nf = st.text_input("ชื่อ")
    nu = st.text_input("เบอร์โทร")
    np = st.text_input("รหัสผ่าน", type="password")
    npc = st.text_input("ยืนยันรหัส", type="password")

    if st.form_submit_button("สมัคร"):

        if nu and np == npc:

            df = get_data("Users")

            if not df.empty and nu in df['phone'].values:
                st.error("เบอร์นี้ถูกใช้แล้ว")

            else:

                new = pd.DataFrame([{
                    "phone":nu,
                    "password":np,
                    "fullname":nf,
                    "role":"user"
                }])

                conn.update(worksheet="Users", data=pd.concat([df,new], ignore_index=True))

                st.success("สมัครสำเร็จ")
                navigate("Login")
---------------- LOGIN ----------------

elif st.session_state.page == "Login":

st.subheader("เข้าสู่ระบบ")

u = st.text_input("เบอร์โทร")
p = st.text_input("รหัสผ่าน", type="password")

if st.button("ตกลง"):

    if u == "admin222" and p == "222":

        st.session_state.update({
            "logged_in":True,
            "user_role":"admin",
            "username":u,
            "fullname":"Admin"
        })

        navigate("Admin")

    else:

        df = get_data("Users")

        user = df[(df['phone']==u) & (df['password']==p)] if not df.empty else pd.DataFrame()

        if not user.empty:

            st.session_state.update({
                "logged_in":True,
                "user_role":"user",
                "username":u,
                "fullname":user.iloc[0]['fullname']
            })

            navigate("Booking")

        else:
            st.error("ข้อมูลไม่ถูกต้อง")
