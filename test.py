from pathlib import Path
from paddleocr import PPStructureV3

input_file = "./反事实-Yang 等 - 2023 - Counterfactual Learning on Heterogeneous Graphs wi.pdf"
output_path = Path("./output")

pipeline = PPStructureV3(device="gpu:0", 
    text_recognition_model_name="en_PP-OCRv4_mobile_rec", 
    text_detection_model_name="PP-OCRv5_mobile_det",
    layout_detection_model_name="PP-DocLayout-S", 
    textline_orientation_model_name=None, 
    table_classification_model_name=None, 
    wired_table_structure_recognition_model_name=None, 
    wireless_table_structure_recognition_model_name=None, 
    wired_table_cells_detection_model_name=None, 
    wireless_table_cells_detection_model_name=None,
    table_orientation_classify_model_name=None,
    seal_text_detection_model_name="PP-OCRv4_mobile_seal_det",
    seal_text_recognition_model_name=None,
    formula_recognition_model_name="PP-FormulaNet_plus-S",
    enable_mkldnn=True,
    enable_hpi=False)

output = pipeline.predict("./反事实-Yang 等 - 2023 - Counterfactual Learning on Heterogeneous Graphs wi.pdf")
markdown_list = []
markdown_images = []

for res in output:
    md_info = res.markdown
    markdown_list.append(md_info)
    markdown_images.append(md_info.get("markdown_images", {}))

markdown_texts = pipeline.concatenate_markdown_pages(markdown_list)

mkd_file_path = output_path / f"{Path(input_file).stem}.md"
mkd_file_path.parent.mkdir(parents=True, exist_ok=True)

with open(mkd_file_path, "w", encoding="utf-8") as f:
 f.write(markdown_texts)

for item in markdown_images:
    if item:
        for path, image in item.items():
            file_path = output_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(file_path)

