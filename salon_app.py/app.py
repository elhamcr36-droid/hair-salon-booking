import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ==========================
# ตั้งค่า Google Sheets
# ==========================

SPREADSHEET_ID = "1seP8Gg3uvUAPEK1Ejd9tAtYCmaduPt6Us7UEgHhMw4k"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(credentials)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1


# ==========================
# ตั้งค่าหน้าเว็บ
# ==========================

st.set_page_config(page_title="ระบบจองคิวร้านทำผม", page_icon="💇‍♀️")

st.title("💇‍♀️ ระบบจองคิวร้านทำผม")

menu = st.sidebar.selectbox(
    "เมนู",
    ["ลงชื่อจองคิว", "ดูข้อมูลการจอง"]
)

# ==========================
# หน้า ลงชื่อจองคิว
# ==========================

if menu == "ลงชื่อจองคิว":

    st.subheader("กรอกข้อมูลเพื่อจองคิว")

    name = st.text_input("ชื่อ")
    phone = st.text_input("เบอร์โทร")
    service = st.selectbox("บริการ", ["ตัดผม", "สระผม", "ทำสี", "ดัดผม"])
    date = st.date_input("วันที่")
    time = st.time_input("เวลา")
    detail = st.text_area("รายละเอียดเพิ่มเติม")

    if st.button("✅ ยืนยันการจอง"):

        if name and phone:
            sheet.append_row([
                name,
                phone,
                service,
                str(date),
                str(time),
                detail,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

            st.success("บันทึกการจองเรียบร้อยแล้ว ✅")
        else:
            st.error("กรุณากรอกชื่อและเบอร์โทร")

# ==========================
# หน้า ดูข้อมูลการจอง
# ==========================

elif menu == "ดูข้อมูลการจอง":

    st.subheader("🗑 ลบข้อมูลการจอง")

    data = sheet.get_all_values()

    if len(data) > 1:

        headers = data[0]
        rows = data[1:]

        import pandas as pd
        df = pd.DataFrame(rows, columns=headers)

        st.dataframe(df, use_container_width=True)

        # เลือกแถวที่จะลบ
        row_to_delete = st.number_input(
            "พิมพ์หมายเลขแถวที่ต้องการลบ (ดูจากลำดับในตาราง เริ่มที่ 1)",
            min_value=1,
            max_value=len(rows),
            step=1
        )

        if st.button("❌ ลบแถวที่เลือก"):
            sheet.delete_rows(row_to_delete + 1)  # +1 เพราะแถวแรกคือ header
            st.success("ลบข้อมูลเรียบร้อยแล้ว ✅")
            st.rerun()

    else:
        st.info("ยังไม่มีข้อมูลการจอง")


