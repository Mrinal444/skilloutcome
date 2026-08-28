# Run the pipeline

```powershell
python -m src.data.prepare_dataset --input "C:\path\to\skillimpact_50000_master_dataset.csv"
python -m src.modeling.train --data-dir data/processed --task both
python -m pytest
uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

Retrain whenever the serving contract changes. If `src/modeling/features.py` changes a feature list,
`TEXT_ENCODING_VERSION`, or `MODEL_BUNDLE_SCHEMA_VERSION`, the saved bundles no longer match their
fingerprint and every prediction endpoint returns 503 until step two is rerun. The persisted-model
packages (pandas, scikit-learn, and XGBoost) are exact pins in `requirements.txt`; bundles record
those versions and the API refuses to serve them under a different runtime. `GET /health` shows
which bundle is stale.

Close `data/processed/*.csv` in Excel or any sync client before regenerating. The pipeline probes
each destination for a lock first and refuses to start rather than leaving a half-written dataset;
if a swap still fails, the previous tables are restored.

Example role-based gap request:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/skill-gap -ContentType 'application/json' -Body '{"target_job_role":"Data Analyst","current_skills":[{"name":"Python","proficiency":82},{"name":"SQL","proficiency":76},{"name":"Power BI","proficiency":68}]}'
```

Check which values the models accept before wiring a caller:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/reference/vocabularies
Invoke-RestMethod http://127.0.0.1:8000/reference/roles
```

The tests do not need the 50k source file or a trained model: `tests/conftest.py` generates a
schema-valid miniature source and runs the real preparation pipeline on it, and the API and model
tests skip themselves when FastAPI or an up-to-date bundle is unavailable.

The API is available at `http://127.0.0.1:8000/docs`.
