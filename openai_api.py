import os
import time
import concurrent.futures
from openai import OpenAI

# API密钥，有些服务可能要求在前面加上 "Bearer "，请根据服务商文档操作
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# 第三方URL，必须包含路径，通常以 /v1 结尾
BASE_URL = "https://your-third-party-url.com/v1"
# CRITICAL: 您需要使用的模型名称，这个需要您的服务商提供
MODEL_NAME = "gpt-4-turbo"
# 输入和输出文件夹：改一下
INPUT_FOLDER = '输入的文件夹目录'
OUTPUT_FOLDER = '输出的文件夹目录'

SYSTEM_PROMPT = """
你是一名专业的文学编辑和语言专家。你的任务是将一部长篇小说中的男性主人公（原名为[]）与换为女性主人公（新名为[]）。在转换过程中，你必须严格遵守以下规则：
1. 保持原有故事情节和所有人物关系（包括[]与女性配偶[]关系）完全不变。
2. 将所有指代[]的男性称谓（如“他”、“先生”、“哥”等）替换为恰当的女性称谓（如“她”、“女士”、“姐”等）。
3. 将所有男性特有的行为、动作和身体描述（如“摸了摸胡子”、“魁梧的身材”、“粗犷的声音”）转换为语义上恰当的女性化表达（如“摸了摸下巴”、矫健的身材”、“柔和的声音”）。
4. 如果遇见男性角色与主角过于亲密的行为请适度更改,例如与男性属下的拥抱改成握手。
5. 避免引入任何性别刻板印象或偏见。
6. 仅对文本中与[]性别相关的部分进行修改，其他内容保持原样。
请改文：
"""


MAX_WORKERS = 5

try:

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=BASE_URL,
    )
    print(f"客户端初始化成功，准备请求URL: {BASE_URL}")
except Exception as e:
    print(f"客户端初始化错误: {e}")
    exit()

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def process_single_file(filename):

    input_filepath = os.path.join(INPUT_FOLDER, filename)
    output_filename = f"processed_{filename}"
    output_filepath = os.path.join(OUTPUT_FOLDER, output_filename)

    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            document_content = f.read()

        if not document_content.strip():
            return f"文件 {filename} 为空，已跳过。"

        # UPDATED: 构建OpenAI格式的 messages 列表
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": document_content}
        ]

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.1,
        )

        result_text = response.choices[0].message.content.strip()

        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(result_text)

        return f"文件 {filename} 处理成功。"
    except Exception as e:
        error_message = f"处理文件 {filename} 时发生错误: {e}"
        with open(os.path.join(OUTPUT_FOLDER, 'error_log.txt'), 'a', encoding='utf-8') as log_file:
            log_file.write(f"{filename}: {e}\n")
        return error_message


def process_all_files_parallel():

    files_to_process = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.txt')]
    total_files = len(files_to_process)
    print(f"找到 {total_files} 个.txt文件，使用最多 {MAX_WORKERS} 个线程并行处理。")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_file = {executor.submit(process_single_file, filename): filename for filename in files_to_process}

        for i, future in enumerate(concurrent.futures.as_completed(future_to_file)):
            result = future.result()
            print(f"[{i + 1}/{total_files}] {result}")


if __name__ == "__main__":
    start_time = time.time()
    process_all_files_parallel()
    end_time = time.time()
    print(f"\n所有文件处理完毕！总耗时: {end_time - start_time:.2f} 秒。")