import os
import glob
import argparse
import codecs

encodings = ['utf-8', 'shift_jis', 'gbk', 'utf-16']
    
def detect_encoding(file_path):
    """
    尝试检测文件的编码格式
    """

    for encoding in encodings:
        try:
            with codecs.open(file_path, 'r', encoding=encoding) as f:
                # 尝试读取前几行来验证编码
                for _ in range(5):
                    line = f.readline()
                    if not line:
                        break
                return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception:
            continue
    
    return 'binary'

def search_in_file(file_path, search_string, encoding=None):
    """
    在文件中搜索指定字符串
    """
    matches = []
    line_num = 0
    
    if encoding is None:
        encoding = detect_encoding(file_path)
    
        if encoding == 'binary':
            # 对于二进制文件，使用二进制模式读取并尝试Unicode解码
            with open(file_path, 'rb') as f:
                content = f.read()
                # 尝试将二进制内容解码为字符串进行搜索
                for c in ['utf-8', 'utf-16']:
                    try:
                        decoded_content = content.decode(c, errors='ignore')
                        line_num = decoded_content.index(search_string)
                        matches.append(f"第{line_num}(binrary pos: {line_num*2})个字符匹配: {search_string}")
                        break
                    except:
                        pass
        else:
            try:
                with codecs.open(file_path, 'r', encoding=encoding) as f:
                    for line in f:
                        line_num += 1
                        if search_string in line:
                            matches.append(f"第{line_num}行: {line.strip()}")
            except:
                pass
    
    return matches

def main():
    parser = argparse.ArgumentParser(description='在文件中搜索指定字符串')
    parser.add_argument('pattern', help='文件名匹配模式(glob规则)')
    parser.add_argument('search_string', help='要搜索的字符串')
    parser.add_argument('-e', '--encoding', help='指定编码(默认自动检测)', 
                        choices=encodings,
                        default=None)
    
    args = parser.parse_args()
    
    # 获取当前目录
    current_dir = os.getcwd()
    print(f"在当前目录搜索: {current_dir}")
    print(f"文件模式: {args.pattern}")
    print(f"搜索字符串: {args.search_string}")
    if args.encoding:
        print(f"指定编码: {args.encoding}")
    else:
        print("编码: 自动检测")
    print("-" * 50)
    
    # 使用glob查找匹配的文件
    file_list = glob.glob(args.pattern, recursive=True)
    
    if not file_list:
        print("没有找到匹配的文件")
        return
    
    found_count = 0
    
    for file_path in file_list:
        # 跳过目录
        if os.path.isdir(file_path):
            continue
            
        # 获取相对路径
        rel_path = os.path.relpath(file_path, current_dir)
        
        # 在文件中搜索
        matches = search_in_file(file_path, args.search_string, args.encoding)
        
        if matches:
            found_count += 1
            print(f"\n找到匹配的文件: {rel_path}")
            for match in matches:
                print(f"  -> {match}")
    
    print("-" * 50)
    print(f"搜索完成! 共找到 {found_count} 个文件包含指定字符串")

if __name__ == "__main__":
    main()