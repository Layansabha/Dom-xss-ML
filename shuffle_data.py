import pandas as pd
import random

positive_path = r"C:\Users\ROG\Downloads\positive_rows.xlsx"
negative_path = r"C:\Users\ROG\Downloads\AI\AI\sampled_clean_data.xlsx"
output_path = r"merged_shuffled_dataset.xlsx"

# Read both files
df_pos = pd.read_excel(positive_path)
df_neg = pd.read_excel(negative_path)

# Combine
df_combined = pd.concat([df_pos, df_neg], ignore_index=True)

# Shuffle
df_shuffled = df_combined.sample(frac=1, random_state=42).reset_index(drop=True)

# Save to Excel
df_shuffled.to_excel(output_path, index=False)
print(f"✅ Merged and shuffled dataset saved to: {output_path}")
