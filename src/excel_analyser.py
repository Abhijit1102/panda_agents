# src/excel_analyser.py
import os
import pandas as pd
import streamlit as st
from langchain_openai import ChatOpenAI
from utils import read_file, run_pandas_command, clean_pandas_command
import atexit

def excel_analyser_app():
    st.title("📊 Excel/CSV Analyzer with LangChain + Pandas")

    os.makedirs("public", exist_ok=True)

    # Cleanup function
    def cleanup_files():
        for file in os.listdir("public"):
            if file.startswith("temp_"):
                os.remove(os.path.join("public", file))
    atexit.register(cleanup_files)

    def make_arrow_compatible(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    df.loc[:, col] = df[col].astype(str)
                except Exception:
                    df.loc[:, col] = df[col].apply(lambda x: str(x) if not pd.isna(x) else "")
        return df

    uploaded_file = st.file_uploader(
        "📂 Upload an Excel or CSV file",
        type=["csv", "xls", "xlsx", "xlsm", "xlsb", "ods"]
    )

    if uploaded_file:
        temp_file_path = f"./public/temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        df = read_file(temp_file_path)
        if df is not None:
            st.success("✅ File loaded successfully!")

            with st.expander("🔎 Data Preview (first 10 rows)", expanded=True):
                st.dataframe(make_arrow_compatible(df.head(10)), width="stretch")

            st.subheader("🤖 Ask Questions About Your Data")
            user_question = st.text_input("💬 Enter your question here:")

            if user_question:
                with st.spinner("Thinking... 🤔"):
                    prompt = f"""
                    You are a pandas expert. 
                    The user uploaded a DataFrame with columns: {list(df.columns)}.
                    User question: "{user_question}"
                    Return ONLY a valid pandas command using the variable `df` 
                    (and `pd` if needed) that directly answers the question. 
                    Do not include explanations, just the code.
                    """
                    llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"), temperature=0)
                    response = llm.invoke(prompt)
                    command = clean_pandas_command(response.content.strip())

                result = run_pandas_command(df, str(command))

                st.divider()
                st.markdown("### 📊 Result")
                if isinstance(result, pd.DataFrame):
                    st.dataframe(make_arrow_compatible(result), width="stretch")
                elif isinstance(result, pd.Series):
                    st.dataframe(make_arrow_compatible(result.to_frame()), width="stretch")
                else:
                    st.success(f"✅ Answer: **{result}**")
