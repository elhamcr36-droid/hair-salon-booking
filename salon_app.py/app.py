def shop_contact():

    st.subheader("📍 ติดต่อร้าน Smart Salon")

    lat = 7.1897
    lon = 100.5951
    phone = "0999999999"

    st.write("🏪 Smart Salon")
    st.write("📍 Songkhla Thailand")

    # แผนที่
    location = pd.DataFrame({
        "lat":[lat],
        "lon":[lon]
    })

    st.map(location)

    st.write("")

    col1,col2,col3 = st.columns(3)

    # ปุ่มโทร
    with col1:
        st.link_button(
            "📞 โทรหาร้าน",
            f"tel:{phone}"
        )

    # ปุ่มนำทาง GPS
    with col2:
        st.link_button(
            "🧭 นำทางมาร้าน",
            f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
        )

    # ปุ่มเปิด Google Maps
    with col3:
        st.link_button(
            "🗺 เปิด Google Maps",
            f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        )
