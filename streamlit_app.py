import streamlit as st

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Interlink Price Checker", page_icon="📈")

# --- 2. ระบบ Login ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ KK-Team Internal System")
    pw = st.text_input("กรุณาใส่รหัสผ่าน", type="password")
    if st.button("เข้าสู่ระบบ"):
        if pw == "KK-Team":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("รหัสไม่ถูกต้อง")
    st.stop()

# --- 3. ฟังก์ชันคำนวณ ---
def calc_net(price, discount_str):
    res = price
    for d in discount_str.split('+'):
        if d.strip():
            res *= (1 - (float(d.strip())/100))
    return res

# --- 4. ฐานข้อมูลส่วนลด 2026 ---
# U = หน่วยสากล, UT = หน่วยภาษาไทย
DB = {
    "1. LAN (UTP)": {"C": [1,3,5,10,20,30,50,100], "U": "Box", "UT": "กล่อง", "R": ["10+10","10+10+2","10+10+3","10+10+5","10+10+5+2","10+10+5+3","10+10+5+5","10+10+5+5+5"]},
    "2. FIBER OPTIC": {"C": [1,500,1000,3000,5000,8000,10000,20000,30000], "U": "M.", "UT": "เมตร", "R": ["10","10+5","10+10","10+10+3","10+10+5","10+10+5+3","10+10+5+5","10+10+5+5+3","10+10+5+5+5"]},
    "3. FTTx / FTTR": {"C": [1,3,5,10,20,30,50,100], "U": "Roll", "UT": "ม้วน", "R": ["10+10","10+10+2","10+10+3","10+10+5","10+10+5+2","10+10+5+3","10+10+5+5","10+10+5+5+5"]},
    "4. COAXIAL (RG)": {"C": [1,500,1000,3000,5000,8000,10000,20000,30000], "U": "M.", "UT": "เมตร", "R": ["20","20+5","20+10","20+10+3","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+3","20+10+5+5+5"]},
    "6. SOLAR": {"C": [1,500,1000,3000,5000,10000,20000,30000,50000], "U": "M.", "UT": "เมตร", "R": ["10","10+5","10+10","10+10+3","10+10+5","10+10+5+3","10+10+5+5","10+10+5+5+3","10+10+5+5+5"]},
    "9/10/11. RACK": {"C": [1,2,3,4,5,10,20], "U": "Unit", "UT": "ตู้", "R": ["20","20+2","20+3","20+4","20+5","20+5+5","20+5+5+3"]}
}

if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- 5. รับข้อมูล ---
st.title("🛒 เช็คราคา Interlink (2026)")
cust_group = st.radio("กลุ่มลูกค้า:", ["Dealer / Installer", "IT Shop / Elec Shop (+5%)"], horizontal=True)

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        p_code = st.text_input("รหัสสินค้า (เช่น US-9106A)")
        cat = st.selectbox("หมวดหมู่สินค้า", list(DB.keys()))
        mode = st.radio("ประเภท", ["สินค้า (Cable)", "อุปกรณ์ (Conn/Acc)"], horizontal=True)
    with col2:
        list_p = st.number_input("ราคาตั้ง (List Price)", min_value=0.0, step=10.0)
        qty = st.number_input("จำนวนที่สั่งซื้อ", min_value=1, step=1)

    is_face = (cat == "1. LAN (UTP)" and mode == "อุปกรณ์ (Conn/Acc)")
    if is_face:
        is_face_check = st.checkbox("เป็นรายการ Face Plate / Cable Mgmt")

    if st.button("🔍 ตรวจสอบราคา", use_container_width=True):
        data = DB[cat]
        counts = data["C"]
        idx = 0
        for i, v in enumerate(counts):
            if qty >= v: idx = i
        
        # คำนวณช่วงจำนวน (เช่น 1-2, 3-4 หรือ 100 ขึ้นไป)
        if idx < len(counts) - 1:
            range_text = f"{counts[idx]}-{counts[idx+1]-1}"
        else:
            range_text = f"{counts[idx]} ขึ้นไป"

        base_rate = data["R"][idx]
        if is_face and is_face_check: base_rate = base_rate.replace("10", "20")
        
        final_rate = base_rate
        if "IT Shop" in cust_group: final_rate += "+5"
            
        net_unit = calc_net(list_p, final_rate)
        unit_th = data["UT"] if mode == "สินค้า (Cable)" else "ชิ้น"
        
        # สร้างรูปแบบคำตอบที่คุณต้องการ
        display_name = p_code if p_code else cat
        result_line = f"{display_name}={net_unit:,.2f}.-/{unit_th} ก่อนแวท (เรท {range_text}{unit_th})"
        
        st.session_state.cart.append({
            "text": result_line,
            "total": net_unit * qty
        })
        st.toast("บันทึกข้อมูลแล้ว")

# --- 6. แสดงผลลัพธ์ ---
if st.session_state.cart:
    st.divider()
    st.subheader(f"📋 สรุปราคา (กลุ่ม {cust_group})")
    
    grand_total = 0
    lines_for_copy = []
    
    for item in st.session_state.cart:
        st.write(item["text"])
        lines_for_copy.append(item["text"])
        grand_total += item["total"]
        
    st.info(f"💰 ยอดรวมก่อน VAT: {grand_total:,.2f} บาท")
    
    full_msg = f"*ราคา Interlink ({cust_group})*\n"
    full_msg += "------------------------------\n"
    full_msg += "\n".join(lines_for_copy)
    full_msg += f"\n------------------------------\n💰 ยอดรวมก่อน VAT: {grand_total:,.2f} บาท"
    
    st.text_area("ก๊อปปี้ไปวางใน Line:", value=full_msg, height=180)
    
    if st.button("🗑️ ล้างข้อมูล"):
        st.session_state.cart = []
        st.rerun()
