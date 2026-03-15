import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="222-Salon",
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

/* ติดต่อร้าน */
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

def get_data(sheet):

    try:
        df = conn.read(worksheet=sheet, ttl=0)

        if df is None or df.empty:
            return pd.DataFrame()

        df = df.dropna(how="all")
        df.columns = [str(c).strip().lower() for c in df.columns]

        return df

    except:
        return pd.DataFrame()

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

menu = st.columns(5)

with menu[0]:
    if st.button("🏠 หน้าแรก"):
        navigate("Home")

with menu[1]:
    if st.button("📅 คิววันนี้"):
        navigate("Queue")

if not st.session_state.logged_in:

    with menu[3]:
        if st.button("📝 สมัครสมาชิก"):
            navigate("Register")

    with menu[4]:
        if st.button("🔑 เข้าสู่ระบบ"):
            navigate("Login")

else:

    role = st.session_state.get("user_role")

    with menu[2]:

        if role=="admin":

            if st.button("📊 จัดการร้าน"):
                navigate("Admin")

        else:

            if st.button("✂️ จองคิว"):
                navigate("Booking")

    with menu[4]:

        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")

st.divider()

# ---------------- HOME ----------------
if st.session_state.page=="Home":

    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1200")

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

    c1,c2=st.columns(2)

    for i,(name,price) in enumerate(services.items()):

        col=c1 if i%2==0 else c2

        col.markdown(
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
elif st.session_state.page=="Queue":

    st.subheader("📅 คิววันนี้")

    df=get_data("Bookings")

    today=datetime.now().strftime("%Y-%m-%d")

    if not df.empty:

        active=df[(df['date']==today)&(df['status']=="รอรับบริการ")]

        if not active.empty:

            st.table(active[['time','service','fullname']].sort_values("time"))

        else:

            st.info("ยังไม่มีคิววันนี้")

    else:

        st.info("ไม่มีข้อมูล")

# ---------------- REGISTER ----------------
elif st.session_state.page=="Register":

    st.subheader("สมัครสมาชิก")

    with st.form("reg"):

        name=st.text_input("ชื่อ")

        phone=st.text_input("เบอร์")

        pw=st.text_input("รหัสผ่าน",type="password")

        pw2=st.text_input("ยืนยันรหัสผ่าน",type="password")

        if st.form_submit_button("สมัคร"):

            if pw!=pw2:

                st.error("รหัสผ่านไม่ตรงกัน")

            else:

                df=get_data("Users")

                new=pd.DataFrame([{
                "phone":phone,
                "password":pw,
                "fullname":name,
                "role":"user"
                }])

                conn.update(
                worksheet="Users",
                data=pd.concat([df,new],ignore_index=True)
                )

                st.success("สมัครสำเร็จ")
                navigate("Login")

# ---------------- LOGIN ----------------
elif st.session_state.page=="Login":

    st.subheader("เข้าสู่ระบบ")

    phone=st.text_input("เบอร์")

    pw=st.text_input("รหัสผ่าน",type="password")

    if st.button("เข้าสู่ระบบ"):

        if phone=="admin222" and pw=="222":

            st.session_state.logged_in=True
            st.session_state.user_role="admin"

            navigate("Admin")

        else:

            df=get_data("Users")

            user=df[(df['phone']==phone)&(df['password']==pw)]

            if not user.empty:

                st.session_state.logged_in=True
                st.session_state.user_role="user"
                st.session_state.username=phone
                st.session_state.fullname=user.iloc[0]['fullname']

                navigate("Booking")

            else:

                st.error("ข้อมูลไม่ถูกต้อง")

# ---------------- BOOKING ----------------
elif st.session_state.page=="Booking":

    st.subheader("จองคิว")

    with st.form("booking"):

        d=st.date_input("วันที่")

        t=st.selectbox("เวลา",
        ["09:30","10:30","11:30","13:00","14:00","15:00","16:00","17:00","18:00"])

        s=st.selectbox("บริการ",
        ["ตัดผมชาย","ตัดผมหญิง","สระไดร์","ทำสีผม","ยืดดัด","ทรีทเม้นท์"])

        if st.form_submit_button("จองคิว"):

            df=get_data("Bookings")

            new=pd.DataFrame([{
            "id":str(uuid.uuid4())[:8],
            "username":st.session_state.username,
            "fullname":st.session_state.fullname,
            "date":str(d),
            "time":t,
            "service":s,
            "status":"รอรับบริการ",
            "price":"0"
            }])

            conn.update(
            worksheet="Bookings",
            data=pd.concat([df,new],ignore_index=True))

            st.success("จองคิวสำเร็จ")

# ---------------- ADMIN ----------------
elif st.session_state.page=="Admin":

    st.subheader("จัดการคิวร้าน")

    df=get_data("Bookings")

    if not df.empty:

        q=df[df['status']=="รอรับบริการ"]

        for i,row in q.iterrows():

            st.write(row['fullname'],row['date'],row['time'],row['service'])

            if st.button("เสร็จสิ้น",key=row['id']):

                df.loc[df['id']==row['id'],'status']="เสร็จสิ้น"

                conn.update(worksheet="Bookings",data=df)

                st.rerun()
