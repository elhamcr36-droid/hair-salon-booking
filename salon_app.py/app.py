import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
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

sheet = spreadsheet.worksheet("Sheet1")

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
page_title="Hair Salon Booking",
page_icon="💈",
layout="wide"
)

st.title("💈 ระบบจองคิวร้านทำผม")

# ---------------- SERVICE MENU ----------------

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
"สระผมสมุนไพร":150,
"บำรุงหนังศีรษะ":350,
"เคราตินผม":1500,
"รีบอนดิ้ง":1800,
"ต่อผมถาวร":3000,
"ต่อผมชั่วคราว":1500,
"ทำสีไฮไลท์":1200,
"ทำสีออมเบร":1500,
"ย้อมผมแฟชั่น":1800,
"เซ็ตผมออกงาน":500,
"ถักเปีย":200,
"ถักเปียแฟชั่น":400
}

# ---------------- LOAD DATA ----------------

def load_data():

    data = sheet.get_all_records()

    df = pd.DataFrame(data)

    return df

df = load_data()

# ---------------- BOOKING SYSTEM ----------------

st.header("📅 จองคิว")

col1,col2 = st.columns(2)

with col1:

    name = st.text_input("ชื่อลูกค้า")

    service = st.selectbox(
    "เลือกบริการ",
    list(services.keys())
    )

with col2:

    date = st.date_input("เลือกวันที่")

    time = st.selectbox(
    "เลือกเวลา",
    [
    "10:00","10:30",
    "11:00","11:30",
    "12:00","12:30",
    "13:00","13:30",
    "14:00","14:30",
    "15:00","15:30",
    "16:00","16:30",
    "17:00","17:30",
    "18:00"
    ]
    )

if st.button("📌 จองคิว"):

    queue = len(df)+1

    price = services[service]

    sheet.append_row([
        queue,
        name,
        service,
        price,
        str(date),
        time,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ])

    st.success(f"จองสำเร็จ เลขคิวของคุณคือ {queue}")

# ---------------- TODAY QUEUE ----------------

st.header("📋 คิววันนี้")

if not df.empty:

    today = str(datetime.today().date())

    today_df = df[df["date"]==today]

    st.dataframe(today_df)

else:

    st.info("ยังไม่มีข้อมูลคิว")

# ---------------- CALENDAR VIEW ----------------

st.header("📅 ตารางคิวทั้งหมด")

if not df.empty:

    st.dataframe(df)

# ---------------- POPULAR SERVICE ----------------

st.header("⭐ บริการยอดนิยม")

if not df.empty:

    pop = df["service"].value_counts().reset_index()

    pop.columns=["service","count"]

    fig = px.bar(
    pop,
    x="service",
    y="count",
    title="บริการยอดนิยม"
    )

    st.plotly_chart(fig,use_container_width=True)

# ---------------- REVENUE DASHBOARD ----------------

st.header("📊 รายได้ร้าน")

if not df.empty:

    revenue = df.groupby("date")["price"].sum().reset_index()

    fig2 = px.line(
    revenue,
    x="date",
    y="price",
    title="รายได้รายวัน"
    )

    st.plotly_chart(fig2,use_container_width=True)

# ---------------- MAP ----------------

st.header("📍 แผนที่ร้าน")

map_data = pd.DataFrame({

"lat":[7.0086],
"lon":[100.4747]

})

st.map(map_data)

st.success("📍 ร้านตั้งอยู่ในหาดใหญ่")

# ---------------- FOOTER ----------------

st.markdown("---")

st.caption("Hair Salon Booking System")
