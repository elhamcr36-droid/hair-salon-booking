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

    st.subheader("📋 จัดการข้อมูลการจอง")

    data = sheet.get_all_values()

    if len(data) > 1:

        headers = data[0]
        rows = data[1:]

        import pandas as pd
        df = pd.DataFrame(rows, columns=headers)

        # เพิ่มคอลัมน์เลือก
        df.insert(0, "เลือก", False)

        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="fixed"
        )

        # -------------------
        # ลบ
        # -------------------
        if st.button("🗑 ลบแถวที่เลือก"):
            rows_to_delete = edited_df[edited_df["เลือก"] == True]

            if not rows_to_delete.empty:
                for index in sorted(rows_to_delete.index, reverse=True):
                    sheet.delete_rows(index + 2)

                st.success("ลบข้อมูลเรียบร้อยแล้ว ✅")
                st.rerun()
            else:
                st.warning("กรุณาเลือกแถวที่ต้องการลบ")

        st.divider()

        # -------------------
        # แก้ไข
        # -------------------
        selected_rows = edited_df[edited_df["เลือก"] == True]

        if len(selected_rows) == 1:

            index = selected_rows.index[0]
            row_data = rows[index]

            st.subheader("✏️ แก้ไขข้อมูล")

            name = st.text_input("ชื่อ", value=row_data[0])
            phone = st.text_input("เบอร์โทร", value=row_data[1])
            service = st.text_input("บริการ", value=row_data[2])
            date = st.text_input("วันที่", value=row_data[3])
            time = st.text_input("เวลา", value=row_data[4])
            detail = st.text_input("รายละเอียด", value=row_data[5])

            if st.button("💾 บันทึกการแก้ไข"):
                sheet.update(
                    f"A{index+2}:F{index+2}",
                    [[name, phone, service, date, time, detail]]
                )
                st.success("แก้ไขข้อมูลเรียบร้อยแล้ว ✅")
                st.rerun()

        elif len(selected_rows) > 1:
            st.warning("เลือกได้ครั้งละ 1 แถวเพื่อแก้ไข")

    else:
        st.info("ยังไม่มีข้อมูลการจอง")


