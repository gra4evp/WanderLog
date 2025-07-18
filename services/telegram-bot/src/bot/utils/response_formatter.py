from typing import Any
from config import CLASS_INFO


def format_classification_result(result: dict[str, Any]) -> str:
    """
    Форматирование результата классификации для отправки пользователю
    
    Args:
        result: Результат от API
        
    Returns:
        Отформатированная строка
    """
    if not result:
        return "❌ Ошибка: неверный формат ответа от сервера"

    return format_single_result(result)
    


def format_single_result(result: dict[str, Any]) -> str:
    """Форматирование результата для одного изображения"""
    predicted_class = result.get('predicted_class', 'Unknown')
    class_confidences = result.get('class_confidences', [])
    top_confidence = result.get('top_confidence', 'Unknown')
    image_name = result.get('image_name', 'Изображение')
    
    # Определяем эмодзи и описание для класса
    class_info = CLASS_INFO.get(predicted_class, {'emoji': '🏠', 'description': 'Unknown'})
    class_emoji = class_info['emoji']
    class_description = class_info['description']
    
    # Форматируем вероятности
    prob_text = format_probabilities(
        class_confidences,
        sorted_by_probability=False
    )
    if top_confidence != 'Unknown':
        top_confidence = f"{top_confidence * 100:.1f}%"
    text_lines = [
        f"🏠 <b>Результат классификации</b>\n",
        f"📸 <b>Файл:</b> {image_name}",
        f"{class_emoji} <b>Класс интерьера:</b> <code>{predicted_class}</code> — {top_confidence}",
        f"ℹ️ <b>Описание:</b> [{class_description}]\n",
        f"📊 <b>Распределение вероятностей:</b>",
        prob_text
    ]
    
    return "\n".join(text_lines)


def format_probabilities(
        probabilities: dict[str, float],
        sorted_by_probability: bool = False
    ) -> str:
    """Форматирование списка вероятностей"""
    class_names = list(CLASS_INFO.keys())
    
    if len(probabilities) != len(class_names):
        return "❌ Ошибка: неверное количество классов"
    
    # Создаем список кортежей (класс, вероятность) и сортируем по убыванию
    class_probs = list(probabilities.items())
    if sorted_by_probability:
        class_probs.sort(key=lambda x: x[1], reverse=True)
    
    formatted_lines = []
    for class_name, prob in class_probs:
        info = CLASS_INFO.get(class_name, {'emoji': '🏠'})
        emoji = info['emoji']
        percentage = prob * 100
        bar_length = round(percentage / 5)  # 5% = 1 символ
        bar = '█' * bar_length + '░' * (20 - bar_length)
        # Добавляем пробел перед процентом, если меньше 10 для выравнивания
        percent_str = f" {percentage:.1f}%" if percentage < 10 else f"{percentage:.1f}%"
        formatted_lines.append(
            f"{emoji} {class_name}: {percent_str} {bar}"
        )
    
    return "\n".join(formatted_lines)
