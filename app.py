import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
from pathlib import Path
from datetime import datetime
import base64

# =========================================================
# KOENIG STRIDE - TAX & ENTITY NEXUS ASSISTANT
# Version 2: Improved UI + Suggested Questions + Better Cards
# =========================================================

st.set_page_config(
    page_title="Koenig Stride",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = Path(__file__).parent
EXCEL_PATH = BASE_DIR / "knowledge" / "Koenig_VoiceBot_FAQ_Master.xlsx"
LOGO_PATH = BASE_DIR / "assets" / "koenig_logo.png"
SARIKA_PATH = BASE_DIR / "assets" / "sarika.png"
CHAT_LOG_PATH = BASE_DIR / "chat_logs.csv"


# -----------------------------
# Utility: Convert Image to Base64
# -----------------------------
def image_to_base64(path):
    if path.exists():
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    return ""


logo_b64 = image_to_base64(LOGO_PATH)
sarika_b64 = image_to_base64(SARIKA_PATH)


# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: #f5f7fb;
}

[data-testid="stHeader"] {
    background: rgba(245,247,251,0.9);
}

.block-container {
    padding-top: 2rem;
    max-width: 1250px;
}

.hero {
    background: linear-gradient(120deg, #0f172a 0%, #123c92 55%, #2563eb 100%);
    border-radius: 28px;
    padding: 28px 32px;
    color: white;
    box-shadow: 0 16px 40px rgba(15,23,42,0.18);
    margin-bottom: 24px;
}

.hero h1 {
    font-size: 44px;
    margin: 0;
    font-weight: 800;
    letter-spacing: -1px;
}

.hero p {
    margin-top: 8px;
    font-size: 16px;
    opacity: 0.92;
}

.assistant-card {
    background: white;
    border-radius: 26px;
    padding: 18px;
    box-shadow: 0 12px 34px rgba(15,23,42,0.08);
    border: 1px solid #e5e7eb;
}

.avatar-wrap {
    position: relative;
    border-radius: 24px;
    overflow: hidden;
    background: #0b1120;
}

.status-dot {
    position: absolute;
    bottom: 22px;
    right: 22px;
    width: 22px;
    height: 22px;
    background: #22c55e;
    border: 4px solid white;
    border-radius: 50%;
}

.online-pill {
    background: #dcfce7;
    color: #166534;
    padding: 10px 14px;
    border-radius: 14px;
    font-weight: 600;
    margin-top: 14px;
}

.help-box {
    background: #f8fafc;
    border-radius: 18px;
    padding: 15px;
    margin-top: 14px;
    border: 1px solid #e2e8f0;
}

.help-box div {
    padding: 4px 0;
}

.chat-panel {
    background: white;
    border-radius: 26px;
    padding: 22px;
    box-shadow: 0 12px 34px rgba(15,23,42,0.08);
    border: 1px solid #e5e7eb;
}

.welcome-card {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    padding: 20px;
    border-radius: 22px;
    margin-bottom: 18px;
}

.user-bubble {
    background: #dbeafe;
    border: 1px solid #bfdbfe;
    color: #0f172a;
    padding: 15px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 12px 0 10px auto;
    max-width: 85%;
}

.bot-bubble {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #0f172a;
    padding: 15px 18px;
    border-radius: 18px 18px 18px 4px;
    margin: 10px 0 16px 0;
    max-width: 90%;
}

.protected-bubble {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-left: 6px solid #f97316;
    color: #7c2d12;
    padding: 16px 18px;
    border-radius: 18px;
    margin: 10px 0 16px 0;
    max-width: 92%;
}

.meta {
    margin-top: 10px;
    font-size: 12px;
    color: #64748b;
}

.suggest-title {
    font-size: 15px;
    font-weight: 700;
    color: #334155;
    margin: 14px 0 8px 0;
}

.footer-note {
    text-align: center;
    color: #64748b;
    font-size: 12px;
    margin-top: 22px;
}

.stButton button {
    border-radius: 14px !important;
    border: 1px solid #dbeafe !important;
    background: #ffffff !important;
    color: #1e3a8a !important;
    font-weight: 600 !important;
}

.stButton button:hover {
    background: #eff6ff !important;
    border-color: #93c5fd !important;
}

div[data-testid="stTextInput"] input {
    border-radius: 14px;
}

@media only screen and (max-width: 768px) {
    .hero h1 {
        font-size: 32px;
    }
    .hero {
        padding: 22px;
        border-radius: 22px;
    }
    .user-bubble, .bot-bubble, .protected-bubble {
        max-width: 100%;
    }
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Load Knowledge
# -----------------------------
@st.cache_data
def load_knowledge():
    if not EXCEL_PATH.exists():
        return pd.DataFrame(), pd.DataFrame(), f"Knowledge file not found: {EXCEL_PATH}"

    try:
        xl = pd.ExcelFile(EXCEL_PATH)
        sheets = xl.sheet_names

        faq_frames = []

        for sheet in ["Salary & Tax FAQs", "Entity Nexus FAQs"]:
            if sheet in sheets:
                df = pd.read_excel(EXCEL_PATH, sheet_name=sheet).fillna("")
                df["Source"] = sheet
                faq_frames.append(df)

        if faq_frames:
            faq_df = pd.concat(faq_frames, ignore_index=True).fillna("")
        else:
            faq_df = pd.DataFrame()

        if "SPOC Master" in sheets:
            spoc_df = pd.read_excel(EXCEL_PATH, sheet_name="SPOC Master").fillna("")
        else:
            spoc_df = pd.DataFrame()

        return faq_df, spoc_df, ""

    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), str(e)


faq_df, spoc_df, load_error = load_knowledge()


# -----------------------------
# Helper Functions
# -----------------------------
def safe_get(row, col, default=""):
    try:
        return str(row.get(col, default)).strip()
    except Exception:
        return default


def normalize(value):
    return str(value).strip().lower()


def is_protected(row):
    protected_value = normalize(safe_get(row, "Protected"))
    return protected_value in ["yes", "y", "true", "1", "protected"]


def build_search_text(row):
    possible_cols = [
        "Question",
        "Alternate Phrases",
        "Keywords",
        "Category",
        "Entity",
        "Country",
        "Topic",
        "Sub Topic",
        "Answer (Internal)",
        "Display Message (Voice)",
        "Voice Response"
    ]

    parts = []
    for col in possible_cols:
        val = safe_get(row, col)
        if val:
            parts.append(val)

    return " ".join(parts)


def search_faq(user_query, df):
    if df.empty or not user_query.strip():
        return None, 0

    user_query = user_query.strip()
    best_row = None
    best_score = 0

    for _, row in df.iterrows():
        question = safe_get(row, "Question")
        search_text = build_search_text(row)

        score_question = fuzz.token_sort_ratio(user_query.lower(), question.lower())
        score_partial = fuzz.partial_ratio(user_query.lower(), search_text.lower())
        score_token_set = fuzz.token_set_ratio(user_query.lower(), search_text.lower())

        score = max(score_question, score_partial, score_token_set)

        if score > best_score:
            best_score = score
            best_row = row

    return best_row, int(best_score)


def get_answer_text(row):
    for col in [
        "Display Message (Voice)",
        "Voice Response",
        "Answer (Internal)",
        "Answer",
        "Response"
    ]:
        value = safe_get(row, col)
        if value:
            return value
    return "Answer found, but response text is blank in the knowledge file."


def get_spoc(row):
    spoc_name = safe_get(row, "SPOC Name", "Relevant SPOC")
    spoc_email = safe_get(row, "SPOC Email", "")
    return spoc_name, spoc_email


def build_response(row, score):
    if row is None or score < 55:
        return {
            "type": "not_found",
            "message": (
                "I could not find an exact answer in the Koenig Stride knowledge base. "
                "Please try asking in a different way or contact the relevant SPOC."
            ),
            "category": "",
            "source": "",
            "spoc_name": "",
            "spoc_email": ""
        }

    category = safe_get(row, "Category")
    source = safe_get(row, "Source")
    spoc_name, spoc_email = get_spoc(row)

    if is_protected(row):
        return {
            "type": "protected",
            "message": "This information is protected and cannot be displayed here.",
            "category": category,
            "source": source,
            "spoc_name": spoc_name,
            "spoc_email": spoc_email
        }

    return {
        "type": "answer",
        "message": get_answer_text(row),
        "category": category,
        "source": source,
        "spoc_name": spoc_name,
        "spoc_email": spoc_email
    }


def log_query(user_query, result_type, score):
    try:
        new_row = pd.DataFrame([{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": user_query,
            "result_type": result_type,
            "score": score
        }])

        if CHAT_LOG_PATH.exists():
            old = pd.read_csv(CHAT_LOG_PATH)
            pd.concat([old, new_row], ignore_index=True).to_csv(CHAT_LOG_PATH, index=False)
        else:
            new_row.to_csv(CHAT_LOG_PATH, index=False)
    except Exception:
        pass


def submit_query(query):
    row, score = search_faq(query, faq_df)
    response = build_response(row, score)
    log_query(query, response["type"], score)

    st.session_state.chat_history.append({
        "query": query,
        "response": response,
        "score": score
    })


# -----------------------------
# Session State
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "input_query" not in st.session_state:
    st.session_state.input_query = ""


# -----------------------------
# Header
# -----------------------------
top1, top2 = st.columns([1, 5])

with top1:
    if logo_b64:
        st.markdown(
            f"<img src='data:image/png;base64,{logo_b64}' style='width:130px;margin-top:12px;'>",
            unsafe_allow_html=True
        )
    else:
        st.markdown("### KOENIG")

with top2:
    st.markdown("""
    <div class="hero">
        <h1>Koenig Stride</h1>
        <p>Tax & Entity Nexus Assistant — Step Forward</p>
    </div>
    """, unsafe_allow_html=True)


if load_error:
    st.error(load_error)


# -----------------------------
# Main Layout
# -----------------------------
left, right = st.columns([1.15, 3.2])

with left:
    st.markdown("<div class='assistant-card'>", unsafe_allow_html=True)
    st.markdown("### 👩‍💼 Sarika")

    if sarika_b64:
        st.markdown(f"""
        <div class="avatar-wrap">
            <img src="data:image/png;base64,{sarika_b64}" style="width:100%; display:block;">
            <span class="status-dot"></span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Sarika image not found in assets folder.")

    st.markdown("<div class='online-pill'>● Sarika is online</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="help-box">
        <b>I can help with:</b>
        <div>✅ Tax FAQs</div>
        <div>✅ Salary FAQs</div>
        <div>✅ Entity Nexus queries</div>
        <div>✅ SPOC guidance</div>
        <div>🔒 Protected info routing</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


with right:
    st.markdown("<div class='chat-panel'>", unsafe_allow_html=True)
    st.markdown("## 💬 Ask Koenig Stride")

    st.markdown("""
    <div class="welcome-card">
        <b>Koenig Stride:</b><br>
        Hello 👋 I am Koenig Stride, your interactive Tax & Entity Nexus Assistant.
        Ask me about tax, salary FAQs, entity details, or SPOC guidance.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='suggest-title'>Suggested questions</div>", unsafe_allow_html=True)

    q1, q2 = st.columns(2)
    q3, q4 = st.columns(2)

    suggestions = [
        "What changed in income tax from 1 April 2026?",
        "Who is the SPOC for tax queries?",
        "What is the company name of South Africa entity?",
        "What is my tax regime?"
    ]

    with q1:
        if st.button(suggestions[0], key="suggest_1"):
            submit_query(suggestions[0])
    with q2:
        if st.button(suggestions[1], key="suggest_2"):
            submit_query(suggestions[1])
    with q3:
        if st.button(suggestions[2], key="suggest_3"):
            submit_query(suggestions[2])
    with q4:
        if st.button(suggestions[3], key="suggest_4"):
            submit_query(suggestions[3])

    with st.form("query_form", clear_on_submit=True):
        user_query = st.text_input(
            "Type your question here",
            placeholder="Example: Who is the SPOC for UAE entity?"
        )
        submitted = st.form_submit_button("Ask Koenig Stride", type="primary")

    if submitted and user_query.strip():
        submit_query(user_query.strip())

    st.markdown("---")

    if st.session_state.chat_history:
        for item in reversed(st.session_state.chat_history[-10:]):
            response = item["response"]

            st.markdown(f"""
            <div class="user-bubble">
                <b>You</b><br>{item["query"]}
            </div>
            """, unsafe_allow_html=True)

            if response["type"] == "protected":
                spoc_email_html = (
                    f"<br><b>Email:</b> {response['spoc_email']}"
                    if response.get("spoc_email") else ""
                )

                st.markdown(f"""
                <div class="protected-bubble">
                    <b>🔒 Koenig Stride</b><br>
                    {response["message"]}<br><br>
                    Please contact the designated SPOC:<br>
                    <b>SPOC:</b> {response.get("spoc_name", "Relevant SPOC")}
                    {spoc_email_html}
                    <div class="meta">
                        Category: {response.get("category", "")} |
                        Source: {response.get("source", "")} |
                        Match Score: {item["score"]}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

            elif response["type"] == "not_found":
                st.markdown(f"""
                <div class="bot-bubble">
                    <b>Koenig Stride</b><br>
                    {response["message"]}
                    <div class="meta">Match Score: {item["score"]}%</div>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                <div class="bot-bubble">
                    <b>Koenig Stride</b><br>
                    {response["message"]}
                    <div class="meta">
                        Category: {response.get("category", "")} |
                        Source: {response.get("source", "")} |
                        Match Score: {item["score"]}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Admin Panel
# -----------------------------
with st.expander("Admin Preview: Knowledge Base"):
    if not faq_df.empty:
        st.success(f"Knowledge base loaded successfully. Total records: {len(faq_df)}")
        preview_cols = [c for c in ["Source", "Category", "Question", "Protected", "SPOC Name", "SPOC Email"] if c in faq_df.columns]
        st.dataframe(faq_df[preview_cols], use_container_width=True)
    else:
        st.warning("No FAQ records loaded.")

with st.expander("Admin Preview: SPOC Master"):
    if not spoc_df.empty:
        st.dataframe(spoc_df, use_container_width=True)
    else:
        st.info("SPOC Master sheet not found or empty.")

with st.expander("Admin Preview: Chat Logs"):
    if CHAT_LOG_PATH.exists():
        st.dataframe(pd.read_csv(CHAT_LOG_PATH), use_container_width=True)
    else:
        st.info("No chat logs yet.")


st.markdown("""
<div class="footer-note">
Koenig Stride · Internal Tax & Entity Nexus Assistant
</div>
""", unsafe_allow_html=True)