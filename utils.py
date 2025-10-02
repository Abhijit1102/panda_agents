
import pandas as pd
import os
# --------------------------
# Function to read any file
# --------------------------
def read_file(file_path, sheet_name=0):
    """
    Reads any Excel (.xls, .xlsx, .xlsm, .xlsb, .ods) or CSV file into a pandas DataFrame.
    """
    ext = os.path.splitext(file_path)[1].lower()
    print(f"📂 File: {file_path}")
    print(f"🔍 Detected extension: {ext}")

    excel_engines = {
        ".xls": "xlrd",
        ".xlsx": "openpyxl",
        ".xlsm": "openpyxl",
        ".xlsb": "pyxlsb",
        ".ods": "odf"
    }

    try:
        if ext == ".csv":
            df = pd.read_csv(file_path)
            print("✅ Successfully read CSV file")
        elif ext in excel_engines:
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine=excel_engines[ext])
            print(f"✅ Successfully read Excel file using engine={excel_engines[ext]}")
        else:
            raise ValueError(f"❌ Unsupported file extension: {ext}")
        return df
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

# --------------------------
# Function to run pandas commands safely
# --------------------------
def run_pandas_command(df, command: str):
    """
    Run a pandas command on the given DataFrame safely.
    """
    try:
        result = eval(command, {"df": df, "pd": pd})
        return result
    except Exception as e:
        print(f"❌ Error running command '{command}': {e}")
        return None


def clean_pandas_command(command: str) -> str:
    """
    Remove markdown code fences and extra whitespace.
    """
    return (
        command.replace("```python", "")
               .replace("```", "")
               .strip()
    )        