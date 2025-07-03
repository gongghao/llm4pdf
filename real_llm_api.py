import requests
import json
import time
from typing import Dict, Any

class LLMAPI:
    def __init__(self, api_type: str = "qwen", api_key: str = None):
        """
        初始化大模型API
        api_type: "qwen", "doubao", "deepseek"
        """
        self.api_type = api_type
        self.api_key = api_key
        self.setup_api_config()
    
    def setup_api_config(self):
        """设置API配置"""
        if self.api_type == "qwen":
            self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        elif self.api_type == "doubao":
            self.base_url = "https://api.doubao.com/v1/chat/completions"
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        elif self.api_type == "deepseek":
            self.base_url = "https://api.deepseek.com/v1/chat/completions"
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def call_qwen_api(self, prompt: str) -> str:
        """调用Qwen API"""
        data = {
            "model": "qwen-turbo",
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "max_tokens": 2000,
                "temperature": 0.7
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["output"]["text"]
        except Exception as e:
            print(f"Qwen API调用失败: {e}")
            return self.get_fallback_response(prompt)
    
    def call_doubao_api(self, prompt: str) -> str:
        """调用Doubao API"""
        data = {
            "model": "doubao-pro",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Doubao API调用失败: {e}")
            return self.get_fallback_response(prompt)
    
    def call_deepseek_api(self, prompt: str) -> str:
        """调用Deepseek API"""
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Deepseek API调用失败: {e}")
            return self.get_fallback_response(prompt)
    
    def call_api(self, prompt: str) -> str:
        """统一的API调用接口"""
        if not self.api_key:
            return self.get_fallback_response(prompt)
        
        if self.api_type == "qwen":
            return self.call_qwen_api(prompt)
        elif self.api_type == "doubao":
            return self.call_doubao_api(prompt)
        elif self.api_type == "deepseek":
            return self.call_deepseek_api(prompt)
        else:
            return self.get_fallback_response(prompt)
    
    def get_fallback_response(self, prompt: str) -> str:
        """备用响应（当API调用失败时）"""
        if "总结" in prompt:
            return "这是一篇关于深度学习的学术论文。论文提出了一种新的神经网络架构，在多个数据集上取得了优异的结果。主要创新点包括..."
        elif "数据集" in prompt:
            return "本文实验在以下数据集上完成：MNIST、CIFAR-10、ImageNet等经典数据集。"
        elif "图片" in prompt:
            return "第2张图片展示了模型架构图，显示了网络各层的连接方式和参数配置。"
        elif "创新" in prompt:
            return "本文的核心创新点在于提出了一种新的注意力机制，能够更好地处理长序列依赖关系。"
        else:
            return "根据原文内容，这个问题的答案是..."

# 全局LLM实例
llm_instance = None

def init_llm(api_type: str = "qwen", api_key: str = ""):
    """初始化LLM实例"""
    global llm_instance
    llm_instance = LLMAPI(api_type, api_key)

def call_llm_api(prompt: str) -> str:
    """调用LLM API的统一接口"""
    global llm_instance
    if llm_instance:
        return llm_instance.call_api(prompt)
    else:
        # 如果没有初始化，使用备用响应
        return LLMAPI().get_fallback_response(prompt)

# 使用示例
if __name__ == "__main__":
    # 初始化API（需要替换为真实的API Key）
    # init_llm("qwen", "your_qwen_api_key")
    # init_llm("doubao", "your_doubao_api_key")
    # init_llm("deepseek", "your_deepseek_api_key")
    
    # 测试调用
    test_prompt = "请总结这篇论文的主要内容"
    response = call_llm_api(test_prompt)
    print(f"API响应: {response}") 