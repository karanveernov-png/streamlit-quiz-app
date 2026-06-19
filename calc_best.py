import streamlit as st
import math

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Glass Calculator",
    page_icon="🧮",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

html, body, [class*="css"] {
    background: linear-gradient(135deg, #0f172a, #111827);
    color: white;
    font-family: 'Poppins', sans-serif;
}

/* Hide Streamlit menu */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Main Title */
.main-title{
    text-align:center;
    font-size:65px;
    font-weight:bold;
    background: linear-gradient(90deg,#00F5A0,#00D9F5);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    margin-bottom:10px;
}

/* Subtitle */
.sub-title{
    text-align:center;
    font-size:20px;
    color:#cbd5e1;
    margin-bottom:35px;
}

/* Glass Container */
.glass{
    background: rgba(255,255,255,0.08);
    border-radius:25px;
    padding:35px;
    backdrop-filter: blur(18px);
    border:1px solid rgba(255,255,255,0.15);
    box-shadow:0 8px 32px rgba(0,0,0,0.35);
}

/* Inputs */
.stNumberInput input,
.stTextInput input {
    background-color: rgba(255,255,255,0.08) !important;
    color: white !important;
    border-radius: 15px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    height: 50px;
    font-size:18px;
}

/* Dropdown */
.stSelectbox div[data-baseweb="select"] {
    background-color: rgba(255,255,255,0.08);
    border-radius:15px;
}

/* Button */
.stButton>button {
    width:100%;
    height:65px;
    border:none;
    border-radius:18px;
    background: linear-gradient(90deg,#00F5A0,#00D9F5);
    color:black;
    font-size:24px;
    font-weight:bold;
    transition:0.3s;
}

.stButton>button:hover {
    transform: scale(1.03);
    box-shadow:0 0 25px cyan;
}

/* Result Box */
.result-box{
    margin-top:30px;
    padding:30px;
    border-radius:22px;
    text-align:center;
    background: linear-gradient(135deg,#00F5A0,#00D9F5);
    color:black;
    font-size:38px;
    font-weight:bold;
    box-shadow:0 0 30px rgba(0,255,255,0.4);
}

/* Feature Cards */
.feature{
    background: rgba(255,255,255,0.05);
    padding:15px;
    border-radius:15px;
    text-align:center;
    border:1px solid rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(
    '<div class="main-title">🧮 Glass Calculator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Modern Premium Streamlit Calculator</div>',
    unsafe_allow_html=True
)

# ---------------- GLASS BOX START ----------------
st.markdown('<div class="glass">', unsafe_allow_html=True)

# ---------------- INPUTS ----------------
st.markdown("## 🔢 Enter Numbers")

col1, col2 = st.columns(2)

with col1:
    num1 = st.number_input("First Number", value=0.0)

with col2:
    num2 = st.number_input("Second Number", value=0.0)

extra = st.text_input(
    "➕ More Numbers (Optional)",
    placeholder="Example: 10,20,30"
)

# ---------------- OPERATIONS ----------------
st.markdown("## ⚡ Choose Operation")

operation = st.selectbox(
    "",
    [
        "Addition (+)",
        "Subtraction (-)",
        "Multiplication (×)",
        "Division (÷)",
        "Remainder (%)",
        "Power (**)",
        "Square Root (√)",
        "Average",
        "Maximum",
        "Minimum"
    ]
)

# ---------------- BUTTON ----------------
if st.button("🚀 Calculate Now"):

    try:

        numbers = [num1, num2]

        # Extra numbers
        if extra.strip():
            extra_numbers = [float(x.strip()) for x in extra.split(",")]
            numbers.extend(extra_numbers)

        # -------- OPERATIONS --------
        if operation == "Addition (+)":
            result = sum(numbers)

        elif operation == "Subtraction (-)":
            result = numbers[0]
            for num in numbers[1:]:
                result -= num

        elif operation == "Multiplication (×)":
            result = 1
            for num in numbers:
                result *= num

        elif operation == "Division (÷)":
            result = numbers[0]
            for num in numbers[1:]:
                if num == 0:
                    st.error("❌ Cannot divide by zero")
                    st.stop()
                result /= num

        elif operation == "Remainder (%)":
            result = numbers[0]
            for num in numbers[1:]:
                if num == 0:
                    st.error("❌ Cannot divide by zero")
                    st.stop()
                result %= num

        elif operation == "Power (**)":
            result = numbers[0]
            for num in numbers[1:]:
                result = result ** num

        elif operation == "Square Root (√)":

            st.markdown("### 📘 Square Roots")

            for num in numbers:
                if num < 0:
                    st.warning(f"Cannot calculate √ of {num}")
                else:
                    st.success(f"√ {num} = {math.sqrt(num):.4f}")

            result = "Completed"

        elif operation == "Average":
            result = sum(numbers) / len(numbers)

        elif operation == "Maximum":
            result = max(numbers)

        elif operation == "Minimum":
            result = min(numbers)

        # ---------------- RESULT ----------------
        st.markdown(
            f"""
            <div class="result-box">
                ✅ RESULT <br><br> {result}
            </div>
            """,
            unsafe_allow_html=True
        )

    except:
        st.error("❌ Invalid Input Format")
