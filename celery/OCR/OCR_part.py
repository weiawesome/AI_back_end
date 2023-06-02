import time
import torch

def get_Prediction(image,boxes):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    processor = torch.load('OCR/predict_model/processor.pt')
    model = torch.load('OCR/predict_model/model.pt').to(device)
    result=''
    start_time=time.time()
    for box in boxes:
        cropped_image = image.crop(box)
        pixel_values = processor(cropped_image, return_tensors="pt").pixel_values.to(device)
        generated_ids = model.generate(pixel_values, max_length=255)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        result+=(generated_text)+' '
    end_time=time.time()
    print('文字預測花費: ',end_time-start_time,'秒')
    return result