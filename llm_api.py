import array
import re
import os
from typing import Tuple, List
from chromadb.utils import embedding_functions
from real_llm_api import call_llm_api, init_llm
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from pdf_parser import extract_specific_image_description

def translate_to_english(question_zh: str) -> str:
    """
    调用大模型API将中文问题翻译为英文
    """
    prompt = f"请将下面的问题翻译成英文：\n{question_zh}"
    translation = call_llm_api(prompt)
    # 只取第一行英文结果，去除多余内容
    if translation:
        return translation.strip().split('\n')[0]
    return question_zh

def extract_relevant_context(question: str):
    """
    根据问题提取相关原文片段（支持中英文自动切换）
    """
    # 检查问题是否为中文，若是则翻译为英文
    # if re.search(r'[\u4e00-\u9fff]', question):
    #     question_en = translate_to_english(question)
    # else:
    #     question_en = question
    # 1. 让LLM提取关键词
    # keywords = extract_keywords_by_llm(question, lang="en")  # 或lang="zh"
    embedding = HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-multilingual")
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding)
    docs = vectorstore.similarity_search(question, k=5)
    
    return docs
    


def get_summary(text: str) -> str:
    """
    生成文献总结
    """
    prompt = f"""
    请对以下学术文献进行总结，要求：
    1. 总结核心研究内容和方法
    2. 突出主要创新点
    3. 说明实验结果和贡献
    4. 用中文回答，语言简洁明了
    
    文献内容：
    {text}...
    """
    
    # 调用真实的大模型API
    response = call_llm_api(prompt)
    return response

def ask_question(text: str, question: str) -> Tuple[str, str, bool]:
    """
    回答问题并返回原文依据
    """
    print(question)

    # 先判断是否询问图片内容
    prompt = f"""
    请判断以下问题是否有关图片，如果是，若询问第n张图片，返回'0, n'，若询问第m页第n张照片，返回'm, n'，若不是则返回'0, 0'，不要输出其他内容。：
    {question}
    """
    answer = call_llm_api(prompt)
    print(answer)
    img_num_all = 0
    # 解析返回的字符串格式
    try:
        parts = answer.split(',')
        page_num = int(parts[0].strip())
        img_num = int(parts[1].strip())
        if len(parts) == 2:    
            if page_num == 0 and img_num > 0:
                # 询问第n张图片
                for file in os.listdir('temp_images'):
                    if file.endswith('.png'):
                        img_num_all += 1
                        if img_num_all == img_num:
                            img_path = os.path.join('temp_images', file)
                            part_name = file.split('_')
                            description = extract_specific_image_description(text, int(part_name[3]), int(part_name[1]))
                            return description, img_path, True


            elif page_num > 0 and img_num > 0:
                # 询问第m页第n张图片
                for file in os.listdir('temp_images'):
                    if file.endswith('.png'):
                        part_name = file.split('_')

                        if part_name[1] == str(page_num) and part_name[3] == str(img_num):
                            img_path = os.path.join('temp_images', file)
                            part_name = file.split('_')
                            description = extract_specific_image_description(text, int(part_name[3]), int(part_name[1]))
                            return description, img_path, True
    except (ValueError, IndexError):
        pass
    
    # 如果不是询问图片，则按正常流程处理
    # 1. 提取相关原文片段
    docs = extract_relevant_context(question)
    relevant_context = [doc.page_content for doc in docs]
    evidence = ""
    for i, context in enumerate(relevant_context):        
        evidence += f"原文片段{i+1}：\n"
        if docs[i].metadata.get('h4'):
            evidence += f"**{docs[i].metadata['h4']}** \n\n"
        elif docs[i].metadata.get('h3'):
            evidence += f"**{docs[i].metadata['h3']}** \n\n"
        elif docs[i].metadata.get('h2'):
            evidence += f"**{docs[i].metadata['h2']}** \n\n"
            
        evidence += f"{context}"
        evidence += "\n\n"
           
    # return relevant_context, relevant_context, False
    # 2. 构建提示词
    prompt = f"""
    # 基于以下原文片段回答问题，要求：
    # 1. 准确回答问题，不要编造信息
    # 2. 如果原文中没有相关信息，请明确说明
    # 3. 用中文回答，语言简洁明了
    # 4. 可以引用原文中的关键信息
    
    # 原文片段：
    # {evidence}
    
    # 问题：{question}
    # """
    
    # # 3. 调用大模型API
    answer = call_llm_api(prompt)
    
    # # 4. 返回答案和原文依据
    return answer, evidence, False

# 初始化大模型API（可选）
def setup_llm_api(api_type: str = "deepseek", api_key: str = ""):
    """
    设置大模型API
    api_type: "qwen", "doubao", "deepseek"
    api_key: 你的API密钥
    """
    if api_key:
        init_llm(api_type, api_key)
        print(f"已初始化 {api_type} API")
    else:
        print("未提供API密钥，将使用备用响应")

# 初始化视觉语言模型API
def setup_vlm_api(api_key: str = ""):
    """
    设置视觉语言模型API
    api_key: 你的API密钥
    """
    if api_key:
        # 这里可以设置全局的VLM API密钥
        import os
        os.environ['VLM_API_KEY'] = api_key
        print("已初始化 VLM API")
    else:
        print("未提供VLM API密钥")
    
    return api_key

def extract_keywords_by_llm(question: str, lang: str = "en") -> list:
    """
    调用大模型API提取检索关键词
    """
    if lang == "en":
        prompt = f"Please extract 3-5 most important keywords for retrieval from the following question. Only output the keywords, separated by commas:\n{question}"
    else:
        prompt = f"请从下面的问题中提取1-2个最重要的检索关键词，按重要度从强到弱排序，只输出关键词，用逗号分隔：\n{question}"
    keywords_str = call_llm_api(prompt)
    # 只保留英文和数字，逗号分割
    keywords = [k.strip() for k in keywords_str.replace('，', ',').split(',') if k.strip()]
    return keywords
