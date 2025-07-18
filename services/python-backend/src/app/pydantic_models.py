from pydantic import BaseModel


class MetaInfo(BaseModel):
    total_images: int
    total_processing_time_ms: int
    model_version: str | None = None
    backbone_name: str | None = None
    # можно добавить дополнительные поля в будущем, например:
    # model_version: str | None = None
    # server_time: str | None = None


class ClassificationResult(BaseModel):
    predicted_class: str | None
    top_confidence: float | None
    class_confidences: dict[str, float]
    image_name: str
    error: str | None = None


class ClassificationResponse(BaseModel):
    results: list[ClassificationResult]
    meta: MetaInfo | None = None

# example_response = {
#   "results": [
#     {
#       "predicted_class": "A0",
#       "top_confidence": 0.92,
#       "class_confidences": {
#         "A0": 0.92,
#         "A1": 0.03,
#         "B0": 0.01,
#         "...": 0.04
#       },
#       "image_name": "kitchen.jpg",
#       "error": None
#     },
#     {
#       "predicted_class": None,
#       "top_confidence": None,
#       "class_confidences": {},
#       "image_name": "broken.png",
#       "error": "Corrupted image file"
#     }
#   ],
#   "meta": {
#     "total_images": 2,
#     "total_processing_time_ms": 250,
#     "model_version": "1.0.0",
#     "backbone_name": "EfficientNet-B3"
#   }
# }