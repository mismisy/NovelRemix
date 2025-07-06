import os
import re


def process_texts_in_folder():

    folder_path = '.'

    pattern = re.compile(r'第.*?章')

    print("--- 开始批量处理 TXT 文件 ---")
    print(f"将在文件夹: {os.path.abspath(folder_path)} 中操作")
    print("\n!!! 警告: 此操作将直接修改文件本身 !!!")
    print("!!! 请确保您已经备份了原始文件。 !!!\n")
    try:
        input("确认已备份后，请按 Enter 键继续，或按 Ctrl+C 取消...")
    except KeyboardInterrupt:
        print("\n操作已取消。")
        return

    processed_count = 0
    skipped_count = 0

    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            content = None
            detected_encoding = None

            # 尝试用两种主要编码格式打开文件
            for encoding in ['utf-8', 'gbk']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    detected_encoding = encoding
                    break  # 如果成功读取，就跳出循环
                except UnicodeDecodeError:
                    continue  # 如果解码失败，就尝试下一种编码

            if not content:
                print(f"跳过: {filename} (无法用 utf-8 或 gbk 解码)")
                skipped_count += 1
                continue

            match = pattern.search(content)

            if match:

                start_index = match.start()

                new_content = content[start_index:]

                # 将处理后的内容写回文件，使用读取时成功的编码
                with open(file_path, 'w', encoding=detected_encoding) as f:
                    f.write(new_content)

                print(f"已处理: {filename} (使用 {detected_encoding} 编码)")
                processed_count += 1
            else:
                print(f"跳过: {filename} (未找到 '第...章' 格式的标题)")
                skipped_count += 1

    print("\n--- 全部处理完毕 ---")
    print(f"成功处理 {processed_count} 个文件，跳过 {skipped_count} 个文件。")
    input("按 Enter 键退出...")


# 运行主函数
if __name__ == "__main__":
    process_texts_in_folder()
