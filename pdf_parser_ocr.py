import os
import time
from paddleocr import PPStructureV3
from pathlib import Path
import numpy as np

class PDFParser:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.output_path = Path("./pages")
        self.pipeline = PPStructureV3(
            text_recognition_model_name="en_PP-OCRv4_mobile_rec",
        )

    def parse(self):
        output = self.pipeline.predict(self.input_file)
        self.save_markdown(output)

    def is_meaningless_img(self, pil_img, threshold=250):
        """
        判断图片是否为全白（或几乎全白）。
        threshold: 允许的最小灰度值，越低越严格。
        """
        arr = np.array(pil_img)
        # 支持RGB和RGBA
        if arr.ndim == 3 and arr.shape[2] >= 3:
            arr = arr[:, :, :3]
        # 判断所有像素是否都大于等于阈值
        return np.all(arr >= threshold)

    
    def save_images(self):
        os.makedirs("./imgs", exist_ok=True)
        img_count = 0
        for page_idx, page_dic in enumerate(self.markdown_images):
            if isinstance(page_dic, dict) and page_dic:
                for img_idx, (path, image) in enumerate(page_dic.items()):
                    if not self.is_meaningless_img(image) and not "table" in path:
                        save_path = os.path.join("./imgs", f"page_{page_idx + 1}_img_{img_idx + 1}_{img_count + 1}.png")
                        image.save(save_path)
                        img_count += 1

    def clear_imgs(self, save_dir = "./imgs"):
        if os.path.exists(save_dir):
            for file in os.listdir(save_dir):
                os.remove(os.path.join(save_dir, file))
            os.rmdir(save_dir)
    
    def save_markdown(self, output):
        markdown_list = []
        markdown_images = []

        for res in output:
            md_info = res.markdown
            markdown_list.append(md_info)
            markdown_images.append(md_info.get("markdown_images", {}))

        markdown_texts = self.pipeline.concatenate_markdown_pages(markdown_list)

        mkd_file_path = self.output_path / f"content.md"
        mkd_file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(mkd_file_path, "w", encoding="utf-8") as f:
            f.write(markdown_texts)

        # for item in markdown_images:
        #     if item:
        #         for path, image in item.items():
        #             file_path = self.output_path / path
        #             file_path.parent.mkdir(parents=True, exist_ok=True)
        #             image.save(file_path)
        
        self.clear_imgs()
        self.markdown_texts = markdown_texts
        self.markdown_images = markdown_images
        self.save_images()



if __name__ == "__main__":
    parser = PDFParser("attention is all you need.pdf")
    parser.parse()
