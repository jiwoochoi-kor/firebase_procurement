import pandas as pd

try:
    # Header is likely at index 2 (3rd row)
    df = pd.read_excel("ref/procurement.xlsx", header=2)
    print("Columns found in header row:")
    print(df.columns.tolist())
except Exception as e:
    print(e)
