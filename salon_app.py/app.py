import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import plotly.express as px

# ---------------- CONFIG ----------------

SPREADSHEET_ID = "1seP8Gg3uvUAPEK1Ejd9tAtYCmaduPt6Us7UEgHhMw4k"

scope = [
"https://www.googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
st.secrets["gcp_service_account"],
scopes=scope
)

client = gspread.authorize(credentials)

spreadsheet = client.open_by_key(SPREADSHEET_ID)

booking_sheet = spreadsheet.worksheet("bookings")
users_sheet = spreadsheet.worksheet("users")

st.set_page_config(page_title="222 Salon",page_icon="💇‍♀️")

# ---------------- UI STYLE ----------------

st.markdown("""
<style>

.stApp{
background-color:#0f172a;
color:white;
}

div[data-testid="metric-container"]{
background-color:#1e293b;
padding:20px;
border-radius:10px;
}

.stButton>button{
background:#6366f1;
color:white;
border-radius:8px;
height:40px;
}

</style>
""",unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_users():

    data = users_sheet.get_all_values()

    if not data:
        return pd.DataFrame(columns=["username","password"])

    headers=data[0]

    if len(data)==1:
        return pd.DataFrame(columns=headers)

    return pd.DataFrame(data[1:],columns=headers)

def get_bookings():

    data=booking_sheet.get_all_values()

    if not data:
        return pd.DataFrame()

    headers=data[0]

    if len(data)==1:
        return pd.DataFrame(columns=headers)

    return pd.DataFrame(data[1:],columns=headers)

# -------- TIME SLOT --------

def generate_times():

    times=[]

    start=datetime.strptime("08:30","%H:%M")
    end=datetime.strptime("17:30","%H:%M")

    current=start

    while current<=end:

        times.append(current.strftime("%H:%M"))
        current+=timedelta(minutes=30)

    return times

def get_available_times(date):

    df=get_bookings()

    all_times=generate_times()

    if df.empty:
        return all_times

    day=df[df["วันที่"]==str(date)]

    booked=day["เวลา"].tolist()

    return [t for t in all_times if t not in booked]

# -------- QUEUE --------

def generate_queue(date):

    df=get_bookings()

    if df.empty:
        return 1

    day=df[df["วันที่"]==str(date)]

    if day.empty:
        return 1

    return len(day)+1

# ---------------- SESSION ----------------

if "login" not in st.session_state:
    st.session_state.login=False

# ---------------- LOGIN ----------------

if not st.session_state.login:

    st.title("💇‍♀️ 222 Salon Booking")

    username=st.text_input("Username")
    password=st.text_input("Password",type="password")

    if st.button("เข้าสู่ระบบ"):

        if username=="admin222" and password=="admin222":

            st.session_state.login=True
            st.session_state.role="admin"
            st.session_state.username="admin"
            st.rerun()

        df=get_users()

        user=df[df["username"]==username]

        if not user.empty:

            if user.iloc[0]["password"]==hash_password(password):

                st.session_state.login=True
                st.session_state.role="customer"
                st.session_state.username=username
                st.rerun()

            else:
                st.error("รหัสผ่านผิด")

        else:
            st.error("ไม่พบผู้ใช้")

    st.divider()

    st.subheader("สมัครสมาชิก")

    new_user=st.text_input("Username ใหม่")
    new_pass=st.text_input("Password ใหม่",type="password")

    if st.button("สมัครสมาชิก"):

        df=get_users()

        if new_user in df["username"].values:

            st.error("Username นี้มีแล้ว")

        else:

            users_sheet.append_row([
            new_user,
            hash_password(new_pass)
            ])

            st.success("สมัครสมาชิกสำเร็จ")

# ---------------- AFTER LOGIN ----------------

else:

    role=st.session_state.role
    username=st.session_state.username

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

    df=get_bookings()

# ---------------- CUSTOMER ----------------

    if role=="customer":

        tab1,tab2,tab3,tab4,tab5=st.tabs([
        "เมนูบริการ",
        "จองคิว",
        "คิวของฉัน",
        "คิววันนี้",
        "แผนที่ร้าน"
        ])

# -------- SERVICE MENU --------

        with tab1:

            st.title("💇‍♀️ เมนูบริการ")

            st.write("✂️ ตัดผมชาย – 120")
            st.write("✂️ ตัดผมหญิง – 150")
            st.write("✂️ ตัดผมเด็ก – 100")
            st.write("🧴 สระ + ไดร์ – 120")
            st.write("🎨 ทำสี – 700")
            st.write("🌀 ดัดผม – 1200")
            st.write("💁‍♀️ ยืดผม – 1200")
            st.write("💆‍♀️ ทรีทเมนต์ – 300")

# -------- BOOKING --------

        with tab2:

            st.header("จองคิว")

            name=st.text_input("ชื่อ")
            phone=st.text_input("เบอร์โทร")

            service=st.selectbox("บริการ",[
            "ตัดผมชาย",
            "ตัดผมหญิง",
            "ตัดผมเด็ก",
            "สระ + ไดร์",
            "ทำสี",
            "ดัดผม",
            "ยืดผม",
            "ทรีทเมนต์"
            ])

            date=st.date_input("วันที่")

            available=get_available_times(date)

            booking_time=st.selectbox("เวลา",available)

            detail=st.text_area("รายละเอียด")

            if st.button("ยืนยันการจอง"):

                queue=generate_queue(date)

                booking_sheet.append_row([
                queue,
                username,
                name,
                phone,
                service,
                str(date),
                booking_time,
                detail,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])

                st.success(f"จองสำเร็จ คิวที่ {queue}")
                st.rerun()

# -------- MY BOOKINGS --------

        with tab3:

            my=df[df["username"]==username]

            st.dataframe(my)

# -------- TODAY --------

        with tab4:

            today=datetime.today().strftime("%Y-%m-%d")

            today_df=df[df["วันที่"]==today]

            st.dataframe(today_df)

# -------- MAP + GPS --------

        with tab5:

            st.title("📍 พิกัดร้าน 222 Salon")

            shop_lat=7.0086
            shop_lon=100.4747

            map_data=pd.DataFrame({
            "lat":[shop_lat],
            "lon":[shop_lon]
            })

            st.map(map_data)

            st.subheader("นำทางไปที่ร้าน")

            maps_url=f"https://www.google.com/maps?q={shop_lat},{shop_lon}"

            st.markdown(f"[🧭 เปิด Google Maps]({maps_url})")

# ---------------- ADMIN ----------------

    if role=="admin":

        tab1,tab2=st.tabs(["Dashboard","จัดการคิว"])

        with tab1:

            st.title("Admin Dashboard")

            col1,col2=st.columns(2)

            col1.metric("การจองทั้งหมด",len(df))

            today=datetime.today().strftime("%Y-%m-%d")

            today_df=df[df["วันที่"]==today]

            col2.metric("คิววันนี้",len(today_df))

            prices={
            "ตัดผมชาย":120,
            "ตัดผมหญิง":150,
            "ตัดผมเด็ก":100,
            "สระ + ไดร์":120,
            "ทำสี":700,
            "ดัดผม":1200,
            "ยืดผม":1200,
            "ทรีทเมนต์":300
            }

            if not df.empty:

                df["ราคา"]=df["บริการ"].map(prices).fillna(0).astype(int)

                revenue=df.groupby("วันที่")["ราคา"].sum().reset_index()

                fig=px.bar(
                revenue,
                x="วันที่",
                y="ราคา",
                title="รายได้รายวัน"
                )

                st.plotly_chart(fig)

        with tab2:

            if not df.empty:

                edited=st.data_editor(df)

                if st.button("บันทึก"):

                    booking_sheet.clear()
                    booking_sheet.append_row(list(df.columns))

                    for i,row in edited.iterrows():
                        booking_sheet.append_row(row.tolist())

                    st.success("บันทึกสำเร็จ")
