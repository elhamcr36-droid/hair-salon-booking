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

        tab1,tab2,tab3,tab4=st.tabs([
        "เมนูบริการ",
        "จองคิว",
        "คิวของฉัน",
        "คิววันนี้"
        ])

# -------- SERVICE MENU --------

        with tab1:

            st.title("💇‍♀️ เมนูบริการ")

            st.markdown("### 👨 ผู้ชาย")
            st.write("✂️ ตัดผมชาย – เริ่มต้น 100 บาท")
            st.write("🧴 สระผมชาย – เริ่มต้น 60 บาท")
            st.write("🎨 ทำสีผมชาย – เริ่มต้น 400 บาท")

            st.markdown("### 👩 ผู้หญิง")
            st.write("✂️ ตัดผมหญิง – เริ่มต้น 150 บาท")
            st.write("🧴 สระ + ไดร์ – เริ่มต้น 120 บาท")
            st.write("🎨 ทำสี – เริ่มต้น 700 บาท")
            st.write("🌀 ดัดผม – เริ่มต้น 1200 บาท")
            st.write("💁‍♀️ ยืดผม – เริ่มต้น 1200 บาท")
            st.write("💆‍♀️ ทรีทเมนต์ – เริ่มต้น 300 บาท")

# -------- BOOKING --------

        with tab2:

            st.header("จองคิว")

            name=st.text_input("ชื่อ")
            phone=st.text_input("เบอร์โทร")

            service=st.selectbox("บริการ",[
            "ตัดผม",
            "สระผม",
            "ทำสี",
            "ดัดผม",
            "ยืดผม",
            "ทรีทเมนต์"
            ])

            date=st.date_input("วันที่")

            available=get_available_times(date)

            if available:

                booking_time=st.selectbox("เวลาที่ว่าง",available)

            else:

                st.error("วันนี้เต็มแล้ว")
                st.stop()

            detail=st.text_area("รายละเอียด")

            if st.button("ยืนยันการจอง"):

                latest=get_bookings()

                duplicate=latest[
                (latest["วันที่"]==str(date)) &
                (latest["เวลา"]==booking_time)
                ]

                if len(duplicate)>0:

                    st.error("❌ เวลานี้มีคนจองแล้ว")
                    st.stop()

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

                st.success(f"✅ จองคิวสำเร็จ คิวที่ {queue}")
                st.rerun()

# -------- MY BOOKINGS --------

        with tab3:

            st.subheader("คิวของฉัน")

            my=df[df["username"]==username]

            if not my.empty:

                st.dataframe(my)

            else:

                st.info("ยังไม่มีการจอง")

# -------- TODAY --------

        with tab4:

            today=datetime.today().strftime("%Y-%m-%d")

            today_df=df[df["วันที่"]==today]

            st.subheader("คิววันนี้")

            if not today_df.empty:

                st.dataframe(today_df)

            else:

                st.info("วันนี้ยังไม่มีคิว")

# ---------------- ADMIN ----------------

    if role=="admin":

        tab1,tab2=st.tabs(["Dashboard","จัดการการจอง"])

        with tab1:

            st.title("Admin Dashboard")

            users=get_users()
            customers=users[users["username"]!="admin222"]

            col1,col2,col3=st.columns(3)

            col1.metric("การจองทั้งหมด",len(df))
            col2.metric("ลูกค้า",len(customers))

            today=datetime.today().strftime("%Y-%m-%d")

            today_df=df[df["วันที่"]==today]

            col3.metric("คิววันนี้",len(today_df))

            st.divider()

# -------- REVENUE --------

            prices={
            "ตัดผม":120,
            "สระผม":80,
            "ทำสี":700,
            "ดัดผม":1200,
            "ยืดผม":1200,
            "ทรีทเมนต์":300
            }

            if not df.empty:

                df["ราคา"]=df["บริการ"].map(prices)

                revenue=df.groupby("วันที่")["ราคา"].sum().reset_index()

                fig=px.bar(
                revenue,
                x="วันที่",
                y="ราคา",
                title="📊 รายได้รายวัน"
                )

                st.plotly_chart(fig)

# -------- POPULAR SERVICE --------

                st.subheader("⭐ บริการยอดนิยม")

                popular=df["บริการ"].value_counts().reset_index()

                popular.columns=["บริการ","จำนวน"]

                st.dataframe(popular)

# -------- CALENDAR --------

                st.subheader("📅 ปฏิทินคิว")

                calendar=df.groupby("วันที่").size().reset_index(name="จำนวนคิว")

                st.dataframe(calendar)

        with tab2:

            if not df.empty:

                edited=st.data_editor(df,num_rows="dynamic")

                if st.button("บันทึก"):

                    booking_sheet.clear()
                    booking_sheet.append_row(list(df.columns))

                    for i,row in edited.iterrows():

                        booking_sheet.append_row(row.tolist())

                    st.success("บันทึกสำเร็จ")

            else:

                st.info("ยังไม่มีข้อมูล")
