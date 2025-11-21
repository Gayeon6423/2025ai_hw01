import streamlit as st
import pandas as pd
import datetime
import re
import requests
headers = {'ngrok-skip-browser-warning': 'true'}
response = requests.get('https://5ac71b8d6f60.ngrok-free.app', headers=headers)

# 🚀 페이지 기본 설정 (가장 먼저 실행되어야 합니다)
st.set_page_config(
    page_title="HW 01 리더보드",
    page_icon="🏆",
    layout="wide"  # 페이지를 넓게 사용합니다.
)

import os
from pathlib import Path
# --- 데이터 관리 ---

def get_leaderboard_data():
    """
    학생 ID 및 점수 데이터를 반환합니다.
    (데이터가 길어서 함수로 분리했습니다.)
    """
    # 학생 ID 리스트 🧑‍🎓
    student_id = [
        20231837, 20211402, 20211733, 20231851, 20231852, 20231846, 20231831, 20231843,
        20230320, 20231854, 20220378, 20211168, 20210261, 20200025, 20231218, 20241901,
        20221593, 20201227, 20241909, 20211166, 20241584, 20200307, 20232241, 20220154,
        20231834, 20231842, 20211352, 20211188, 20181599, 20201608, 20201625, 20191347,
        20221931, 20201396, 20221995, 20221201, 20201638, 20200595, 20201607, 20211014,
        20201663, 20221300, 20231838, 20191666, 20191579
    ]

    # Accuracy 점수 (예시 데이터) 🎯
    accuracy_dict = {
        20231837: 0, 20211402: 0, 20211733: 0, 20231851: 0, 20231852: 0,
        20231846: 0, 20231831: 0, 20231843: 0, 20230320: 0, 20231854: 0,
        20220378: 0, 20211168: 0, 20210261: 0, 20200025: 0, 20231218: 0,
        20241901: 0, 20221593: 0, 20201227: 0, 20241909: 0, 20211166: 0,
        20241584: 0, 20200307: 0, 20232241: 0, 20220154: 0, 20231834: 0,
        20231842: 0, 20211352: 0, 20211188: 0, 20181599: 0, 20201608: 0,
        20201625: 0, 20191347: 0, 20221931: 0, 20201396: 0, 20221995: 0,
        20221201: 0, 20201638: 0, 20200595: 0, 20201607: 0, 20211014: 0,
        20201663: 0, 20221300: 0, 20231838: 0, 20191666: 0, 20191579: 0
    }
    
    # RMSE 점수 (예시 데이터) 📉
    rmse_dict = {
        20231837: 999, 20211402: 999, 20211733: 999, 20231851: 999, 20231852: 999,
        20231846: 999, 20231831: 999, 20231843: 999, 20230320: 999, 20231854: 999,
        20220378: 999, 20211168: 999, 20210261: 999, 20200025: 999, 20231218: 999,
        20241901: 999, 20221593: 999, 20201227: 999, 20241909: 999, 20211166: 999,
        20241584: 999, 20200307: 999, 20232241: 999, 20220154: 999, 20231834: 999,
        20231842: 999, 20211352: 999, 20211188: 999, 20181599: 999, 20201608: 999,
        20201625: 999, 20191347: 999, 20221931: 999, 20201396: 999, 20221995: 999,
        20221201: 999, 20201638: 999, 20200595: 999, 20201607: 999, 20211014: 999,
        20201663: 999, 20221300: 999, 20231838: 999, 20191666: 999, 20191579: 999
    }
    
    

# --- DataFrame 생성 함수 ---

    
    # ---  추가: grading CSV가 있으면 최신 파일을 불러와 dict 업데이트 ---
    try:
        grading_dir = Path(__file__).resolve().parent.parent / "grading"
        if grading_dir.exists():
            files = list(grading_dir.glob('grading_mymethod_*.csv'))
        else:
            files = []

        if files:
            latest = max(files, key=lambda p: p.stat().st_mtime)
            # 읽기 및 매핑
            try:
                df_new = pd.read_csv(latest)
                updated_count = 0
                added_count = 0
                for _, row in df_new.iterrows():
                    try:
                        sid = int(row['student_id'])
                    except Exception:
                        # student_id가 비정상이면 건너뜀
                        continue

                    # Accuracy 업데이트 (있고 변화가 있을 때만)
                    if 'Accuracy' in row and pd.notna(row['Accuracy']):
                        new_acc = float(row['Accuracy'])
                        old_acc = accuracy_dict.get(sid)
                        if old_acc is None or abs(old_acc - new_acc) > 1e-9:
                            accuracy_dict[sid] = new_acc
                            updated_count += 1

                    # RMSE 업데이트
                    if 'RMSE' in row and pd.notna(row['RMSE']):
                        new_rmse = float(row['RMSE'])
                        old_rmse = rmse_dict.get(sid)
                        if old_rmse is None or abs(old_rmse - new_rmse) > 1e-9:
                            rmse_dict[sid] = new_rmse
                            updated_count += 1

                    # student_id 목록에 없으면 추가
                    if sid not in student_id:
                        student_id.append(sid)
                        added_count += 1

                # 간단한 로그 출력 (Streamlit UI에서 확인 가능)
                try:
                    m = re.search(r'(\d{8})_(\d{4})', latest.name)
                    date_part = m.group(1)
                    time_part = m.group(2) 
                    dt = datetime.datetime.strptime(date_part + time_part, '%Y%m%d%H%M')
                    formatted = dt.strftime('%Y-%m-%d %H:%M:%S')
                    st.info(f"🗓️ 리더보드는 매일 오전 업데이트 됩니다. (업데이트 시간: {formatted})")
                except Exception:
                    print(f"업데이트: {latest}")

            except Exception as e:
                # CSV 파싱 실패시 무시하고 기존 dict 사용
                print(f"Failed to parse grading CSV {latest}: {e}")

    except Exception as e:
        print(f"Failed to load grading updates: {e}")

    # 함수 종료 시 최신화된 값을 반환
    return student_id, accuracy_dict, rmse_dict

def create_leaderboard_df(student_id, scores_dict, metric_name, ascending=False):
    """리더보드 순위가 매겨진 DataFrame을 생성합니다."""
    
    df = pd.DataFrame({'Student_ID': student_id})
    df[metric_name] = df['Student_ID'].map(scores_dict)
    
    # 점수가 없는 학생은 리더보드에서 제외
    df = df.dropna(subset=[metric_name])
    
    # 점수 기준으로 정렬
    df = df.sort_values(by=metric_name, ascending=ascending).reset_index(drop=True)
    
    # 순위(Rank)를 1부터 시작하도록 설정
    df.index += 1
    df.index.name = 'Rank'
    
    # Student_ID를 문자열로 변경 (표시용)
    df['Student_ID'] = df['Student_ID'].astype(str)
    
    # RMSE는 소수점 3자리까지만 표시
    if metric_name == 'RMSE':
        df[metric_name] = df[metric_name].round(3)
        
    return df

# --- Streamlit 앱 메인 로직 ---

def main():
    # --- 1. 타이틀 및 설명 ---
    st.title("🏆 HW 01 Leaderboard")
    st.markdown("본 리더보드는 당뇨병 및 자살 예측 모델의 **My Method 성능**을 평가하여 순위를 매긴 것입니다.")

    # --- 2. 업데이트 시간 표시 ---
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # st.info(f"🗓️ 리더보드는 매일 오전 업데이트 됩니다. (업데이트 시간: {now})")

    # --- 3. 데이터 로드 ---
    student_id, scores_acc, scores_rmse = get_leaderboard_data()

    # --- 4. Accuracy 리더보드 (당뇨병 예측) ---
    st.divider()  # 시각적 구분선
    st.subheader("🎯 Accuracy (당뇨병 예측 성능)")
    st.markdown("`Accuracy`는 **높을수록** 좋습니다. (1에 가까울수록 우수)")
    
    df_acc = create_leaderboard_df(
        student_id=student_id,
        scores_dict=scores_acc,
        metric_name='Accuracy',
        ascending=False  # 높은 점수가 위로
    )
    # width='stretch'로 설정하여 표를 페이지 너비에 맞춥니다. (이전 use_container_width=True 대체)
    st.dataframe(df_acc, width='stretch')

    # --- 5. RMSE 리더보드 (자살 예측) ---
    st.divider()  # 시각적 구분선
    st.subheader("📉 RMSE (자살 예측 성능)")
    st.markdown("`RMSE`는 **낮을수록** 좋습니다. (0에 가까울수록 우수)")
    
    df_rmse = create_leaderboard_df(
        student_id=student_id,
        scores_dict=scores_rmse,
        metric_name='RMSE',
        ascending=True  # 낮은 점수가 위로
    )
    # width='stretch'로 설정하여 표를 페이지 너비에 맞춥니다. (이전 use_container_width=True 대체)
    st.dataframe(df_rmse, width='stretch')

# --- 스크립트 실행 ---
if __name__ == "__main__":
    main()