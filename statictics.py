import json
import argparse

def format_size(size):
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def process_file(file_path):
    results = []
    # 读取文件并处理每一行
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 解析每一行的 JSON 数据
            data = json.loads(line)
            
            # 提取 'ext' 和 'text' 字段
            ext = data.get('ext', 'unknown')
            text = data.get('text', '')
            
            # 计算 text 字段的大小（以字节为单位）
            size = len(text.encode('utf-8'))
            
            # 格式化大小
            formatted_size = format_size(size)
            
            # 存储结果
            results.append((ext, size, formatted_size))
    
    # 按照大小降序排序
    results.sort(key=lambda x: x[1], reverse=True)
    
    # 输出对齐的结果
    print(f"{'ext':<8} {'size':>15}")
    print("=" * 25)
    for ext, _, formatted_size in results[:20]:
        print(f"{ext:<8} {formatted_size:>15}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a JSONL file to extract and sort data by text size.")
    parser.add_argument('filepath', type=str, help="The path to the JSONL file.")
    
    args = parser.parse_args()
    process_file(args.filepath)
