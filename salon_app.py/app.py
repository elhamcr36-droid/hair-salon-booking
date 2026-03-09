import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import hashlib

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

st.set_page_config(page_title="222 Salon", page_icon="💇‍♀️")

# ---------------- FUNCTIONS ----------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_users():

    data = users_sheet.get_all_values()

    if not data:
        return pd.DataFrame(columns=["username","password"])

    headers = data[0]

    if len(data) == 1:
        return pd.DataFrame(columns=headers)

    df = pd.DataFrame(data[1:], columns=headers)
    return df


def get_bookings():

    data = booking_sheet.get_all_values()

    if not data:
        return pd.DataFrame()

    headers = data[0]

    if len(data) == 1:
        return pd.DataFrame(columns=headers)

    df = pd.DataFrame(data[1:], columns=headers)
    return df


def generate_times():

    times = []

    start = datetime.strptime("08:30","%H:%M")
    end = datetime.strptime("17:30","%H:%M")

    current = start

    while current <= end:

        times.append(current.strftime("%H:%M"))

        current += timedelta(minutes=30)

    return times


def get_available_times(date):

    df = get_bookings()

    all_times = generate_times()

    if df.empty:
        return all_times

    day = df[df["วันที่"] == str(date)]

    booked = day["เวลา"].tolist()

    available = [t for t in all_times if t not in booked]

    return available


# -------- CHECK DUPLICATE (กันจองซ้ำ) --------

def check_duplicate(date,time):

    df = get_bookings()

    if df.empty:
        return False

    duplicate = df[
        (df["วันที่"] == str(date)) &
        (df["เวลา"] == time)
    ]

    if len(duplicate) > 0:
        return True

    return False


# ---------------- SESSION ----------------

if "login" not in st.session_state:
    st.session_state.login = False

if "go_booking" not in st.session_state:
    st.session_state.go_booking = False


# ---------------- LOGIN ----------------

if not st.session_state.login:

    st.title("💇‍♀️ 222 Salon")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("เข้าสู่ระบบ"):

        if username=="admin222" and password=="admin222":

            st.session_state.login=True
            st.session_state.role="admin"
            st.session_state.username="admin"
            st.rerun()

        df=get_users()

        user=df[df["username"]==username]

        if not user.empty:

            stored=user.iloc[0]["password"]

            if stored==hash_password(password):

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


# ---------------- SERVICE MENU ----------------

        with tab1:

            st.title("💇‍♀️ เมนูบริการ Salon")

            col1,col2,col3=st.columns(3)

            with col1:
                with st.container(border=True):

                    st.markdown("## ✂️ ตัดผม")
                    st.markdown("### 💰 120 บาท")

                    if st.button("จองคิวทันที",key="cut"):
                        st.session_state.go_booking=True
                        st.rerun()


            with col2:
                with st.container(border=True):

                    st.markdown("## 🧴 สระ + ไดร์")
                    st.markdown("### 💰 80 บาท")

                    if st.button("จองคิวทันที",key="wash"):
                        st.session_state.go_booking=True
                        st.rerun()


            with col3:
                with st.container(border=True):

                    st.markdown("## 🎨 ทำสีผม")
                    st.markdown("### 💰 600 บาท")

                    if st.button("จองคิวทันที",key="color"):
                        st.session_state.go_booking=True
                        st.rerun()


# ---------------- BOOKING ----------------

        with tab2:

            st.header("จองคิว")

            name=st.text_input("ชื่อ")
            phone=st.text_input("เบอร์โทร")

            service=st.selectbox(
            "บริการ",
            ["ตัดผม","สระผม","ทำสี","ดัดผม"]
            )

            date=st.date_input("วันที่")

            available=get_available_times(date)

            if available:

                booking_time=st.selectbox(
                "เวลาที่ว่าง",
                available
                )

            else:

                st.error("วันนี้เต็มแล้ว")
                st.stop()


            detail=st.text_area("รายละเอียด")

            if st.button("ยืนยันการจอง"):

                if check_duplicate(date,booking_time):

                    st.error("❌ เวลานี้มีคนจองแล้ว")
                    st.stop()

                booking_sheet.append_row([

                username,
                name,
                phone,
                service,
                str(date),
                booking_time,
                detail,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                ])

                st.success("✅ จองคิวสำเร็จ")
                st.rerun()


# ---------------- MY BOOKINGS ----------------

        with tab3:

            st.subheader("คิวของฉัน")

            my=df[df["username"]==username]

            if not my.empty:

                st.dataframe(my.drop(columns=["username"]))

            else:

                st.info("ยังไม่มีการจอง")


# ---------------- TODAY ----------------

        with tab4:

            today=datetime.today().strftime("%Y-%m-%d")

            today_df=df[df["วันที่"]==today]

            st.subheader("คิววันนี้")

            if not today_df.empty:

                st.dataframe(today_df.drop(columns=["username"]))

            else:

                st.info("วันนี้ยังไม่มีคิว")


# ---------------- ADMIN ----------------

    if role=="admin":

        tab1,tab2=st.tabs(["Dashboard","จัดการการจอง"])


        with tab1:

            st.title("Admin Dashboard")

            col1,col2,col3=st.columns(3)

            col1.metric("การจองทั้งหมด",len(df))
            col2.metric("ลูกค้า",len(get_users()))

            today=datetime.today().strftime("%Y-%m-%d")

            today_df=df[df["วันที่"]==today]

            col3.metric("คิววันนี้",len(today_df))

            st.dataframe(df)


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
