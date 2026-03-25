คุณส่ง
import streamlit as st

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Interlink Sales Master (KK-Team)", layout="wide")

# --- ระบบ Login ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 เข้าสู่ระบบ (KK-Team Only)")
    username = st.text_input("กรุณากรอก Username", placeholder="ระบุชื่อทีมของคุณ")
    if st.button("ตกลง"):
        if username == "KK-Team":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Username ไม่ถูกต้อง")
    st.stop()

# --- ฟังก์ชันคำนวณราคา Net ---
def calculate_net(list_price, discount_str):
    current = list_price
    for p in discount_str.split('+'):
        try:
            val = p.strip()
            if val:
                current *= (1 - (float(val)/100))
        except:
            pass
    return current

# --- ฐานข้อมูลส่วนลด 2569 (รวม FTTx/FTTR แล้ว) ---
DATA = {
    "1. LAN (UTP)": {
        "CABLE": {"tiers": [1, 3, 5, 10, 20, 30, 50, 100], "unit": "Box", "rates": ["10+10", "10+10+2", "10+10+3", "10+10+5", "10+10+5+2", "10+10+5+3", "10+10+5+5", "10+10+5+5+5"]},
        "CONN": {"low": [1, 10, 30, 50, 100, 200, 300, 500, 1000], "high": [1, 2, 3, 5, 10, 20, 30, 50, 100], "unit": "Pcs", "rates": ["10", "10+2", "10+3", "10+5", "10+10", "10+10+5", "10+10+5+3", "10+10+5+5", "10+10+5+5+5"]}
    },
    "2. FIBER OPTIC": {
        "CABLE": {"tiers": [1, 500, 1000, 3000, 5000, 8000, 10000, 20000, 30000], "unit": "M.", "rates": ["10", "10+5", "10+10", "10+10+3", "10+10+5", "10+10+5+3", "10+10+5+5", "10+10+5+5+3", "10+10+5+5+5"]},
        "CONN": {"low": [1, 10, 30, 50, 100, 200, 300, 500, 1000], "high": [1, 2, 3, 5, 10, 20, 30, 50, 100], "unit": "Pcs", "rates": ["20", "20+2", "20+3", "20+5", "20+10", "20+10+5", "20+10+5+3", "20+10+5+5", "20+10+5+5+5"]}
    },
    "3. FTTx / FTTR": {
        "CABLE": {"tiers": [1, 3, 5, 10, 20, 30, 50, 100], "unit": "Roll", "rates": ["10+10", "10+10+2", "10+10+3", "10+10+5", "10+10+5+2", "10+10+5+3", "10+10+5+5", "10+10+5+5+5"]},
        "CONN": {"low": [1, 10, 30, 50, 100, 200, 300, 500, 1000], "high": [1, 2, 3, 5, 10, 20, 30, 50, 100], "unit": "Pcs", "rates": ["20", "20+2", "20+3", "20+5", "20+10", "20+10+5", "20+10+5+3", "20+10+5+5", "20+10+5+5+5"]}
    },
    "4. COAXIAL (RG)": {
        "CABLE": {"tiers": [1, 500, 1000, 3000, 5000, 8000, 10000, 20000, 30000], "unit": "M.", "rates": ["20", "20+5", "20+10", "20+10+3", "20+10+5", "20+10+5+3", "20+10+5+5", "20+10+5+5+3", "20+10+5+5+5"]},
        "CONN": {"low": [1, 10, 30, 50, 100, 200, 300, 500, 1000], "high": [1, 2, 3, 5, 10, 20, 30, 50, 100], "unit": "Pcs", "rates": ["20", "20+2", "20+3", "20+5", "20+10", "20+10+5", "20+10+5+3", "20+10+5+5", "20+10+5+5+5"]}
    },
    "6. SOLAR": {
        "CABLE": {"tiers": [1, 500, 1000, 3000, 5000, 10000, 20000, 30000, 50000], "unit": "M.", "rates": ["10", "10+5", "10+10", "10+10+3", "10+10+5", "10+10+5+3", "10+10+5+5", "10+10+5+5+3", "10+10+5+5+5"]},
        "CONN": {"low": [1, 10, 30, 50, 100, 200, 300, 500, 1000], "high": [1, 2, 3, 5, 10, 20, 30, 50, 100], "unit": "Pcs", "rates": ["20", "20+2", "20+3", "20+5", "20+10", "20+10+5", "20+10+5+3", "20+10+5+5", "20+10+5+5+5"]}
    },
    "9/10/11. 19\" RACK": {
        "CABLE": {"tiers": [1, 2, 3, 4, 5, 10, 20], "unit": "Unit", "rates": ["20", "20+2", "20+3", "20+4", "20+5", "20+5+5", "20+5+5+3"]},
        "CONN": {"low": [1, 3, 5, 10, 15, 20, 50], "high": [1, 3, 5, 10, 15, 20, 50], "unit": "Pcs", "rates": ["20", "20+3", "20+5", "20+5+3", "20+5+5", "20+5+5+3", "20+5+5+5"]}
    }
}

if 'basket' not in st.session_state:
    st.session_state.basket = []

st.title("🛒 Interlink Sales Master (KK-Team)")

# --- 1. เลือกกลุ่มลูกค้า ---
st.subheader("🚩 เลือกกลุ่มลูกค้า")
cust_group = st.radio(
    "ราคานี้สำหรับกลุ่มลูกค้า:",
    ["Dealer / Installer", "IT Shop / Elec Shop"],
    horizontal=True
)

# --- 2. กรอกข้อมูลสินค้า ---
with st.container(border=True):
    st.subheader("➕ เพิ่มรายการสินค้า")
    c1, c2 = st.columns(2)
    with c1:
        p_code = st.text_input("รหัสสินค้า (ระบุหรือไม่ก็ได้)", key="p_code")
        cat = st.selectbox("หมวดหมู่สินค้า", list(DATA.keys()))
        sub_type = st.radio("ประเภท", ["สินค้า", "อุปกรณ์"], horizontal=True)
        
        is_faceplate = False
        if cat == "1. LAN (UTP)" and sub_type == "อุปกรณ์":
            is_faceplate = st.checkbox("เป็น Face Plate / Cable Management (ฐาน 20%)")

    with c2:
        l_price = st.number_input("ราคาตั้ง (List Price)", min_value=0.0, step=100.0)
        qty = st.number_input("จำนวน", min_value=1, step=1)
        
    if st.button("📥 เพิ่มเข้าตะกร้า", use_container_width=True):
        target = "CABLE" if sub_type == "สินค้า" else "CONN"
        prod_data = DATA[cat][target]
        
        if target == "CONN":
            tier_key = "low" if l_price < 300 else "high"
            tiers = prod_data[tier_key]
        else:
            tiers = prod_data["tiers"]
            
        rates = prod_data["rates"]
        unit = prod_data["unit"]
        
        idx = 0
        for i, t in enumerate(tiers):
            if qty >= t: idx = i
        
        base_rate = rates[idx]
        range_txt = f"{tiers[idx]}-{tiers[idx+1]-1}" if idx < len(tiers)-1 else f"{tiers[idx]}+"

        if is_faceplate: 
            base_rate = base_rate.replace("10", "20")
            
        final_discount = base_rate
        if "IT Shop" in cust_group:
            final_discount = f"{base_rate}+5"
        
        net_val = calculate_net(l_price, final_discount)
        
        st.session_state.basket.append({
            "code": p_code.strip(),
            "category": cat,
            "qty": qty,
            "unit": unit,
            "range": range_txt,
            "discount": final_discount,
            "net_unit": net_val,
            "total": net_val * qty
        })
        st.toast(f"เพิ่มแล้ว! เรทส่วนลด: {final_discount}")

# --- 3. สรุปรายการ ---
if st.session_state.basket:
    st.divider()
    st.subheader(f"📋 รายการสรุปราคา Net (กลุ่ม {cust_group})")
    
    summary_list = []
    total_net = 0
    
    for i, item in enumerate(st.session_state.basket):
        display_name = item['code'] if item['code'] else item['category']
        line = f"{i+1}. {display_name} = {item['net_unit']:,.2f}/{item['unit']} (เรท {item['range']} {item['unit']})"
        st.write(line)
        summary_list.append(line)
        total_net += item['total']
    
    st.write(f*💰 ยอดรวม Net ทั้งสิ้น: {total_net:,.2f} บาท**")

    # ส่วนข้อความสำหรับคัดลอก
    full_text = f"*ใบเสนอราคาจำลอง Interlink (กลุ่ม {cust_group})*\n"
    full_text += "------------------------------\n"
    full_text += "\n".join(summary_list)
    full_text += f"\n------------------------------\n💰 ยอดรวม Net: {total_net:,.2f} บาท\n*(อ้างอิงราคา Discount Rate 2026)*"

    st.text_area("ก๊อปปี้ข้อความด้านล่างนี้ไปวางใน Line:", value=full_text, height=200)

    if st.button("🗑️ ล้างรายการทั้งหมด"):
        st.session_state.basket = []
        st.rerun()

