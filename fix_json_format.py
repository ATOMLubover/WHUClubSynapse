import json
import re
import sys

def parse_concatenated_json(json_string):
    decoder = json.JSONDecoder()
    all_objects = []
    idx = 0
    while idx < len(json_string):
        try:
            obj, end_idx = decoder.raw_decode(json_string, idx)
            all_objects.append(obj)
            idx = end_idx
            # 跳过任何对象之间的空白字符
            while idx < len(json_string) and json_string[idx].isspace():
                idx += 1
        except json.JSONDecodeError:
            # 如果解码失败，尝试跳过一个字符并继续
            # 这可以帮助跳过不属于 JSON 结构但又存在于文件中的异常字符
            idx += 1
            # print(f"Warning: Decoding failed at index {idx-1}. Skipping character.", file=sys.stderr)
    return all_objects

def fix_data_json(input_json_string):
    parsed_objects = parse_concatenated_json(input_json_string)
    all_users = []
    for data in parsed_objects:
        if "users" in data and isinstance(data["users"], list):
            all_users.extend(data["users"])
    combined_data = {"users": all_users}
    return json.dumps(combined_data, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    file_path = "data.json"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        fixed_content = fix_data_json(raw_content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"Successfully fixed {file_path}")
    except FileNotFoundError:
        print(f"Error: {file_path} not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1) 