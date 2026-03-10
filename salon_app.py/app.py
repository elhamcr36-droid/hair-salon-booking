import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import hashlib

# ---------------- CONFIG ----------------

SPREADSHEET_ID = "YOUR_SPREADSHEET_ID"

scope = [
"https://spreadsheets.google.com/feeds",
"https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
st.secrets["gcp_service_account"],
scopes=scope
)

client = gspread.authorize(credentials)

sheet_users = client.open_by_key(SPREADSHEET_ID).worksheet("users")
sheet_bookings = client.open_by_key(SPREADSHEET_ID).worksheet("bookings")

# ---------------- UTILS ----------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    data = sheet_users.get_all_records()
    return pd.DataFrame(data)

def load_bookings():
    data = sheet_bookings.get_all_records()
    return pd.DataFrame(data)

def next_queue():

    df = load_bookings()

    if len(df) == 0:
        return "Q001"

    last = df.iloc[-1]["queue"]
    num = int(last.replace("Q","")) + 1

    return f"Q{num:03d}"

# ---------------- LOGIN ----------------

def login():

    st.title("✂️ Smart Salon Booking")

    menu = ["Login","Register"]
    choice = st.selectbox("Menu",menu)

    if choice == "Login":

        username = st.text_input("Username")
        password = st.text_input("Password",type="password")

        if st.button("Login"):

            df = load_users()

            user = df[
            (df["username"]==username) &
            (df["password"]==hash_password(password))
            ]

            if len(user)>0:

                st.session_state.user = username
                st.session_state.role = user.iloc[0]["role"]

                st.success("Login success")
                st.rerun()

            else:
                st.error("Login failed")

    if choice == "Register":

        username = st.text_input("Username")
        password = st.text_input("Password",type="password")
        phone = st.text_input("Phone")

        if st.button("Register"):

            sheet_users.append_row([
            username,
            hash_password(password),
            phone,
            "customer"
            ])

            st.success("Register success")

# ---------------- BOOKING ----------------

def booking_page():

    st.subheader("✂️ จองคิวร้านทำผม")

    services = [
    "ตัดผม",
    "สระผม",
    "ย้อมผม",
    "ดัดผม",
    "ยืดผม",
    "ทำสีผม",
    "ทรีทเมนต์"
    ]

    service = st.selectbox("บริการ",services)

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
    "17:00"
    ])

    if st.button("จองคิว"):

        queue = next_queue()

        sheet_bookings.append_row([
        queue,
        st.session_state.user,
        service,
        str(date),
        time
        ])

        st.success(f"จองสำเร็จ เลขคิว {queue}")

# ---------------- MY QUEUE ----------------

def my_queue():

    st.subheader("📅 คิวของฉัน")

    df = load_bookings()

    df = df[df["user"]==st.session_state.user]

    st.dataframe(df,use_container_width=True)

# ---------------- CALENDAR ----------------

def booking_calendar():

    st.subheader("📅 ปฏิทินคิวร้าน")

    df = load_bookings()

    if len(df)==0:
        st.info("ยังไม่มีคิว")
        return

    df["datetime"]=pd.to_datetime(df["date"]+" "+df["time"])

    df = df.sort_values("datetime")

    st.dataframe(df,use_container_width=True)

# ---------------- ADMIN ----------------

def admin_panel():

    st.title("✂️ Admin Panel")

    df = load_bookings()

    for i,row in df.iterrows():

        col1,col2,col3,col4,col5 = st.columns(5)

        col1.write(row["queue"])
        col2.write(row["user"])
        col3.write(row["service"])
        col4.write(row["date"]+" "+row["time"])

        if col5.button("ลบ",key="del"+str(row["queue"])):

            sheet_bookings.delete_rows(i+2)
            st.rerun()

# ---------------- SHOP CONTACT ----------------

def shop_contact():

    st.subheader("📍 ติดต่อร้าน")

    lat = 7.1897
    lon = 100.5951
    phone = "0999999999"

    st.write("🏪 Smart Salon")

    location = pd.DataFrame({
    "lat":[lat],
    "lon":[lon]
    })

    st.map(location)

    col1,col2,col3 = st.columns(3)

    with col1:

        st.link_button(
        "📞 โทรหาร้าน",
        f"tel:{phone}"
        )

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

# ---------------- MAIN ----------------

def main():

    if "user" not in st.session_state:
        login()
        return

    menu = [
    "จองคิว",
    "คิวของฉัน",
    "ปฏิทินคิว",
    "ติดต่อร้าน",
    "Logout"
    ]

    if st.session_state.role=="admin":
        menu.insert(3,"Admin")

    choice = st.sidebar.selectbox("Menu",menu)

    if choice=="จองคิว":
        booking_page()

    elif choice=="คิวของฉัน":
        my_queue()

    elif choice=="ปฏิทินคิว":
        booking_calendar()

    elif choice=="Admin":
        admin_panel()

    elif choice=="ติดต่อร้าน":
        shop_contact()

    elif choice=="Logout":

        del st.session_state["user"]
        st.rerun()

# ---------------- RUN ----------------

main()
