import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime
from scipy.optimize import linprog
import plotly.express as px
import numpy as np
import time

# --- 1. CONFIGURATION & FULL TRANSLATION DICTIONARY ---
st.set_page_config(page_title="Layer Smart AI System v4.2", layout="wide")
DB_FILE = "smart_layer_final.db"

LANG = {
    "TH": {
        "title": "🥚 ระบบ Smart Layer AI Professional v4.2",
        "login_header": "🔐 เข้าสู่ระบบ",
        "reg_header": "📝 สมัครสมาชิก",
        "forgot_header": "❓ กู้คืนรหัสผ่าน",
        "reset_header": "🔄 ตั้งรหัสผ่านใหม่",
        "user_label": "ชื่อผู้ใช้",
        "pass_label": "รหัสผ่าน",
        "fn_label": "ชื่อ-นามสกุล",
        "em_label": "อีเมล",
        "bd_label": "วันเกิด",
        "cp_label": "ยืนยันรหัสผ่าน",
        "btn_login": "เข้าสู่ระบบ",
        "btn_reg": "สมัครสมาชิกใหม่",
        "btn_forgot": "ลืมรหัสผ่าน?",
        "btn_reg_submit": "ตกลงสมัคร",
        "btn_back": "กลับ",
        "btn_check": "ตรวจสอบอีเมล",
        "btn_save": "บันทึก",
        "nav_home": "หน้าหลัก",
        "nav_admin": "ระบบแอดมิน",
        "nav_logout": "ออกจากระบบ",
        "tab_calc": "🧮 คำนวณสูตรอาหาร",
        "tab_hist": "📜 ประวัติสูตรอาหารที่บันทึก",
        "tab_stock": "🌾 คลังวัตถุดิบ",
        "tab_feed": "💬 แนะนำติชม&ติดต่อเเอดมิน",
        "tab_profile": "👤 โปรไฟล์",
        "config_sec": "⚙️ ตั้งค่าเงื่อนไข",
        "group_label": "กลุ่มไก่ไข่",
        "breed_label": "สายพันธุ์",
        "stage_label": "ระยะการให้ไข่",
        "count_label": "จำนวนไก่ (ตัว)",
        "batch_label": "ปริมาณที่จะผสม (กก.)",
        "opt_label": "เป้าหมายการประมวลผล:",
        "mode_price": "💰 ราคาถูกที่สุด (Best Price)",
        "mode_nutri": "✨ สารอาหารแม่นยำที่สุด (Best Nutrition)",
        "income_sec": "💰 พยากรณ์รายได้",
        "egg_price_label": "ราคาไข่คาดการณ์ (บาท/ฟอง)",
        "lay_rate_label": "อัตราการให้ไข่ (%)",
        "btn_ai": "🚀 ประมวลผลสูตร AI",
        "res_header": "📊 ผลลัพธ์สัดส่วนวัตถุดิบ",
        "chart_title": "สัดส่วนการผสมวัตถุดิบ (%)",
        "protein_actual": "โปรตีนที่ได้จริง (%)",
        "energy_actual": "พลังงานที่ได้จริง (kcal)",
        "target_label": "เป้าหมาย",
        "table_name": "ชื่อวัตถุดิบ",
        "table_ratio": "สัดส่วน (%)",
        "table_need": "ต้องใช้ (กก.)",
        "profit_sec": "📈 พยากรณ์กำไรรายวัน",
        "cost_day": "ต้นทุนอาหาร/วัน",
        "rev_day": "รายได้ไข่/วัน",
        "profit_month": "กำไร/เดือน",
        "btn_save_rec": "💾 บันทึกสูตรส่วนตัว",
        "hist_header": "📜 รายการสูตรของคุณ",
        "btn_del": "🗑️ ลบ",
        "stock_header": "🌾 จัดการคลังวัตถุดิบ",
        "btn_update_stock": "🔄 อัปเดตข้อมูลคลัง",
        "feed_header": "ส่งข้อความถึงระบบ",
        "rating_label": "⭐️ คะแนนความพึงพอใจ (1-5)",
        "btn_feed_send": "ส่งข้อมูล",
        "admin_user_tab": "👥 รายชื่อผู้ใช้",
        "admin_feed_tab": "📩 ข้อความติชม",
        "admin_del_msg": "ลบข้อความนี้",
        "admin_save_user_btn": "💾 บันทึกการเปลี่ยนแปลงรายชื่อผู้ใช้",
        "admin_info_del": "💡 วิธีการลบผู้ใช้: คลิกเลือกแถวที่ต้องการแล้วกด Delete",
        "msg_success": "✅ ดำเนินการสำเร็จ",
        "msg_error": "❌ ข้อมูลไม่ถูกต้อง หรือเกิดข้อผิดพลาด",
        "msg_email_not_found": "❌ ไม่พบอีเมลนี้ในระบบ กรุณาตรวจสอบอีกครั้ง",
        "msg_no_balance": "❌ ไม่พบจุดสมดุลที่เหมาะสม",
        "new_un_label": "ชื่อผู้ใช้ใหม่",
        "btn_update_un": "อัปเดตชื่อผู้ใช้"
    },
    "EN": {
        "title": "🥚 Smart Layer AI Professional v4.2",
        "login_header": "🔐 Login",
        "reg_header": "📝 Registration",
        "forgot_header": "❓ Forgot Password",
        "reset_header": "🔄 Reset Password",
        "user_label": "Username",
        "pass_label": "Password",
        "fn_label": "Full Name",
        "em_label": "Email",
        "bd_label": "Birthdate",
        "cp_label": "Confirm Password",
        "btn_login": "Login",
        "btn_reg": "Register New Account",
        "btn_forgot": "Forgot Password?",
        "btn_reg_submit": "Submit Registration",
        "btn_back": "Back",
        "btn_check": "Check Email",
        "btn_save": "Save",
        "nav_home": "Home",
        "nav_admin": "Admin Panel",
        "nav_logout": "Logout",
        "tab_calc": "🧮 Calculator",
        "tab_hist": "📜 My Recipes",
        "tab_stock": "🌾 Stock",
        "tab_feed": "💬 Feedback",
        "tab_profile": "👤 Profile",
        "config_sec": "⚙️ Configuration",
        "group_label": "Layer Group",
        "breed_label": "Breed",
        "stage_label": "Laying Stage",
        "count_label": "Bird Count",
        "batch_label": "Batch Size (kg)",
        "opt_label": "Optimization Goal:",
        "mode_price": "💰 Best Price",
        "mode_nutri": "✨ Best Nutrition",
        "income_sec": "💰 Revenue Forecast",
        "egg_price_label": "Exp. Price (THB/Egg)",
        "lay_rate_label": "Lay Rate (%)",
        "btn_ai": "🚀 Run AI Optimization",
        "res_header": "📊 Ingredient Results",
        "chart_title": "Mixing Ratio (%)",
        "protein_actual": "Actual Protein (%)",
        "energy_actual": "Actual Energy (kcal)",
        "target_label": "Target",
        "table_name": "Ingredient",
        "table_ratio": "Ratio (%)",
        "table_need": "Required (kg)",
        "profit_sec": "📈 Daily Profit Forecast",
        "cost_day": "Feed Cost/Day",
        "rev_day": "Revenue/Day",
        "profit_month": "Profit/Month",
        "btn_save_rec": "💾 Save My Recipe",
        "hist_header": "📜 Your Saved Recipes",
        "btn_del": "🗑️ Delete",
        "stock_header": "🌾 Stock Management",
        "btn_update_stock": "🔄 Update Stock",
        "feed_header": "Send Feedback",
        "rating_label": "Satisfaction Rating (1-5)",
        "btn_feed_send": "Submit",
        "admin_user_tab": "👥 Users",
        "admin_feed_tab": "📩 Feedbacks",
        "admin_del_msg": "Delete Message",
        "admin_save_user_btn": "💾 Save User Changes",
        "admin_info_del": "💡 To delete: select row and press Delete key",
        "msg_success": "✅ Success",
        "msg_error": "❌ Invalid data or error occurred",
        "msg_email_not_found": "❌ Email not found in our system.",
        "msg_no_balance": "❌ Balanced formulation not found",
        "new_un_label": "New Username",
        "btn_update_un": "Update Username"
    }
}

# --- 2. MASTER DATA ---
STANDARD_INGREDIENTS = [
    ("ข้าวโพดบด", "Ground Corn", 8.5, 3350, 2.2, 0.02, 0.28, 0.24, 0.18, 12.5),
    ("ปลายข้าว", "Broken Rice", 8.0, 3400, 1.0, 0.03, 0.08, 0.23, 0.15, 14.0),
    ("รำละเอียด", "Rice Bran", 12.5, 2450, 12.0, 0.12, 1.35, 0.60, 0.22, 10.0),
    ("มันสำปะหลังเส้น", "Cassava Chips", 2.5, 3100, 3.5, 0.18, 0.09, 0.07, 0.03, 8.5),
    ("น้ำมันปาล์ม/ไขมัน", "Vegetable Oil", 0.0, 8800, 0.0, 0.0, 0.0, 0.0, 0.0, 35.0),
    ("กากถั่วเหลือง (48%)", "Soybean Meal 48%", 48.0, 2450, 3.5, 0.27, 0.62, 3.10, 0.65, 23.0),
    ("ปลาป่น (60%)", "Fish Meal 60%", 60.0, 2800, 1.0, 5.00, 3.00, 4.50, 1.70, 38.0),
    ("เปลือกหอยบด/แคลเซียม", "Limestone", 0.0, 0, 0.0, 38.0, 0.0, 0.0, 0.0, 5.0),
    ("ดีแคลเซียมฟอสเฟต (DCP)", "DCP", 0.0, 0, 0.0, 21.0, 18.0, 0.0, 0.0, 28.0),
    ("พรีมิกซ์ไก่ไข่", "Layer Premix", 2.0, 500, 0.0, 12.0, 4.0, 1.0, 0.5, 150.0),
    ("ใบกระถินป่น", "Leucaena Meal", 22.0, 1200, 12.0, 1.5, 0.2, 0.0, 0.0, 7.0),
    ("เกลือ", "Salt", 0.0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0),
    ("ดีแอล-เมทไธโอนีน", "DL-Methionine", 99.0, 0, 0.0, 0.0, 0.0, 0.0, 99.0, 180.0),
    ("แอล-ไลซีน", "L-Lysine", 78.0, 0, 0.0, 0.0, 0.0, 78.0, 0.0, 95.0)
]

ANIMAL_MASTER = {
    "TH": {
        "Commercial Brown Layers (ไก่ไข่สีน้ำตาล)": {
            "breeds": ["อิซ่า บราวน์ (Isa Brown)", "ไฮ-ไลน์ บราวน์ (Hy-Line Brown)", "โลมัน บราวน์ (Lohmann Brown)", "โนโวเจน บราวน์ (Novogen Brown)", "ซีพี บราวน์ (CP Brown)", "บาวานส์ บราวน์ (Bovans Brown)"],
            "stages": {
                "ระยะเริ่มแรก (Starter 0-6 wk)": {"vals": [20.0, 2900, 4.0]},
                "ระยะไก่รุ่น (Grower 6-18 wk)": {"vals": [16.0, 2750, 5.0]},
                "ระยะให้ไข่สูงสุด (Peak Production)": {"vals": [17.5, 2850, 3.5]},
                "ระยะให้ไข่ช่วงท้าย (Late Laying)": {"vals": [16.5, 2750, 4.0]}
            }
        },
        "Commercial White Layers (ไก่ไข่สีขาว)": {
            "breeds": ["ไฮ-ไลน์ W-36 (Hy-Line White)", "โลมัน แอลเอสแอล (Lohmann LSL)", "ดีคัลบ์ ไวท์ (Dekalb White)", "บาวานส์ ไวท์ (Bovans White)"],
            "stages": {
                "ระยะเริ่มแรก (Starter 0-6 wk)": {"vals": [21.0, 2950, 3.5]},
                "ระยะให้ไข่สูงสุด (Peak Production)": {"vals": [18.5, 2900, 3.0]},
                "ระยะให้ไข่ช่วงท้าย (Late Laying)": {"vals": [17.0, 2800, 3.5]}
            }
        },
        "Heritage & Specialty (สายพันธุ์มรดก/พื้นเมือง)": {
            "breeds": ["โร้ดไอแลนด์เรด (Rhode Island Red)", "บาร์ พลีมัธร็อค (Barred Rock)", "ออสตราลอป (Australorp)", "อาราอูคาน่า (Araucana - ไข่สีฟ้า)", "มารันส์ (Marans - ไข่สีช็อกโกแลต)"],
            "stages": {
                "ระยะเจริญเติบโต (Grower Period)": {"vals": [15.5, 2700, 6.0]},
                "ระยะให้ไข่ (Laying Period)": {"vals": [16.5, 2750, 5.0]}
            }
        }
    },
    "EN": {
        "Commercial Brown Layers": {
            "breeds": ["Isa Brown", "Hy-Line Brown", "Lohmann Brown", "Novogen Brown", "CP Brown", "Bovans Brown"],
            "stages": {
                "Starter (0-6 wk)": {"vals": [20.0, 2900, 4.0]},
                "Grower (6-18 wk)": {"vals": [16.0, 2750, 5.0]},
                "Peak Production": {"vals": [17.5, 2850, 3.5]},
                "Late Laying": {"vals": [16.5, 2750, 4.0]}
            }
        },
        "Commercial White Layers": {
            "breeds": ["Hy-Line W-36", "Lohmann LSL", "Dekalb White", "Bovans White"],
            "stages": {
                "Starter (0-6 wk)": {"vals": [21.0, 2950, 3.5]},
                "Peak Production": {"vals": [18.5, 2900, 3.0]},
                "Late Laying": {"vals": [17.0, 2800, 
