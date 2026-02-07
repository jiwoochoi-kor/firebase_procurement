import streamlit as st
import pandas as pd
import altair as alt

# 페이지 설정
st.set_page_config(
    page_title="구매현황 대시보드",
    page_icon="📊",
    layout="wide"
)

# 데이터 로드 함수
@st.cache_data
def load_data():
    file_path = "ref/procurement.xlsx"
    try:
        # 헤더가 3행(index 2)에 위치함
        df = pd.read_excel(file_path, header=2)
        
        # 필요한 컬럼만 선택 (실제 데이터에 존재하는 컬럼인지 확인 필요)
        # '연' 컬럼이 연도인 것으로 추정
        target_cols = ['연', '전체 구매금액', 'ETC', 'CH', '건기식', '글로벌', '기타']
        
        # 존재하는 컬럼만 필터링
        existing_cols = [col for col in target_cols if col in df.columns]
        df = df[existing_cols]
        
        # 연도 데이터가 있는 행만 필터링 (NaN 제거)
        df = df.dropna(subset=['연'])
        
        # 연도를 정수로 변환
        df['연'] = df['연'].astype(int)
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None

# 메인 함수
def main():
    st.title("📊 구매현황 대시보드")
    st.markdown("---")

    df = load_data()

    if df is not None:
        # 사이드바 설정
        st.sidebar.header("설정")
        year_list = sorted(df['연'].unique().tolist())
        selected_years = st.sidebar.multiselect("연도 선택", year_list, default=year_list)

        # 데이터 필터링
        filtered_df = df[df['연'].isin(selected_years)]

        # --- KPI 섹션 ---
        st.subheader("📌 주요 지표 (Key Metrics)")
        
        col1, col2, col3, col4 = st.columns(4)

        # 1. 전체 기간 총 구매금액
        total_purchases = filtered_df['전체 구매금액'].sum()
        col1.metric("총 구매금액", f"{total_purchases:,.0f} 원")

        # 2. 최신 연도 구매금액 & YoY
        if not filtered_df.empty:
            latest_year = filtered_df['연'].max()
            latest_val = filtered_df[filtered_df['연'] == latest_year]['전체 구매금액'].values[0]
            
            # 전년도 찾기
            prev_year = latest_year - 1
            prev_val_df = df[df['연'] == prev_year]
            
            delta = None
            if not prev_val_df.empty:
                prev_val = prev_val_df['전체 구매금액'].values[0]
                delta = f"{((latest_val - prev_val) / prev_val * 100):.1f}%"
            
            col2.metric(f"{latest_year}년 구매금액", f"{latest_val:,.0f} 원", delta=delta)
        else:
            col2.metric("최신 연도 구매금액", "-")

        # 3. 평균 구매금액
        avg_purchase = filtered_df['전체 구매금액'].mean()
        col3.metric("연평균 구매금액", f"{avg_purchase:,.0f} 원")

        # 4. 품목군별 평균 입고 주기 (구매금액 기반 추정)
        # 로직: 구매금액이 높을수록 주기가 짧다 (더 자주 입고)
        # 기준: 연간 1000만원 -> 30일 주기
        # 주기 = (기준금액 / (해당 품목 평균 구매액)) * 기준주기
        
        category_cols = ['ETC', 'CH', '건기식', '글로벌', '기타']
        valid_cat_cols = [c for c in category_cols if c in filtered_df.columns]
        
        estimated_cycles = {}
        if valid_cat_cols:
            base_amount = 1000  # 기준 금액 (단위: 원, 데이터 스케일에 맞게 조정 필요)
            base_cycle = 30     # 기준 주기 (일)
            
            # 전체 데이터에서의 평균값 계산 (필터링 전 전체 기준)
            mean_vals = df[valid_cat_cols].mean()
            
            for cat in valid_cat_cols:
                avg_val = mean_vals[cat]
                if avg_val > 0:
                    # 금액이 클수록 주기가 작아지도록 역수 관계 설정
                    # (스케일 조정: 전체 평균의 평균값으로 정규화)
                    normalized_val = avg_val / mean_vals.mean()
                    cycle = base_cycle / normalized_val if normalized_val > 0 else 90
                    estimated_cycles[cat] = round(max(5, min(cycle, 180))) # 5일 ~ 180일 사이로 제한
                else:
                    estimated_cycles[cat] = 0

            avg_cycle_all = sum(estimated_cycles.values()) / len(estimated_cycles) if estimated_cycles else 0
            col4.metric("평균 입고 주기 (추정)", f"약 {avg_cycle_all:.0f}일")
            col4.markdown("<p style='font-size:12px; color:gray'>*구매금액 기반 추정치 (금액↑ 주기↓)</p>", unsafe_allow_html=True)
        else:
             col4.metric("평균 입고 주기", "-")

        st.markdown("---")

        # --- 차트 섹션 ---
        col_chart1, col_chart2 = st.columns(2)

        # 1. 연도별 전체 구매금액 추이
        with col_chart1:
            st.subheader("📅 연도별 구매금액 추이")
            chart_trend = alt.Chart(filtered_df).mark_bar().encode(
                x=alt.X('연:O', title='연도'),
                y=alt.Y('전체 구매금액', title='구매금액'),
                tooltip=['연', '전체 구매금액']
            ).properties(height=300)
            st.altair_chart(chart_trend, use_container_width=True)

        # 2. 품목군별 비중
        with col_chart2:
            st.subheader("📦 품목군별 구매 현황")
            if valid_cat_cols:
                df_melted = filtered_df.melt(id_vars=['연'], value_vars=valid_cat_cols, var_name='품목군', value_name='금액')
                
                chart_cat = alt.Chart(df_melted).mark_bar().encode(
                    x=alt.X('연:O', title='연도'),
                    y=alt.Y('금액', title='구매금액'),
                    color='품목군',
                    tooltip=['연', '품목군', '금액']
                ).properties(height=300)
                st.altair_chart(chart_cat, use_container_width=True)
            else:
                st.info("품목군 데이터가 없습니다.")

        # 3. 품목군별 트렌드 (라인 차트)
        st.subheader("📈 품목군별 성장 추이")
        if valid_cat_cols:
            chart_line = alt.Chart(df_melted).mark_line(point=True).encode(
                x=alt.X('연:O', title='연도'),
                y=alt.Y('금액', title='구매금액'),
                color='품목군',
                tooltip=['연', '품목군', '금액']
            ).properties(height=400)
            st.altair_chart(chart_line, use_container_width=True)

        # --- 입고 주기 상세 (추정 데이터) ---
        st.subheader("⏱️ 품목군별 입고 주기 (추정)")
        
        if estimated_cycles:
            cycle_data = pd.DataFrame(list(estimated_cycles.items()), columns=['품목군', '추정입고주기(일)'])
            
            # 바 차트로 표시
            chart_cycle = alt.Chart(cycle_data).mark_bar(color='orange').encode(
                x=alt.X('품목군', sort='-y'),
                y=alt.Y('추정입고주기(일)'),
                tooltip=['품목군', '추정입고주기(일)']
            ).properties(height=250)
            st.altair_chart(chart_cycle, use_container_width=True)
            st.info("ℹ️ 입고 주기는 각 품목군의 평균 구매금액에 반비례한다고 가정하여 산출했습니다. (구매액이 높을수록 자주 입고)")

        # --- 데이터 테이블 ---
        with st.expander("📄 상세 데이터 보기"):
            st.dataframe(filtered_df.style.format("{:,.0f}"))

if __name__ == "__main__":
    main()
