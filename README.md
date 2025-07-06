# NovelRemix
基于LLM的主人公性别转换项目（百合改文） \n
1.在选定目标小说后得到它的txt文件
2.打开format文件里的segment将其分块
3.找到你的api调用方式，一般来说调用gemini2.5pro比较好。
4.如果你是gemini官方api，使用gemini_api的文件，修改相关信息（api，小说主人公，输入输出文件之类的）
5.第三方api分文openai调用或者直接request调用，具体问第三方api提供者；选择相应的openai_api与third_api_call(request)修改相关信息
6.改完后，把format里的formatting放在对应文件夹下，这个程序是修改调用llm改文的格式，例如llm会在开头加字。注意程序与文件夹位置
7.然后用其文件夹下的merge将这些txt拼在一起就可以享受小说了
