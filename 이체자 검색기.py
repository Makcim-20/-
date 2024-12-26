import os
import csv
from opencc import OpenCC

# 하위 폴더 포함 여부 설정
include_subfolders = input("하위 폴더의 파일도 포함하시겠습니까? (y/n): ").strip().lower() == 'y'


def extract_variants_with_file_info(input_folder, output_csv):
    """텍스트 파일 내의 문자 중 이체자 기록 및 등장 파일 정보 추가"""
    converter_t2s = OpenCC('t2s')  # 번체 → 간체 변환
    converter_s2t = OpenCC('s2t')  # 간체 → 번체 변환

    # 문자별 등장 파일 기록
    char_to_files = {}
    for root, dirs, files in os.walk(input_folder):
        # 하위 폴더 포함 여부 확인
        if not include_subfolders and root != input_folder:
            continue

        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                    for char in set(content):  # 중복 문자 방지
                        if char not in char_to_files:
                            char_to_files[char] = set()
                        char_to_files[char].add(file)

    # 이체자 탐색 및 정리
    results = []
    for char, files in sorted(char_to_files.items()):
        variants = set()
        queue = [char]
        visited = set()

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            # OpenCC 변환
            simplified = converter_t2s.convert(current)
            traditional = converter_s2t.convert(current)

            # 변환된 문자가 파일 내에 존재하면 추가
            for variant in [simplified, traditional]:
                if variant in char_to_files and variant != char:
                    variants.add(variant)
                    queue.append(variant)

        # 결과 저장 (이체자만 기록, 본래 문자 제외)
        if variants:
            results.append({
                'Character': char,
                'Character Files': ', '.join(files),
                'Variants': ', '.join(sorted(variants)),
                'Variants Files': ', '.join(
                    set(file for variant in variants for file in char_to_files.get(variant, []))
                )
            })

    # 결과 CSV 저장
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Character', 'Character Files', 'Variants', 'Variants Files'])
        writer.writeheader()
        writer.writerows(results)

    print(f"처리 완료! 결과 파일: {output_csv}")


def main():
    # 실행 폴더 경로
    current_folder = os.getcwd()
    output_csv = os.path.join(current_folder, "이체자 검색 결과.csv")

    print("텍스트 파일 처리 중...")
    extract_variants_with_file_info(current_folder, output_csv)


if __name__ == "__main__":
    main()
