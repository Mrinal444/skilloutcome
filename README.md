# skilloutcome

SIH Problem Statement ID: SIH26135. Placement prediction, attrition risk, and a role-based
skill-gap engine, served as an internal ML API.

## Layout

- `src/data/prepare_dataset.py` — rebuilds the 13 normalized tables in `data/processed` from the illustrative source CSV. All-or-nothing: tables are staged, destinations are probed for locks, and a failure mid-swap restores the previous dataset.
- `src/modeling/features.py` — the single feature contract shared by training and serving, plus the skill-gap calculation and the contract fingerprint.
- `src/modeling/train.py` — chronological splits, six candidate models per task, probability calibration on the validation window, decision thresholds and band summaries written to `reports/`.
- `src/api/main.py` — `POST /predict-placement`, `POST /predict-attrition`, `POST /skill-gap`, and the `GET /reference/*` lookups.
- `tests/` — feature unit tests plus fixture-based pipeline tests that need neither the source CSV nor scikit-learn.
- `docs/` — data model, ML plan, model card, API contract, and the input-ownership boundary.

## Usage

```powershell
pip install -r requirements.txt
python -m src.data.prepare_dataset --input "C:\path\to\skillimpact_50000_master_dataset.csv"
python -m src.modeling.train --data-dir data/processed --task both
python -m pytest
uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

Training and serving agree through a feature-contract fingerprint and bundle schema stored in each
model bundle. Change the feature lists, skills tokenisation, calibration contract, or supported
runtime versions and the API returns 503 until both models are retrained; `GET /health` reports
which bundles still match.

Neither model is read at a 0.5 cut-off. Placement returns a `support_priority` band (priority rises
as placement probability falls, because ~86% of completers are placed) and attrition returns a
Low/Medium/High risk band; both sets of cuts are fitted on the calibration split and stored in the
bundle, so retraining moves them. See `docs/model_card.md`.

The API is an internal service contract, not an end-user form. See `docs/input_ownership.md`.

Scope note: prediction and recommendation components only — no chatbot, LLM, or frontend work in
this repository.
