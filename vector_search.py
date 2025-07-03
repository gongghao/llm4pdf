import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import List, Tuple

class VectorSearchEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.text_chunks = []
        self.vectors = None
    
    def split_text_into_chunks(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        将文本分割成重叠的块
        """
        chunks = []
        sentences = re.split(r'[.!?]+', text)
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def build_index(self, text: str):
        """
        构建文本索引
        """
        self.text_chunks = self.split_text_into_chunks(text)
        if self.text_chunks:
            self.vectors = self.vectorizer.fit_transform(self.text_chunks)
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        搜索最相关的文本块
        """
        if not self.vectors or not self.text_chunks:
            return []
        
        # 向量化查询
        query_vector = self.vectorizer.transform([query])
        
        # 计算相似度
        similarities = cosine_similarity(query_vector, self.vectors).flatten()
        
        # 获取top-k结果
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # 相似度阈值
                results.append((self.text_chunks[idx], similarities[idx]))
        
        return results
    
    def extract_context_with_keywords(self, text: str, keywords: List[str], window_size: int = 300) -> str:
        """
        基于关键词提取上下文
        """
        sentences = re.split(r'[.!?]+', text)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword.lower() in sentence.lower() for keyword in keywords):
                relevant_sentences.append(sentence)
        
        if not relevant_sentences:
            return text[:window_size] if len(text) > window_size else text
        
        # 找到最相关的句子位置
        best_sentence = relevant_sentences[0]
        text_parts = text.split('.')
        
        for i, part in enumerate(text_parts):
            if best_sentence in part:
                # 提取前后文
                start = max(0, i - window_size // 2)
                end = min(len(text_parts), i + window_size // 2)
                context = '. '.join(text_parts[start:end])
                return context
        
        return text[:window_size] if len(text) > window_size else text

def extract_relevant_context_advanced(text: str, question: str) -> str:
    """
    高级原文依据提取
    """
    # 创建搜索引擎
    search_engine = VectorSearchEngine()
    search_engine.build_index(text)
    
    # 搜索相关文本块
    results = search_engine.search(question, top_k=2)
    
    if results:
        # 合并最相关的文本块
        relevant_text = " ".join([chunk for chunk, score in results])
        
        # 进一步基于关键词提取
        keywords = extract_keywords_from_question(question)
        final_context = search_engine.extract_context_with_keywords(relevant_text, keywords)
        
        return final_context
    
    # 如果向量搜索失败，回退到关键词搜索
    return extract_relevant_context_simple(text, question)

def extract_keywords_from_question(question: str) -> List[str]:
    """
    从问题中提取关键词
    """
    # 问题类型识别
    question_types = {
        'dataset': ['数据集', 'dataset', 'data', '训练', '测试', '验证', 'benchmark'],
        'experiment': ['实验', 'experiment', '方法', 'method', '算法', 'algorithm'],
        'result': ['结果', 'result', '性能', 'performance', '准确率', 'accuracy'],
        'contribution': ['创新', 'contribution', '贡献', 'novel', '新方法', '改进'],
        'image': ['图片', '图', 'figure', 'image', '图表', 'chart']
    }
    
    keywords = []
    question_lower = question.lower()
    
    for category, words in question_types.items():
        if any(word in question_lower for word in words):
            keywords.extend(words)
    
    # 提取特定模式
    if '第' in question and ('张' in question or '图片' in question):
        match = re.search(r'第(\d+)张', question)
        if match:
            keywords.extend([f"图片{match.group(1)}", "figure", "image"])
    
    # 提取其他关键词
    words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', question)
    stop_words = {'的', '是', '在', '有', '和', '与', '或', '什么', '哪些', '如何', '为什么'}
    keywords.extend([word for word in words if word not in stop_words])
    
    return list(set(keywords))  # 去重

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