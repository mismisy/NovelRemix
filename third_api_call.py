import os
import time
import requests
import concurrent.futures

# ==============================================================================
# 1. 基础配置
# 注意：如果需要把配角也改名字，请在prompt中加入以下被注释的信息：
# -- 【【【新增】】】次要角色性别转换映射表 --
# 在这里定义需要同步转换性别的次要角色（如室友、发小等）
# 格式： "原男性名": "新女性名"
# SECONDARY_CHARACTER_MAP = {
#     "张伟": "张薇",
#     "李浩": "李静",
#     "王强": "王晴"
# }
# 次要角色性别转换映射: {str(SECONDARY_CHARACTER_MAP)} #加到故事配置信息里面
# **具名次要角色**: 严格按照上方“次要角色性别转换映射”的配置，对指定的次要角色进行姓名、性别、代词和相关描述的全面转换。#加入提示词
# ==============================================================================
# ！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
# ！！！！！！！！！！请务必替换为您自己的API_KEY！！！！！！！！！！
# ！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
API_KEY = "你的"  # <--- 在这里填入您的API Key

# CRITICAL: 您的服务API的完整URL
API_URL = "你的"
# CRITICAL: 您需要使用的模型名称
MODEL_NAME = "gemini-2.5-pro"

# 输入和输出文件夹
INPUT_FOLDER = '你自己选一个'
OUTPUT_FOLDER = 'output_你自己选一个'

# 并发线程数与超时设置
MAX_WORKERS = 8
REQUEST_TIMEOUT = 320


# ==============================================================================
# 2. AI指令配置区域 (在此处修改角色信息)
# ==============================================================================
# -- 主角信息 --
original_protagonist_name = "原名"
new_protagonist_name = "新的名字"
original_protagonist_gender = "男"
new_protagonist_gender = "女"

# -- 故事背景与人物关系 (帮助AI更好地理解上下文) --
story_context = "近未来科幻，社会观念相对开放" #看情况需求更改
key_relationship_character_name = "伴侣名字"  # 将伴侣名字也作为变量
key_relationship = f"主角与“{key_relationship_character_name}”是核心伴侣关系"


# ==============================================================================
# 3. 系统提示词模板 (根据上方配置自动生成)
# ==============================================================================
# 使用f-string将配置动态插入到提示词中，无需手动修改此处
SYSTEM_PROMPT = f"""
# AI角色与核心任务
你是一位兼具顶级文学编辑、社会学家和逻辑推理能力的专家。你的核心任务是为一个长篇故事的主角进行性别转换，并确保整个故事在逻辑、情感和社交层面上保持高度的真实性和一致性。

**核心原则：优先确保逻辑自洽与角色真实性，绝不进行机械、无脑的文本替换。**

---
# 故事配置信息
-   原主角名: {original_protagonist_name}
-   新主角名: {new_protagonist_name}
-   原主角性别: {original_protagonist_gender}
-   新主角性别: {new_protagonist_gender}
-   关键人物关系: {key_relationship}
-   故事背景简介: {story_context}
-   **【【【绝对规则】】】**: {new_protagonist_name}与{key_relationship_character_name}的关系是 **同性女性伴侣（女同性恋）关系**。**严禁** 为了维持异性恋关系而更改 {key_relationship_character_name} 或任何其他角色的性别。所有角色的性别（除主角外）必须保持原样。

---
# 修改执行阶段

## 第一阶段：表层文本编辑 (Surface Edit)
此阶段处理最直观的文本变更。
1.  **称谓与指代**: 将所有与原性别相关的代词（如“他/她”）、称谓（如“先生/女士”、“哥/姐”）等，准确无误地替换为符合新性别的词语。
2.  **物理与外貌描述**: 将基于原性别的外貌和生理特征描述（如“宽阔的肩膀”、“喉结”），转换为符合新性别且贴合角色设定的描述。

## 第二阶段：行为互动调整 (Behavioral Edit)
此阶段专注于角色的行为和社交方式。
3.  **标志性动作**: 审视并调整带有性别色彩的习惯动作（如“抚摸胡茬”）。将其改为符合新性别身份和角色性格的新动作（如“将碎发拨到耳后”）。
4.  **社交礼仪与物理接触**: 根据社会文化背景，重新评估主角与他人的物理接触尺度和社交方式。例如，表示赞许的“拥抱”可能需调整为“有力的握手”或“一个鼓励的眼神”。

## 第三阶段：深层逻辑重构 (Deep Logical Reconstruction)
这是整个任务最核心、最重要的阶段。你必须模拟真人的思考过程，推理并重写因性别变化而受到冲击的逻辑链。
5.  **【外部逻辑】重构他人视角**:
    -   **核心思考点**: “世界和其他角色看待主角的方式，会因其性别变化而产生何种根本性的不同？”
    -   **执行要求**: 重写对话和旁白中其他角色的猜测、评判和反应。他们的逻辑起点和推理过程必须符合社会对新性别的普遍认知或刻板印象。
6.  **【内部逻辑】深化主角自我认知**:
    -   **核心思考点**: “作为一个[{new_protagonist_gender}]，这件事对我意味着什么？”
    -   **执行要求**: 重写主角的内心独白。当遭遇重大事件时，其内心活动必须加入基于新性别身份的独特考量层次（如社会期望、人身安全、身份认同等）。
7.  **【社会背景融入】思考同性关系**:
    -   **核心思考点**: “在‘{story_context}’这个时代背景下，她们的同性伴侣关系会被如何看待？是完全接纳，还是会面临独特的审视或挑战？”
    -   **执行要求**: 在角色与外界（如家人、同事、路人）的互动中，适当地体现出这种社会背景。她们的对话、公开场合的亲密程度、对未来的规划，都应与此背景相符，使关系更真实可信。

---
# FINAL OUTPUT INSTRUCTION (CRITICAL)
你的输出 **必须且只能** 是最终修改好的小说正文。
- **绝对不要** 包含任何修改日志、执行过程、分析、注释、总结或任何形式的解释性文字。
- **绝对不要** 输出如“修改日志:”、“修改后文本”、“第一阶段”等任何标题或元信息。
- 你的回复必须 **直接以修改后正文的第一个字开始**。
- 输出内容应该是纯粹、干净、可以直接发表的最终稿。

需要处理的文档内容如下：
"""


# ==============================================================================
# 4. 主程序逻辑 (无需改动)
# ==============================================================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
print(f"配置完成，准备请求URL: {API_URL} | 模型: {MODEL_NAME}")

def process_single_file(filename):
    """处理单个文件的函数，包括读取、API请求和写入结果。"""
    input_filepath = os.path.join(INPUT_FOLDER, filename)
    output_filename = f"processed_{filename}"
    output_filepath = os.path.join(OUTPUT_FOLDER, output_filename)

    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            document_content = f.read()

        if not document_content.strip():
            return f"文件 {filename} 为空，已跳过。"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": document_content}
            ],
            "temperature": 0.1
        }

        response = requests.post(API_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()  # 如果请求失败 (例如 4xx 或 5xx)，则抛出异常

        data = response.json()
        result_text = data['choices'][0]['message']['content'].strip()

        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(result_text)

        return f"文件 {filename} 处理成功。"

    except requests.exceptions.RequestException as e:
        error_message = f"处理文件 {filename} 时发生网络错误: {e}"
        with open(os.path.join(OUTPUT_FOLDER, 'error_log.txt'), 'a', encoding='utf-8') as log_file:
            log_file.write(f"{filename}: {e}\n")
        return error_message
    except Exception as e:
        error_message = f"处理文件 {filename} 时发生未知错误: {e}"
        with open(os.path.join(OUTPUT_FOLDER, 'error_log.txt'), 'a', encoding='utf-8') as log_file:
            log_file.write(f"{filename}: {e}\n")
        return error_message


def process_all_files_parallel():
    """使用线程池并行处理所有文件。"""
    files_to_process = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.txt')]
    total_files = len(files_to_process)

    if total_files == 0:
        print(f"在文件夹 '{INPUT_FOLDER}' 中未找到.txt文件。")
        return

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
