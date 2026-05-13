import streamlit as st
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import numpy as np

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Koenig Stride",
    page_icon="🤖",
    layout="wide"
)

# =====================================================
# PATHS
# =====================================================

BASE_DIR = Path(__file__).parent

EXCEL_PATH = BASE_DIR / "knowledge" / "Koenig_VoiceBot_FAQ_Master.xlsx"
LOGO_PATH = BASE_DIR / "assets" / "koenig_logo.png"
SARIKA_PATH = BASE_DIR / "assets" / "sarika.png"

# =====================================================
# OPENAI
# =====================================================

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# =====================================================
# EMBEDDING MODEL
# =====================================================

@st.cache_resource

def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_embedding_model()

# =====================================================
# LOAD KNOWLEDGE
# =====================================================

@st.cache_data

def load_knowledge():
    salary_df = pd.read_excel(
        EXCEL_PATH,
        sheet_name="Salary & Tax FAQs"
    ).fillna("")

    entity_df = pd.read_excel(
        EXCEL_PATH,
        sheet_name="Entity Nexus FAQs"
    ).fillna("")

    salary_df["Source"] = "Salary & Tax FAQs"
    entity_df["Source"] = "Entity Nexus FAQs"

    faq_df = pd.concat([
        salary_df,
        entity_df
    ], ignore_index=True)

    return faq_df

faq_df = load_knowledge()

# =====================================================
# PREPARE SEARCH TEXT
# =====================================================

faq_df["combined_text"] = (
    faq_df["Question"].astype(str) + " " +
    faq_df["Keywords"].astype(str) + " " +
    faq_df["Alternate Phrases"].astype(str)
)

# =====================================================
# CREATE EMBEDDINGS
# =====================================================

@st.cache_resource

def create_embeddings(texts):
    return model.encode(texts, show_progress_bar=False)

embeddings = create_embeddings(
    faq_df["combined_text"].tolist()
)

# =====================================================
# SEMANTIC SEARCH
# =====================================================

def semantic_search(user_query, top_k=3):

    query_embedding = model.encode([user_query])

    similarities = cosine_similarity(
        query_embedding,
        embeddings
    )[0]

    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = faq_df.iloc[top_indices].copy()
    results["similarity"] = similarities[top_indices]

    return results

# =====================================================
# PROTECTION LOGIC
# =====================================================

def is_protected(row):
    return str(row.get("Protected", "")).strip().lower() == "yes"

# =====================================================
# GPT RESPONSE
# =====================================================

def generate_gpt_response(user_query, search_results):

    context = ""

    for _, row in search_results.iterrows():
        context += f"""
        Question: {row.get('Question','')}
        Answer: {row.get('Display Message (Voice)','')}
        Protected: {row.get('Protected','')}
        SPOC: {row.get('SPOC Name','')}
        Email: {row.get('SPOC Email','')}
        \n
        """

    system_prompt = f"""

    You are Koenig Stride.

    You are an internal Tax & Entity Nexus Assistant.

    Rules:

    1. Never expose protected information.
    2. If Protected = YES, ask employee to contact SPOC.
    3. Be professional and concise.
    4. Use only provided knowledge.
    5. Do not hallucinate.

    Knowledge Base:

    {context}

    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_query
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content

# =====================================================
# UI
# =====================================================

st.title("🤖 Koenig Stride")
st.caption("Tax & Entity Nexus Assistant")

col1, col2 = st.columns([1,3])

with col1:

    if SARIKA_PATH.exists():
        st.image(str(SARIKA_PATH))

    st.success("Sarika is online")

    st.markdown("""
    ### I can help with:

    - Tax FAQs
    - Salary queries
    - Entity Nexus
    - SPOC routing
    - Compliance support
    """)

with col2:

    user_query = st.text_input(
        "Ask Koenig Stride",
        placeholder="Example: Who handles UAE entity compliance?"
    )

    if st.button("Ask"):

        if user_query:

            with st.spinner("Koenig Stride is thinking..."):

                results = semantic_search(user_query)

                top_row = results.iloc[0]

                if is_protected(top_row):

                    st.warning("This information is protected.")

                    st.info(f"""
                    Please contact:

                    SPOC: {top_row.get('SPOC Name','Relevant SPOC')}

                    Email: {top_row.get('SPOC Email','')}
                    """)

                else:

                    answer = generate_gpt_response(
                        user_query,
                        results
                    )

                    st.success(answer)

                with st.expander("Matched Knowledge"):
                    st.dataframe(results[[
                        'Question',
                        'similarity',
                        'Source'
                    ]])
