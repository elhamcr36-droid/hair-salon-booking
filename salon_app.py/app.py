import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import hashlib
import plotly.express as px


# ---------------- CONFIG ----------------

SPREADSHEET_ID = "1seP8Gg3uvUAPEK1Ejd9tAtYCmaduPt6Us7UEgHhMw4k"

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

# ---------------- SERVICES ----------------

services = {
"Haircut":150,
"Hair Wash":80,
"Hair Color":500,
"Hair Straightening":1000,
"Hair Spa":600,
"Beard Trim":120,
"Head Massage":200,
"Keratin Treatment":1500
}

timeslots = [
"10:00","11:00","12:00","13:00",
"14:00","15:00","16:00","17:00"
]

# ---------------- PASSWORD HASH ----------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- LOAD DATA ----------------

def load_users():
    data = sheet_users.get_all_records()
    return pd.DataFrame(data)

def load_bookings():
    data = sheet_bookings.get_all_records()
    return pd.DataFrame(data)

# ---------------- REGISTER ----------------

def register(username,password):

    users = load_users()

    if username in users["username"].values:
        st.error("User already exists")
        return

    sheet_users.append_row([
        username,
        hash_password(password),
        "user"
    ])

    st.success("Register success")

# ---------------- LOGIN ----------------

def login(username,password):

    users = load_users()

    user = users[
        (users["username"]==username) &
        (users["password"]==hash_password(password))
    ]

    if len(user)>0:
        st.session_state.user=username
        st.session_state.role=user.iloc[0]["role"]
        st.rerun()
    else:
        st.error("Login failed")

# ---------------- GENERATE QUEUE ----------------

def generate_queue():

    bookings = load_bookings()

    if len(bookings)==0:
        return "Q001"

    last = bookings.iloc[-1]["queue"]
    num = int(last[1:]) + 1

    return "Q"+str(num).zfill(3)

# ---------------- CHECK TIME ----------------

def time_available(date,time):

    bookings = load_bookings()

    same = bookings[
        (bookings["date"]==str(date)) &
        (bookings["time"]==time)
    ]

    return len(same)==0

# ---------------- BOOK ----------------

def book(service,date,time):

    if not time_available(date,time):
        st.error("Time slot already booked")
        return

    queue = generate_queue()

    price = services[service]

    sheet_bookings.append_row([
        queue,
        st.session_state.user,
        service,
        str(date),
        time,
        price
    ])

    st.success(f"Booking successful! Your queue is {queue}")

# ---------------- DELETE BOOKING ----------------

def delete_booking(queue):

    data = sheet_bookings.get_all_records()

    for i,row in enumerate(data):

        if row["queue"] == queue:

            sheet_bookings.delete_rows(i+2)

            st.success("Booking deleted")

            st.rerun()

# ---------------- UPDATE BOOKING ----------------

def update_booking(queue,new_service,new_date,new_time):

    data = sheet_bookings.get_all_records()

    for i,row in enumerate(data):

        if row["queue"] == queue:

            price = services[new_service]

            sheet_bookings.update(
                f"C{i+2}:F{i+2}",
                [[new_service,str(new_date),new_time,price]]
            )

            st.success("Booking updated")

            st.rerun()

# ---------------- LOGIN PAGE ----------------

def login_page():

    st.title("💈 Hair Salon Booking System")

    menu = st.radio("Menu",["Login","Register"])

    username = st.text_input("Username")

    password = st.text_input("Password",type="password")

    if menu=="Login":

        if st.button("Login"):
            login(username,password)

    if menu=="Register":

        if st.button("Register"):
            register(username,password)

# ---------------- USER PAGE ----------------

def user_page():

    st.title("📅 Book Appointment")

    service = st.selectbox(
        "Service",
        list(services.keys())
    )

    date = st.date_input("Select Date")

    time = st.selectbox(
        "Select Time",
        timeslots
    )

    price = services[service]

    st.info(f"Price : {price} บาท")

    if st.button("Book Now"):
        book(service,date,time)

    st.divider()

    st.subheader("📍 Shop Location")

    st.markdown(
    "[Open Google Maps](https://maps.google.com/?q=7.0086,100.4747)"
    )

    st.subheader("📞 Call Shop")

    st.markdown("[Call 0812345678](tel:0812345678)")

# ---------------- ADMIN PAGE ----------------

def admin_page():

    st.title("🛠 Admin Dashboard")

    bookings = load_bookings()

    if len(bookings)==0:
        st.warning("No bookings")
        return

    st.subheader("All Bookings")

    st.dataframe(bookings)

    st.divider()

    queue_list = bookings["queue"].tolist()

    selected_queue = st.selectbox(
        "Select Queue",
        queue_list
    )

    booking = bookings[
        bookings["queue"]==selected_queue
    ].iloc[0]

    st.subheader("Edit Booking")

    new_service = st.selectbox(
        "Service",
        list(services.keys()),
        index=list(services.keys()).index(booking["service"])
    )

    new_date = st.date_input(
        "Date",
        pd.to_datetime(booking["date"])
    )

    new_time = st.selectbox(
        "Time",
        timeslots,
        index=timeslots.index(booking["time"])
    )

    col1,col2 = st.columns(2)

    with col1:
        if st.button("Update Booking"):
            update_booking(
                selected_queue,
                new_service,
                new_date,
                new_time
            )

    with col2:
        if st.button("Delete Booking"):
            delete_booking(selected_queue)

    st.divider()

    st.subheader("📊 Revenue Dashboard")

    total = bookings["price"].sum()

    st.metric("Total Revenue",total)

    fig = px.bar(
        bookings,
        x="service",
        y="price",
        title="Revenue by Service"
    )

    st.plotly_chart(fig)

    popular = bookings["service"].value_counts()

    fig2 = px.pie(
        names=popular.index,
        values=popular.values,
        title="Popular Services"
    )

    st.plotly_chart(fig2)

# ---------------- MAIN ----------------

if "user" not in st.session_state:

    login_page()

else:

    st.sidebar.write("Logged in as:",st.session_state.user)

    if st.session_state.role=="admin":

        admin_page()

    else:

        user_page()

    if st.sidebar.button("Logout"):

        st.session_state.clear()

        st.rerun()




