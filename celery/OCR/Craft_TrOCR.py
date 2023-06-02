import numpy as np
from OCR.Detect_part import get_Boxes
from OCR.OCR_part import get_Prediction
from PIL import Image
from OCR.utils import rotate_image_based_on_exif


def image_to_texts(file):
    image = Image.open(file)
    image = rotate_image_based_on_exif(image)
    image = image.convert('RGB')
    np_image = np.array(image)
    boxes = get_Boxes(np_image)
    result = get_Prediction(image, boxes)
    return result