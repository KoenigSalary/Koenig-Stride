import streamlit as st
import pandas as pd

st.set_page_config(page_title="Koenig Stride", layout="wide")

st.markdown("""
<style>
#MainMenu, footer, header {visibility:hidden;}
[data-testid="stToolbar"] {display:none !important;}
</style>
""", unsafe_allow_html=True)

st.title("Koenig Stride")
st.subheader("Tax & Entity Nexus Assistant")

if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

if st.button("🚀 Start Here", use_container_width=True):
    st.session_state.menu_open = True

module_map = {
    "✅ Tax FAQs": [
        "Advance Tax",
        "Form 16",
        "Home Loan & Insurance",
        "HRA",
        "Income Tax 2026",
        "NPS",
        "Penalty & Delay",
        "Salary Tax Basics",
        "Sodexo / Meal Benefit",
        "Tax Claim Process",
        "Tax Regime",
    ],
    "✅ Salary Queries": [
        "Reimbursements",
        "Salary Structure",
    ],
    "⚖️ Labour Code": [
        "Labour Code"
    ],
    "✅ Entity Nexus": [
        "Entity – Australia",
        "Entity – UAE",
        "Entity – Netherlands",
    ],
    "✅ SPOC Routing": [
        "Payroll SPOC",
        "Tax SPOC",
        "Entity SPOC",
    ],
    "🔒 Protected Information Routing": [
        "Protected Salary Data",
        "Protected Entity Data",
    ],
    "✅ Compliance Support": [
        "TDS",
        "GST",
        "Compliance Filing",
    ]
}

sample_questions = {
    "NPS": [
        "What is NPS?",
        "Is NPS mandatory for all employees?",
        "What are the two types of NPS contribution?"
    ],
    "Labour Code": [
        "What is Labour Code?",
        "When will Labour Code apply?"
    ]
}

if st.session_state.menu_open:
    st.markdown("## Select Area")

    cols = st.columns(2)
    buttons = list(module_map.keys())

    for i, btn in enumerate(buttons):
        with cols[i % 2]:
            if st.button(btn, use_container_width=True):
                st.session_state.selected_module = btn

if "selected_module" in st.session_state:

    module = st.session_state.selected_module

    st.success(f"Selected: {module}")

    for category in module_map.get(module, []):

        with st.expander(f"📂 {category}", expanded=False):

            questions = sample_questions.get(category, [
                f"What is {category}?",
                f"How does {category} work?"
            ])

            for q in questions:

                with st.expander(f"❓ {q}"):

                    if "Protected" in category:
                        st.warning("Protected Information")
                        st.info("Please contact SPOC.")
                    else:
                        st.write(f"Answer for: {q}")

st.markdown("---")

st.subheader("💬 Ask Koenig Stride Directly")

query = st.text_input("Ask your question")

if st.button("Ask") and query:
    st.success(f"You asked: {query}")
    st.write("This will connect with GPT + Excel knowledge base.")
