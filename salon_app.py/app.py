import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import hashlib
import plotly.express as px

# ---------------- CONFIG ----------------

SPREADSHEET_ID = "1seP8Gg3uvUAPEK1Ejd9tAtYCmaduPt6Us7UEgHhMw4k"

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

    same = bookings[
        (bookings["date"] == date) &
        (bookings["time"] == time)
    ]

    if len(same) > 0:
        return False

    queue = len(bookings) + 1

    sheet_booking.append_row([
        queue,
        user,
        service,
        date,
        time,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ])

    return True

def cancel_booking(queue_id):

    cell = sheet_booking.find(str(queue_id))

    if cell:
        sheet_booking.delete_rows(cell.row)

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

        users = load_users()

        if username in users["username"].values:

            st.error("Username นี้มีแล้ว")

        else:

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

        success = add_booking(
            st.session_state.user,
            service,
            str(date),
            time
        )

        if success:
            st.success("จองคิวสำเร็จ")
        else:
            st.error("เวลานี้มีคนจองแล้ว")

# ---------------- MY QUEUE ----------------

def my_queue():

    st.title("📅 คิวของฉัน")

    df = load_bookings()

    df = df[df["user"] == st.session_state.user]

    if len(df) > 0:

        for i,row in df.iterrows():

            col1,col2,col3,col4 = st.columns(4)

            col1.write(row["service"])
            col2.write(row["date"])
            col3.write(row["time"])

            if col4.button("ยกเลิก",key=row["queue"]):

                cancel_booking(row["queue"])

                st.success("ยกเลิกคิวแล้ว")

                st.rerun()

    else:

        st.info("ยังไม่มีคิว")

# ---------------- ADMIN PANEL ----------------

def admin_panel():

    st.title("🛠 Admin Panel")

    df = load_bookings()

    if len(df) == 0:
        st.info("ไม่มีข้อมูล")
        return

    user_filter = st.selectbox(
        "เลือกลูกค้า",
        ["ทั้งหมด"] + list(df["user"].unique())
    )

    if user_filter != "ทั้งหมด":

        df = df[df["user"] == user_filter]

    for i,row in df.iterrows():

        col1,col2,col3,col4,col5 = st.columns(5)

        col1.write(row["user"])
        col2.write(row["service"])
        col3.write(row["date"])
        col4.write(row["time"])

        if col5.button("ลบ",key="del"+str(row["queue"])):

            cancel_booking(row["queue"])

            st.success("ลบคิวแล้ว")

            st.rerun()

# ---------------- MAP ----------------

def map_shop():

    st.title("📍 แผนที่ร้าน")

    df = pd.DataFrame({
        "lat":[7.0084],
        "lon":[100.4747]
    })

    st.map(df)

    st.write("พิกัดร้าน : 7.0084 , 100.4747")

# ---------------- MENU TOP ----------------

if st.session_state.login:

    if st.session_state.user == "admin":

        menu = st.selectbox(
            "เมนู",
            [
                "จองคิว",
                "คิวของฉัน",
                "Admin Panel",
                "แผนที่ร้าน",
                "Logout"
            ]
        )

    else:

        menu = st.selectbox(
            "เมนู",
            [
                "จองคิว",
                "คิวของฉัน",
                "แผนที่ร้าน",
                "Logout"
            ]
        )

    if menu == "จองคิว":
        booking()

    elif menu == "คิวของฉัน":
        my_queue()

    elif menu == "Admin Panel":
        admin_panel()

    elif menu == "แผนที่ร้าน":
        map_shop()

    elif menu == "Logout":

        st.session_state.login = False
        st.rerun()

else:

    menu = st.selectbox(
        "เมนู",
        [
            "Login",
            "Register"
        ]
    )

    if menu == "Login":
        login()
    else:
        register()
