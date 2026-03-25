import streamlit as st
import sqlite3
import pandas as pd

# =========================
# 🔧 CONFIG
# =========================
st.set_page_config(page_title="KK-Team Smart System PRO", layout="wide")

DB_FILE = "kkteam.db"

# =========================
# 🧠 DATABASE
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
    df = pd.read_sql("SELECT * FROM products WHERE code=?", conn, params=(code,))
    conn.close()
    return df

def search_code(keyword):
    conn = get_conn()
    df = pd.read_sql(
        "SELECT code FROM products WHERE code LIKE ? LIMIT 10",
        conn,
        params=(f"{keyword}%",)
    )
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
    """, (code, price, cat, sub))
    conn.commit()
    conn.close()

def load_all():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM products ORDER BY code DESC", conn)
    conn.close()
    return df

# =========================
# 🔐 LOGIN
# =========================
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 KK-Team System PRO")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        if pw == "KK-Team":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Wrong Password")

    st.stop()

# =========================
# 📊 RATE TABLE
# =========================
DB_RATES = {
    "LAN": {"C":[1,3,5,10], "UT":"กล่อง", "R":["10","10+5","10+10","10+10+5"]},
    "FIBER": {"C":[1,1000,5000], "UT":"เมตร", "R":["10","10+5","10+10"]},
    "SOLAR": {"C":[1,1000,5000], "UT":"เมตร", "R":["10","10+5","10+10"]}
}

# =========================
# 🛒 UI
# =========================
st.title("🛒 KK-Team Smart Calculator PRO")

col1, col2 = st.columns(2)

with col1:
    keyword = st.text_input("🔍 พิมพ์รหัสสินค้า")

    suggestions = []
    if keyword:
        suggestions = search_code(keyword)

    selected_code = st.selectbox(
        "📌 Auto Suggest",
        options=[""] + suggestions
    )

    input_code = selected_code if selected_code else keyword.upper()

    product = get_product(input_code)

    if not product.empty:
        price = float(product.iloc[0]['price'])
        cat = product.iloc[0]['category']
        sub = product.iloc[0]['sub_category']
        st.success(f"เจอสินค้า: {price}")
    else:
        price = 0.0
        cat = "LAN"
        sub = "Cable"

    cat = st.selectbox("Category", list(DB_RATES.keys()), index=list(DB_RATES.keys()).index(cat))
    sub = st.radio("Type", ["Cable", "Accessory"], horizontal=True)

with col2:
    price = st.number_input("Price", value=price)
    qty = st.number_input("Qty", value=1)

# =========================
# 💰 CALCULATE
# =========================
if st.button("🚀 Calculate & Save"):
    if not input_code:
        st.warning("ใส่รหัสก่อน")
    else:
        # SAVE
        save_product(input_code, price, cat, sub)

        # CALC
        data = DB_RATES[cat]

        idx = 0
        for i, v in enumerate(data["C"]):
            if qty >= v:
                idx = i

        rate = data["R"][idx]

        final_price = price
        steps = f"{price}"

        for d in [float(x) for x in rate.split("+")]:
            steps += f" -{d}%"
            final_price *= (1 - d/100)

        result = f"{input_code} = {final_price:,.2f}"

        st.success(result)
        st.caption(f"วิธีคิด: {steps}")

# =========================
# 📊 TABLE
# =========================
st.divider()
st.subheader("📊 Database")

df = load_all()
st.dataframe(df, use_container_width=True)
