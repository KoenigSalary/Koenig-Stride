        Question: {row.get('Question','')}
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
