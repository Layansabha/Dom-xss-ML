import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV, train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix, roc_curve
)
import matplotlib.pyplot as plt

# إعدادات
threads = 16
random_state = 42
k_folds = 5
vocab_path = "vocab_top500_filtered.pkl"
data_path = r"C:\Users\ROG\Downloads\vectorized_dataset.csv"

# تحميل البيانات
print("📥 Loading dataset...")
df = pd.read_csv(data_path)
X = df.drop(columns=["lbl", "wght", "dbg"])
y = df["lbl"].map({"n": 0, "p": 1}).values

# تقسيم البيانات 80 / 10 / 10
X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.10, stratify=y, random_state=random_state)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.1111, stratify=y_temp, random_state=random_state)

print(f"✅ Split: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")

# إعداد Grid Search
param_grid = {
    "learning_rate": [0.1, 0.05],
    "max_depth": [7, 15],
    "min_child_weight": [1, 5],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0],
    "gamma": [0, 1]
}

base_model = XGBClassifier(
    objective="binary:logistic",
    use_label_encoder=False,
    eval_metric="logloss",
    scale_pos_weight=1,
    n_jobs=threads,
    random_state=random_state
)

cv = StratifiedKFold(n_splits=k_folds, shuffle=True, random_state=random_state)

grid = GridSearchCV(
    estimator=base_model,
    param_grid=param_grid,
    scoring="f1",
    cv=cv,
    verbose=1,
    n_jobs=threads
)

print("🔍 Starting Grid Search on 80% training data...")
grid.fit(X_train, y_train)

print("\n✅ Best Params:", grid.best_params_)
print("🏆 Best F1 from cross-val:", grid.best_score_)

# تدريب نهائي على train
final_model = XGBClassifier(
    **grid.best_params_,
    objective="binary:logistic",
    use_label_encoder=False,
    eval_metric="logloss",
    scale_pos_weight=1,
    n_jobs=threads,
    random_state=random_state
)
final_model.fit(X_train, y_train)

# تقييم على Validation
y_val_pred = final_model.predict(X_val)
y_val_proba = final_model.predict_proba(X_val)[:, 1]

print("\n📊 Validation Report:\n", classification_report(y_val, y_val_pred, digits=4))
print("F1:", f1_score(y_val, y_val_pred))
print("ROC AUC:", roc_auc_score(y_val, y_val_proba))
print("Confusion Matrix:\n", confusion_matrix(y_val, y_val_pred))

# تقييم على Test
y_test_pred = final_model.predict(X_test)
y_test_proba = final_model.predict_proba(X_test)[:, 1]

print("\n🧪 Test Report:\n", classification_report(y_test, y_test_pred, digits=4))
print("F1:", f1_score(y_test, y_test_pred))
print("ROC AUC:", roc_auc_score(y_test, y_test_proba))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_test_pred))

# حفظ التقارير
with open("validation_report_xgboost.txt", "w") as f:
    f.write(classification_report(y_val, y_val_pred, digits=4))
with open("test_report_xgboost.txt", "w") as f:
    f.write(classification_report(y_test, y_test_pred, digits=4))

# حفظ الموديل
joblib.dump(final_model, "xgboost_best_model_final.pkl")

# حفظ أهم الميزات
vocab = joblib.load(vocab_path)
importances = final_model.feature_importances_
top_tokens = sorted([(token, importances[idx]) for token, idx in vocab.items()],
                    key=lambda x: x[1], reverse=True)[:50]

with open("top_features_xgboost.txt", "w", encoding="utf-8") as f:
    for token, score in top_tokens:
        f.write(f"{token}: {score}\n")

# رسم ROC Curve على test
fpr, tpr, _ = roc_curve(y_test, y_test_proba)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label="ROC AUC = %.4f" % roc_auc_score(y_test, y_test_proba))
plt.plot([0, 1], [0, 1], "k--")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve - Test Set (XGBoost)")
plt.legend()
plt.grid(True)
plt.savefig("roc_curve_test_xgboost.png")
print("📈 ROC curve saved as roc_curve_test_xgboost.png")

print("\n✅ All done with XGBoost!")
