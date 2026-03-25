import streamlit as st
import sqlite3
import pandas as pd

# ==========================================
# 📊 [ส่วนที่ 1] ศูนย์รวมเรทราคา (ห้ามยุ่ง - ข้อมูลตามที่คุณดนย์ตั้งไว้)
# ==========================================
DB_RATES = {
    "1. LAN (UTP)": {
        "Cable": {"C": [1,3,5,10,20,30,50,100], "R": ["10+10","10+10+2","10+10+3","10+10+5","10+10+5+2","10+10+5+3","10+10+5+5","10+10+5+5+5"], "UT": "กล่อง"},
        "Acc": {"Price_Split": 300, 
                "Under": {"C": [1,10,30,50,100,200,300,500,1000], "R": ["10","10+2","10+3","10+5","10+10","10+10+5","10+10+5+3","10+10+5+5","10+10+5+5+5"]},
                "Over":  {"C": [1,2,3,5,10,20,30,50,100], "R": ["10","10+2","10+3","10+5","10+10","10+10+5","10+10+5+3","10+10+5+5","10+10+5+5+5"]}, "UT": "ชิ้น"}
    },
    "2. FIBER OPTIC": {
        "Cable": {"C": [1,500,1000,3000,5000,8000,10000,20000,30000], "R": ["10","10+5","10+10","10+10+3","10+10+5","10+10+5+3","10+10+5+5","10+10+5+5+3","10+10+5+5+5"], "UT": "เมตร"},
        "Acc": {"Price_Split": 300, 
                "Under": {"C": [1,10,30,50,100,200,300,500,1000], "R": ["20","20+2","20+3","20+5","20+10","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+5"]},
                "Over":  {"C": [1,2,3,5,10,20,30,50,100], "R": ["20","20+2","20+3","20+5","20+10","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+5"]}, "UT": "ชิ้น"}
    },
    "3. FTTx / FTTR": {
        "Cable": {"C": [1,3,5,10,20,30,50,100], "R": ["10+10","10+10+2","10+10+3","10+10+5","10+10+5+2","10+10+5+3","10+10+5+5","10+10+5+5+5"], "UT": "ม้วน"},
        "Acc": {"Price_Split": 300, 
                "Under": {"C": [1,10,30,50,100,200,300,500,1000], "R": ["20","20+2","20+3","20+5","20+10","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+5"]},
                "Over":  {"C": [1,2,3,5,10,20,30,50,100], "R": ["20","20+2","20+3","20+5","20+10","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+5"]}, "UT": "ชิ้น"}
    },
    "4. COAXIAL (RG)": {
        "Cable": {"C": [1,500,1000,3000,5000,8000,10000,20000,30000], "R": ["20","20+5","20+10","20+10+3","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+3","20+10+5+5+5"], "UT": "เมตร"},
        "Acc": {"Price_Split": 300, 
                "Under": {"C": [1,10,30,50,100,200,300,500,1000], "R": ["20","20+2","20+3","20+5","20+10","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+5"]},
                "Over":  {"C": [1,2,3,5,10,20,30,50,100], "R": ["20","20+2","20+3","20+5","20+10","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+5"]}, "UT": "ชิ้น"}
    },
    "5. SECURITY & CONTROL": {
        "Cable": {"C": [1,500,1000,3000,5000,10000,20000,30000], "R": ["10","10+5","10+10","10+10+3","10+10+5","10+10+5+5","10+10+5+5+3","10+10+5+5+5"], "UT": "เมตร"},
        "Acc": {"Price_Split": 300, 
                "Under": {"C": [1,10,30,50,100,200,300,500,1000], "R": ["20","20+2","20+3","20+5","20+10","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+5"]},
                "Over":  {"C": [1,2,3,5,10,20,30,50,100], "R": ["20","20+2","20+3","20+5","20+10","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+5"]}, "UT": "ชิ้น"}
    },
    "6. SOLAR": {
        "Cable": {"C": [1,500,1000,3000,5000,10000,20000,30000,50000], "R": ["10","10+5","10+10","10+10+3","10+10+5","10+10+5+3","10+10+5+5","10+10+5+5+3","10+10+5+5+5"], "UT": "เมตร"},
        "Acc": {"Price_Split": 300, 
                "Under": {"C": [1,10,30,50,100,200,300,500,1000], "R": ["20","20+2","20+3","20+5","20+10","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+5"]},
                "Over":  {"C": [1,2,3,5,10,20,30,50,100], "R": ["20","20+2","20+3","20+5","20+10","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+5"]}, "UT": "ชิ้น"}
    },
    "7. TELEPHONE": {
        "Cable": {"C": [1,500,1000,3000,5000,10000,20000,30000,50000], "R": ["10","10+5","10+10","10+10+3","10+10+5","10+10+5+3","10+10+5+5","10+10+5+5+3","10+10+5+5+5"], "UT": "เมตร"},
        "Acc": {"Price_Split": 300, 
                "Under": {"C": [1,10,30,50,100,200,300,500,1000], "R": ["20","20+2","20+3","20+5","20+10","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+5"]},
                "Over":  {"C": [1,2,3,5,10,20,30,50,100], "R": ["20","20+2","20+3","20+5","20+10","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+5"]}, "UT": "ชิ้น"}
    },
    "8. NETWORKING": {
        "Cable": {"C": [1,3,5,10,15,20,50], "R": ["20","20+3","20+5","20+5+3","20+5+5","20+5+5+3","20+5+5+5"], "UT": "เครื่อง"},
        "Acc": {"C": [1,3,5,10,30,50], "R": ["20","20+5","20+5+5","20+5+5+5","20+5+5+5+5"], "UT": "ชิ้น"}
    },
    "9/10/11. RACK": {
        "Cable": {"C": [1,2,3,4,5,10,20], "R": ["20","20+2","20+3","20+4","20+5","20+5+5","20+5+5+3"], "UT": "ตู้"},
        "Acc": {"C": [1,3,5,10,20,50], "R": ["20","20+3","20+5","20+5+3","20+5+5","20+5+5+3","20+5+5+5"], "UT": "หน่วย"}
    },
}

# ==========================================
# ⚙️ [ส่วนที่ 2] ระบบหลังบ้าน (DB & Login)
# ==========================================
st.set_page_config(page_title="KK-Team No.1", layout="wide")
DB_FILE = "kkteam_pro_v15.db"

def get_conn(): return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with get_conn() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS products (code TEXT PRIMARY KEY, price REAL, category TEXT, sub_category TEXT)")

init_db()

def save_data(code, price, cat, sub):
    with get_conn() as conn:
        conn.execute("INSERT INTO products VALUES (?,?,?,?) ON CONFLICT(code) DO UPDATE SET price=excluded.price, category=excluded.category, sub_category=excluded.sub_category", 
                    (code.strip().upper(), price, cat, sub))

# เช็คสถานะการ Login
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# ==========================================
# 🔐 [หน้า Login]
# ==========================================
if not st.session_state.authenticated:
    st.markdown("### 🛡️ KK-Team Smart PRO Login")
    pwd = st.text_input("กรุณาใส่รหัสผ่านเพื่อเข้าใช้งาน:", type="password")
    if st.button("เข้าสู่ระบบ"):
        if pwd == "KK-Team":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("รหัสผ่านไม่ถูกต้อง!")
    st.stop() # หยุดการทำงานถ้ารหัสไม่ถูก

# ==========================================
# 🛒 [ส่วนที่ 3] หน้าหลักแอป (เมื่อ Login ผ่านแล้ว)
# ==========================================
st.title("🛡️ KK-Team Smart PRO V17")

col_top1, col_top2 = st.columns([1, 6])
with col_top1:
    if st.button("🔄 เริ่มใหม่"):
        st.session_state.cart = []
        st.rerun()
with col_top2:
    if st.button("🚪 ออกจากระบบ"):
        st.session_state.authenticated = False
        st.rerun()

cust_group = st.radio("เลือกกลุ่มลูกค้า:", ["Dealer / Installer", "IT Shop (+5%)"], horizontal=True)

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        known_codes = pd.read_sql("SELECT code FROM products", get_conn())['code'].tolist()
        selected_code = st.selectbox("🔍 ค้นหาหรือพิมพ์รหัสสินค้า", options=[""] + known_codes)
        
        res = pd.read_sql("SELECT * FROM products WHERE code=?", get_conn(), params=(selected_code,))
        d_price, d_cat, d_sub = 0.0, "1. LAN (UTP)", "Cable"
        if not res.empty:
            d_price, d_cat, d_sub = float(res.iloc[0]['price']), res.iloc[0]['category'], res.iloc[0]['sub_category']
            st.success(f"📌 ข้อมูลเดิม: {d_cat} | {d_sub}")

        f_code = st.text_input("✨ ยืนยันรหัสสินค้า", value=selected_code).strip().upper()
        f_cat = st.selectbox("หมวดหมู่หลัก", list(DB_RATES.keys()), index=list(DB_RATES.keys()).index(d_cat) if d_cat in DB_RATES else 0)
        f_sub = st.radio("ประเภท", ["Cable", "Acc"], format_func=lambda x: "สินค้าหลัก (สาย/ตู้/ม้วน)" if x=="Cable" else "อุปกรณ์ (Connector/Acc)", 
                         index=0 if d_sub=="Cable" else 1, horizontal=True)

    with col2:
        f_price = st.number_input("ราคาตั้ง (List Price)", value=d_price, format="%.2f")
        qty = st.number_input("จำนวนที่สั่งซื้อ", min_value=1, value=1)

# ==========================================
# 💰 [ส่วนที่ 4] เครื่องยนต์คำนวณ (Calculation)
# ==========================================
if st.button("🚀 คำนวณและบันทึกข้อมูล", use_container_width=True):
    if f_code:
        save_data(f_code, f_price, f_cat, f_sub)
        cat_info = DB_RATES[f_cat][f_sub]
        
        if f_sub == "Acc" and "Price_Split" in cat_info:
            split = cat_info["Price_Split"]
            rate_info = cat_info["Under"] if f_price < split else cat_info["Over"]
        else:
            rate_info = cat_info

        idx = 0
        for i, v in enumerate(rate_info["C"]):
            if qty >= v: idx = i
        
        low_val = rate_info["C"][idx]
        unit = cat_info["UT"]
        if idx + 1 < len(rate_info["C"]):
            high_val = rate_info["C"][idx+1] - 1
            range_desc = f"เรท {low_val} ถึง {high_val} {unit}"
        else:
            range_desc = f"เรท {low_val} {unit} ขึ้นไป"

        base_rate = rate_info["R"][idx]
        final_rate_str = base_rate + ("+5" if "IT Shop" in cust_group else "")
        
        net_p = f_price
        calc_steps = f"{f_price:,.2f}"
        discount_list = [x for x in final_rate_str.split("+") if x.strip()]
        for d in discount_list:
            d_val = float(d)
            calc_steps += f" - {d_val}%"
            net_p *= (1 - d_val/100)
            
        res_line = f"{f_code} = {net_p:,.2f}.-/{unit} ({range_desc}) *ราคาตั้ง {f_price:,.2f}*"
        res_note = f"💡 ส่วนลด: {final_rate_str}% | วิธีคิด: {calc_steps}"
        
        if 'cart' not in st.session_state: st.session_state.cart = []
        st.session_state.cart.append({"main": res_line, "note": res_note})
        st.rerun()

# สรุปรายการ
if 'cart' in st.session_state and st.session_state.cart:
    st.divider()
    summary_text = []
    for item in st.session_state.cart:
        st.write(f"✅ **{item['main']}**")
        st.caption(item['note'])
        summary_text.append(item['main'])
    
    st.text_area("📋 คัดลอกลง LINE:", value="\n".join(summary_text), height=150)
    if st.button("🗑️ ล้างรายการ"):
        st.session_state.cart = []
        st.rerun()

st.divider()
st.subheader("📊 ประวัติสินค้าที่เคยบันทึก")
st.dataframe(pd.read_sql("SELECT * FROM products ORDER BY code DESC", get_conn()), use_container_width=True, hide_index=True)
# 📊 แสดงฐานข้อมูล
