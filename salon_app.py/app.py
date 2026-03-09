import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import hashlib

# ---------------- CONFIG ----------------

SPREADSHEET_ID = "ใส่_SPREADSHEET_ID_ของคุณ"

# ---------------- GOOGLE CONNECT ----------------

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

# ---------------- CREATE SHEET IF NOT EXIST ----------------

def get_or_create_sheet(name, headers):

    try:
        sheet = spreadsheet.worksheet(name)
    except:
        sheet = spreadsheet.add_worksheet(title=name, rows="1000", cols="20")
        sheet.append_row(headers)

    return sheet

sheet_users = get_or_create_sheet(
    "users",
    ["username","password"]
)

sheet_booking = get_or_create_sheet(
    "booking",
    ["queue","user","service","date","time","created"]
)

# ---------------- FUNCTIONS ----------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():

    data = sheet_users.get_all_records()

    return pd.DataFrame(data)

def load_bookings():

    data = sheet_booking.get_all_records()

    return pd.DataFrame(data)

def add_user(username,password):

    sheet_users.append_row([
        username,
        hash_password(password)
    ])

def add_booking(user,service,date,time):

    bookings = load_bookings()

    queue = len(bookings) + 1

    sheet_booking.append_row([
        queue,
        user,
        service,
        date,
        time,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ])

# ---------------- SESSION ----------------

if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.user = ""

# ---------------- LOGIN ----------------

def login():

    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        users = load_users()

        if len(users) > 0:

            user = users[
                (users["username"] == username) &
                (users["password"] == hash_password(password))
            ]

            if not user.empty:

                st.session_state.login = True
                st.session_state.user = username

                st.success("Login สำเร็จ")

                st.rerun()

        st.error("Username หรือ Password ไม่ถูกต้อง")

# ---------------- REGISTER ----------------

def register():

    st.title("📝 สมัครสมาชิก")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):

        add_user(username,password)

        st.success("สมัครสมาชิกสำเร็จ")

# ---------------- BOOKING ----------------

def booking():

    st.title("✂️ จองคิวทำผม")

    services = [

        "ตัดผมชาย",
        "ตัดผมหญิง",
        "สระผม",
        "ไดร์ผม",
        "ย้อมผม",
        "ดัดผม",
        "ยืดผม",
        "ทำสีแฟชั่น",
        "ไฮไลท์ผม",
        "ทรีทเมนต์",
        "โกนหนวด",
        "สปาผม",
        "บำรุงเส้นผม",
        "ซอยผม",
        "ตัดหน้าม้า",
        "ย้อมโคนผม"
    ]

    service = st.selectbox("เลือกบริการ", services)

    date = st.date_input("เลือกวันที่")

    time = st.selectbox(
        "เลือกเวลา",
        [
            "10:00","11:00","12:00",
            "13:00","14:00","15:00",
            "16:00","17:00","18:00"
        ]
    )

    if st.button("จองคิว"):

        add_booking(
            st.session_state.user,
            service,
            str(date),
            time
        )

        st.success("จองคิวสำเร็จ")

# ---------------- QUEUE ----------------

def queue():

    st.title("📅 คิวทั้งหมด")

    df = load_bookings()

    if len(df) > 0:

        st.dataframe(df)

    else:

        st.info("ยังไม่มีคิว")

# ---------------- MAP ----------------

def map_shop():

    st.title("📍 แผนที่ร้าน")

    df = pd.DataFrame({
        "lat":[7.0084],
        "lon":[100.4747]
    })

    st.map(df)

    st.write("พิกัดร้าน : 7.0084 , 100.4747")

# ---------------- SIDEBAR MENU ----------------

if st.session_state.login:

    st.sidebar.title("📋 เมนู")

    menu = st.sidebar.selectbox(
        "เลือกเมนู",
        [
            "จองคิว",
            "ดูคิว",
            "แผนที่ร้าน",
            "Logout"
        ]
    )

    if menu == "จองคิว":
        booking()

    elif menu == "ดูคิว":
        queue()

    elif menu == "แผนที่ร้าน":
        map_shop()

    elif menu == "Logout":

        st.session_state.login = False

        st.rerun()

else:

    st.sidebar.title("📋 Menu")

    menu = st.sidebar.selectbox(
        "เลือกเมนู",
        [
            "Login",
            "Register"
        ]
    )

    if menu == "Login":
        login()

    else:
        register()
