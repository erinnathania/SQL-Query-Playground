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
                numeric_cols = result_df.select_dtypes(include='number').columns.tolist()
            
            if len(numeric_cols) >= 1:
                st.subheader("Chart")
                fig, ax = plt.subplots()
                x_col = result_df.columns[0]
                y_col = numeric_cols[0]
                result_df.plot(kind="bar", x=x_col, y=y_col, ax=ax)
                st.pyplot(fig)
            else:
                st.info("No numeric columns to chart — showing table only.")
                
        except Exception as e:
            st.error(f"SQL Error: {e}")

