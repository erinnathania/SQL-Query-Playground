import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import sqlite3

st.set_page_config(page_title="SQL Query Playground", layout="wide")
st.title("SQL Query Playground")

#File Upload + Loading into SQLite
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    st.subheader("Data Preview")
    st.dataframe(df.head())
    
    conn = sqlite3.connect(":memory:")
    df.to_sql("data", conn, index=False, if_exists="replace")
    st.success("CSV loaded! You can now query it as a table called `data`")

    #SQL Query Input + Results
    st.subheader("Write your SQL Query")

    query = st.text_area("Type your SQL query below:", 
                            value="SELECT * FROM data LIMIT 10;")

    if st.button("▶️ Run Query"):
        try:
            result_df = pd.read_sql(query, conn)
            
            st.subheader("Query Results")
            st.dataframe(result_df)
            
            if len(result_df.columns) >= 2:
                st.subheader("Chart")
                fig, ax = plt.subplots()
                result_df.plot(kind="bar", x=result_df.columns[0], 
                                y=result_df.columns[1], ax=ax)
                st.pyplot(fig)
                
        except Exception as e:
            st.error(f"SQL Error: {e}")