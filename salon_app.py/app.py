import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time

# --- CONFIG ---
st.set_page_config(page_title="222-Salon-Final", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
.main-header {text-align:center;color:#FF4B4B;font-weight:bold;margin-bottom:20px;}
.stButton>button {width:100%;border-radius:10px;font-weight:bold;height:3em;}
.price-card {background:#fff;padding:18px;border-radius:12px;border-left:6px solid #FF4B4B;margin-bottom:12px;box-shadow:2px 4px 12px rgba(0,0,0,0.08);color:#000;}
.price-text {float:right;color:#FF4B4B;font-weight:bold;}
.contact-section {background:#fff;padding:30px;border-radius:15px;text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCTIONS ---

def get_data(sheet):

    try:

        df = conn.read(worksheet=sheet, ttl=0)

        if df is None or df.empty:
            return pd.DataFrame()

        df = df.dropna(how='all')
        df.columns = [str(c).strip().lower() for c in df.columns]

        for col in df.columns:

            df[col] = df[col].astype(str).str.strip().replace(r'\.0$', '', regex=True).replace('nan','')

            if 'phone' in col or 'username' in col:
                df[col] = df[col].apply(lambda x: '0'+x if len(x)==9 and x.isdigit() else x)

        return df

    except:
        return pd.DataFrame()


def get_new_booking_count():

    df = get_data("Bookings")

    if not df.empty:

        waiting = df[df['status']=="รอรับบริการ"]

        return len(waiting)

    return 0


def get_new_msg_count():

    df = get_data("Messages")

    if not df.empty:

        unreplied = df[df['admin_reply']==""]

        return len(unreplied)

    return 0


# --- SESSION ---

if 'page' not in st.session_state:
    st.session_state.page="Home"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in=False


def navigate(p):
    st.session_state.page=p
    st.rerun()


# --- HEADER ---

st.markdown("<h1 class='main-header'>✂️ 222-Salon</h1>", unsafe_allow_html=True)

m_cols = st.columns(5)

with m_cols[0]:
    if st.button("🏠 หน้าแรก"):
        navigate("Home")

with m_cols[1]:
    if st.button("📅 คิววันนี้"):
        navigate("ViewQueues")

if not st.session_state.logged_in:

    with m_cols[3]:
        if st.button("📝 สมัครสมาชิก"):
            navigate("Register")

    with m_cols[4]:
        if st.button("🔑 เข้าสู่ระบบ"):
            navigate("Login")

else:

    role = st.session_state.get("user_role")

    with m_cols[2]:

        if role=="admin":

            new_book = get_new_booking_count()

            new_msg = get_new_msg_count()

            alert = "🔴" if (new_book>0 or new_msg>0) else ""

            if st.button(f"📊 จัดการร้าน {alert}"):

                navigate("Admin")

        else:

            if st.button("✂️ จองคิว"):
                navigate("Booking")

    with m_cols[4]:

        if st.button("🚪 ออกจากระบบ"):

            st.session_state.clear()

            navigate("Home")

st.divider()

# --- HOME ---

if st.session_state.page=="Home":

    st.image("https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1000")

    st.info("⏰ ร้านเปิด 09:30 - 19:30 (หยุดวันเสาร์)")

    st.subheader("📋 บริการ")

    services = {
    "✂️ ตัดผมชาย":"150-350",
    "💇‍♀️ ตัดผมหญิง":"350-800",
    "🚿 สระไดร์":"200-450",
    "🎨 ทำสี":"1500+",
    "✨ ยืด/ดัด":"1000+",
    "🌿 ทรีทเม้นท์":"500+"
    }

    p1,p2 = st.columns(2)

    for i,(n,p) in enumerate(services.items()):

        t = p1 if i%2==0 else p2

        t.markdown(f"<div class='price-card'><b>{n}</b><span class='price-text'>{p} บ.</span></div>", unsafe_allow_html=True)


# --- VIEW TODAY ---

elif st.session_state.page=="ViewQueues":

    st.subheader("📅 คิววันนี้")

    df = get_data("Bookings")

    today = datetime.now().strftime("%Y-%m-%d")

    if not df.empty:

        active = df[(df['date']==today)&(df['status']=="รอรับบริการ")]

        if not active.empty:

            st.table(active[['time','service','fullname']].sort_values('time'))

        else:

            st.info("ยังไม่มีคิววันนี้")


# --- REGISTER ---

elif st.session_state.page=="Register":

    st.subheader("สมัครสมาชิก")

    with st.form("reg"):

        nf = st.text_input("ชื่อ")

        nu = st.text_input("เบอร์")

        np = st.text_input("รหัส", type="password")

        npc = st.text_input("ยืนยัน", type="password")

        if st.form_submit_button("สมัคร"):

            df = get_data("Users")

            if not df.empty and nu in df['phone'].values:

                st.error("เบอร์ซ้ำ")

            else:

                new = pd.DataFrame([{
                "phone":nu,
                "password":np,
                "fullname":nf,
                "role":"user"}])

                conn.update(worksheet="Users", data=pd.concat([df,new], ignore_index=True))

                st.success("สมัครสำเร็จ")


# --- LOGIN ---

elif st.session_state.page=="Login":

    st.subheader("เข้าสู่ระบบ")

    u = st.text_input("เบอร์")

    p = st.text_input("รหัส", type="password")

    if st.button("เข้าสู่ระบบ"):

        if u=="admin222" and p=="222":

            st.session_state.update({
            "logged_in":True,
            "user_role":"admin",
            "username":u,
            "fullname":"Admin"
            })

            navigate("Admin")

        else:

            df = get_data("Users")

            user = df[(df['phone']==u)&(df['password']==p)]

            if not user.empty:

                st.session_state.update({
                "logged_in":True,
                "user_role":"user",
                "username":u,
                "fullname":user.iloc[0]['fullname']
                })

                navigate("Booking")

            else:

                st.error("ข้อมูลผิด")


# --- BOOKING ---

elif st.session_state.page=="Booking" and st.session_state.logged_in:

    t1,t2,t3 = st.tabs(["จองคิว","ประวัติคิวของฉัน","แชท"])

    # BOOK

    with t1:

        with st.form("book"):

            b_d = st.date_input("วันที่", min_value=datetime.now().date())

            b_t = st.selectbox("เวลา",["09:30","10:30","11:30","13:00","14:00","15:00","16:00","17:00","18:00"])

            b_s = st.selectbox("บริการ",["ตัดผมชาย","ตัดผมหญิง","สระ-ไดร์","ทำสี","ยืด","ทรีทเม้นท์"])

            if st.form_submit_button("จอง"):

                if b_d.weekday()==5:

                    st.error("ร้านหยุดเสาร์")

                else:

                    df = get_data("Bookings")

                    clash = df[(df['date']==str(b_d))&(df['time']==b_t)&(df['status']=="รอรับบริการ")]

                    if not clash.empty:

                        st.error("เวลานี้มีคนจองแล้ว")

                    else:

                        new = pd.DataFrame([{
                        "id":str(uuid.uuid4())[:8],
                        "username":st.session_state.username,
                        "fullname":st.session_state.fullname,
                        "date":str(b_d),
                        "time":b_t,
                        "service":b_s,
                        "status":"รอรับบริการ",
                        "price":"0"
                        }])

                        conn.update(worksheet="Bookings", data=pd.concat([df,new], ignore_index=True))

                        st.success("จองสำเร็จ")

    # HISTORY

    with t2:

        df = get_data("Bookings")

        my = df[df['username']==st.session_state.username]

        for idx,r in my.iterrows():

            with st.container(border=True):

                st.write(f"{r['date']} | {r['time']} | {r['service']}")

                st.write(r['status'])

                if r['status']=="รอรับบริการ":

                    if st.button("❌ ยกเลิกคิว", key=f"c{r['id']}"):

                        df.loc[df['id']==r['id'], 'status']="ยกเลิก"

                        conn.update(worksheet="Bookings", data=df)

                        st.rerun()

    # CHAT

    with t3:

        st.info("แชทระบบ")


# --- ADMIN ---

elif st.session_state.page=="Admin":

    at1,at2 = st.tabs(["สรุปยอด","จัดการคิว"])

    with at1:

        df = get_data("Bookings")

        if not df.empty:

            df['price']=pd.to_numeric(df['price'], errors='coerce').fillna(0)

            total = df[df['status']=="เสร็จสิ้น"]['price'].sum()

            waiting = df[df['status']=="รอรับบริการ"]

            if len(waiting)>0:

                st.error(f"🔔 มีคิวใหม่ {len(waiting)} คิว")

            st.metric("รายได้รวม", f"{total:,.0f} บาท")


    with at2:

        df = get_data("Bookings")

        active = df[df['status']=="รอรับบริการ"]

        for idx,row in active.iterrows():

            with st.container(border=True):

                st.write(f"{row['fullname']} | {row['date']} | {row['time']}")

                c1,c2,c3 = st.columns(3)

                with c1:

                    price = st.number_input("ราคา",0,5000, key=f"p{row['id']}")

                with c2:

                    if st.button("เสร็จสิ้น", key=f"s{row['id']}"):

                        df.loc[df['id']==row['id'],'price']=price

                        df.loc[df['id']==row['id'],'status']="เสร็จสิ้น"

                        conn.update(worksheet="Bookings", data=df)

                        st.rerun()

                with c3:

                    if st.button("ยกเลิก", key=f"x{row['id']}"):

                        df.loc[df['id']==row['id'],'status']="ยกเลิก"

                        conn.update(worksheet="Bookings", data=df)

                        st.rerun()
