import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, time
import pandas as pd

# ==========================
# ตั้งค่า Google Sheets
# ==========================
SPREADSHEET_ID = "ใส่_spreadsheet_id_ของคุณ"

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
    ["ลงชื่อจองคิว", "จัดการข้อมูลการจอง", "รายงานสรุป"]
)

# ==========================
# ฟังก์ชันช่วย
# ==========================
def get_data():
    data = sheet.get_all_values()
    if len(data) > 1:
        return pd.DataFrame(data[1:], columns=data[0])
    return pd.DataFrame()

# ==========================
# หน้า ลงชื่อจองคิว
# ==========================
if menu == "ลงชื่อจองคิว":

    st.subheader("กรอกข้อมูลเพื่อจองคิว")

    name = st.text_input("ชื่อ")
    phone = st.text_input("เบอร์โทร")
    service = st.selectbox("บริการ", ["ตัดผม", "สระผม", "ทำสี", "ดัดผม"])
    date = st.date_input("วันที่")

    # จำกัดเวลา 08:30 - 17:30
    booking_time = st.time_input(
        "เวลา",
        value=time(8,30)
    )

    detail = st.text_area("รายละเอียดเพิ่มเติม")

    if st.button("✅ ยืนยันการจอง"):

        if not name or not phone:
            st.error("กรุณากรอกชื่อและเบอร์โทร")
        elif booking_time < time(8,30) or booking_time > time(17,30):
            st.error("เวลาจองต้องอยู่ระหว่าง 08:30 - 17:30")
        else:
            df = get_data()

            # ตรวจเวลาซ้ำ
            if not df.empty:
                duplicate = df[
                    (df["วันที่"] == str(date)) &
                    (df["เวลา"] == str(booking_time))
                ]

                if not duplicate.empty:
                    st.error("❌ เวลานี้มีคนจองแล้ว กรุณาเลือกเวลาอื่น")
                    st.stop()

            sheet.append_row([
                name,
                phone,
                service,
                str(date),
                str(booking_time),
                detail,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

            st.success("บันทึกการจองเรียบร้อยแล้ว ✅")

# ==========================
# หน้า จัดการข้อมูล
# ==========================
elif menu == "จัดการข้อมูลการจอง":

    st.subheader("📋 จัดการข้อมูล")

    df = get_data()

    if not df.empty:

        df.insert(0, "เลือก", False)

        edited_df = st.data_editor(df, use_container_width=True)

        # ลบ
        if st.button("🗑 ลบแถวที่เลือก"):
            rows_to_delete = edited_df[edited_df["เลือก"] == True]

            for index in sorted(rows_to_delete.index, reverse=True):
                sheet.delete_rows(index + 2)

            st.success("ลบเรียบร้อยแล้ว ✅")
            st.rerun()

        # แก้ไข
        selected = edited_df[edited_df["เลือก"] == True]

        if len(selected) == 1:
            index = selected.index[0]
            row = df.iloc[index]

            st.subheader("✏️ แก้ไขข้อมูล")

            new_name = st.text_input("ชื่อ", row["ชื่อ"])
            new_phone = st.text_input("เบอร์โทร", row["เบอร์โทร"])
            new_service = st.text_input("บริการ", row["บริการ"])
            new_date = st.text_input("วันที่", row["วันที่"])
            new_time = st.text_input("เวลา", row["เวลา"])
            new_detail = st.text_input("รายละเอียด", row["รายละเอียดเพิ่มเติม"])

            if st.button("💾 บันทึกการแก้ไข"):
                sheet.update(
                    f"A{index+2}:F{index+2}",
                    [[new_name, new_phone, new_service, new_date, new_time, new_detail]]
                )
                st.success("แก้ไขเรียบร้อยแล้ว ✅")
                st.rerun()

    else:
        st.info("ยังไม่มีข้อมูล")

# ==========================
# หน้า รายงานสรุป
# ==========================
elif menu == "รายงานสรุป":

    st.subheader("📊 รายงานสรุป")

    df = get_data()

    if not df.empty:

        df["วันที่"] = pd.to_datetime(df["วันที่"])

        # รายวัน
        st.markdown("### 📅 สรุปรายวัน")
        daily = df.groupby(df["วันที่"].dt.date).size()
        st.dataframe(daily)

        # รายเดือน
        st.markdown("### 📆 สรุปรายเดือน")
        monthly = df.groupby(df["วันที่"].dt.to_period("M")).size()
        st.dataframe(monthly)

    else:
        st.info("ยังไม่มีข้อมูลให้สรุป")
