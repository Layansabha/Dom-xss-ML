import pandas as pd
import joblib
import ast
import numpy as np
from tqdm import tqdm

# إعدادات المسارات
dataset_path = r"C:\Users\ROG\Downloads\merged_shuffled_dataset.xlsx"
vocab_path = r"vocab_top500_filtered.pkl"
output_csv = r"vectorized_dataset.csv"
output_excel_preview = r"vectorized_preview.xlsx"

# تحميل الفوكاب
vocab = joblib.load(vocab_path)
vocab_size = len(vocab)

# تحميل الداتا
df = pd.read_excel(dataset_path)

# تحويل كل row إلى فيكتور
vectors = []

for feat_str in tqdm(df['feat'].fillna('{}'), desc="🔄 Vectorizing feats"):
    try:
        feat_dict = ast.literal_eval(feat_str)
        vector = np.zeros(vocab_size, dtype=np.float32)
        for token, count in feat_dict.items():
            token = token.lower().strip()
            if token in vocab:
                vector[vocab[token]] = count
        vectors.append(vector)
    except:
        vectors.append(np.zeros(vocab_size, dtype=np.float32))

# تحويل إلى DataFrame
vec_df = pd.DataFrame(vectors, columns=[f"feat_{i}" for i in range(vocab_size)])

# دمج مع الأعمدة الأصلية
final_df = pd.concat([df[['lbl', 'wght', 'dbg']], vec_df], axis=1)

# حفظ CSV كامل (أفضل أداء)
final_df.to_csv(output_csv, index=False)
print(f"✅ Saved full vectorized dataset to: {output_csv}")

# حفظ Excel معاينة أول 1000 صف فقط
final_df.head(1000).to_excel(output_excel_preview, index=False)
print(f"✅ Saved preview (first 1000 rows) to: {output_excel_preview}")

# طباعة معلومات
print(f"\n📐 Final shape: {final_df.shape}")
print(f"🧠 Feature columns: {vec_df.columns[:5].tolist()} ...")
