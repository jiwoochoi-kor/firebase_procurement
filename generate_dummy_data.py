import pandas as pd
import os

# 디렉토리 생성
os.makedirs("ref", exist_ok=True)

# 더미 데이터 생성
data = {
    "연": [2020, 2021, 2022, 2023, 2024],
    "전체 구매금액": [50000000, 55000000, 60000000, 58000000, 70000000],
    "ETC": [10000000, 11000000, 12000000, 11500000, 14000000],
    "CH": [20000000, 22000000, 24000000, 23000000, 28000000],
    "건기식": [5000000, 5500000, 6000000, 6500000, 7000000],
    "글로벌": [10000000, 11000000, 12000000, 11000000, 13000000],
    "기타": [5000000, 5500000, 6000000, 6000000, 8000000]
}

df = pd.DataFrame(data)

# 헤더가 3행(index 2)에 위치하도록 빈 행 추가
empty_row = pd.DataFrame([[None] * len(df.columns)], columns=df.columns)
df_final = pd.concat([empty_row, empty_row, df], ignore_index=True)

# 엑셀 파일로 저장
file_path = "ref/procurement.xlsx"
df_final.to_excel(file_path, index=False, header=True)
print(f"Created {file_path}")
