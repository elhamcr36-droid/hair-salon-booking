import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Hair Salon Booking", layout="wide")

# สร้างตัวเก็บข้อมูลจำลอง (Session State)
if 'bookings' not in st.session_state:
    st.session_state.bookings = []

# ส่วนของ Sidebar
st.sidebar.title("💈 ร้านทำผม222")
page = st.sidebar.radio("เลือกเมนู:", ["ลงชื่อจองคิว", "จัดการข้อมูลคิว"])

# --- หน้าที่ 1: การลงชื่อจองคิว ---
if page == "ลงชื่อจองคิว":
    st.header("💇‍♀️ ลงทะเบียนจองคิวใหม่")
    
    with st.form(key='add_form', clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("ชื่อ-นามสกุล")
            phone = st.text_input("เบอร์โทรศัพท์")
        with col2:
            service = st.selectbox("เลือกบริการ", ["ตัดผม", "สระ-ไดร์", "ทำสีผม", "ยืดผม/ดัดผม"])
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
                st.session_state.bookings.append(new_data)
                st.success(f"บันทึกคิวคุณ {name} เรียบร้อย!")
            else:
                st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")

# --- หน้าที่ 2: จัดการข้อมูลในตาราง (Edit & Delete) ---
elif page == "จัดการข้อมูลคิว":
    st.header("📋 จัดการคิวลูกค้า")
    st.write("💡 คุณสามารถ **ดับเบิลคลิกในช่อง** เพื่อแก้ไขข้อมูลได้ทันที")

    if not st.session_state.bookings:
        st.info("ยังไม่มีข้อมูลการจอง")
    else:
        # 1. แปลงข้อมูลเป็น DataFrame
        df = pd.DataFrame(st.session_state.bookings)

        # 2. ใช้ Data Editor เพื่อให้แก้ข้อมูลได้ในตารางเลย
        # num_rows="dynamic" จะช่วยให้สามารถกดปุ่มลบแถวได้
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

        # 3. ปุ่มบันทึกการเปลี่ยนแปลง
        if st.button("💾 บันทึกการเปลี่ยนแปลงทั้งหมด"):
            st.session_state.bookings = edited_df.to_dict('records')
            st.success("อัปเดตข้อมูลในระบบเรียบร้อยแล้ว!")
            st.rerun()

        st.divider()
        st.caption("วิธีลบ: ติ๊กถูกหน้าแถวที่ต้องการ แล้วกดปุ่ม Delete บนคีย์บอร์ด หรือใช้เมนูด้านขวาของตาราง")