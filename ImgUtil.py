from PIL import Image
import numpy as np
import os
def is_meaningless_img(pil_img, threshold=250):
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

def save_imgs(figures, save_dir = "./pics"):
    os.makedirs(save_dir, exist_ok=True)
    img_count = 0
    for page_idx, page_dict in enumerate(figures):
        if isinstance(page_dict, dict) and page_dict:
            for img_idx, (path, image) in enumerate(page_dict.items()):
                if not is_meaningless_img(image) and not "table" in path:
                    save_path = os.path.join(save_dir, f"page_{img_count+1}.png")
                    image.save(save_path)
                    img_count += 1
    print(f"已保存{img_count}张图片")