from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"


def _save_figure(figure: plt.Figure, output_path: str | Path | None) -> None:
    if output_path is not None:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(destination, bbox_inches="tight")


def plot_salary_distribution(
    dataframe: pd.DataFrame,
    output_path: str | Path | None = FIGURES_DIR / "distribution_salaires.png",
) -> tuple[plt.Figure, plt.Axes]:
    figure, axes = plt.subplots(figsize=(10, 5))
    sns.histplot(data=dataframe, x="ConvertedCompYearly", bins=50, ax=axes)
    axes.set(title="Distribution des salaires annuels", xlabel="Salaire annuel (USD)")
    _save_figure(figure, output_path)
    return figure, axes


def plot_salary_vs_experience(
    dataframe: pd.DataFrame,
    output_path: str | Path | None = FIGURES_DIR / "salaire_vs_experience.png",
) -> tuple[plt.Figure, plt.Axes]:
    figure, axes = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        data=dataframe,
        x="YearsCodePro",
        y="ConvertedCompYearly",
        alpha=0.3,
        ax=axes,
    )
    axes.set(
        title="Salaire annuel selon l'expérience professionnelle",
        xlabel="Années d'expérience professionnelle",
        ylabel="Salaire annuel (USD)",
    )
    _save_figure(figure, output_path)
    return figure, axes


def plot_salary_by_language(
    dataframe: pd.DataFrame,
    min_responses: int = 50,
    top_n: int = 15,
    output_path: str | Path | None = FIGURES_DIR / "salaire_par_langage.png",
) -> tuple[plt.Figure, plt.Axes]:
    language_rows = dataframe[
        ["LanguageHaveWorkedWith", "ConvertedCompYearly"]
    ].copy()
    language_rows["LanguageHaveWorkedWith"] = language_rows[
        "LanguageHaveWorkedWith"
    ].str.split(";")
    language_rows = language_rows.explode("LanguageHaveWorkedWith")
    language_rows["LanguageHaveWorkedWith"] = language_rows[
        "LanguageHaveWorkedWith"
    ].str.strip()

    language_summary = (
        language_rows.groupby("LanguageHaveWorkedWith")["ConvertedCompYearly"]
        .agg(median="median", count="count")
        .query("count >= @min_responses")
        .sort_values("median")
        .tail(top_n)
        .reset_index()
    )

    figure, axes = plt.subplots(figsize=(10, 7))
    sns.barplot(
        data=language_summary,
        x="median",
        y="LanguageHaveWorkedWith",
        ax=axes,
    )
    axes.set(
        title="Salaire médian annuel par langage",
        xlabel="Salaire médian annuel (USD)",
        ylabel="Langage",
    )
    _save_figure(figure, output_path)
    return figure, axes