import logging
from fastapi import UploadFile, File, HTTPException, Depends
from fastapi import APIRouter
from datetime import datetime
from PIL import Image
import io
import torch
from pydantic_models import ClassificationResult, ClassificationResponse, MetaInfo
from models.interior_classifier_EfficientNet_B3 import (
    InteriorClassifier,
    get_inference_transforms,
    get_model
)


logger = logging.getLogger(f"uvicorn.{__file__}")
router = APIRouter()


# Инициализация глобальных переменных
try:
    MODEL = get_model()  # инициализируем при старте первый раз
    CLASS_NAMES = ["A0", "A1", "B0", "B1", "C0", "C1", "D0", "D1"]
    MODEL_VERSION = "1.0.0"  # Можно получить из checkpoint или задать явно
    BACKBONE_NAME = "EfficientNet-B3"
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    raise RuntimeError("Failed to initialize model")


def classify_images_batch(
        images: list[Image.Image],
        image_names: list[str],
        model: InteriorClassifier
    ) -> list[ClassificationResult]:
    transforms = get_inference_transforms(img_size=448)
    tensors = [transforms(img).unsqueeze(0) for img in images]
    batch_tensor = torch.cat(tensors, dim=0)
    with torch.no_grad():
        outputs = model(batch_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        results = []
        for i in range(len(images)):
            probs = probabilities[i]
            confidences = {CLASS_NAMES[j]: round(float(probs[j]), 4) for j in range(len(CLASS_NAMES))}
            top_confidence, predicted = torch.max(probs, 0)
            results.append(
                ClassificationResult(
                    predicted_class=CLASS_NAMES[predicted.item()],
                    top_confidence=round(float(top_confidence.item()), 4),
                    class_confidences=confidences,
                    image_name=image_names[i],
                    error=None
                )
            )
    return results


@router.post("/classify_batch", response_model=ClassificationResponse)
async def classify_batch(
    images: list[UploadFile] = File(...),
    model: InteriorClassifier = Depends(get_model)
):
    start_time = datetime.now()
    image_objs = []
    image_names = []
    error_results = []
    for image_file in images:
        try:
            image_data = await image_file.read()
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            image_objs.append(image)
            image_names.append(image_file.filename)
        except Exception as e:
            err_msg = str(e)
            if "cannot identify image file" in err_msg:
                user_msg = (
                    "File is not a supported image format. "
                    "Supported formats: jpg, jpeg, png, bmp, gif, tiff, webp, ico."
                )
            else:
                user_msg = err_msg
            error_results.append(
                ClassificationResult(
                    predicted_class=None,
                    top_confidence=None,
                    class_confidences={},
                    image_name=image_file.filename,
                    error=user_msg
                )
            )
            logger.error(f"Error processing image {image_file.filename}: {err_msg}")
    
    batch_results = []
    if image_objs:
        try:
            batch_results = classify_images_batch(image_objs, image_names, model)
        except Exception as e:
            logger.error(f"Error during batch model inference: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Model inference error: {str(e)}")
    
    results = batch_results + error_results
    total_processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
    response = ClassificationResponse(
        results=results,
        meta=MetaInfo(
            total_images=len(images),
            total_processing_time_ms=total_processing_time_ms,
            model_version=MODEL_VERSION,
            backbone_name=BACKBONE_NAME
        )
    )
    logger.info(f"Request processed in {total_processing_time_ms} ms")
    logger.info(f"Processed {len(images)} images")
    return response
