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
.stButton>button {width: 100%; border-radius: 10px; font-weight: bold; height: 3.2em;}
.price-card {
background-color:#ffffff;padding:18px;border-radius:12px;
border-left:6px solid #FF4B4B;margin-bottom:12px;
box-shadow:2px 4px 12px rgba(0,0,0,0.08);color:#000000;
}
.price-text {float:right;color:#FF4B4B;font-weight:bold;}
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet):
    try:
        df = conn.read(worksheet=sheet, ttl=0)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.dropna(how='all')
        df.columns=[str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- SESSION ---
if 'page' not in st.session_state:
    st.session_state.page="Home"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in=False

def navigate(p):
    st.session_state.page=p
    st.rerun()

# --- MENU ---
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
        if role=="admin":
            if st.button("📊 จัดการร้าน"):
                navigate("Admin")
        else:
            if st.button("✂️ จองคิว"):
                navigate("Booking")

    with m_cols[4]:
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.clear()
            navigate("Home")

st.divider()

# --- HOME ---
if st.session_state.page=="Home":

    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")
    st.info("⏰ ร้านเปิด 09:30 - 19:30 (หยุดเสาร์)")

# --- VIEW QUEUE ---
elif st.session_state.page=="ViewQueues":

    st.subheader("📅 คิววันนี้")

    df=get_data("Bookings")
    today=datetime.now().strftime("%Y-%m-%d")

    if not df.empty:

        active=df[(df['date']==today)&(df['status']=="รอรับบริการ")]

        if not active.empty:
            st.table(active[['time','service','fullname']])
        else:
            st.info("ยังไม่มีคิววันนี้")

# --- REGISTER ---
elif st.session_state.page=="Register":

    st.subheader("สมัครสมาชิก")

    with st.form("reg"):

        name=st.text_input("ชื่อ")
        phone=st.text_input("เบอร์")
        pw=st.text_input("รหัสผ่าน",type="password")
        pw2=st.text_input("ยืนยัน",type="password")

        if st.form_submit_button("สมัคร"):

            if pw==pw2:

                df=get_data("Users")

                new=pd.DataFrame([{
                    "phone":phone,
                    "password":pw,
                    "fullname":name,
                    "role":"user"
                }])

                conn.update(worksheet="Users",data=pd.concat([df,new],ignore_index=True))
                st.success("สมัครสำเร็จ")

# --- LOGIN ---
elif st.session_state.page=="Login":

    st.subheader("เข้าสู่ระบบ")

    u=st.text_input("เบอร์")
    p=st.text_input("รหัส",type="password")

    if st.button("เข้าสู่ระบบ"):

        if u=="admin222" and p=="222":

            st.session_state.logged_in=True
            st.session_state.user_role="admin"
            navigate("Admin")

        else:

            df=get_data("Users")

            user=df[(df['phone']==u)&(df['password']==p)]

            if not user.empty:

                st.session_state.logged_in=True
                st.session_state.user_role="user"
                st.session_state.username=u
                st.session_state.fullname=user.iloc[0]['fullname']

                navigate("Booking")

# --- BOOKING ---
elif st.session_state.page=="Booking":

    with st.form("book"):

        d=st.date_input("วันที่")
        t=st.selectbox("เวลา",["09:30","10:30","11:30","13:00","14:00","15:00","16:00","17:00"])
        s=st.selectbox("บริการ",["ตัดผมชาย","ตัดผมหญิง","ทำสี"])

        if st.form_submit_button("จอง"):

            df=get_data("Bookings")

            new=pd.DataFrame([{
                "id":str(uuid.uuid4())[:8],
                "username":st.session_state.username,
                "fullname":st.session_state.fullname,
                "date":str(d),
                "time":t,
                "service":s,
                "status":"รอรับบริการ",
                "price":0
            }])

            conn.update(worksheet="Bookings",data=pd.concat([df,new],ignore_index=True))

            st.success("จองสำเร็จ")

# --- ADMIN ---
elif st.session_state.page=="Admin":

    at1,at2=st.tabs(["📊 รายได้","📅 จัดการคิว"])

# --- REPORT ---
    with at1:

        df=get_data("Bookings")

        if not df.empty:

            df['price']=pd.to_numeric(df['price'],errors='coerce').fillna(0)

            total=df[df['status']=="เสร็จสิ้น"]['price'].sum()

            st.metric("รายได้รวม",f"{total:,.0f} บาท")

# --- MANAGE QUEUE ---
    with at2:

        df=get_data("Bookings")

        active=df[df['status']=="รอรับบริการ"]

        for _,row in active.iterrows():

            with st.container(border=True):

                st.write(f"{row['fullname']} | {row['date']} | {row['time']} | {row['service']}")

                price=st.number_input("ราคา",0,5000,key=f"p{row['id']}")

                c1,c2=st.columns(2)

                with c1:
                    if st.button("✅ เสร็จสิ้น",key=f"d{row['id']}"):

                        df.loc[df['id']==row['id'],'status']="เสร็จสิ้น"
                        df.loc[df['id']==row['id'],'price']=price

                        conn.update(worksheet="Bookings",data=df)

                        st.rerun()

                with c2:
                    if st.button("❌ ยกเลิก",key=f"c{row['id']}"):

                        df.loc[df['id']==row['id'],'status']="ยกเลิก"

                        conn.update(worksheet="Bookings",data=df)

                        st.rerun()
