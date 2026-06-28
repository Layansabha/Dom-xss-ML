# Setup

Basic setup depends on the final source code location.

Suggested local workflow:

```bash
git clone https://github.com/Layansabha/Dom-xss-ML.git
cd Dom-xss-ML
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If the project has a React frontend, install dependencies from the frontend folder:

```bash
npm install
npm run dev
```
