import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import hashlib
import plotly.express as px

# ---------------- CONFIG ----------------

SPREADSHEET_ID = "ใส่_SPREADSHEET_ID"

scope = [
"https://www.googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
st.secrets["gcp_service_account"],
scopes=scope
)

client = gspread.authorize(creds)

spreadsheet = client.open_by_key(SPREADSHEET_ID)

users_sheet = spreadsheet.worksheet("users")
booking_sheet = spreadsheet.worksheet("bookings")

# ---------------- FUNCTIONS ----------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_users():
    data = users_sheet.get_all_records()
    return pd.DataFrame(data)

def get_bookings():
    data = booking_sheet.get_all_records()
    return pd.DataFrame(data)

def add_user(username,password):
    users_sheet.append_row([
        username,
        hash_password(password)
    ])

def add_booking(name,service,date,time,price):

    df = get_bookings()

    queue = len(df) + 1

    booking_sheet.append_row([
        queue,
        name,
        service,
        price,
        date,
        time,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ])

# ---------------- SERVICES ----------------

services = {
"ตัดผมชาย":120,
"ตัดผมหญิง":200,
"ตัดผมเด็ก":100,
"สระผม":80,
"ไดร์ผม":80,
"โกนหนวด":60,
"ซอยผม":150,
"เซ็ตผม":120,
"ดัดผม":800,
"ยืดผม":1200,
"ทำสีผม":1000,
"ฟอกสีผม":1200,
"ทรีทเม้นท์":500,
"สปาผม":400,
"อบไอน้ำ":300,
"ต่อผม":2000,
"ตัดหน้าม้า":50,
"สระ+ไดร์":150,
"ตัด+สระ":200,
"ตัด+สระ+เซ็ต":250,
"เคราติน":1500,
"ทำสีแฟชั่น":1800,
"ถักเปีย":200
}

# ---------------- SESSION ----------------

if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- LOGIN PAGE ----------------

if st.session_state.user is None:

    st.title("💈 ระบบจองคิวร้านทำผม")

    menu = st.selectbox(
    "เมนู",
    ["Login","Register"]
    )

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if menu == "Login":

        if st.button("Login"):

            users = get_users()

            if username in users["username"].values:

                pw = users.loc[
                users["username"]==username,
                "password"
                ].values[0]

                if pw == hash_password(password):

                    st.session_state.user = username
                    st.rerun()

                else:
                    st.error("Password incorrect")

            else:
                st.error("User not found")

    if menu == "Register":

        if st.button("Register"):

            add_user(username,password)

            st.success("Register success")

# ---------------- MAIN APP ----------------

else:

    st.sidebar.title("เมนู")

    menu = st.sidebar.radio(
    "เลือกเมนู",
    [
    "จองคิว",
    "ตารางคิว",
    "สถิติร้าน",
    "แผนที่ร้าน",
    "Logout"
    ]
    )

# ---------------- BOOKING ----------------

    if menu == "จองคิว":

        st.title("📅 จองคิวร้านทำผม")

        name = st.text_input("ชื่อลูกค้า")

        service = st.selectbox(
        "เลือกบริการ",
        list(services.keys())
        )

        date = st.date_input("วันที่")

        time = st.selectbox(
        "เวลา",
        [
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00"
        ]
        )

        price = services[service]

        st.write("ราคา:",price,"บาท")

        if st.button("ยืนยันการจอง"):

            add_booking(
            name,
            service,
            str(date),
            time,
            price
            )

            st.success("จองคิวสำเร็จ")

# ---------------- QUEUE TABLE ----------------

    elif menu == "ตารางคิว":

        st.title("📋 ตารางคิวลูกค้า")

        df = get_bookings()

        st.dataframe(df)

# ---------------- STATS ----------------

    elif menu == "สถิติร้าน":

        st.title("📊 สถิติร้าน")

        df = get_bookings()

        if len(df) > 0:

            total = df["price"].sum()

            st.metric(
            "รายได้รวม",
            f"{total} บาท"
            )

            fig = px.bar(
            df,
            x="service",
            title="บริการยอดนิยม"
            )

            st.plotly_chart(fig)

            fig2 = px.pie(
            df,
            names="service",
            title="สัดส่วนบริการ"
            )

            st.plotly_chart(fig2)

# ---------------- MAP ----------------

    elif menu == "แผนที่ร้าน":

        st.title("📍 ที่ตั้งร้าน")

        st.map(
        pd.DataFrame({
        "lat":[7.0084],
        "lon":[100.4747]
        })
        )

        st.write("📍 พิกัดร้าน: 7.0084 , 100.4747")

# ---------------- LOGOUT ----------------

    elif menu == "Logout":

        st.session_state.user = None
        st.rerun()
