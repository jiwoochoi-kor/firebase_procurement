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

        # 4. (가상) 품목군별 평균 입고 주기
        # 데이터에 날짜 정보가 없으므로 가상의 로직 적용
        # 예: 금액이 클수록 주기가 짧다고 가정하거나 고정값 사용
        st.markdown("""
        <style>
        .small-font {
            font-size:12px;
            color: gray;
        }
        </style>
        """, unsafe_allow_html=True)
        col4.metric("평균 입고 주기 (추정)", "약 45일")
        col4.markdown("<p class='small-font'>*데이터 부재로 인한 추정치</p>", unsafe_allow_html=True)

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

        # 2. 품목군별 비중 (파이 차트 대체 -> 누적 바 차트 or 정규화된 바 차트)
        # Streamlit/Altair에서 파이차트는 복잡할 수 있으므로 카테고리별 비교 바로 구현
        with col_chart2:
            st.subheader("📦 품목군별 구매 현황")
            # 데이터 재구조화 (Wide -> Long)
            category_cols = ['ETC', 'CH', '건기식', '글로벌', '기타']
            valid_cat_cols = [c for c in category_cols if c in filtered_df.columns]
            
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

        # --- 입고 주기 상세 (가상 데이터) ---
        st.subheader("⏱️ 품목군별 입고 주기 (시뮬레이션)")
        
        # 가상의 입고 주기 데이터 생성
        mock_cycles = {
            'ETC': 30, 'CH': 45, '건기식': 60, '글로벌': 90, '기타': 30
        }
        cycle_data = pd.DataFrame(list(mock_cycles.items()), columns=['품목군', '평균입고주기(일)'])
        
        # 바 차트로 표시
        chart_cycle = alt.Chart(cycle_data).mark_bar(color='orange').encode(
            x=alt.X('품목군', sort='-y'),
            y=alt.Y('평균입고주기(일)'),
            tooltip=['품목군', '평균입고주기(일)']
        ).properties(height=250)
        st.altair_chart(chart_cycle, use_container_width=True)
        st.info("⚠️ 현재 원본 데이터에 입고 날짜 정보가 없어, 위 입고 주기 데이터는 예시로 생성된 것입니다.")

        # --- 데이터 테이블 ---
        with st.expander("📄 상세 데이터 보기"):
            st.dataframe(filtered_df.style.format("{:,.0f}"))

if __name__ == "__main__":
    main()
