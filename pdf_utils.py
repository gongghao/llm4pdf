import fitz
import os
import re

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text += f"\n--- 第{page_num+1}页 ---\n"
        text += page.get_text()
    
    return text


def extract_large_images(pdf_path, min_width=200, min_height=100):
    doc = fitz.open(pdf_path)
    images = []
    pics_dir = "pics"
    os.makedirs(pics_dir, exist_ok=True)
    for page_num in range(len(doc)):
        page = doc[page_num]
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.width >= min_width and pix.height >= min_height:
                    img_path = os.path.join(pics_dir, f"page{page_num+1}_img{img_index+1}.png")
                    pix.save(img_path)
                    images.append({
                        'img_path': img_path,
                        'page': page_num+1,
                        'width': pix.width,
                        'height': pix.height
                    })
            except Exception as e:
                print(f"图片提取失败: {e}")
    return images

