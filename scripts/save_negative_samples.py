import pandas as pd
import random
import lzma
import json

input_file = r"G:\My Drive\dataset\Original dataset\vulnerabilitydata\vulnerability-data\confirmed\shuf.comp.wb.training.100.data.xz"
output_file = "sampled_clean_data.xlsx"
sample_size = 50000

def parse_json_lines(filepath):
    data = []
    with lzma.open(filepath, mode='rt', encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                data.append(obj)
            except json.JSONDecodeError:
                continue
    return data

def main():
    data = parse_json_lines(input_file)
    print(f"✅ Total parsed lines: {len(data)}")

    if len(data) < sample_size:
        raise ValueError(f"Only {len(data)} entries found, less than requested {sample_size}")

    sampled = random.sample(data, sample_size)
    df = pd.DataFrame(sampled, columns=["lbl", "wght", "dbg", "feat"])
    df.to_excel(output_file, index=False)
    print(f"✅ Saved {sample_size} JSON entries to: {output_file}")

if __name__ == "__main__":
    main()
