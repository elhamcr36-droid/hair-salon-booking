import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import hashlib
from streamlit_calendar import calendar

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Smart Salon Booking",
    page_icon="✂️",
    layout="centered"
)

st.title("✂️ 222-Salon")

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

def get_or_create_sheet(name,headers):

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


# ---------------- QUEUE AUTO ----------------

def generate_queue():

    df = load_bookings()

    if len(df) == 0:
        return "Q001"

    last = df.iloc[-1]["queue"]

    num = int(last.replace("Q","")) + 1

    return "Q"+str(num).zfill(3)


# ---------------- USER ----------------

def add_user(username,password,phone):

    sheet_users.append_row([
        username,
        hash_password(password),
        phone
    ])


# ---------------- BOOKING ----------------

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


def cancel_booking(queue):

    cell = sheet_booking.find(queue)

    if cell:
        sheet_booking.delete_rows(cell.row)


# ---------------- SESSION ----------------

if "login" not in st.session_state:

    st.session_state.login = False
    st.session_state.user = ""


# ---------------- LOGIN ----------------

def login():

    st.subheader("🔐 Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if username == ADMIN_USER and password == ADMIN_PASS:

            st.session_state.login = True
            st.session_state.user = ADMIN_USER

            st.success("Admin Login")
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

        st.error("Login ไม่ถูกต้อง")


# ---------------- REGISTER ----------------

def register():

    st.subheader("📝 Register")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    phone = st.text_input("Phone")

    if st.button("Register"):

        users = load_users()

        if len(users) > 0 and username in users["username"].values:

            st.error("Username ซ้ำ")

        else:

            add_user(username,password,phone)

            st.success("สมัครสมาชิกสำเร็จ")


# ---------------- BOOKING PAGE ----------------

def booking():

    st.subheader("✂️ จองคิว")

    services = [
    "ตัดผมชาย","ตัดผมหญิง","สระผม","ไดร์ผม",
    "ย้อมผม","ดัดผม","ยืดผม","ไฮไลท์",
    "ทำสีแฟชั่น","ทรีทเมนต์","โกนหนวด",
    "สปาผม","บำรุงเส้นผม","ซอยผม",
    "ตัดหน้าม้า","ย้อมโคนผม"
    ]

    service = st.selectbox("บริการ",services)

    date = st.date_input("วันที่")

    if date < datetime.today().date():

        st.error("ห้ามจองย้อนหลัง")
        return

    time = st.selectbox(
        "เวลา",
        [
        "10:00","11:00","12:00",
        "13:00","14:00","15:00",
        "16:00","17:00","18:00"
        ]
    )

    if st.button("จองคิว"):

        ok = add_booking(
            st.session_state.user,
            service,
            str(date),
            time
        )

        if ok:
            st.success("จองคิวสำเร็จ")

        else:
            st.error("เวลานี้มีคนจองแล้ว")


# ---------------- MY QUEUE ----------------

def my_queue():

    st.subheader("📅 คิวของฉัน")

    df = load_bookings()

    df = df[df["user"] == st.session_state.user]

    if len(df) == 0:

        st.info("ไม่มีคิว")

        return

    for i,row in df.iterrows():

        st.write("---")

        st.write("เลขคิว:",row["queue"])
        st.write("บริการ:",row["service"])
        st.write("วันที่:",row["date"])
        st.write("เวลา:",row["time"])

        if st.button("ยกเลิก",key="cancel"+str(row["queue"])):

            cancel_booking(row["queue"])

            st.success("ยกเลิกแล้ว")
            st.rerun()


# ---------------- CALENDAR ----------------

def booking_calendar():

    st.subheader("📅 ปฏิทินคิว")

    df = load_bookings()

    events = []

    for i,row in df.iterrows():

        events.append({
            "title": row["service"]+"-"+row["user"],
            "start": row["date"]+"T"+row["time"]
        })

    calendar(
        events=events,
        options={
            "initialView":"dayGridMonth",
            "height":600
        }
    )


# ---------------- CONTACT / MAP ----------------

def shop_contact():

    st.subheader("📍 ติดต่อร้าน 222-Salon")

    lat = 7.1897
    lon = 100.5951
    phone = "0999999999"

    st.write("🏪 Smart Salon")
    st.write("📍 Songkhla Thailand")

    location = pd.DataFrame({
        "lat":[lat],
        "lon":[lon]
    })

    st.map(location)

    col1,col2,col3 = st.columns(3)

    with col1:
        st.link_button("📞 โทรหาร้าน",f"tel:{phone}")

    with col2:
        st.link_button(
            "🧭 นำทางมาร้าน",
            f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
        )

    with col3:
        st.link_button(
            "🗺 เปิด Google Maps",
            f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        )


# ---------------- ADMIN QUEUE ----------------

def admin_panel():

    st.subheader("🛠 Admin Panel")

    df = load_bookings()

    users = load_users()

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
        st.write("เบอร์:",row.get("phone",""))

        if st.button("ลบ",key="del"+str(row["queue"])):

            cancel_booking(row["queue"])

            st.success("ลบแล้ว")
            st.rerun()


# ---------------- ADMIN USERS ----------------

def admin_users():

    st.subheader("👥 จัดการลูกค้า")

    users = load_users()

    for i,row in users.iterrows():

        st.write("---")

        st.write("Username:",row["username"])

        phone = st.text_input(
            "Phone",
            value=row["phone"],
            key="phone"+row["username"]
        )

        col1,col2 = st.columns(2)

        if col1.button("บันทึก",key="save"+row["username"]):

            cell = sheet_users.find(row["username"])

            if cell:

                sheet_users.update_cell(cell.row,3,phone)

                st.success("แก้ไขแล้ว")
                st.rerun()

        if col2.button("ลบ",key="deluser"+row["username"]):

            cell = sheet_users.find(row["username"])

            if cell:

                sheet_users.delete_rows(cell.row)

                st.success("ลบลูกค้าแล้ว")
                st.rerun()


# ---------------- MENU ----------------

if st.session_state.login:

    if st.session_state.user == ADMIN_USER:

        menu = st.sidebar.selectbox(
            "Menu",
            [
            "จองคิว",
            "คิวของฉัน",
            "ปฏิทินคิว",
            "Admin Panel",
            "จัดการลูกค้า",
            "ติดต่อร้าน",
            "Logout"
            ]
        )

    else:

        menu = st.sidebar.selectbox(
            "Menu",
            [
            "จองคิว",
            "คิวของฉัน",
            "ปฏิทินคิว",
            "ติดต่อร้าน",
            "Logout"
            ]
        )

    if menu == "จองคิว":
        booking()

    elif menu == "คิวของฉัน":
        my_queue()

    elif menu == "ปฏิทินคิว":
        booking_calendar()

    elif menu == "Admin Panel":
        admin_panel()

    elif menu == "จัดการลูกค้า":
        admin_users()

    elif menu == "ติดต่อร้าน":
        shop_contact()

    elif menu == "Logout":

        st.session_state.login = False
        st.rerun()

else:

    menu = st.selectbox(
        "Menu",
        ["Login","Register"]
    )

    if menu == "Login":
        login()

    else:
        register()

