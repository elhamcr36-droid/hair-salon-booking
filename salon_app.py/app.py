import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import hashlib

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Smart Salon Booking",
    page_icon="✂️",
    layout="centered"
)

st.title("✂️ Smart Salon Booking System")

# ---------------- CONFIG ----------------

SPREADSHEET_ID = "1seP8Gg3uvUAPEK1Ejd9tAtYCmaduPt6Us7UEgHhMw4k"

ADMIN_USER = "admin222"
ADMIN_PASS = "admin222"

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

# ---------------- CREATE SHEET ----------------

def get_or_create_sheet(name, headers):

    try:
        sheet = spreadsheet.worksheet(name)

    except:

        sheet = spreadsheet.add_worksheet(
            title=name,
            rows="1000",
            cols="20"
        )

        sheet.append_row(headers)

    return sheet


sheet_users = get_or_create_sheet(
"users",
["username","password","phone"]
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

# ---------------- QUEUE GENERATOR ----------------

def generate_queue():

    df = load_bookings()

    if len(df) == 0:
        return "Q001"

    last = df.iloc[-1]["queue"]

    num = int(last.replace("Q","")) + 1

    return "Q"+str(num).zfill(3)

# ---------------- ADD USER ----------------

def add_user(username,password,phone):

    sheet_users.append_row([
        username,
        hash_password(password),
        phone
    ])

# ---------------- ADD BOOKING ----------------

def add_booking(user,service,date,time):

    bookings = load_bookings()

    same = bookings[
        (bookings["date"] == date) &
        (bookings["time"] == time)
    ]

    if len(same) > 0:
        return False

    queue = generate_queue()

    sheet_booking.append_row([
        queue,
        user,
        service,
        date,
        time,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ])

    return True

# ---------------- CANCEL ----------------

def cancel_booking(queue_id):

    cell = sheet_booking.find(queue_id)

    if cell:
        sheet_booking.delete_rows(cell.row)

# ---------------- UPDATE ----------------

def update_booking(queue_id,service,date,time):

    bookings = load_bookings()

    same = bookings[
        (bookings["date"] == date) &
        (bookings["time"] == time) &
        (bookings["queue"] != queue_id)
    ]

    if len(same) > 0:
        return False

    cell = sheet_booking.find(queue_id)

    if cell:

        row = cell.row

        sheet_booking.update_cell(row,3,service)
        sheet_booking.update_cell(row,4,date)
        sheet_booking.update_cell(row,5,time)

    return True

# ---------------- SESSION ----------------

if "login" not in st.session_state:

    st.session_state.login = False
    st.session_state.user = ""

# ---------------- LOGIN ----------------

def login():

    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Login"):

        if username == ADMIN_USER and password == ADMIN_PASS:

            st.session_state.login = True
            st.session_state.user = ADMIN_USER

            st.success("Admin Login สำเร็จ")
            st.rerun()

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

    st.subheader("📝 สมัครสมาชิก")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")
    phone = st.text_input("เบอร์โทร")

    if st.button("Register"):

        if username == ADMIN_USER:

            st.error("ไม่สามารถใช้ชื่อนี้ได้")
            return

        if phone == "":
            st.error("กรุณาใส่เบอร์โทร")
            return

        users = load_users()

        if len(users) > 0 and username in users["username"].values:

            st.error("Username นี้มีแล้ว")

        else:

            add_user(username,password,phone)

            st.success("สมัครสมาชิกสำเร็จ")

# ---------------- BOOKING ----------------

def booking():

    st.subheader("✂️ จองคิวทำผม")

    services = [

    "ตัดผมชาย","ตัดผมหญิง","สระผม","ไดร์ผม",
    "ย้อมผม","ดัดผม","ยืดผม","ทำสีแฟชั่น",
    "ไฮไลท์","ทรีทเมนต์","โกนหนวด",
    "สปาผม","บำรุงเส้นผม","ซอยผม",
    "ตัดหน้าม้า","ย้อมโคนผม",
    "ทำสีผมแฟชั่น","ดัดวอลลุ่ม",
    "ทรีทเมนต์เคราติน","รีบอนดิ้ง",
    "สปาหนังศีรษะ","ย้อมผมเทา"
    ]

    service = st.selectbox("เลือกบริการ",services)

    date = st.date_input("เลือกวันที่")

    if date < datetime.today().date():
        st.error("ไม่สามารถจองวันย้อนหลังได้")
        return

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

    st.subheader("📅 คิวของฉัน")

    df = load_bookings()

    df = df[df["user"] == st.session_state.user]

    if len(df) > 0:

        for i,row in df.iterrows():

            st.write("---")

            st.write("เลขคิว:",row["queue"])
            st.write("บริการ:",row["service"])
            st.write("วันที่:",row["date"])
            st.write("เวลา:",row["time"])

            if st.button("❌ ยกเลิก",key=row["queue"]):

                cancel_booking(row["queue"])

                st.success("ยกเลิกคิวแล้ว")
                st.rerun()

    else:

        st.info("ยังไม่มีคิว")

# ---------------- ADMIN ----------------

def admin_panel():

    st.subheader("🛠 Admin Panel")

    df = load_bookings()
    users = load_users()

    if len(df) == 0:
        st.info("ไม่มีข้อมูล")
        return

    df = df.merge(
        users,
        left_on="user",
        right_on="username",
        how="left"
    )

    for i,row in df.iterrows():

        st.write("---")

        st.write("เลขคิว:",row["queue"])
        st.write("ลูกค้า:",row["user"])
        st.write("เบอร์โทร:",row.get("phone","ไม่มี"))

        col1,col2 = st.columns(2)

        if col1.button("ลบ",key="del"+row["queue"]):

            cancel_booking(row["queue"])
            st.success("ลบคิวแล้ว")
            st.rerun()

# ---------------- SHOP INFO ----------------

def shop_info():

    st.subheader("🏪 ข้อมูลร้าน")

    st.write("📍 ร้าน Smart Salon")
    st.write("Songkhla Thailand")

    st.write("⏰ เวลาเปิด")
    st.write("10:00 - 19:00")

    st.map(pd.DataFrame({
        'lat':[7.1897],
        'lon':[100.5951]
    }))

# ---------------- MENU ----------------

if st.session_state.login:

    if st.session_state.user == ADMIN_USER:

        menu = st.sidebar.selectbox(
            "เมนู",
            [
            "จองคิว",
            "คิวของฉัน",
            "Admin Panel",
            "ข้อมูลร้าน",
            "Logout"
            ]
        )

    else:

        menu = st.sidebar.selectbox(
            "เมนู",
            [
            "จองคิว",
            "คิวของฉัน",
            "ข้อมูลร้าน",
            "Logout"
            ]
        )

    if menu == "จองคิว":
        booking()

    elif menu == "คิวของฉัน":
        my_queue()

    elif menu == "Admin Panel":
        admin_panel()

    elif menu == "ข้อมูลร้าน":
        shop_info()

    elif menu == "Logout":

        st.session_state.login = False
        st.rerun()

else:

    menu = st.selectbox(
        "เมนู",
        ["Login","Register"]
    )

    if menu == "Login":
        login()

    else:
        register()
