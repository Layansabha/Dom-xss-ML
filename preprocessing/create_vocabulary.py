import pandas as pd
import joblib
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import ast
import re

# إعدادات
input_file = "C:\\Users\\ROG\\Downloads\\AI\\AI\\merged_shuffled_dataset.xlsx"
output_vocab_file = "vocab_top500_filtered.pkl"
top_k = 500
min_count = 5
num_threads = 16

# فلترة التوكنات
def is_valid_token(token):
    if not isinstance(token, str):
        return False
    token = token.lower().strip()

    if len(token) < 3:
        return False
    if token.isnumeric():
        return False
    if re.match(r"^[^a-zA-Z0-9]+$", token):  # رموز فقط
        return False
    return True

# معالجة جزء من البيانات
def process_feats(feats):
    local_counter = Counter()
    for feat_str in feats:
        try:
            feat_dict = ast.literal_eval(feat_str)
            if isinstance(feat_dict, dict):
                cleaned = {t.lower().strip(): c for t, c in feat_dict.items() if is_valid_token(t)}
                local_counter.update(cleaned)
        except:
            continue
    return local_counter

def main():
    print(f"📥 Loading dataset from: {input_file}")
    df = pd.read_excel(input_file)

    all_feats = df['feat'].dropna().tolist()
    print(f"📊 Total feat rows: {len(all_feats)}")

    chunk_size = max(1, len(all_feats) // num_threads)
    chunks = [all_feats[i:i + chunk_size] for i in range(0, len(all_feats), chunk_size)]

    token_counter = Counter()
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for local_counter in tqdm(executor.map(process_feats, chunks), total=len(chunks), desc="🧠 Counting tokens"):
            token_counter.update(local_counter)

    # تصفية التوكنات
    filtered_tokens = [(token, count) for token, count in token_counter.items() if count >= min_count]
    filtered_tokens = sorted(filtered_tokens, key=lambda x: x[1], reverse=True)[:top_k]
    vocab = {token: idx for idx, (token, _) in enumerate(filtered_tokens)}

    # حفظ الفوكاب
    joblib.dump(vocab, output_vocab_file)
    print(f"\n✅ Saved vocabulary of {len(vocab)} tokens to: {output_vocab_file}")

if __name__ == "__main__":
    main()
