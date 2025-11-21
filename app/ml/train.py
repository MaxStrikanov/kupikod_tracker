"""Простейший скрипт обучения ML-модели для детекции интеграций Kupikod.

Ожидает CSV-файл с колонками:

- has_kupikod (0/1)
- has_promo_triggers (0/1)
- has_promo_codes (0/1)
- label (0/1) — 1 = реклама Kupikod, 0 = нет

Пример запуска:

    python -m app.ml.train --csv data/kupikod_labeled.csv

После обучения модель сохранится в app/ml/kupikod_model.joblib
и будет автоматически подхватываться KupikodMLClassifier.
"""

import argparse
import os

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

from .model import MODEL_PATH


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Путь к CSV с разметкой")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)

    required_cols = ["has_kupikod", "has_promo_triggers", "has_promo_codes", "label"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"В CSV отсутствует колонка {col}")

    X = df[["has_kupikod", "has_promo_triggers", "has_promo_codes"]].astype(float)
    y = df["label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\nОтчёт по качеству модели:\n")
    print(classification_report(y_test, y_pred, digits=4))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nМодель сохранена в {MODEL_PATH}")


if __name__ == "__main__":
    main()
