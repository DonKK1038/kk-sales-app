import streamlit as st
import pandas as pd
import os

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Interlink Smart Pro (KK-Team)", page_icon="🛡️", layout="wide")

# --- 2. ระบบจัดการไฟล์ Database ---
DB_FILE = "database.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['code'] = df['code'].astype(str).str.strip().upper()
        return df.drop_duplicates(subset=['code'], keep='last')
    return pd.DataFrame(columns=["code", "price"])

def save_data(code, price):
    df = load_data()
    code = str(code).strip().upper()
    if not code: return 
    df = df[df['code'] != code]
    new_entry = pd.DataFrame([{"code": code, "price": float(price)}])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

def delete_data(code):
    df = load_data()
    df = df[df['code'] != code]
    df.to_csv(DB_FILE, index=False)

if 'master_data' not in st.session_state:
    st.session_state.master_data = load_data()

# --- 3. ระบบ Login ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 KK-Team Internal System")
    pw = st.text_input("กรุณาใส่รหัสผ่าน", type="password")
    if st.button("เข้าสู่ระบบ"):
        if pw == "KK-Team":
            st.session_state.auth = True; st.rerun()
        else: st.error("รหัสไม่ถูกต้อง")
    st.stop()

# --- 4. ฟังก์ชันคำนวณ ---
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

if 'cart' not in st.session_state: st.session_state.cart = []

# --- ฟังก์ชันช่วยเหลือสำหรับพิมพ์ปุ่มประวัติ ---
def set_search_code(code):
    st.session_state.search_code_input = code

# --- 5. ส่วนหน้าจอแสดงผล (Tabs) ---
tab1, tab2 = st.tabs(["🛒 เช็คราคา & คำนวณ", "⚙️ จัดการฐานข้อมูลสินค้า"])

with tab1:
    st.header("ตรวจสอบราคา Interlink (2026)")
    cust_group = st.radio("เลือกกลุ่มลูกค้า:", ["Dealer / Installer", "IT Shop / Elec Shop (+5%)"], horizontal=True)

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.master_data = load_data()
            codes_list = st.session_state.master_data['code'].tolist()
            
            # 💥 1. ช่องป้อนรหัส (ช่องเดียวจบ!)
            final_code = st.text_input("🔍 รหัสสินค้า (พิมพ์เพื่อหา หรือ เพิ่มของใหม่ได้เลย)", key="search_code_input").strip().upper()
            
            # 💥 2. ระบบ Auto-suggest แสดงปุ่มกดเมื่อพิมพ์ตรงกับประวัติ
            if final_code and final_code not in codes_list:
                matches = [c for c in codes_list if final_code in c]
                if matches:
                    st.caption("💡 พบรหัสใกล้เคียงในระบบ (คลิกเพื่อเลือก):")
                    btn_cols = st.columns(min(len(matches), 4)) # แสดงสูงสุด 4 ปุ่ม
                    for i, m in enumerate(matches[:4]):
                        btn_cols[i].button(m, on_click=set_search_code, args=(m,), use_container_width=True)
            
            cat = st.selectbox("หมวดหมู่สินค้า", list(DB_RATES.keys()))
            mode = st.radio("ประเภท", ["สินค้า (Cable)", "อุปกรณ์ (Conn/Acc)"], horizontal=True)

        with col2:
            # ดึงราคาตั้งมาโชว์อัตโนมัติ 
            auto_price = 0.0
            if final_code and (final_code in codes_list):
                match = st.session_state.master_data[st.session_state.master_data['code'] == final_code]
                if not match.empty:
                    auto_price = float(match.iloc[0]['price'])
            
            list_p = st.number_input("ราคาตั้ง (List Price)", min_value=0.0, value=auto_price, step=10.0, format="%.2f")
            qty = st.number_input("จำนวนที่สั่งซื้อ", min_value=1, step=1)

        is_face = (cat == "1. LAN (UTP)" and mode == "อุปกรณ์ (Conn/Acc)")
        if is_face: is_face_check = st.checkbox("เป็นรายการ Face Plate / Cable Mgmt (ฐาน 20%)")

        if st.button("🔍 ตรวจสอบและบันทึกราคา", use_container_width=True):
            if not final_code:
                st.warning("⚠️ กรุณากรอกรหัสสินค้าก่อนคำนวณ")
            else:
                # บันทึกหรือเขียนทับราคาลง Database ทันที
                save_data(final_code, list_p)
                st.session_state.master_data = load_data()
                
                data = DB_RATES[cat]
                idx = 0
                for i, v in enumerate(data["C"]):
                    if qty >= v: idx = i
                
                range_text = f"{data['C'][idx]}-{data['C'][idx+1]-1}" if idx < len(data["C"])-1 else f"{data['C'][idx]} ขึ้นไป"
                base_rate = data["R"][idx]
                if is_face and is_face_check: base_rate = base_rate.replace("10", "20")
                final_rate = base_rate + "+5" if "IT Shop" in cust_group else base_rate
                    
                net_unit, calc_steps = get_calculation_detail(list_p, final_rate)
                unit_th = data["UT"] if mode == "สินค้า (Cable)" else "ชิ้น"
                
                result_line = f"{final_code}={net_unit:,.2f}.-/{unit_th} ก่อนแวท (เรท {range_text}{unit_th}) *หมายเหตุ ราคาตั้ง {list_p:,.2f}*"
                st.session_state.cart.append({"text": result_line, "total": net_unit * qty, "calc_note": f"💡 วิธีคิด: {calc_steps} = {net_unit:,.2f}"})
                st.rerun()

    # แสดงรายการที่คำนวณไว้
    if st.session_state.cart:
        st.divider()
        grand_total = 0
        lines = []
        for item in st.session_state.cart:
            st.write(f"**{item['text']}**")
            st.caption(item["calc_note"])
            lines.append(item["text"])
            grand_total += item["total"]
        
        st.info(f"💰 ยอดรวมก่อน VAT: {grand_total:,.2f} บาท")
        full_msg = f"*ราคา Interlink ({cust_group})*\n---\n" + "\n".join(lines) + f"\n---\n💰 ยอดรวมก่อน VAT: {grand_total:,.2f} บาท"
        st.text_area("คัดลอกข้อความไปวางใน Line:", value=full_msg, height=150)
        if st.button("🗑️ ล้างรายการทั้งหมด"):
            st.session_state.cart = []; st.rerun()

with tab2:
    st.header("⚙️ ระบบจัดการข้อมูลหลังบ้าน")
    current_db = load_data()
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("รายการสินค้าที่บันทึกไว้")
        if not current_db.empty:
            st.dataframe(current_db, use_container_width=True, hide_index=True)
        else:
            st.info("ยังไม่มีข้อมูลในระบบ")
            
    with col_b:
        st.subheader("เครื่องมือจัดการ")
        existing_codes = current_db['code'].tolist()
        del_code = st.selectbox("เลือกรหัสที่ต้องการลบ", ["-- เลือก --"] + existing_codes)
        if st.button("❌ ยืนยันการลบ", type="primary"):
            if del_code != "-- เลือก --":
                delete_data(del_code)
                st.success(f"ลบ {del_code} เรียบร้อย!")
                st.rerun()
        
        st.divider()
        csv_data = current_db.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ Database (CSV)",
            data=csv_data,
            file_name='interlink_db.csv',
            mime='text/csv',
        )
