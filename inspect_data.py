import pandas as pd

try:
    df = pd.read_excel("ref/procurement.xlsx")
    print("Columns:", df.columns.tolist())
    print("First few rows:")
    print(df.head())
    print("Data types:")
    print(df.dtypes)
except Exception as e:
    print(e)
