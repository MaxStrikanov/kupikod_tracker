from dataclasses import dataclass
from typing import Dict, Any, Optional

import joblib
import os


MODEL_PATH = os.getenv("KUPIKOD_ML_MODEL_PATH", os.path.join(os.path.dirname(__file__), "kupikod_model.joblib"))


@dataclass
class KupikodMLClassifier:
    """
    Обёртка над ML-моделью (например, LogisticRegression из scikit-learn),
    которая предсказывает вероятность того, что пост — рекламная интеграция Kupikod.

    Ожидается, что обученная модель лежит по пути MODEL_PATH
    и принимает на вход вектор из фич.
    """

    model: Optional[object] = None

    def __post_init__(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception as e:
                print("Не удалось загрузить ML-модель Kupikod:", e)
                self.model = None
        else:
            # Модель не обязательна: если файла нет, работаем только на правилах
            self.model = None

    def _build_features(self, features: Dict[str, Any]):
        """
        Простейший вектор признаков для примера.
        Здесь можно развернуть полноценную обработку текста:
        - длина текста
        - количество вхождений 'kupikod'
        - TF-IDF признаки и т.д.

        Сейчас — только бинарные флаги.
        """
        return [
            1.0 if features.get("has_kupikod") else 0.0,
            1.0 if features.get("has_promo_triggers") else 0.0,
            1.0 if features.get("has_promo_codes") else 0.0,
        ]

    def predict_proba(self, features: Dict[str, Any]) -> float:
        # Если модели нет — возвратим эвристику, чтобы не ломать пайплайн
        if self.model is None:
            base = 0.5
            if features.get("has_promo_triggers"):
                base += 0.2
            if features.get("has_promo_codes"):
                base += 0.2
            return max(0.0, min(1.0, base))

        vec = [self._build_features(features)]
        try:
            proba = self.model.predict_proba(vec)[0][1]
        except Exception as e:
            print("Ошибка при работе ML-модели Kupikod:", e)
            proba = 0.5
        return float(proba)
