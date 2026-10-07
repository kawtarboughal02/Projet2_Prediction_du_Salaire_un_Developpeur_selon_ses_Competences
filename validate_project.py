"""Validate the salary-prediction project and optionally execute its notebooks."""

import argparse
import ast
import json
import math
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NOTEBOOK_DIR = ROOT / "notebooks"
MODEL_DIR = ROOT / "models"
NOTEBOOKS = (
    "01_exploration.ipynb",
    "02_nettoyage.ipynb",
    "03_analyse_visualisation.ipynb",
    "04_modelisation.ipynb",
)
REQUIRED_COLUMNS = {
    "YearsCodePro",
    "Country",
    "EdLevel",
    "LanguageHaveWorkedWith",
    "Employment",
    "ConvertedCompYearly",
}
MODEL_FILES = (
    "salary_model.pkl",
    "le_country.pkl",
    "le_edlevel.pkl",
    "mlb_langages.pkl",
    "top_langages.pkl",
    "metriques.json",
    "importance.json",
)


class ProjectValidationError(RuntimeError):
    """Raised when a required project check fails."""


def require(condition, message):
    if not condition:
        raise ProjectValidationError(message)


def validate_required_files(require_raw_data=False):
    required_files = (
        ROOT / "README.md",
        ROOT / "rapport_final.md",
        ROOT / "requirements.txt",
        ROOT / "requirements-api.txt",
        ROOT / "Procfile",
        ROOT / "app" / "app.py",
        ROOT / "frontend" / "package.json",
        ROOT / "frontend" / "src" / "App.jsx",
        ROOT / "frontend" / "src" / "pages" / "Prediction.jsx",
        ROOT / "frontend" / "src" / "pages" / "Compare.jsx",
        ROOT / "frontend" / "src" / "pages" / "Dashboard.jsx",
        ROOT / "frontend" / "src" / "pages" / "About.jsx",
        ROOT / "data" / "processed" / "donnees_salaires_developpeurs.csv",
    )
    if require_raw_data:
        required_files += (ROOT / "data" / "raw" / "survey_results_public.csv",)
    for path in required_files:
        require(path.is_file(), f"Fichier requis introuvable : {path.relative_to(ROOT)}")
        require(path.stat().st_size > 0, f"Fichier vide : {path.relative_to(ROOT)}")

    for filename in MODEL_FILES:
        path = MODEL_DIR / filename
        require(path.is_file(), f"Artefact requis introuvable : models/{filename}")
        require(path.stat().st_size > 0, f"Artefact vide : models/{filename}")


def load_notebooks():
    notebooks = []
    for filename in NOTEBOOKS:
        path = NOTEBOOK_DIR / filename
        require(path.is_file(), f"Notebook requis introuvable : notebooks/{filename}")
        notebook = json.loads(path.read_text(encoding="utf-8"))
        cells = notebook.get("cells")
        require(isinstance(cells, list), f"Structure de notebook invalide : {filename}")

        code_cells = 0
        for cell_number, cell in enumerate(cells, start=1):
            if cell.get("cell_type") != "code":
                continue
            source = "".join(cell.get("source", []))
            if not source.strip():
                continue
            try:
                ast.parse(source, filename=f"{filename}:cell_{cell_number}")
            except SyntaxError as error:
                raise ProjectValidationError(
                    f"Erreur de syntaxe dans {filename}, cellule {cell_number} : {error}"
                ) from error
            code_cells += 1

        require(code_cells > 0, f"Aucune cellule Python non vide : {filename}")
        notebooks.append((path, notebook))
        print(f"OK — structure et syntaxe de {filename} ({code_cells} cellules)")
    return notebooks


def execute_notebooks(notebooks):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as pyplot

    def suppress_display(*args, **kwargs):
        return None

    pyplot.show = suppress_display
    previous_directory = Path.cwd()
    try:
        os.chdir(NOTEBOOK_DIR)
        for notebook_path, notebook in notebooks:
            namespace = {"__name__": "__main__"}
            print(f"Exécution de {notebook_path.name}")
            for cell_number, cell in enumerate(notebook.get("cells", []), start=1):
                if cell.get("cell_type") != "code":
                    continue
                source = "".join(cell.get("source", []))
                if not source.strip():
                    continue
                try:
                    exec(
                        compile(
                            source,
                            f"{notebook_path.name}:cell_{cell_number}",
                            "exec",
                        ),
                        namespace,
                    )
                except Exception as error:
                    raise RuntimeError(
                        f"{notebook_path.name}, cellule {cell_number}: {error}"
                    ) from error
            print(f"OK — exécution de {notebook_path.name}")
    finally:
        os.chdir(previous_directory)


def validate_dataset():
    import pandas as pd

    processed_path = ROOT / "data" / "processed" / "donnees_salaires_developpeurs.csv"
    dataframe = pd.read_csv(processed_path)
    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)
    require(
        not missing_columns,
        "Colonnes absentes du jeu nettoyé : " + ", ".join(sorted(missing_columns)),
    )
    require(not dataframe.empty, "Le jeu de données nettoyé est vide.")

    salaries = pd.to_numeric(dataframe["ConvertedCompYearly"], errors="coerce")
    require(salaries.notna().all(), "Le jeu nettoyé contient des salaires invalides.")
    require(
        (salaries.between(5_000, 500_000)).all(),
        "Des salaires nettoyés sortent des bornes [5 000, 500 000] USD.",
    )
    print(f"OK — données nettoyées : {len(dataframe):,} lignes")


def validate_model_artifacts():
    metrics_path = MODEL_DIR / "metriques.json"
    importance_path = MODEL_DIR / "importance.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    importance = json.loads(importance_path.read_text(encoding="utf-8"))

    expected_models = {
        "Linear Regression",
        "Random Forest",
        "XGBoost",
        "TensorFlow (NN)",
    }
    require(
        set(metrics) == expected_models,
        "Les métriques doivent contenir exactement les quatre modèles comparés.",
    )
    for model_name, values in metrics.items():
        require(
            {"mae", "rmse", "r2"} <= set(values),
            f"Métriques incomplètes pour {model_name}.",
        )
        require(
            all(math.isfinite(float(values[key])) for key in ("mae", "rmse", "r2")),
            f"Métriques non finies pour {model_name}.",
        )
    require(bool(importance), "Le fichier d’importance des variables est vide.")
    require(
        all(math.isfinite(float(value)) for value in importance.values()),
        "Le fichier d’importance contient une valeur non finie.",
    )
    print("OK — artefacts du modèle et métriques des quatre modèles")


def validate_api():
    from app.app import app

    client = app.test_client()
    health = client.get("/")
    require(health.status_code == 200, "La route de santé de l’API ne répond pas.")
    require(health.get_json().get("status") == "ok", "État API inattendu.")

    languages = client.get("/api/languages")
    options = client.get("/api/options")
    metrics_response = client.get("/api/metrics")
    require(languages.status_code == 200, "La route /api/languages a échoué.")
    require(options.status_code == 200, "La route /api/options a échoué.")
    require(metrics_response.status_code == 200, "La route /api/metrics a échoué.")

    language_list = languages.get_json()
    categories = options.get_json()
    require(bool(language_list), "La liste de langages est vide.")
    require(
        bool(categories.get("countries"))
        and bool(categories.get("education_levels"))
        and bool(categories.get("languages")),
        "Les options de l’API sont incomplètes.",
    )

    prediction = client.post(
        "/api/predict",
        json={
            "years": 5,
            "country": categories["countries"][0],
            "edlevel": categories["education_levels"][0],
            "langages": [categories["languages"][0]],
        },
    )
    require(
        prediction.status_code == 200,
        f"La prédiction valide a échoué : {prediction.get_json()}",
    )
    predicted_salary = prediction.get_json().get("prediction")
    require(
        isinstance(predicted_salary, (int, float))
        and not isinstance(predicted_salary, bool)
        and math.isfinite(float(predicted_salary)),
        "La réponse de prédiction n’est pas un nombre fini.",
    )

    invalid_prediction = client.post(
        "/api/predict",
        json={
            "years": 5,
            "country": "Pays inconnu",
            "edlevel": categories["education_levels"][0],
            "langages": [],
        },
    )
    require(
        invalid_prediction.status_code == 400,
        "L’API doit refuser une catégorie de pays inconnue avec HTTP 400.",
    )
    missing_fields = client.post("/api/predict", json={})
    require(
        missing_fields.status_code == 400,
        "L’API doit refuser les champs manquants avec HTTP 400.",
    )

    metric_data = metrics_response.get_json()
    require(
        len(metric_data.get("metriques", {})) == 4,
        "La réponse métriques ne contient pas les quatre modèles.",
    )
    require(
        bool(metric_data.get("importance"))
        and bool(metric_data.get("salaire_par_langage")),
        "Le tableau de bord n’a pas ses données d’importance ou de salaires.",
    )
    print(f"OK — API Flask (prédiction test : {predicted_salary:,} USD)")


def validate_frontend_manifest():
    package_path = ROOT / "frontend" / "package.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    scripts = package.get("scripts", {})
    require("build" in scripts, "Le script frontend `build` est absent.")
    require("lint" in scripts, "Le script frontend `lint` est absent.")
    print("OK — scripts npm de build et de lint présents")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute-notebooks",
        action="store_true",
        help="exécute les notebooks dans l’ordre et régénère les artefacts",
    )
    arguments = parser.parse_args()

    validate_required_files(require_raw_data=arguments.execute_notebooks)
    notebooks = load_notebooks()
    if arguments.execute_notebooks:
        execute_notebooks(notebooks)
        validate_required_files(require_raw_data=True)
    validate_dataset()
    validate_model_artifacts()
    validate_api()
    validate_frontend_manifest()
    print("VALIDATION_COMPLETE")


if __name__ == "__main__":
    try:
        main()
    except ProjectValidationError as error:
        raise SystemExit(f"VALIDATION_FAILED: {error}") from error
