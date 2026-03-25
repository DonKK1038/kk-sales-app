import streamlit as st
import pandas as pd
import os

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Interlink Smart Pro", page_icon="🛡️", layout="wide")

# --- 2. ระบบจัดการ Database ---
DB_FILE = "database_final.csv"

def load_data():
    cols = ["code", "price", "category", "sub_category"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if not all(c in df.columns for c in cols): return pd.DataFrame(columns=cols)
            df['code'] = df['code'].astype(str).str.strip().upper()
            return df.drop_duplicates(subset=['code'], keep='last')
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_to_db(code, price, cat, sub_cat):
    df = load_data()
    code = str(code).strip().upper()
    if not code: return 
    # ลบข้อมูลเก่าถ้ามีรหัสซ้ำ เพื่ออัปเดตราคา/หมวดหมู่ล่าสุด
    df = df[df['code'] != code]
    new_data = pd.DataFrame([{"code": code, "price": float(price), "category": cat, "sub_category": sub_cat}])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    return df

# --- 3. ฟังก์ชันคำนวณแบบละเอียด ---
def get_calculation_detail(price, discount_str):
    current_price = price
    discounts = [d.strip() for d in discount_str.split('+') if d.strip()]
    calc_text = f"{price:,.2f}"
    for d in discounts:
        calc_text += f" - {d}%"
        current_price *= (1 - float(d)/100)
    return current_price, calc_text

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

# --- 4. หน้าจอหลัก ---
if 'cart' not in st.session_state: st.session_state.cart = []

tab1, tab2 = st.tabs(["🛒 เช็คราคา & คำนวณ", "⚙️ จัดการฐานข้อมูล"])

with tab1:
    st.header("ตรวจสอบราคา Interlink (2026)")
    cust_group = st.radio("เลือกกลุ่มลูกค้า:", ["Dealer / Installer", "IT Shop / Elec Shop (+5%)"], horizontal=True)

    master_df = load_data()
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            # --- ช่องเดียวจบ ---
            input_code = st.text_input("🔍 รหัสสินค้า (พิมพ์เพื่อหาหรือเพิ่มใหม่)", key="input_code_box").strip().upper()
            
            # ดึงข้อมูล Auto-fill
            match = master_df[master_df['code'] == input_code]
            s_price, s_cat, s_sub = 0.0, list(DB_RATES.keys())[0], "สินค้า (Cable)"
            
            if not match.empty:
                s_price = float(match.iloc[0]['price'])
                s_cat = match.iloc[0]['category']
                s_sub = match.iloc[0]['sub_category']
                st.success(f"📌 ข้อมูลเดิม: {s_cat} | ราคาล่าสุด {s_price:,.2f}")

            f_cat = st.selectbox("หมวดหมู่สินค้า", list(DB_RATES.keys()), index=list(DB_RATES.keys()).index(s_cat))
            f_sub = st.radio("ประเภท", ["สินค้า (Cable)", "อุปกรณ์ (Conn/Acc)"], index=0 if s_sub == "สินค้า (Cable)" else 1, horizontal=True)

        with col2:
            f_price = st.number_input("ราคาตั้ง (List Price)", min_value=0.0, value=s_price, format="%.2f", step=0.01)
            qty = st.number_input("จำนวนที่สั่งซื้อ", min_value=1, value=1)

        if st.button("🚀 คำนวณและบันทึกข้อมูล", use_container_width=True):
            if not input_code:
                st.warning("⚠️ กรุณากรอกรหัสสินค้า")
            else:
                # 1. บันทึกเข้าฐานข้อมูล (Real-time)
                save_to_db(input_code, f_price, f_cat, f_sub)
                
                # 2. คำนวณราคาแบบละเอียด
                data = DB_RATES[f_cat]
                idx = 0
                for i, v in enumerate(data["C"]):
                    if qty >= v: idx = i
                
                base_rate = data["R"][idx]
                # กรณี Faceplate LAN
                if (f_cat == "1. LAN (UTP)" and f_sub == "อุปกรณ์ (Conn/Acc)"):
                    base_rate = base_rate.replace("10", "20")
                
                final_rate = base_rate + "+5" if "IT Shop" in cust_group else base_rate
                net_unit, calc_steps = get_calculation_detail(f_price, final_rate)
                
                unit_th = data["UT"] if f_sub == "สินค้า (Cable)" else "ชิ้น"
                range_text = f"{data['C'][idx]}-{data['C'][idx+1]-1}" if idx < len(data["C"])-1 else f"{data['C'][idx]} ขึ้นไป"

                # 3. สร้างข้อความคำตอบแบบยาว (เหมือนเวอร์ชันเดิมที่คุณชอบ)
                result_line = f"{input_code}={net_unit:,.2f}.-/{unit_th} ก่อนแวท (เรท {range_text}{unit_th}) *หมายเหตุ ราคาตั้ง {f_price:,.2f}*"
                calc_note = f"💡 วิธีคิด: {calc_steps} = {net_unit:,.2f}"
                
                st.session_state.cart.append({"text": result_line, "note": calc_note})
                st.rerun()

    # แสดงตะกร้าสินค้า
    if st.session_state.cart:
        st.divider()
        all_text = []
        for item in st.session_state.cart:
            st.write(f"**{item['text']}**")
            st.caption(item["note"])
            all_text.append(item['text'])
        
        st.text_area("คัดลอกข้อความ:", value="\n".join(all_text), height=150)
        if st.button("🗑️ ล้างรายการ"):
            st.session_state.cart = []; st.rerun()

with tab2:
    st.subheader("ฐานข้อมูลสินค้า (ตรวจสอบการบันทึก)")
    db_display = load_data()
    st.dataframe(db_display, use_container_width=True, hide_index=True)
    
    if st.button("📥 อัปเดตตาราง"): st.rerun()
