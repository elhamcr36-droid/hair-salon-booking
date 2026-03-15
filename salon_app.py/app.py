import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="222-Salon-Final",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- STYLE ----------------
st.markdown("""
<style>
[data-testid="stSidebar"] {display:none;}

.main-header{
text-align:center;
color:#FF4B4B;
font-weight:bold;
margin-bottom:20px;
}

.stButton>button{
width:100%;
border-radius:10px;
font-weight:bold;
height:3.2em;
}

.price-card{
background-color:#ffffff;
padding:18px;
border-radius:12px;
border-left:6px solid #FF4B4B;
margin-bottom:12px;
box-shadow:2px 4px 12px rgba(0,0,0,0.08);
color:#000;
}

.price-text{
float:right;
color:#FF4B4B;
font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- CONNECTION ----------------
conn = st.connection("gsheets", type=GSheetsConnection)

# ---------------- FUNCTIONS ----------------
def get_data(sheet):

    try:

        df = conn.read(worksheet=sheet, ttl=0)

        if df is None:
            return pd.DataFrame()

        if df.empty:
            return pd.DataFrame()

        df = df.dropna(how="all")

        df.columns = [str(c).strip().lower() for c in df.columns]

        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()

        return df

    except:
        return pd.DataFrame()


def get_new_msg_count():

    df_m = get_data("Messages")

    if 'admin_reply' not in df_m.columns:
        df_m['admin_reply'] = ""

    if not df_m.empty:
        unreplied = df_m[df_m['admin_reply'] == ""]
        return len(unreplied)

    return 0


# ---------------- SESSION ----------------
if 'page' not in st.session_state:
    st.session_state.page = "Home"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


def navigate(p):
    st.session_state.page = p
    st.rerun()


# ---------------- HEADER ----------------
st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)

menu = st.columns(5)

with menu[0]:
    if st.button("🏠 หน้าแรก"):
        navigate("Home")

with menu[1]:
    if st.button("📅 คิววันนี้"):
        navigate("ViewQueues")

if not st.session_state.logged_in:

    with menu[3]:
        if st.button("📝 สมัครสมาชิก"):
            navigate("Register")

    with menu[4]:
        if st.button("🔑 เข้าสู่ระบบ"):
            navigate("Login")

else:

    role = st.session_state.get("user_role")

    with menu[2]:

        if role == "admin":

            new_msgs = get_new_msg_count()

            lbl = f"📊 จัดการร้าน {'🔴' if new_msgs>0 else ''}"

            if st.button(lbl):
                navigate("Admin")

        else:

            if st.button("✂️ จองคิว"):
                navigate("Booking")

    with menu[4]:

        if st.button("🚪 ออกจากระบบ"):

            st.session_state.clear()
            navigate("Home")

st.divider()

# ---------------- HOME ----------------
if st.session_state.page == "Home":

    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")

    st.info("⏰ ร้านเปิดบริการ 09:30 - 19:30 น. (หยุดวันเสาร์)")

    st.subheader("📋 บริการและราคา")

    services = {
        "✂️ ตัดผมชาย":"150-350",
        "💇‍♀️ ตัดผมหญิง":"350-800",
        "🚿 สระไดร์":"200-450",
        "🎨 ทำสีผม":"1500+",
        "✨ ยืดดัด":"1000+",
        "🌿 ทรีทเม้นท์":"500+"
    }

    c1,c2 = st.columns(2)

    for i,(name,price) in enumerate(services.items()):

        target = c1 if i%2==0 else c2

        target.markdown(
        f"<div class='price-card'><b>{name}</b><span class='price-text'>{price} บ.</span></div>",
        unsafe_allow_html=True
        )

# ---------------- VIEW QUEUE ----------------
elif st.session_state.page == "ViewQueues":

    st.subheader("📅 คิววันนี้")

    df = get_data("Bookings")

    today = datetime.now().strftime("%Y-%m-%d")

    if not df.empty:

        active = df[(df['date']==today) & (df['status']=="รอรับบริการ")]

        if not active.empty:

            st.table(active[['time','service','fullname']].sort_values("time"))

        else:

            st.info("ยังไม่มีคิววันนี้")

    else:

        st.info("ไม่มีข้อมูล")

# ---------------- REGISTER ----------------
elif st.session_state.page == "Register":

    st.subheader("สมัครสมาชิก")

    with st.form("reg"):

        name = st.text_input("ชื่อ")

        phone = st.text_input("เบอร์")

        pw = st.text_input("รหัสผ่าน", type="password")

        pw2 = st.text_input("ยืนยันรหัสผ่าน", type="password")

        if st.form_submit_button("สมัคร"):

            if pw != pw2:

                st.error("รหัสผ่านไม่ตรงกัน")

            else:

                df = get_data("Users")

                new = pd.DataFrame([{
                    "phone":phone,
                    "password":pw,
                    "fullname":name,
                    "role":"user"
                }])

                conn.update(
                    worksheet="Users",
                    data=pd.concat([df,new], ignore_index=True)
                )

                st.success("สมัครสำเร็จ")
                navigate("Login")

# ---------------- LOGIN ----------------
elif st.session_state.page == "Login":

    st.subheader("เข้าสู่ระบบ")

    u = st.text_input("เบอร์")

    p = st.text_input("รหัสผ่าน", type="password")

    if st.button("เข้าสู่ระบบ"):

        if u=="admin222" and p=="222":

            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            navigate("Admin")

        else:

            df = get_data("Users")

            user = df[(df['phone']==u) & (df['password']==p)]

            if not user.empty:

                st.session_state.logged_in = True
                st.session_state.user_role = "user"
                st.session_state.username = u
                st.session_state.fullname = user.iloc[0]['fullname']

                navigate("Booking")

            else:

                st.error("ข้อมูลไม่ถูกต้อง")

# ---------------- BOOKING ----------------
elif st.session_state.page == "Booking":

    st.subheader("จองคิว")

    with st.form("book"):

        d = st.date_input("วันที่")

        t = st.selectbox("เวลา",
        ["09:30","10:30","11:30","13:00","14:00","15:00","16:00","17:00","18:00"]
        )

        s = st.selectbox("บริการ",
        ["ตัดผมชาย","ตัดผมหญิง","สระไดร์","ทำสีผม","ยืดดัด","ทรีทเม้นท์"]
        )

        if st.form_submit_button("จอง"):

            if d.weekday()==5:

                st.error("ร้านหยุดวันเสาร์")

            else:

                df = get_data("Bookings")

                new = pd.DataFrame([{
                    "id":str(uuid.uuid4())[:8],
                    "username":st.session_state.username,
                    "fullname":st.session_state.fullname,
                    "date":str(d),
                    "time":t,
                    "service":s,
                    "status":"รอรับบริการ",
                    "price":"0"
                }])

                conn.update(
                    worksheet="Bookings",
                    data=pd.concat([df,new], ignore_index=True)
                )

                st.success("จองสำเร็จ")

# ---------------- ADMIN ----------------
elif st.session_state.page == "Admin":

    tab1,tab2,tab3 = st.tabs(["รายได้","คิว","แชท"])

    with tab1:

        df = get_data("Bookings")

        if not df.empty:

            df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)

            total = df[df['status']=="เสร็จสิ้น"]['price'].sum()

            st.metric("รายได้รวม", f"{total:,.0f} บาท")

    with tab2:

        df = get_data("Bookings")

        if not df.empty:

            q = df[df['status']=="รอรับบริการ"]

            for i,row in q.iterrows():

                st.write(row['fullname'],row['date'],row['time'])

                if st.button("เสร็จสิ้น", key=row['id']):

                    df.loc[df['id']==row['id'],'status']="เสร็จสิ้น"

                    conn.update(worksheet="Bookings", data=df)

                    st.rerun()

    with tab3:

        df_msg = get_data("Messages")

        if 'admin_reply' not in df_msg.columns:
            df_msg['admin_reply'] = ""

        new_count = len(df_msg[df_msg['admin_reply']==""])

        if new_count > 0:
            st.error(f"มี {new_count} ข้อความยังไม่ตอบ")

        if not df_msg.empty:

            users = df_msg['username'].unique()

            u = st.selectbox("เลือกลูกค้า", users)

            chat = df_msg[df_msg['username']==u]

            for idx,row in chat.iterrows():

                st.chat_message("user").write(row['message'])

                if row['admin_reply']:

                    st.chat_message("assistant").write(row['admin_reply'])

                else:

                    ans = st.text_input("ตอบกลับ", key=f"ans{idx}")

                    if st.button("ส่ง", key=f"send{idx}"):

                        df_msg.at[idx,'admin_reply'] = ans

                        conn.update(
                            worksheet="Messages",
                            data=df_msg
                        )

                        st.rerun()
