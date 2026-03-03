import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# -------------------------
# เชื่อมต่อ Google Sheets
# -------------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open("Hair Salon Booking Data").sheet1

# -------------------------
# ตั้งค่าหน้าเว็บ
# -------------------------
st.set_page_config(page_title="Hair Salon Booking", layout="wide")

# -------------------------
# สร้างตัวเก็บข้อมูลชั่วคราว
# -------------------------
if 'bookings' not in st.session_state:
    st.session_state.bookings = []

# -------------------------
# Sidebar
# -------------------------
st.sidebar.title("💈 ร้านทำผม")
page = st.sidebar.radio("เลือกเมนู:", ["ลงชื่อจองคิว", "จัดการข้อมูลคิว"])

# =========================
# หน้า 1: ลงชื่อจองคิว
# =========================
if page == "ลงชื่อจองคิว":
    st.header("💇‍♀️ ลงทะเบียนจองคิวใหม่")

    with st.form(key='add_form', clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("ชื่อ-นามสกุล")
            phone = st.text_input("เบอร์โทรศัพท์")

        with col2:
            service = st.selectbox(
                "เลือกบริการ",
                ["ตัดผม", "สระ-ไดร์", "ทำสีผม", "ยืดผม/ดัดผม"]
            )
            date = st.date_input("เลือกวันที่")
            time = st.time_input("เลือกเวลา")

        note = st.text_area("รายละเอียดเพิ่มเติม")
        submit = st.form_submit_button("✅ ยืนยันการจอง")

        if submit:
            if name and phone:
                new_data = {
                    "ชื่อ": name,
                    "เบอร์โทร": phone,
                    "บริการ": service,
                    "วันที่": str(date),
                    "เวลา": str(time),
                    "หมายเหตุ": note
                }

                # บันทึกใน session
                st.session_state.bookings.append(new_data)

                # ✅ บันทึกลง Google Sheets
                sheet.append_row([
                    name,
                    phone,
                    service,
                    str(date),
                    str(time),
                    note
                ])

                st.success(f"บันทึกคิวคุณ {name} เรียบร้อยแล้ว! 🎉")
            else:
                st.warning("กรุณากรอกชื่อและเบอร์โทรให้ครบถ้วน")

# =========================
# หน้า 2: จัดการข้อมูล
# =========================
elif page == "จัดการข้อมูลคิว":
    st.header("📋 จัดการคิวลูกค้า")

    if not st.session_state.bookings:
        st.info("ยังไม่มีข้อมูลการจอง")
    else:
        df = pd.DataFrame(st.session_state.bookings)

        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "บริการ": st.column_config.SelectboxColumn(
                    options=["ตัดผม", "สระ-ไดร์", "ทำสีผม", "ยืดผม/ดัดผม"]
                )
            }
        )

        if st.button("💾 บันทึกการเปลี่ยนแปลงทั้งหมด"):
            st.session_state.bookings = edited_df.to_dict('records')
            st.success("อัปเดตข้อมูลในระบบเรียบร้อยแล้ว!")
            st.rerun()
