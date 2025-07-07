from pathlib import Path
from paddleocr import PPStructureV3

class PDFParser:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.output_path = Path("./output_markdown")
        self.pipeline = PPStructureV3(
            text_recognition_model_name="en_PP-OCRv4_mobile_rec",
        )

    def parse(self):
        output = self.pipeline.predict(self.input_file)
        self.save_markdown(output)

    def save_markdown(self, output):
        markdown_list = []
        markdown_images = []

        for res in output:
            md_info = res.markdown
            markdown_list.append(md_info)
            markdown_images.append(md_info.get("markdown_images", {}))

        markdown_texts = self.pipeline.concatenate_markdown_pages(markdown_list)

        mkd_file_path = self.output_path / f"{Path(self.input_file).stem}.md"
        mkd_file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(mkd_file_path, "w", encoding="utf-8") as f:
            f.write(markdown_texts)

        for item in markdown_images:
            if item:
                for path, image in item.items():
                    file_path = self.output_path / path
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    image.save(file_path)
        
        self.markdown_texts = markdown_texts
        self.markdown_images = markdown_images