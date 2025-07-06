from google import genai
import os
import asyncio
from pathlib import Path

# --- 1. 配置区域 ---
try:

    client = genai.Client(api_key="你的key")
except (ValueError, KeyError, NameError):
    print("错误：请在代码中直接提供您的 API 密钥。")
    exit()

MODEL_NAME = "gemini-2.5-pro"

# 定义您任务所需的特定提示词
PROMPT_TEMPLATE = """
你是一名专业的文学编辑和语言专家。你的任务是将一部长篇小说中的男性主人公（原名为[]）与换为女性主人公（新名为[]）。在转换过程中，你必须严格遵守以下规则：
1. 保持原有故事情节和所有人物关系（包括[]与女性配偶[]关系）完全不变。
2. 将所有指代[]的男性称谓（如“他”、“先生”、“哥”等）替换为恰当的女性称谓（如“她”、“女士”、“姐”等）。
3. 将所有男性特有的行为、动作和身体描述（如“摸了摸胡子”、“魁梧的身材”、“粗犷的声音”）转换为语义上恰当的女性化表达（如“摸了摸下巴”、矫健的身材”、“柔和的声音”）。
4. 如果遇见男性角色与主角过于亲密的行为请适度更改,例如与男性属下的拥抱改成握手。
5. 避免引入任何性别刻板印象或偏见。
6. 仅对文本中与[]性别相关的部分进行修改，其他内容保持原样。
请改文：
{document_content}
"""

SOURCE_DOCUMENTS_DIR = Path("output")
PROCESSED_RESULTS_DIR = Path("processed_results")
CONCURRENT_REQUESTS_LIMIT = 5


async def process_single_document(file_path, semaphore):

    async with semaphore:
        print(f" 正在处理: {file_path.name}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            full_prompt = PROMPT_TEMPLATE.format(document_content=content)


            response = await asyncio.to_thread(
                client.models.generate_content,
                model=MODEL_NAME,
                contents=full_prompt
            )

            output_path = PROCESSED_RESULTS_DIR / file_path.name
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            print(f" 处理完成并已保存: {output_path.name}")
            return (file_path.name, "成功")

        except Exception as e:
            print(f" 处理失败: {file_path.name}, 错误: {e}")
            return (file_path.name, f"失败: {e}")


async def main():
    """主执行函数。"""
    print("--- Gemini 文档批量处理器 ---")

    SOURCE_DOCUMENTS_DIR.mkdir(exist_ok=True)
    PROCESSED_RESULTS_DIR.mkdir(exist_ok=True)
    print(f"源文件夹: {SOURCE_DOCUMENTS_DIR.resolve()}")
    print(f"结果文件夹: {PROCESSED_RESULTS_DIR.resolve()}")

    txt_files = list(SOURCE_DOCUMENTS_DIR.glob("*.txt"))

    if not txt_files:
        print("\n在源文件夹中未找到 .txt 文件。请添加您的文档后重试。")
        return

    print(f"\n发现 {len(txt_files)} 个文档。开始处理...")

    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS_LIMIT)
    tasks = [process_single_document(file_path, semaphore) for file_path in txt_files]
    results = await asyncio.gather(*tasks)

    print("\n--- 处理结果汇总 ---")
    success_count = sum(1 for _, status in results if status == "成功")
    failure_count = len(results) - success_count

    print(f"总计文件数: {len(results)}")
    print(f"成功: {success_count}")
    print(f"失败: {failure_count}")

    if failure_count > 0:
        print("\n处理失败的文件列表:")
        for filename, status in results:
            if status != "成功":
                print(f"- {filename}: {status}")


if __name__ == "__main__":
    asyncio.run(main())