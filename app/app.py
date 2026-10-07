import json
import math
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"
PROCESSED_DATA_PATH = (
    PROJECT_ROOT / "data" / "processed" / "donnees_salaires_developpeurs.csv"
)

model = joblib.load(MODELS_DIR / "salary_model.pkl")
le_country = joblib.load(MODELS_DIR / "le_country.pkl")
le_edlevel = joblib.load(MODELS_DIR / "le_edlevel.pkl")
top_langages = joblib.load(MODELS_DIR / "top_langages.pkl")

with (MODELS_DIR / "metriques.json").open(encoding="utf-8") as metrics_file:
    metriques = json.load(metrics_file)
with (MODELS_DIR / "importance.json").open(encoding="utf-8") as importance_file:
    importance = json.load(importance_file)


@lru_cache(maxsize=1)
def _salary_by_language():
    dataframe = pd.read_csv(
        PROCESSED_DATA_PATH,
        usecols=["LanguageHaveWorkedWith", "ConvertedCompYearly"],
    )
    dataframe["LanguageHaveWorkedWith"] = dataframe[
        "LanguageHaveWorkedWith"
    ].str.split(";")
    language_rows = dataframe.explode("LanguageHaveWorkedWith")
    summary = (
        language_rows.groupby("LanguageHaveWorkedWith")["ConvertedCompYearly"]
        .agg(median="median", responses="count")
        .query("responses >= 50")
        .sort_values("median", ascending=False)
        .head(15)
        .reset_index()
    )
    return [
        {
            "language": row.LanguageHaveWorkedWith,
            "median_salary": round(float(row.median)),
            "responses": int(row.responses),
        }
        for row in summary.itertuples(index=False)
    ]


@app.get("/")
def health_check():
    return jsonify({"status": "ok", "service": "salary-prediction-api"})


@app.get("/api/languages")
def get_languages():
    return jsonify([str(language) for language in top_langages])


@app.get("/api/options")
def get_options():
    return jsonify(
        {
            "countries": [str(country) for country in le_country.classes_],
            "education_levels": [str(level) for level in le_edlevel.classes_],
            "languages": [str(language) for language in top_langages],
        }
    )


@app.post("/api/predict")
def predict():
    if not request.is_json:
        return jsonify({"error": "Le corps de la requête doit être au format JSON."}), 400

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Le corps JSON doit être un objet."}), 400

    required_fields = ("years", "country", "edlevel", "langages")
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify(
            {"error": "Champs manquants : " + ", ".join(missing_fields) + "."}
        ), 400

    try:
        years = float(data["years"])
    except (TypeError, ValueError):
        return jsonify({"error": "L'expérience doit être un nombre valide."}), 400
    if isinstance(data["years"], bool) or not math.isfinite(years) or not 0 <= years <= 60:
        return jsonify(
            {"error": "L'expérience doit être comprise entre 0 et 60 ans."}
        ), 400

    country = data["country"]
    if not isinstance(country, str) or country not in le_country.classes_:
        return jsonify(
            {"error": "Choisissez un pays présent dans la liste des options."}
        ), 400

    education_level = data["edlevel"]
    if (
        not isinstance(education_level, str)
        or education_level not in le_edlevel.classes_
    ):
        return jsonify(
            {"error": "Choisissez un niveau d'études présent dans la liste des options."}
        ), 400

    selected_languages = data["langages"]
    if not isinstance(selected_languages, list) or any(
        not isinstance(language, str) for language in selected_languages
    ):
        return jsonify({"error": "Les compétences doivent être une liste de textes."}), 400

    supported_languages = {str(language) for language in top_langages}
    unknown_languages = sorted(set(selected_languages) - supported_languages)
    if unknown_languages:
        return jsonify(
            {
                "error": "Compétences non prises en charge : "
                + ", ".join(unknown_languages)
                + "."
            }
        ), 400

    selected_languages = list(dict.fromkeys(selected_languages))
    country_encoded = int(le_country.transform([country])[0])
    education_encoded = int(le_edlevel.transform([education_level])[0])
    language_vector = [
        int(language in selected_languages) for language in top_langages
    ]
    feature_names = [
        "YearsCodePro",
        "Country_enc",
        "EdLevel_enc",
        "nb_competences",
        *[str(language) for language in top_langages],
    ]
    model_input = pd.DataFrame(
        [[years, country_encoded, education_encoded, len(selected_languages), *language_vector]],
        columns=feature_names,
    )
    prediction = float(model.predict(model_input)[0])
    if not math.isfinite(prediction):
        return jsonify({"error": "Le modèle n'a pas produit de prédiction valide."}), 500

    return jsonify({"prediction": round(prediction)})


@app.get("/api/metrics")
def get_metrics():
    return jsonify(
        {
            "metriques": metriques,
            "importance": importance,
            "salaire_par_langage": _salary_by_language(),
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
