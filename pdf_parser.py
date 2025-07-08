import base64
import requests
from openai import OpenAI
import fitz
import os
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
import re
import shutil
import time
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_text_from_image(image_path, file_path, description:bool, prompt="", api_key=None):
    """使用Qwen-VL-Max提取图片中的文本"""
    while True:
        try:
            # 如果没有提供api_key，尝试从环境变量获取
            if api_key is None:
                import os
                api_key = os.environ.get('VLM_API_KEY')
                if not api_key:
                    return "错误：未提供API密钥"
            
            # 读取图片文件并转换为base64
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            client = OpenAI(api_key = api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
            completion = client.chat.completions.create(
                model="qwen-vl-plus",  # 此处以qwen-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages=[
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": prompt}],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_string}"
                            },
                            },
                            {"type": "text", "text": "请描述这张图片的内容"},
                        ],
                    },
                ],
                stream = True,
            )

            with open(file_path, 'a', encoding='utf-8') as f:
                if description:
                    splits = image_path.split('/')[-1].split('_')
                    page_num = splits[1]
                    image_index = splits[3]
                    
                    f.write(f"<PAGE_{page_num}_IMAGE_{image_index}>")
                for chunk in completion:
                    if chunk.choices:
                        content = chunk.choices[0].delta.content
                        if content is not None:
                            f.write(content)
                if description:
                    f.write(f"</PAGE_{page_num}_IMAGE_{image_index}>\n")
            return True
        except Exception as e:
            print("提取图片文本时出错: ",image_path, e)
            

def extract_images_from_pdf_page(page, page_num: int, img_idx_all: int) -> List[Dict[str, Any]]:
    """从PDF页面提取图像"""
    images = []
    image_list = page.get_images()
    
    for img_index, img in enumerate(image_list):
        xref = img[0]
        pix = fitz.Pixmap(page.parent, xref)
        
        # 过滤掉太小的图像
        if pix.width < 100 or pix.height < 100:
            continue
            
        # 保存图像
        img_path = f"temp_images/page_{page_num}_img_{img_index + 1}_{img_idx_all}.png"   
        os.makedirs("temp_images", exist_ok=True)
        pix.save(img_path)
        
        images.append({
            'path': img_path,
            'width': pix.width,
            'height': pix.height,
            'index': img_index
        })
        
        pix = None
        img_idx_all += 1
        
    return images

def describe_image_with_qwen(image_path: str, image_index: int):
    """使用Qwen-VL描述图片内容"""
    try:
        # 调用Qwen-VL API描述图片
        extract_text_from_image(image_path, f'pages/img_descriptions.md',description=True, prompt="请用简洁的语言描述这张图片的内容，不要输出任何其他信息。")

    except Exception as e:
        print(f"图片描述失败: {e}")
        return f"<IMAGE_{image_index}>[图片内容描述失败]</IMAGE_{image_index}>"

def extract_text_and_images_from_pdf(pdf_path: str) -> Tuple[str, str]:
    """从PDF提取文本和图片描述"""
    doc = fitz.open(pdf_path)
    all_content = []
    text_only = []
    
    # 清理临时图片
    if os.path.exists("temp_images"):
        shutil.rmtree("temp_images")
    if os.path.exists("pages"):
        shutil.rmtree("pages")
    os.makedirs("pages", exist_ok=True)
    with open('pages/img_descriptions.md', 'w', encoding='utf-8') as f:
        f.truncate(0)

    img_idx = 1
    try:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # 提取文本
            pix = page.get_pixmap(dpi=100)
            page_image = 'pages/page_'+str(page_num+1)+'.png'
            pix.save(page_image)
            extract_text_from_image(page_image, f'pages/content.md', description=False, prompt="请提取图片中的所有文本内容，包括标题、正文、图表标题、公式等。请以markdown格式返回，保持原文的层次结构和格式。只输出你提取出的所有信息，不要提供其他信息。输出的markdown不需要用```markdown包裹。")
            # 提取并描述图片
            images = extract_images_from_pdf_page(page, page_num + 1, img_idx)
            for img in images:
                describe_image_with_qwen(img['path'], img['index'])
    except Exception as e:
            print("提取图片文本时出错: ",  e)
        
    
    doc.close()
    return "\n\n".join(all_content), "\n\n".join(text_only)

def extract_specific_image_description(text: str, image_number: int, page_number: int) -> str:
    """提取指定图片的描述"""
    pattern = fr"<PAGE_{page_number}_IMAGE_{image_number}>(.*?)</PAGE_{page_number}_IMAGE_{image_number}>"
    match = re.search(pattern, text, re.DOTALL)
    print(pattern)
    if match:
        return match.group(1).strip()
    else:
        return f"未找到图片的描述"

def get_all_image_descriptions(text: str) -> List[Dict[str, str]]:
    """获取所有图片描述"""
    pattern = r"<IMAGE_(\d+)>(.*?)</IMAGE_\d+>"
    matches = re.findall(pattern, text, re.DOTALL)
    
    images = []
    for img_num, description in matches:
        images.append({
            'number': int(img_num),
            'description': description.strip()
        })
    
    return images