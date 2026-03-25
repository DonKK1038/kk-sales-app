import streamlit as st
import pandas as pd
import os

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Interlink Smart Pro", page_icon="🛡️", layout="wide")

# --- 2. ระบบจัดการ Database ---
DB_FILE = "database_v3.csv"

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

def save_data(code, price, cat, sub_cat):
    df = load_data()
    code = str(code).strip().upper()
    if not code: return 
    df = df[df['code'] != code]
    new_entry = pd.DataFrame([{"code": code, "price": float(price), "category": cat, "sub_category": sub_cat}])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- 3. ข้อมูลเรทส่วนลด ---
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

tab1, tab2 = st.tabs(["🛒 เช็คราคา", "⚙️ ฐานข้อมูล"])

with tab1:
    st.header("Interlink Smart Pro")
    cust_group = st.radio("กลุ่มลูกค้า:", ["Dealer / Installer", "IT Shop (+5%)"], horizontal=True)

    master_df = load_data()
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            # 💥 ช่องเดียวจบ: ใช้ text_input แทน selectbox เพื่อความอิสระ
            input_code = st.text_input("🔍 รหัสสินค้า (พิมพ์รหัสใหม่ได้ทันที)", key="main_code_input").strip().upper()
            
            # ตรวจสอบว่ารหัสที่พิมพ์มีในฐานข้อมูลไหม
            match = master_df[master_df['code'] == input_code]
            saved_price, saved_cat, saved_sub = 0.0, list(DB_RATES.keys())[0], "สินค้า (Cable)"
            
            if not match.empty:
                saved_price = float(match.iloc[0]['price'])
                saved_cat = match.iloc[0]['category']
                saved_sub = match.iloc[0]['sub_category']
                st.success(f"✅ พบข้อมูลเก่า: {saved_cat} / {saved_sub}")

            final_cat = st.selectbox("หมวดหมู่", list(DB_RATES.keys()), index=list(DB_RATES.keys()).index(saved_cat))
            final_sub = st.radio("ประเภท", ["สินค้า (Cable)", "อุปกรณ์ (Conn/Acc)"], index=0 if saved_sub == "สินค้า (Cable)" else 1, horizontal=True)

        with col2:
            final_price = st.number_input("ราคาตั้ง (List Price)", min_value=0.0, value=saved_price, format="%.2f", step=1.0)
            qty = st.number_input("จำนวน", min_value=1, value=1)

        if st.button("🚀 คำนวณและบันทึก", use_container_width=True):
            if not input_code:
                st.warning("⚠️ โปรดใส่รหัสสินค้า")
            else:
                # บันทึกข้อมูล Real-time
                save_data(input_code, final_price, final_cat, final_sub)
                
                # คำนวณราคา
                data = DB_RATES[final_cat]
                idx = 0
                for i, v in enumerate(data["C"]):
                    if qty >= v: idx = i
                
                base_rate = data["R"][idx]
                if (final_cat == "1. LAN (UTP)" and final_sub == "อุปกรณ์ (Conn/Acc)"):
                    base_rate = base_rate.replace("10", "20")
                
                final_rate = base_rate + "+5" if "IT Shop" in cust_group else base_rate
                
                # คิดเงิน
                current_p = final_price
                for d in [float(x) for x in final_rate.split('+')]:
                    current_p *= (1 - d/100)
                
                unit_th = data["UT"] if final_sub == "สินค้า (Cable)" else "ชิ้น"
                st.session_state.cart.append(f"{input_code}={current_p:,.2f}.-/{unit_th} (เรท {qty})")
                st.rerun()

    if st.session_state.cart:
        st.divider()
        st.text_area("รายการ:", value="\n".join(st.session_state.cart), height=120)
        if st.button("🗑️ ล้าง"): st.session_state.cart = []; st.rerun()

with tab2:
    st.subheader("จัดการฐานข้อมูล")
    df_show = load_data()
    st.dataframe(df_show, use_container_width=True, hide_index=True)
    
    col_del1, col_del2 = st.columns([3,1])
    code_to_del = col_del1.text_input("พิมพ์รหัสที่ต้องการลบ")
    if col_del2.button("❌ ลบข้อมูล", use_container_width=True):
        if code_to_del:
            df_new = df_show[df_show['code'] != code_to_del.upper()]
            df_new.to_csv(DB_FILE, index=False)
            st.rerun()
