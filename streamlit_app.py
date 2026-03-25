import streamlit as st
import sqlite3
import pandas as pd

# =========================
# 🔧 CONFIG
# =========================
st.set_page_config(page_title="KK-Team Smart PRO V7", layout="wide")
DB_FILE = "kkteam_pro_v7.db"

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        code TEXT PRIMARY KEY,
        price REAL,
        category TEXT,
        sub_category TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# =========================
# 🔍 DB FUNCTIONS (Live Search)
# =========================
def search_all_codes():
    conn = get_conn()
    df = pd.read_sql("SELECT code FROM products ORDER BY code ASC", conn)
    conn.close()
    return df['code'].tolist()

def get_product_detail(code):
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM products WHERE code=?", conn, params=(code,))
    conn.close()
    return df

def save_product(code, price, cat, sub):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    INSERT INTO products (code, price, category, sub_category)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(code) DO UPDATE SET
        price=excluded.price,
        category=excluded.category,
        sub_category=excluded.sub_category
    """, (code.strip().upper(), price, cat, sub))
    conn.commit()
    conn.close()

# =========================
# 🔐 LOGIN
# =========================
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 KK-Team System PRO")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if pw == "KK-Team":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Wrong Password")
    st.stop()

# =========================
# 📊 MASTER RATES
# =========================
DB_RATES = {
    "1. LAN (UTP)": {"C": [1,3,5,10,20,30,50,100], "UT": "กล่อง", "R": ["10+10","10+10+2","10+10+3","10+10+5","10+10+5+2","10+10+5+3","10+10+5+5","10+10+5+5+5"]},
    "2. FIBER OPTIC": {"C": [1,500,1000,3000,5000,8000,10000,20000,30000], "UT": "เมตร", "R": ["10","10+5","10+10","10+10+3","10+10+5","10+10+5+3","10+10+5+5","10+10+5+5+3","10+10+5+5+5"]},
    "3. FTTx / FTTR": {"C": [1,3,5,10,20,30,50,100], "UT": "ม้วน", "R": ["10+10","10+10+2","10+10+3","10+10+5","10+10+5+2","10+10+5+3","10+10+5+5","10+10+5+5+5"]},
    "4. COAXIAL (RG)": {"C": [1,500,1000,3000,5000,8000,10000,20000,30000], "UT": "เมตร", "R": ["20","20+5","20+10","20+10+3","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+3","20+10+5+5+5"]},
    "5. SECURITY & CONTROL": {"C": [1,100,200,500,1000,2000], "UT": "เมตร", "R": ["10+10","10+10+5","10+10+10","10+10+10+5","10+10+10+10","10+10+10+10+5"]},
    "6. SOLAR": {"C": [1,500,1000,3000,5000,10000,20000,30000,50000], "UT": "เมตร", "R": ["10","10+5","10+10","10+10+3","10+10+5","10+10+5+3","10+10+5+5","10+10+5+5+3","10+10+5+5+5"]},
    "7. TELEPHONE": {"C": [1,100,200,300,500,1000], "UT": "เมตร", "R": ["15","15+5","15+10","15+10+5","15+10+10","15+10+10+5"]},
    "8. NETWORKING": {"C": [1,2,5,10,20], "UT": "เครื่อง", "R": ["10","10+2","10+3","10+5","10+5+2"]},
    "9/10/11. RACK": {"C": [1,2,3,4,5,10,20], "UT": "ตู้", "R": ["20","20+2","20+3","20+4","20+5","20+5+5","20+5+5+3"]},
    "COMMSCOPE": {"C": [1,5,10,20,50], "UT": "หน่วย", "R": ["10","10+2","10+3","10+5","10+5+5"]}
}

# =========================
# 🛒 MAIN UI
# =========================
st.title("🛡️ KK-Team Smart PRO V7")

# ปุ่มล้างหน้าจอแบบด่วน (Refresh)
if st.button("🔄 เริ่มรายการใหม่ (Refresh Screen)"):
    st.rerun()

cust_group = st.radio("เลือกกลุ่มลูกค้า:", ["Dealer / Installer", "IT Shop (+5%)"], horizontal=True)

if 'cart' not in st.session_state: st.session_state.cart = []

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        # ระบบค้นหาที่รวมร่างกัน: พิมพ์รหัสที่นี่ จะขึ้นคำแนะนำทันที
        all_known_codes = search_all_codes()
        input_code = st.selectbox(
            "🔍 พิมพ์หรือเลือกรหัสสินค้า (ระบบจะแนะนำรหัสที่เคยบันทึกทันที)",
            options=all_known_codes,
            index=None,
            placeholder="เริ่มพิมพ์รหัสสินค้าที่นี่...",
        )
        
        # ช่องสำรองกรณีรหัสใหม่เอี่ยม
        new_code = st.text_input("✨ หรือกรอกรหัสใหม่ (ถ้าไม่มีในรายการแนะนำ)").strip().upper()
        final_code = new_code if new_code else (input_code if input_code else "")

        # ดึงข้อมูลมาเติมให้อัตโนมัติ (Autofill)
        product = get_product_detail(final_code)
        def_price, def_cat, def_sub = 0.0, list(DB_RATES.keys())[0], "สินค้า (Cable)"
        if not product.empty:
            def_price = float(product.iloc[0]['price'])
            def_cat = product.iloc[0]['category']
            def_sub = product.iloc[0]['sub_category']
            st.info(f"📌 ข้อมูลล่าสุด: {def_price:,.2f} | {def_cat}")

        f_cat = st.selectbox("หมวดหมู่สินค้า", list(DB_RATES.keys()), index=list(DB_RATES.keys()).index(def_cat))
        f_sub = st.radio("ประเภท", ["สินค้า (Cable)", "อุปกรณ์ (Conn/Acc)"], index=0 if def_sub == "สินค้า (Cable)" else 1, horizontal=True)

    with col2:
        f_price = st.number_input("ราคาตั้ง (List Price)", value=def_price, format="%.2f")
        qty = st.number_input("จำนวนที่สั่งซื้อ", min_value=1, value=1)

# =========================
# 💰 CALCULATION
# =========================
if st.button("🚀 คำนวณและบันทึก", use_container_width=True):
    if not final_code:
        st.warning("⚠️ โปรดระบุรหัสสินค้า")
    else:
        save_product(final_code, f_price, f_cat, f_sub)
        
        data = DB_RATES[f_cat]
        idx = 0
        for i, v in enumerate(data["C"]):
            if qty >= v: idx = i
        
        base_rate = data["R"][idx]
        if f_cat == "1. LAN (UTP)" and f_sub == "อุปกรณ์ (Conn/Acc)":
            base_rate = base_rate.replace("10", "20")
            
        final_rate_str = base_rate + "+5" if "IT Shop" in cust_group else base_rate
        
        # คำนวณราคาสุทธิแบบละเอียด
        net_price = f_price
        calc_steps = f"{f_price:,.2f}"
        for d in [float(x) for x in final_rate_str.split("+")]:
            calc_steps += f" - {d}%"
            net_price *= (1 - d/100)
        
        unit = data["UT"] if f_sub == "สินค้า (Cable)" else "ชิ้น"
        res_line = f"{final_code}={net_price:,.2f}.-/{unit} (สั่ง {qty} {unit})"
        res_note = f"💡 วิธีคิด: {calc_steps} = {net_price:,.2f}"
        
        st.session_state.cart.append({"main": res_line, "note": res_note})
        st.rerun()

# =========================
# 📝 SUMMARY
# =========================
if st.session_state.cart:
    st.divider()
    summary_text = []
    for item in st.session_state.cart:
        st.write(f"**{item['main']}**")
        st.caption(item['note'])
        summary_text.append(item['main'])
    
    st.text_area("Copy ไปวางใน Line:", value="\n".join(summary_text), height=150)
    if st.button("🗑️ ล้างรายการคำนวณ"): st.session_state.cart = []; st.rerun()

# =========================
# 📊 DATABASE
# =========================
st.divider()
st.subheader("📊 ตารางฐานข้อมูล")
st.dataframe(pd.read_sql("SELECT * FROM products ORDER BY code DESC", get_conn()), use_container_width=True, hide_index=True)
