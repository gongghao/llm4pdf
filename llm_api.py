import re
import requests
from typing import Tuple, List
from vector_search import extract_relevant_context_advanced, extract_keywords_from_question
from real_llm_api import call_llm_api, init_llm
import os
import fitz

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

def extract_relevant_context(text: str, question: str, window_size: int = 200) -> str:
    """
    根据问题提取相关原文片段（支持中英文自动切换）
    """
    # 检查问题是否为中文，若是则翻译为英文
    if re.search(r'[\u4e00-\u9fff]', question):
        question_en = translate_to_english(question)
    else:
        question_en = question
    # 1. 让LLM提取关键词
    keywords = extract_keywords_by_llm(question_en, lang="en")  # 或lang="zh"
    try:
        # 2. 用关键词做检索
        # 这里可以用TF-IDF、向量法或直接关键词高亮
        print(keywords)
        relevant_sentences = []
        for sentence in text.split('.'):
            if any(k.lower() in sentence.lower() for k in keywords):
                relevant_sentences.append(sentence)
        if relevant_sentences:
            return '. '.join(relevant_sentences[:5])
        return text[:1000] if len(text) > 1000 else text
    except Exception as e:
        # 如果向量检索失败，回退到简单方法
        print(f"向量检索失败，使用简单方法: {e}")
        print(keywords)
        return extract_relevant_context_simple(text, keywords[0])

def extract_relevant_context_simple(text: str, question: str) -> str:
    """
    简单的关键词匹配方法（备用）
    """
    keywords = extract_keywords_from_question(question)
    
    # 在文本中搜索关键词
    sentences = re.split(r'[.!?]+', text)
    relevant_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if any(keyword.lower() in sentence.lower() for keyword in keywords):
            relevant_sentences.append(sentence)
    
    if relevant_sentences:
        # 返回包含关键词的句子及其上下文
        context = ". ".join(relevant_sentences[:5])  # 最多5个句子
        return context
    
    # 如果没有找到相关句子，返回开头部分
    return text[:1000] if len(text) > 1000 else text

def extract_keywords(question: str) -> List[str]:
    """
    从问题中提取关键词
    """
    # 移除常见停用词
    stop_words = {'的', '是', '在', '有', '和', '与', '或', '什么', '哪些', '如何', '为什么', '第', '张', '图片', '图'}
    
    # 提取中文和英文关键词
    keywords = []
    
    # 处理"第X张图片"类问题
    if '第' in question and ('张' in question or '图片' in question):
        match = re.search(r'第(\d+)张', question)
        if match:
            keywords.append(f"图片{match.group(1)}")
            keywords.append("figure")
            keywords.append("image")
    
    # 处理数据集相关问题
    if '数据集' in question or 'dataset' in question.lower():
        keywords.extend(['数据集', 'dataset', 'data', '训练', '测试', '验证'])
    
    # 处理实验相关问题
    if '实验' in question or 'experiment' in question.lower():
        keywords.extend(['实验', 'experiment', '方法', 'method', '结果', 'result'])
    
    # 处理创新点相关问题
    if '创新' in question or 'contribution' in question.lower():
        keywords.extend(['创新', 'contribution', '贡献', 'novel', '新方法'])
    
    # 提取其他关键词
    words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', question)
    keywords.extend([word for word in words if word not in stop_words])
    
    return keywords

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
    {text[:3000]}...
    """
    
    # 调用真实的大模型API
    response = call_llm_api(prompt)
    return response

def ask_question(text: str, question: str) -> Tuple[str, str]:
    """
    回答问题并返回原文依据
    """
    # 1. 提取相关原文片段
    relevant_context = extract_relevant_context(text, question)
    
    # 2. 构建提示词
    prompt = f"""
    基于以下原文片段回答问题，要求：
    1. 准确回答问题，不要编造信息
    2. 如果原文中没有相关信息，请明确说明
    3. 用中文回答，语言简洁明了
    4. 可以引用原文中的关键信息
    
    原文片段：
    {relevant_context}
    
    问题：{question}
    """
    
    # 3. 调用大模型API
    answer = call_llm_api(prompt)
    
    # 4. 返回答案和原文依据
    return answer, relevant_context

def find_image_by_number(text: str, image_number: int) -> str:
    """
    根据图片编号找到对应的图片描述
    """
    # 在文本中搜索图片引用
    patterns = [
        rf'图\s*{image_number}[：:]\s*(.+)',
        rf'Figure\s*{image_number}[：:]\s*(.+)',
        rf'图片\s*{image_number}[：:]\s*(.+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return f"未找到第{image_number}张图片的描述"

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
