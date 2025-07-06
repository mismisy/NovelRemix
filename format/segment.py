import re
import os


def split_novel_chapters(input_file, output_dir="output"):
    """
    分割小说章节到单独文件
    :param input_file: 输入文件路径
    :param output_dir: 输出目录（默认chapters）
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件 '{input_file}' 不存在！")
        return

    try:
        # 读取小说内容
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件出错: {e}")
        return

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 增强版正则匹配章节标题（兼容中文数字和多种章节标识）
    chapter_pattern = re.compile(
        r'(第\s*[零一二三四五六七八九十百千\d]+\s*[章节卷集部篇回]\s*[^\n]*)'
    )

    matches = list(chapter_pattern.finditer(content))

    if not matches:
        print("未找到章节标题！")
        # 尝试保存整个文件作为补偿
        output_file = os.path.join(output_dir, "full_content.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已将全部内容保存到: {output_file}")
        return

    # 提取所有章节位置
    chapter_starts = [m.start() for m in matches]
    chapter_titles = [m.group(0).strip() for m in matches]

    # 添加结束位置
    chapter_starts.append(len(content))

    # 分割并保存章节
    for i in range(len(chapter_starts) - 1):
        start = chapter_starts[i]
        end = chapter_starts[i + 1]
        chapter_content = content[start:end].strip()

        # 清理文件名中的非法字符
        clean_title = re.sub(r'[\\/*?:"<>|]', "", chapter_titles[i])
        # 生成文件名（序号+标题）
        output_file = os.path.join(output_dir, f"{i + 1:04d}_{clean_title}.txt")

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(chapter_content)
            print(f"已保存: {os.path.basename(output_file)}")
        except Exception as e:
            print(f"保存章节失败: {e}")

    print(f"\n完成！共分割 {len(matches)} 个章节")


# 使用示例
if __name__ == "__main__":
    novel_file = "苟在妖武乱世修仙1-1100全本完结.txt"  # 替换为你的小说文件路径
    split_novel_chapters(novel_file)
