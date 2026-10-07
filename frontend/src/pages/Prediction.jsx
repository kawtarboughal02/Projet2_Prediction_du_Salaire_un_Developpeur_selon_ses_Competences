import { useEffect, useState } from "react";
import { fetchJson } from "../api";

function Prediction() {
  const [options, setOptions] = useState({
    countries: [],
    education_levels: [],
    languages: [],
  });
  const [selected, setSelected] = useState([]);
  const [years, setYears] = useState("");
  const [country, setCountry] = useState("");
  const [edlevel, setEdlevel] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingOptions, setLoadingOptions] = useState(true);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);

  useEffect(() => {
    let active = true;
    fetchJson("/api/options")
      .then((data) => {
        if (active) setOptions(data);
      })
      .catch((requestError) => {
        if (active) setError(requestError.message);
      })
      .finally(() => {
        if (active) setLoadingOptions(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const toggleLanguage = (language) => {
    setSelected((previous) =>
      previous.includes(language)
        ? previous.filter((item) => item !== language)
        : [...previous, language],
    );
  };

  const exportPdf = async () => {
    if (prediction === null) return;

    const { default: jsPDF } = await import("jspdf");
    const document = new jsPDF();
    document.setFontSize(16);
    document.text("Prédiction de salaire — développeur", 20, 20);
    document.setFontSize(11);
    document.text(`Expérience : ${years} ans`, 20, 40);
    document.text(`Pays : ${country}`, 20, 50);
    document.text(`Niveau d’études : ${edlevel}`, 20, 60);
    document.text(
      document.splitTextToSize(
        `Compétences : ${selected.length ? selected.join(", ") : "Aucune"}`,
        170,
      ),
      20,
      70,
    );
    document.setFontSize(14);
    document.text(
      `Salaire annuel estimé : ${prediction.toLocaleString("fr-FR")} USD`,
      20,
      95,
    );
    document.save("prediction-salaire-developpeur.pdf");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const data = await fetchJson("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          years,
          country,
          edlevel,
          langages: selected,
        }),
      });

      const result = {
        years,
        country,
        edlevel,
        langages: [...selected],
        prediction: data.prediction,
        date: new Date().toLocaleTimeString("fr-FR"),
      };
      setHistory((previous) => [result, ...previous]);
      setPrediction(data.prediction);
    } catch (requestError) {
      setError(requestError.message);
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container">
      <section className="page-intro">
        <p className="eyebrow">Simulation individuelle</p>
        <h1>Estimez un salaire annuel</h1>
        <p>
          Renseignez un profil de développeur pour obtenir une estimation
          exploratoire en dollars US.
        </p>
      </section>

      <form className="panel prediction-form" onSubmit={handleSubmit}>
        {loadingOptions ? (
          <p role="status">Chargement des options du modèle…</p>
        ) : (
          <>
            <label htmlFor="years">Années d’expérience professionnelle</label>
            <input
              id="years"
              type="number"
              min="0"
              max="60"
              step="0.5"
              value={years}
              onChange={(event) => setYears(event.target.value)}
              required
            />

            <label htmlFor="country">Pays</label>
            <select
              id="country"
              value={country}
              onChange={(event) => setCountry(event.target.value)}
              required
            >
              <option value="">Sélectionner un pays</option>
              {options.countries.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>

            <label htmlFor="education">Niveau d’études</label>
            <select
              id="education"
              value={edlevel}
              onChange={(event) => setEdlevel(event.target.value)}
              required
            >
              <option value="">Sélectionner un niveau d’études</option>
              {options.education_levels.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>

            <fieldset>
              <legend>Compétences (sélection multiple)</legend>
              <div className="checkboxes">
                {options.languages.map((language) => (
                  <label key={language} className="checkbox-item">
                    <input
                      type="checkbox"
                      checked={selected.includes(language)}
                      onChange={() => toggleLanguage(language)}
                    />
                    {language}
                  </label>
                ))}
              </div>
            </fieldset>

            <button type="submit" disabled={loading}>
              {loading ? "Calcul en cours…" : "Prédire mon salaire"}
            </button>
          </>
        )}
      </form>

      {error && (
        <p className="message message-error" role="alert">
          {error}
        </p>
      )}

      {prediction !== null && (
        <section className="panel result-panel" aria-live="polite">
          <p className="eyebrow">Résultat estimatif</p>
          <h2>{prediction.toLocaleString("fr-FR")} USD par an</h2>
          <p>
            Cette estimation reflète les données et les limites du modèle ; elle
            ne constitue pas une recommandation salariale.
          </p>
          <button type="button" className="button-secondary" onClick={exportPdf}>
            Exporter le résultat en PDF
          </button>
        </section>
      )}

      {history.length > 0 && (
        <section className="panel history">
          <h2>Historique de cette session</h2>
          <ul>
            {history.map((item, index) => (
              <li key={`${item.date}-${index}`}>
                {item.date} — {item.years} ans, {item.country},{" "}
                {item.langages.length} compétence(s) —{" "}
                <strong>
                  {item.prediction.toLocaleString("fr-FR")} USD
                </strong>
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}

export default Prediction;
