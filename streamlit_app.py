###### import streamlit as st

###### 

###### \# --- ตั้งค่าหน้าจอ ---

###### st.set\_page\_config(page\_title="Interlink Sales Master (KK-Team)", layout="wide")

###### 

###### \# --- ระบบ Login ---

###### if 'logged\_in' not in st.session\_state:

###### &#x20;   st.session\_state.logged\_in = False

###### 

###### if not st.session\_state.logged\_in:

###### &#x20;   st.title("🔐 เข้าสู่ระบบ (KK-Team Only)")

###### &#x20;   username = st.text\_input("กรุณากรอก Username", placeholder="ระบุชื่อทีมของคุณ")

###### &#x20;   if st.button("ตกลง"):

###### &#x20;       if username == "KK-Team":

###### &#x20;           st.session\_state.logged\_in = True

###### &#x20;           st.rerun()

###### &#x20;       else:

###### &#x20;           st.error("Username ไม่ถูกต้อง")

###### &#x20;   st.stop()

###### 

###### \# --- ฟังก์ชันคำนวณราคา Net ---

###### def calculate\_net(list\_price, discount\_str):

###### &#x20;   current = list\_price

###### &#x20;   for p in discount\_str.split('+'):

###### &#x20;       try:

###### &#x20;           val = p.strip()

###### &#x20;           if val:

###### &#x20;               current \*= (1 - (float(val)/100))

###### &#x20;       except:

###### &#x20;           pass

###### &#x20;   return current

###### 

###### \# --- ฐานข้อมูลส่วนลด 2569 (รวม FTTx/FTTR แล้ว) ---

###### DATA = {

###### &#x20;   "1. LAN (UTP)": {

###### &#x20;       "CABLE": {"tiers": \[1, 3, 5, 10, 20, 30, 50, 100], "unit": "Box", "rates": \["10+10", "10+10+2", "10+10+3", "10+10+5", "10+10+5+2", "10+10+5+3", "10+10+5+5", "10+10+5+5+5"]},

###### &#x20;       "CONN": {"low": \[1, 10, 30, 50, 100, 200, 300, 500, 1000], "high": \[1, 2, 3, 5, 10, 20, 30, 50, 100], "unit": "Pcs", "rates": \["10", "10+2", "10+3", "10+5", "10+10", "10+10+5", "10+10+5+3", "10+10+5+5", "10+10+5+5+5"]}

###### &#x20;   },

###### &#x20;   "2. FIBER OPTIC": {

###### &#x20;       "CABLE": {"tiers": \[1, 500, 1000, 3000, 5000, 8000, 10000, 20000, 30000], "unit": "M.", "rates": \["10", "10+5", "10+10", "10+10+3", "10+10+5", "10+10+5+3", "10+10+5+5", "10+10+5+5+3", "10+10+5+5+5"]},

###### &#x20;       "CONN": {"low": \[1, 10, 30, 50, 100, 200, 300, 500, 1000], "high": \[1, 2, 3, 5, 10, 20, 30, 50, 100], "unit": "Pcs", "rates": \["20", "20+2", "20+3", "20+5", "20+10", "20+10+5", "20+10+5+3", "20+10+5+5", "20+10+5+5+5"]}

###### &#x20;   },

###### &#x20;   "3. FTTx / FTTR": {

###### &#x20;       "CABLE": {"tiers": \[1, 3, 5, 10, 20, 30, 50, 100], "unit": "Roll", "rates": \["10+10", "10+10+2", "10+10+3", "10+10+5", "10+10+5+2", "10+10+5+3", "10+10+5+5", "10+10+5+5+5"]},

###### &#x20;       "CONN": {"low": \[1, 10, 30, 50, 100, 200, 300, 500, 1000], "high": \[1, 2, 3, 5, 10, 20, 30, 50, 100], "unit": "Pcs", "rates": \["20", "20+2", "20+3", "20+5", "20+10", "20+10+5", "20+10+5+3", "20+10+5+5", "20+10+5+5+5"]}

###### &#x20;   },

###### &#x20;   "4. COAXIAL (RG)": {

###### &#x20;       "CABLE": {"tiers": \[1, 500, 1000, 3000, 5000, 8000, 10000, 20000, 30000], "unit": "M.", "rates": \["20", "20+5", "20+10", "20+10+3", "20+10+5", "20+10+5+3", "20+10+5+5", "20+10+5+5+3", "20+10+5+5+5"]},

###### &#x20;       "CONN": {"low": \[1, 10, 30, 50, 100, 200, 300, 500, 1000], "high": \[1, 2, 3, 5, 10, 20, 30, 50, 100], "unit": "Pcs", "rates": \["20", "20+2", "20+3", "20+5", "20+10", "20+10+5", "20+10+5+3", "20+10+5+5", "20+10+5+5+5"]}

###### &#x20;   },

###### &#x20;   "6. SOLAR": {

###### &#x20;       "CABLE": {"tiers": \[1, 500, 1000, 3000, 5000, 10000, 20000, 30000, 50000], "unit": "M.", "rates": \["10", "10+5", "10+10", "10+10+3", "10+10+5", "10+10+5+3", "10+10+5+5", "10+10+5+5+3", "10+10+5+5+5"]},

###### &#x20;       "CONN": {"low": \[1, 10, 30, 50, 100, 200, 300, 500, 1000], "high": \[1, 2, 3, 5, 10, 20, 30, 50, 100], "unit": "Pcs", "rates": \["20", "20+2", "20+3", "20+5", "20+10", "20+10+5", "20+10+5+3", "20+10+5+5", "20+10+5+5+5"]}

###### &#x20;   },

###### &#x20;   "9/10/11. 19\\" RACK": {

###### &#x20;       "CABLE": {"tiers": \[1, 2, 3, 4, 5, 10, 20], "unit": "Unit", "rates": \["20", "20+2", "20+3", "20+4", "20+5", "20+5+5", "20+5+5+3"]},

###### &#x20;       "CONN": {"low": \[1, 3, 5, 10, 15, 20, 50], "high": \[1, 3, 5, 10, 15, 20, 50], "unit": "Pcs", "rates": \["20", "20+3", "20+5", "20+5+3", "20+5+5", "20+5+5+3", "20+5+5+5"]}

###### &#x20;   }

###### }

###### 

###### if 'basket' not in st.session\_state:

###### &#x20;   st.session\_state.basket = \[]

###### 

###### st.title("🛒 Interlink Sales Master (KK-Team)")

###### 

###### \# --- 1. เลือกกลุ่มลูกค้า ---

###### st.subheader("🚩 เลือกกลุ่มลูกค้า")

###### cust\_group = st.radio(

###### &#x20;   "ราคานี้สำหรับกลุ่มลูกค้า:",

###### &#x20;   \["Dealer / Installer", "IT Shop / Elec Shop"],

###### &#x20;   horizontal=True

###### )

###### 

###### \# --- 2. กรอกข้อมูลสินค้า ---

###### with st.container(border=True):

###### &#x20;   st.subheader("➕ เพิ่มรายการสินค้า")

###### &#x20;   c1, c2 = st.columns(2)

###### &#x20;   with c1:

###### &#x20;       p\_code = st.text\_input("รหัสสินค้า (ระบุหรือไม่ก็ได้)", key="p\_code")

###### &#x20;       cat = st.selectbox("หมวดหมู่สินค้า", list(DATA.keys()))

###### &#x20;       sub\_type = st.radio("ประเภท", \["สินค้า", "อุปกรณ์"], horizontal=True)

###### &#x20;       

###### &#x20;       is\_faceplate = False

###### &#x20;       if cat == "1. LAN (UTP)" and sub\_type == "อุปกรณ์":

###### &#x20;           is\_faceplate = st.checkbox("เป็น Face Plate / Cable Management (ฐาน 20%)")

###### 

###### &#x20;   with c2:

###### &#x20;       l\_price = st.number\_input("ราคาตั้ง (List Price)", min\_value=0.0, step=100.0)

###### &#x20;       qty = st.number\_input("จำนวน", min\_value=1, step=1)

###### &#x20;       

###### &#x20;   if st.button("📥 เพิ่มเข้าตะกร้า", use\_container\_width=True):

###### &#x20;       target = "CABLE" if sub\_type == "สินค้า" else "CONN"

###### &#x20;       prod\_data = DATA\[cat]\[target]

###### &#x20;       

###### &#x20;       if target == "CONN":

###### &#x20;           tier\_key = "low" if l\_price < 300 else "high"

###### &#x20;           tiers = prod\_data\[tier\_key]

###### &#x20;       else:

###### &#x20;           tiers = prod\_data\["tiers"]

###### &#x20;           

###### &#x20;       rates = prod\_data\["rates"]

###### &#x20;       unit = prod\_data\["unit"]

###### &#x20;       

###### &#x20;       idx = 0

###### &#x20;       for i, t in enumerate(tiers):

###### &#x20;           if qty >= t: idx = i

###### &#x20;       

###### &#x20;       base\_rate = rates\[idx]

###### &#x20;       range\_txt = f"{tiers\[idx]}-{tiers\[idx+1]-1}" if idx < len(tiers)-1 else f"{tiers\[idx]}+"

###### 

###### &#x20;       if is\_faceplate: 

###### &#x20;           base\_rate = base\_rate.replace("10", "20")

###### &#x20;           

###### &#x20;       final\_discount = base\_rate

###### &#x20;       if "IT Shop" in cust\_group:

###### &#x20;           final\_discount = f"{base\_rate}+5"

###### &#x20;       

###### &#x20;       net\_val = calculate\_net(l\_price, final\_discount)

###### &#x20;       

###### &#x20;       st.session\_state.basket.append({

###### &#x20;           "code": p\_code.strip(),

###### &#x20;           "category": cat,

###### &#x20;           "qty": qty,

###### &#x20;           "unit": unit,

###### &#x20;           "range": range\_txt,

###### &#x20;           "discount": final\_discount,

###### &#x20;           "net\_unit": net\_val,

###### &#x20;           "total": net\_val \* qty

###### &#x20;       })

###### &#x20;       st.toast(f"เพิ่มแล้ว! เรทส่วนลด: {final\_discount}")

###### 

###### \# --- 3. สรุปรายการ ---

###### if st.session\_state.basket:

###### &#x20;   st.divider()

###### &#x20;   st.subheader(f"📋 รายการสรุปราคา Net (กลุ่ม {cust\_group})")

###### &#x20;   

###### &#x20;   summary\_list = \[]

###### &#x20;   total\_net = 0

###### &#x20;   

###### &#x20;   for i, item in enumerate(st.session\_state.basket):

###### &#x20;       display\_name = item\['code'] if item\['code'] else item\['category']

###### &#x20;       line = f"{i+1}. {display\_name} = {item\['net\_unit']:,.2f}/{item\['unit']} (เรท {item\['range']} {item\['unit']})"

###### &#x20;       st.write(line)

###### &#x20;       summary\_list.append(line)

###### &#x20;       total\_net += item\['total']

###### &#x20;   

###### &#x20;   st.write(f\*💰 ยอดรวม Net ทั้งสิ้น: {total\_net:,.2f} บาท\*\*")

###### 

###### &#x20;   # ส่วนข้อความสำหรับคัดลอก

###### &#x20;   full\_text = f"\*ใบเสนอราคาจำลอง Interlink (กลุ่ม {cust\_group})\*\\n"

###### &#x20;   full\_text += "------------------------------\\n"

###### &#x20;   full\_text += "\\n".join(summary\_list)

###### &#x20;   full\_text += f"\\n------------------------------\\n💰 ยอดรวม Net: {total\_net:,.2f} บาท\\n\*(อ้างอิงราคา Discount Rate 2026)\*"

###### 

###### &#x20;   st.text\_area("ก๊อปปี้ข้อความด้านล่างนี้ไปวางใน Line:", value=full\_text, height=200)

###### 

###### &#x20;   if st.button("🗑️ ล้างรายการทั้งหมด"):

###### &#x20;       st.session\_state.basket = \[]

###### &#x20;       st.rerun()

