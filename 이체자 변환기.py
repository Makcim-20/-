import os
import pandas as pd

# 하위 폴더 포함 여부 설정
include_subfolders = input("하위 폴더의 파일도 포함하시겠습니까? (y/n): ").strip().lower() == 'y'

# 현재 스크립트 실행 폴더 설정
folder_path = os.path.dirname(os.path.abspath(__file__))

# CSV 파일 탐색 및 로드
csv_file_path = None

# 폴더 내의 CSV 파일 검색
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith('.csv'):
            csv_file_path = os.path.join(root, file)
            break

if csv_file_path is None:
    raise FileNotFoundError("CSV 파일을 찾을 수 없습니다.")

replacement_data = pd.read_csv(csv_file_path)

# CSV 데이터를 문자열로 변환 및 NaN 제거
replacement_data = replacement_data.fillna('')
replacement_data['Character'] = replacement_data['Character'].astype(str)
replacement_data['Variants'] = replacement_data['Variants'].astype(str)

# 빈칸 - 빈칸 제거
replacement_data = replacement_data[(replacement_data['Character'] != '') & (replacement_data['Variants'] != '')]

# CSV 데이터를 딕셔너리로 변환 (한자 치환 매핑)
replace_dict = dict(zip(replacement_data['Character'], replacement_data['Variants']))

# 로그 파일 설정
log_file_path = os.path.join(folder_path, 'replacement_log.txt')

with open(log_file_path, 'w', encoding='utf-8') as log_file:
    log_file.write('File Change Log\n')
    log_file.write('================\n')

# 폴더 내의 모든 TXT 파일 검색
for root, dirs, files in os.walk(folder_path):
    # 하위 폴더 포함 여부 확인
    if not include_subfolders and root != folder_path:
        continue

    for file in files:
        if file.endswith('.txt'):
            file_path = os.path.join(root, file)

            # 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 치환 작업 수행 및 로그 작성
            updated_lines = []
            with open(log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(f'{file_path}\n')

                for line_num, line in enumerate(lines):
                    original_line = line
                    modified_line = line
                    line_logged = False

                    for old_char, new_char in replace_dict.items():
                        if old_char in modified_line:
                            # 변환 수행
                            modified_line = modified_line.replace(old_char, new_char)

                            # 로그 즉시 기록
                            if not line_logged:
                                log_file.write(f'Line {line_num + 1}:\n')
                                log_file.write(f'  Original: {original_line.strip()}\n')
                                line_logged = True

                            log_file.write(f'  {old_char} -> {new_char}\n')

                    updated_lines.append(modified_line)

            # 파일 덮어쓰기
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)

print("모든 파일의 한자 치환 작업이 완료되었습니다. 로그가 생성되었습니다.")
