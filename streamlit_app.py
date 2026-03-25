import streamlit as st
import sqlite3
import pandas as pd

# =========================
# 🔧 CONFIG & INITIALIZATION
# =========================
st.set_page_config(page_title="KK-Team Smart System PRO V6", layout="wide")
DB_FILE = "kkteam_pro_v6.db"

# =========================
# 🧠 DATABASE SYSTEM (SQLite)
# =========================
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
# 🔍 DB FUNCTIONS
# =========================
def get_product(code):
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM products WHERE code=?", conn, params=(code.strip().upper(),))
    conn.close()
    return df

def search_code(keyword):
    if not keyword: return []
    conn = get_conn()
    df = pd.read_sql("SELECT code FROM products WHERE code LIKE ? LIMIT 10", 
                     conn, params=(f"{keyword.strip().upper()}%",))
    conn.close()
    return df['code'].tolist()

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

def load_all():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM products ORDER BY code DESC", conn)
    conn.close()
    return df

# =========================
# 🔐 LOGIN SYSTEM
# =========================
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 KK-Team System PRO")
    pw = st.text_input("กรุณาใส่รหัสผ่าน", type="password")
    if st.button("Login"):
        if pw == "KK-Team":
            st.session_state.auth = True
            st.rerun()
        else: st.error("รหัสไม่ถูกต้อง")
    st.stop()

# =========================
# 📊 MASTER RATE TABLE (FULL SET)
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
st.title("🛡️ KK-Team Smart Calculator PRO")
cust_group = st.radio("เลือกกลุ่มลูกค้า:", ["Dealer / Installer", "IT Shop / Elec Shop (+5%)"], horizontal=True)

if 'cart' not in st.session_state: st.session_state.cart = []

with st.container(border=True):
    col1, col2 = st.columns(2)
    
    with col1:
        keyword = st.text_input("🔍 พิมพ์รหัสสินค้าที่ต้องการหาหรือเพิ่มใหม่").strip().upper()
        suggestions = search_code(keyword) if keyword else []
        
        selected_code = st.selectbox("📌 รายการที่เคยบันทึก (ถ้ามี)", options=["-- พิมพ์รหัสใหม่ด้านบน --"] + suggestions)
        final_input_code = selected_code if selected_code != "-- พิมพ์รหัสใหม่ด้านบน --" else keyword
        
        # ดึงข้อมูล Auto-fill
        product = get_product(final_input_code)
        def_price, def_cat, def_sub = 0.0, list(DB_RATES.keys())[0], "สินค้า (Cable)"
        
        if not product.empty:
            def_price = float(product.iloc[0]['price'])
            def_cat = product.iloc[0]['category']
            def_sub = product.iloc[0]['sub_category']
            st.success(f"เจอราคาเดิม: {def_price:,.2f}")

        f_cat = st.selectbox("หมวดหมู่สินค้า", list(DB_RATES.keys()), index=list(DB_RATES.keys()).index(def_cat))
        f_sub = st.radio("ประเภท", ["สินค้า (Cable)", "อุปกรณ์ (Conn/Acc)"], 
                         index=0 if def_sub == "สินค้า (Cable)" else 1, horizontal=True)

    with col2:
        f_price = st.number_input("ราคาตั้ง (List Price)", value=def_price, format="%.2f")
        qty = st.number_input("จำนวนที่สั่งซื้อ", min_value=1, value=1)

# =========================
# 💰 CALCULATION ENGINE
# =========================
if st.button("🚀 คำนวณและบันทึกฐานข้อมูล", use_container_width=True):
    if not final_input_code:
        st.warning("⚠️ กรุณากรอกรหัสสินค้า")
    else:
        # 1. บันทึก/อัปเดต SQLite
        save_product(final_input_code, f_price, f_cat, f_sub)
        
        # 2. ค้นหาเรทตาม Qty
        data = DB_RATES[f_cat]
        idx = 0
        for i, v in enumerate(data["C"]):
            if qty >= v: idx = i
        
        base_rate = data["R"][idx]
        
        # 3. เงื่อนไขพิเศษ: Accessory LAN เปลี่ยน 10 เป็น 20
        if f_cat == "1. LAN (UTP)" and f_sub == "อุปกรณ์ (Conn/Acc)":
            base_rate = base_rate.replace("10", "20")
            
        # 4. เงื่อนไขกลุ่มลูกค้า (Shop +5%)
        final_rate_str = base_rate + "+5" if "IT Shop" in cust_group else base_rate
        
        # 5. คำนวณราคาสุทธิแบบละเอียด
        net_price = f_price
        calc_steps = f"{f_price:,.2f}"
        for d in [float(x) for x in final_rate_str.split("+")]:
            calc_steps += f" - {d}%"
            net_price *= (1 - d/100)
        
        # 6. บันทึกผลลงตะกร้าหน้าจอ
        unit_th = data["UT"] if f_sub == "สินค้า (Cable)" else "ชิ้น"
        range_text = f"{data['C'][idx]}-{data['C'][idx+1]-1}" if idx < len(data["C"])-1 else f"{data['C'][idx]} ขึ้นไป"
        
        res_line = f"{final_input_code}={net_price:,.2f}.-/{unit_th} ก่อนแวท (เรท {range_text}{unit_th}) *ราคาตั้ง {f_price:,.2f}*"
        res_note = f"💡 วิธีคิด: {calc_steps} = {net_price:,.2f}"
        
        st.session_state.cart.append({"main": res_line, "note": res_note})
        st.rerun()

# =========================
# 📝 OUTPUT & HISTORY
# =========================
if st.session_state.cart:
    st.divider()
    summary = []
    for item in st.session_state.cart:
        st.write(f"**{item['main']}**")
        st.caption(item['note'])
        summary.append(item['main'])
    
    st.text_area("ก๊อปปี้ไปวางใน Line:", value="\n".join(summary), height=150)
    if st.button("🗑️ ล้างรายการ"): st.session_state.cart = []; st.rerun()

# =========================
# 📊 DATABASE VIEW
# =========================
st.divider()
st.subheader("📊 ฐานข้อมูลสินค้า (SQLite)")
df_db = load_all()
st.dataframe(df_db, use_container_width=True, hide_index=True)

col_del1, col_del2 = st.columns([3,1])
code_del = col_del1.text_input("ใส่รหัสที่ต้องการลบ")
if col_del2.button("❌ ลบรายการ", use_container_width=True):
    conn = get_conn()
    conn.execute("DELETE FROM products WHERE code=?", (code_del.upper(),))
    conn.commit()
    conn.close()
    st.rerun()
