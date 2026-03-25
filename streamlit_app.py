import streamlit as st
import pandas as pd
import os

# --- 1. ตั้งค่าพื้นฐาน ---
st.set_page_config(page_title="KK-Team Smart System", layout="wide")
DB_FILE = "interlink_database_v5.csv"

# --- 2. ฟังก์ชันจัดการฐานข้อมูล (ปรับปรุงให้บันทึกทันที) ---
def load_data():
    cols = ["code", "price", "category", "sub_category"]
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['code'] = df['code'].astype(str).str.strip().upper()
        return df.drop_duplicates(subset=['code'], keep='last')
    return pd.DataFrame(columns=cols)

def force_save(code, price, cat, sub_cat):
    df = load_data()
    code = str(code).strip().upper()
    # ลบของเก่าออกก่อน (Overwrite)
    df = df[df['code'] != code]
    # เพิ่มของใหม่
    new_row = pd.DataFrame([{"code": code, "price": float(price), "category": cat, "sub_category": sub_cat}])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    return df

# --- 3. ระบบ Login ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 KK-Team Internal System")
    pw = st.text_input("กรุณาใส่รหัสผ่าน", type="password")
    if st.button("เข้าสู่ระบบ"):
        if pw == "KK-Team":
            st.session_state.auth = True
            st.rerun()
        else: st.error("รหัสไม่ถูกต้อง")
    st.stop()

# --- 4. ข้อมูลเรทส่วนลด (คงเดิมตามมาตรฐาน) ---
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

# --- 5. การแสดงผลหน้าหลัก ---
if 'cart' not in st.session_state: st.session_state.cart = []

tab1, tab2 = st.tabs(["🛒 คำนวณราคา", "📊 ฐานข้อมูล"])

with tab1:
    st.header("Interlink Price Calculator")
    cust_group = st.radio("กลุ่มลูกค้า:", ["Dealer / Installer", "IT Shop (+5%)"], horizontal=True)
    
    master_df = load_data()
    
    # --- ส่วนรับข้อมูล (ใช้ Form เพื่อบังคับบันทึก) ---
    with st.form("calc_form"):
        col1, col2 = st.columns(2)
        with col1:
            input_code = st.text_input("🔍 รหัสสินค้า (พิมพ์รหัสใหม่หรือเดิมก็ได้)").strip().upper()
            
            # ดึงข้อมูลเก่ามาตั้งต้นถ้ามี
            match = master_df[master_df['code'] == input_code]
            s_price, s_cat, s_sub = 0.0, list(DB_RATES.keys())[0], "สินค้า (Cable)"
            if not match.empty:
                s_price = float(match.iloc[0]['price'])
                s_cat = match.iloc[0]['category']
                s_sub = match.iloc[0]['sub_category']
                st.info(f"ดึงข้อมูลเดิม: {s_cat} | ราคา {s_price:,.2f}")

            f_cat = st.selectbox("หมวดหมู่", list(DB_RATES.keys()), index=list(DB_RATES.keys()).index(s_cat))
            f_sub = st.radio("ประเภท", ["สินค้า (Cable)", "อุปกรณ์ (Conn/Acc)"], index=0 if s_sub == "สินค้า (Cable)" else 1, horizontal=True)
            
        with col2:
            f_price = st.number_input("ราคาตั้ง (List Price)", value=s_price, format="%.2f")
            qty = st.number_input("จำนวนที่สั่งซื้อ", min_value=1, value=1)
            
        submit = st.form_submit_button("🚀 คำนวณและบันทึกฐานข้อมูลทันที", use_container_width=True)

        if submit:
            if not input_code:
                st.error("กรุณาใส่รหัสสินค้า!")
            else:
                # บันทึกเข้า DB ทันที
                save_to_db = force_save(input_code, f_price, f_cat, f_sub)
                
                # คำนวณราคาแบบละเอียด
                data = DB_RATES[f_cat]
                idx = 0
                for i, v in enumerate(data["C"]):
                    if qty >= v: idx = i
                
                base_rate = data["R"][idx]
                if (f_cat == "1. LAN (UTP)" and f_sub == "อุปกรณ์ (Conn/Acc)"):
                    base_rate = base_rate.replace("10", "20")
                
                final_rate = base_rate + "+5" if "IT Shop" in cust_group else base_rate
                
                # คิดเงินแบบ Step-by-Step
                current_p = f_price
                calc_steps = f"{f_price:,.2f}"
                for d in [float(x) for x in final_rate.split('+')]:
                    calc_steps += f" - {d}%"
                    current_p *= (1 - d/100)
                
                unit = data["UT"] if f_sub == "สินค้า (Cable)" else "ชิ้น"
                res_line = f"{input_code}={current_p:,.2f}.-/{unit} (เรทสั่งซื้อ {qty} {unit})"
                res_note = f"💡 วิธีคิด: {calc_steps} = {current_p:,.2f}"
                
                st.session_state.cart.append({"main": res_line, "note": res_note})
                st.success("บันทึกข้อมูลเข้าตารางเรียบร้อย!")
                st.rerun()

    # แสดงผลตะกร้า
    if st.session_state.cart:
        st.divider()
        copy_text = []
        for item in st.session_state.cart:
            st.write(f"**{item['main']}**")
            st.caption(item['note'])
            copy_text.append(item['main'])
        st.text_area("ก๊อปปี้ไปวางใน Line:", value="\n".join(copy_text))
        if st.button("🗑️ ล้างรายการ"): st.session_state.cart = []; st.rerun()

with tab2:
    st.subheader("📊 ตารางฐานข้อมูล (อัปเดตแบบ Real-time)")
    display_df = load_data()
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    if st.button("🔄 บังคับรีเฟรชตาราง"): st.rerun()
