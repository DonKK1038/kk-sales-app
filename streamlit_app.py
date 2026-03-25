import streamlit as st

# --- 1. ตั้งค่าหน้าจอ (UI Config) ---
st.set_page_config(page_title="Interlink Sales Master (KK-Team)", page_icon="📈")

# --- 2. ระบบ Login ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ KK-Team Internal System")
    pw = st.text_input("กรุณาใส่รหัสผ่านเข้าใช้งาน", type="password")
    if st.button("เข้าสู่ระบบ"):
        if pw == "KK-Team":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("รหัสไม่ถูกต้อง")
    st.stop()

# --- 3. ฟังก์ชันคำนวณราคา Net (Recursive Discount) ---
def calc_net(price, discount_str):
    res = price
    for d in discount_str.split('+'):
        if d.strip():
            res *= (1 - (float(d.strip())/100))
    return res

# --- 4. ฐานข้อมูลส่วนลด 2026 (ครบทุกหมวดสินค้า) ---
DB = {
    "1. LAN (UTP)": {"C": [1,3,5,10,20,30,50,100], "U": "Box", "R": ["10+10","10+10+2","10+10+3","10+10+5","10+10+5+2","10+10+5+3","10+10+5+5","10+10+5+5+5"]},
    "2. FIBER OPTIC": {"C": [1,500,1000,3000,5000,8000,10000,20000,30000], "U": "M.", "R": ["10","10+5","10+10","10+10+3","10+10+5","10+10+5+3","10+10+5+5","10+10+5+5+3","10+10+5+5+5"]},
    "3. FTTx / FTTR": {"C": [1,3,5,10,20,30,50,100], "U": "Roll", "R": ["10+10","10+10+2","10+10+3","10+10+5","10+10+5+2","10+10+5+3","10+10+5+5","10+10+5+5+5"]},
    "4. COAXIAL (RG)": {"C": [1,500,1000,3000,5000,8000,10000,20000,30000], "U": "M.", "R": ["20","20+5","20+10","20+10+3","20+10+5","20+10+5+3","20+10+5+5","20+10+5+5+3","20+10+5+5+5"]},
    "6. SOLAR": {"C": [1,500,1000,3000,5000,10000,20000,30000,50000], "U": "M.", "R": ["10","10+5","10+10","10+10+3","10+10+5","10+10+5+3","10+10+5+5","10+10+5+5+3","10+10+5+5+5"]},
    "9/10/11. 19\" RACK": {"C": [1,2,3,4,5,10,20], "U": "Unit", "R": ["20","20+2","20+3","20+4","20+5","20+5+5","20+5+5+3"]}
}

if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- 5. หน้าจอการใช้งาน ---
st.title("🛒 Interlink Sales Master (2026)")
cust_group = st.radio("เลือกกลุ่มลูกค้าเพื่อคิดเรทราคา:", ["Dealer / Installer", "IT Shop / Elec Shop (+5%)"], horizontal=True)

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        p_code = st.text_input("รหัสสินค้า (ระบุหรือไม่ก็ได้)")
        cat = st.selectbox("เลือกหมวดหมู่สินค้า", list(DB.keys()))
        mode = st.radio("ประเภทรายการ", ["สินค้า (Cable)", "อุปกรณ์ (Conn/Acc)"], horizontal=True)
    with col2:
        list_p = st.number_input("ราคาตั้งต่อหน่วย (List Price)", min_value=0.0, step=10.0)
        qty = st.number_input("จำนวนที่สั่งซื้อ", min_value=1, step=1)
    
    # กรณีพิเศษ LAN อุปกรณ์
    is_face = False
    if cat == "1. LAN (UTP)" and mode == "อุปกรณ์ (Conn/Acc)":
        is_face = st.checkbox("เป็นรายการ Face Plate / Cable Management (ฐาน 20%)")

    if st.button("📥 เพิ่มเข้าตะกร้าสินค้า", use_container_width=True):
        data = DB[cat]
        idx = 0
        for i, v in enumerate(data["C"]):
            if qty >= v: idx = i
        
        # เลือกเรทพื้นฐาน
        base_rate = data["R"][idx]
        
        # ปรับฐานตามเงื่อนไข Face Plate
        if is_face:
            base_rate = base_rate.replace("10", "20")
        
        # บวกส่วนลดกลุ่มร้านค้า
        final_rate = base_rate
        if "IT Shop" in cust_group:
            final_rate += "+5"
            
        net_unit = calc_net(list_p, final_rate)
        
        st.session_state.cart.append({
            "name": p_code if p_code else cat,
            "net": net_unit,
            "unit": data["U"] if mode == "สินค้า (Cable)" else "Pcs",
            "rate": final_rate,
            "qty": qty,
            "total": net_unit * qty
        })
        st.toast("เพิ่มรายการสำเร็จ!")

# --- 6. สรุปรายการเสนอราคา ---
if st.session_state.cart:
    st.divider()
    st.subheader(f"📋 สรุปรายการ Net (กลุ่ม {cust_group})")
    
    copy_lines = []
    grand_total = 0
    
    for i, item in enumerate(st.session_state.cart):
        line = f"{i+1}. {item['name']} = {item['net']:,.2f}/{item['unit']} (เรท {item['rate']})"
        st.write(line)
        copy_lines.append(line)
        grand_total += item['total']
        
    st.success(f"💰 ยอดรวม Net ทั้งสิ้น: {grand_total:,.2f} บาท")
    st.caption("ราคาข้างต้นเป็นราคา Net ที่หักส่วนลดแล้ว และไม่รวมภาษีมูลค่าเพิ่ม (Vat)")
    
    # ข้อความสำหรับก๊อปปี้ไปวางใน Line
    full_msg = f"*ใบเสนอราคาจำลอง Interlink (กลุ่ม {cust_group})*\n"
    full_msg += "------------------------------\n"
    full_msg += "\n".join(copy_lines)
    full_msg += f"\n------------------------------\n💰 ยอดรวม Net ทั้งสิ้น: {grand_total:,.2f} บาท\n*(อ้างอิงราคา Discount Rate 2026)*"
    
    st.text_area("ก๊อปปี้ข้อความไปวางใน Line:", value=full_msg, height=200)
    
    if st.button("🗑️ ล้างรายการทั้งหมด"):
        st.session_state.cart = []
        st.rerun()
