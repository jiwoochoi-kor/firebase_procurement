import pandas as pd

try:
    # 엑셀 파일의 모든 시트 이름을 확인
    xl = pd.ExcelFile("ref/procurement.xlsx")
    print("Sheet names:", xl.sheet_names)
    
    # 첫 번째 시트의 데이터를 좀 더 자세히 확인 (헤더가 첫 번째 행이 아닐 수 있음)
    df = pd.read_excel("ref/procurement.xlsx", header=None)
    print("\nFirst 10 rows without header:")
    print(df.head(10))
except Exception as e:
    print(e)
