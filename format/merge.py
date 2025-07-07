import os
import glob

# --- 配置 ---
# 合并后输出的文件名
output_filename = '某小说改.txt'
# 每个文件之间的分隔符，\n 代表换行。你可以自定义成任何你想要的格式。
# 例如：'\n\n----------\n\n' 会在文件之间插入一条分割线
separator = '\n\n'


def merge_txt_files():

    all_txt_files = sorted(glob.glob('*.txt'))

    if os.path.basename(__file__) in all_txt_files:
        all_txt_files.remove(os.path.basename(__file__))
    if output_filename in all_txt_files:
        all_txt_files.remove(output_filename)

    print(f"准备合并以下 {len(all_txt_files)} 个文件到 {output_filename}:")
    for f in all_txt_files:
        print(f" - {f}")

    # 使用 'w' 模式打开输出文件，这意味着如果文件已存在，会先清空它
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for index, filename in enumerate(all_txt_files):
            content = None
            # 尝试用 utf-8 和 gbk 两种编码读取，提高成功率
            for encoding in ['utf-8', 'gbk']:
                try:
                    with open(filename, 'r', encoding=encoding) as infile:
                        content = infile.read()
                    break  # 读取成功
                except Exception:
                    continue  # 尝试下一种编码

            if content:
                outfile.write(content)
                # 在文件之间添加分隔符，但最后一个文件后面不加
                if index < len(all_txt_files) - 1:
                    outfile.write(separator)
            else:
                print(f"警告: 读取文件 {filename} 失败，已跳过。")

    print(f"\n合并完成！所有内容已保存至 {output_filename}")


# --- 运行 ---
if __name__ == '__main__':
    merge_txt_files()
    input("按 Enter 键退出...")
