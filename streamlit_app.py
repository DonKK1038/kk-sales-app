import streamlit as st
import pandas as pd
import os

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Interlink Smart Database", page_icon="🛡️", layout="wide")

# --- 2. ระบบจัดการ Database (เพิ่มคอลัมน์หมวดหมู่) ---
DB_FILE = "database_v2.csv"

def load_data():
    cols = ["code", "price", "category", "sub_category"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # ตรวจสอบว่ามีคอลัมน์ครบไหม ถ้าไม่ครบให้สร้างใหม่
            if not all(c in df.columns for c in cols):
                return pd.DataFrame(columns=cols)
            df['code'] = df['code'].astype(str).str.strip().upper()
            return df.drop_duplicates(subset=['code'], keep='last')
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_data(code, price, cat, sub_cat):
    df = load_data()
    code = str(code).strip().upper()
    if not code: return 
    # ลบอันเก่า บันทึกอันใหม่ (Overwrite)
    df = df[df['code'] != code]
    new_entry = pd.DataFrame([{"code": code, "price": float(price), "category": cat, "sub_category": sub_cat}])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- 3. ข้อมูลเรทส่วนลด (คงเดิม) ---
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

# --- 4. หน้าจอ UI ---
if 'cart' not in st.session_state: st.session_state.cart = []

tab1, tab2 = st.tabs(["🛒 คำนวณราคาอัจฉริยะ", "⚙️ จัดการฐานข้อมูล"])

with tab1:
    st.header("Interlink Smart Pro (2026)")
    cust_group = st.radio("เลือกกลุ่มลูกค้า:", ["Dealer / Installer", "IT Shop / Elec Shop (+5%)"], horizontal=True)

    # โหลดข้อมูล
    master_df = load_data()
    all_codes = master_df['code'].tolist()

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            # --- ช่องค้นหา/กรอก อันเดียวจบ ---
            search_code = st.selectbox("🔍 ค้นหารหัสสินค้า (หรือพิมพ์ใหม่ลงไป)", options=all_codes, index=None, placeholder="พิมพ์รหัสที่นี่...")
            
            # ดึงข้อมูลจากฐานข้อมูลถ้าเลือกรายการเดิม
            saved_price, saved_cat, saved_sub = 0.0, list(DB_RATES.keys())[0], "สินค้า (Cable)"
            if search_code:
                row = master_df[master_df['code'] == search_code].iloc[0]
                saved_price = float(row['price'])
                saved_cat = row['category']
                saved_sub = row['sub_category']

            final_cat = st.selectbox("หมวดหมู่สินค้า", list(DB_RATES.keys()), index=list(DB_RATES.keys()).index(saved_cat))
            final_sub = st.radio("ประเภท", ["สินค้า (Cable)", "อุปกรณ์ (Conn/Acc)"], index=0 if saved_sub == "สินค้า (Cable)" else 1, horizontal=True)

        with col2:
            final_price = st.number_input("ราคาตั้ง (List Price)", min_value=0.0, value=saved_price, format="%.2f")
            qty = st.number_input("จำนวนที่สั่งซื้อ", min_value=1, value=1)

        if st.button("🚀 คำนวณและบันทึกข้อมูล", use_container_width=True):
            if not search_code:
                st.warning("⚠️ โปรดพิมพ์รหัสสินค้าก่อน")
            else:
                # 1. บันทึกข้อมูลลง DB แบบ Real-time (รหัส + ราคา + หมวดหมู่)
                save_data(search_code, final_price, final_cat, final_sub)
                
                # 2. คำนวณราคา
                data = DB_RATES[final_cat]
                idx = 0
                for i, v in enumerate(data["C"]):
                    if qty >= v: idx = i
                
                base_rate = data["R"][idx]
                if (final_cat == "1. LAN (UTP)" and final_sub == "อุปกรณ์ (Conn/Acc)"):
                    base_rate = base_rate.replace("10", "20") # สูตร Faceplate
                
                final_rate = base_rate + "+5" if "IT Shop" in cust_group else base_rate
                
                # Logic คำนวณลดหลั่น
                current_p = final_price
                for d in [float(x) for x in final_rate.split('+')]:
                    current_p *= (1 - d/100)
                
                unit_th = data["UT"] if final_sub == "สินค้า (Cable)" else "ชิ้น"
                res = f"{search_code}={current_p:,.2f}.-/{unit_th} (เรท {qty} {unit_th})"
                st.session_state.cart.append(res)
                st.success("บันทึกและคำนวณเรียบร้อย!")
                st.rerun()

    # แสดงตะกร้าสินค้า
    if st.session_state.cart:
        st.divider()
        st.text_area("รายการราคาสำหรับส่งต่อ:", value="\n".join(st.session_state.cart), height=150)
        if st.button("🗑️ ล้างรายการ"):
            st.session_state.cart = []; st.rerun()

with tab2:
    st.subheader("ฐานข้อมูลสินค้าทั้งหมด")
    st.dataframe(load_data(), use_container_width=True, hide_index=True)
    if st.button("⚠️ ล้างฐานข้อมูลทั้งหมด (ระวัง!)"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()
