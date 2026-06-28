# Setup

Clone the repository:

```bash
git clone https://github.com/Layansabha/Dom-xss-ML.git
cd Dom-xss-ML
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Update dataset paths inside the scripts before running training or preprocessing.

Example:

```bash
python preprocessing/create_vocabulary.py
python preprocessing/vectorize_data.py
python training/train_lightgbm.py
```
