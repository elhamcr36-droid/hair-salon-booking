import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import hashlib
import plotly.express as px

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

# ---------------- SERVICES ----------------

services = {
"Haircut":150,
"Hair Wash":80,
"Hair Color":500,
"Hair Straightening":1000,
"Hair Spa":600,
"Beard Trim":120
}

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
        st.success("Login success")
    else:
        st.error("Login failed")

# ---------------- QUEUE ----------------

def generate_queue():

    bookings = load_bookings()

    if len(bookings)==0:
        return "Q001"

    last = bookings.iloc[-1]["queue"]

    number = int(last[1:])+1

    return "Q"+str(number).zfill(3)

# ---------------- BOOK ----------------

def book(service,date,time):

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

    st.success(f"Booked! Your queue is {queue}")

# ---------------- LOGIN PAGE ----------------

def login_page():

    st.title("💈 Hair Salon Booking")

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

    service = st.selectbox("Service",list(services.keys()))

    date = st.date_input("Date")

    time = st.selectbox("Time",[
    "10:00","11:00","12:00","13:00",
    "14:00","15:00","16:00","17:00"
    ])

    if st.button("Book Now"):
        book(service,date,time)

    st.divider()

    st.subheader("📍 Shop Location")

    st.markdown(
    "[Open Google Maps](https://maps.google.com)"
    )

    st.subheader("📞 Call Shop")

    st.markdown("[Call 0812345678](tel:0812345678)")

# ---------------- ADMIN PAGE ----------------

def admin_page():

    st.title("🛠 Admin Dashboard")

    bookings = load_bookings()

    st.subheader("All Bookings")
    st.dataframe(bookings)

    if len(bookings)>0:

        total = bookings["price"].sum()

        st.metric("Total Revenue",total)

        fig = px.bar(
        bookings,
        x="service",
        y="price",
        title="Revenue by Service"
        )

        st.plotly_chart(fig)

# ---------------- MAIN ----------------

if "user" not in st.session_state:
    login_page()

else:

    if st.session_state.role=="admin":
        admin_page()
    else:
        user_page()

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
