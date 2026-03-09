import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, time
import pandas as pd
import hashlib

# --------------------------
# Google Sheets Config
# --------------------------

SPREADSHEET_ID = "ใส่ไอดีชีทของคุณ"

scope = [
"https://www.googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
st.secrets["gcp_service_account"],
scopes=scope
)

client = gspread.authorize(credentials)

booking_sheet = client.open_by_key(SPREADSHEET_ID).worksheet("bookings")
users_sheet = client.open_by_key(SPREADSHEET_ID).worksheet("users")

# --------------------------
# Page
# --------------------------

st.set_page_config(page_title="222Salon", page_icon="💇‍♀️")

# --------------------------
# Helper
# --------------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_bookings():
    data = booking_sheet.get_all_values()
    if len(data) > 1:
        return pd.DataFrame(data[1:], columns=data[0])
    return pd.DataFrame()

def get_users():
    data = users_sheet.get_all_values()
    if len(data) > 1:
        return pd.DataFrame(data[1:], columns=data[0])
    return pd.DataFrame()

# --------------------------
# Session
# --------------------------

if "login" not in st.session_state:
    st.session_state.login = False

# --------------------------
# LOGIN PAGE
# --------------------------

if not st.session_state.login:

    menu = st.sidebar.selectbox(
    "เมนู",
    ["เข้าสู่ระบบ","สมัครสมาชิก"]
    )

    st.title("💇‍♀️ 222Salon")

    # ----------------------
    # REGISTER
    # ----------------------

    if menu == "สมัครสมาชิก":

        st.subheader("สมัครสมาชิก")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("สมัครสมาชิก"):

            df = get_users()

            if username in df["username"].values:
                st.error("Username นี้มีแล้ว")
            else:
                users_sheet.append_row([
                username,
                hash_password(password)
                ])

                st.success("สมัครสมาชิกสำเร็จ")

    # ----------------------
    # LOGIN
    # ----------------------

    if menu == "เข้าสู่ระบบ":

        st.subheader("เข้าสู่ระบบ")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            # ADMIN LOGIN
            if username == "admin222" and password == "admin222":

                st.session_state.login = True
                st.session_state.role = "admin"
                st.session_state.username = "admin"

                st.rerun()

            df = get_users()

            user = df[df["username"] == username]

            if not user.empty:

                stored_password = user.iloc[0]["password"]

                if stored_password == hash_password(password):

                    st.session_state.login = True
                    st.session_state.role = "customer"
                    st.session_state.username = username

                    st.rerun()

                else:
                    st.error("รหัสผ่านผิด")

            else:
                st.error("ไม่พบผู้ใช้")

# --------------------------
# AFTER LOGIN
# --------------------------

else:

    role = st.session_state.role
    username = st.session_state.username

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    df = get_bookings()

# --------------------------
# CUSTOMER PAGE
# --------------------------

    if role == "customer":

        menu = st.sidebar.selectbox(
        "เมนู",
        ["จองคิว","คิวของฉัน","คิววันนี้"]
        )

        st.title("💇‍♀️ ระบบจองคิวร้านทำผม")

        # ----------------------
        # BOOKING
        # ----------------------

        if menu == "จองคิว":

            name = st.text_input("ชื่อ")
            phone = st.text_input("เบอร์โทร")

            service = st.selectbox(
            "บริการ",
            ["ตัดผม","สระผม","ทำสี","ดัดผม"]
            )

            date = st.date_input("วันที่")

            booking_time = st.time_input(
            "เวลา",
            value=time(8,30)
            )

            detail = st.text_area("รายละเอียด")

            if st.button("ยืนยันการจอง"):

                if booking_time < time(8,30) or booking_time > time(17,30):
                    st.error("เวลาต้องอยู่ 08:30 - 17:30")

                else:

                    if not df.empty:

                        duplicate = df[
                        (df["วันที่"] == str(date)) &
                        (df["เวลา"] == str(booking_time))
                        ]

                        if not duplicate.empty:
                            st.error("เวลานี้มีคนจองแล้ว")
                            st.stop()

                    booking_sheet.append_row([

                    username,
                    name,
                    phone,
                    service,
                    str(date),
                    str(booking_time),
                    detail,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    ])

                    st.success("จองคิวสำเร็จ")

        # ----------------------
        # MY QUEUE
        # ----------------------

        if menu == "คิวของฉัน":

            my = df[df["username"] == username]

            st.subheader("คิวของฉัน")

            st.dataframe(my)

        # ----------------------
        # TODAY
        # ----------------------

        if menu == "คิววันนี้":

            today = datetime.today().strftime("%Y-%m-%d")

            today_df = df[df["วันที่"] == today]

            st.subheader("คิววันนี้")

            st.dataframe(today_df)

# --------------------------
# ADMIN PAGE
# --------------------------

    if role == "admin":

        menu = st.sidebar.selectbox(
        "เมนู",
        ["Dashboard","จัดการการจอง"]
        )

        st.title("👑 Admin Panel")

        # ----------------------
        # DASHBOARD
        # ----------------------

        if menu == "Dashboard":

            col1,col2,col3 = st.columns(3)

            col1.metric("การจองทั้งหมด", len(df))

            col2.metric("ลูกค้า", len(get_users()))

            today = datetime.today().strftime("%Y-%m-%d")

            today_df = df[df["วันที่"] == today]

            col3.metric("คิววันนี้", len(today_df))

        # ----------------------
        # MANAGE BOOKINGS
        # ----------------------

        if menu == "จัดการการจอง":

            if not df.empty:

                df.insert(0,"เลือก",False)

                edited = st.data_editor(df)

                if st.button("ลบแถวที่เลือก"):

                    rows = edited[edited["เลือก"]==True]

                    for index in sorted(rows.index, reverse=True):
                        booking_sheet.delete_rows(index+2)

                    st.success("ลบสำเร็จ")
                    st.rerun()

            else:

                st.info("ยังไม่มีข้อมูล")
