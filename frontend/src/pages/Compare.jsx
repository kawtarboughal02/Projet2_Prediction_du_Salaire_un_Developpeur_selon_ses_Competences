import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchJson } from "../api";

function Compare() {
  const [options, setOptions] = useState({
    countries: [],
    education_levels: [],
    languages: [],
  });
  const [selectedLanguages, setSelectedLanguages] = useState([]);
  const [selectedCountries, setSelectedCountries] = useState([]);
  const [years, setYears] = useState("");
  const [edlevel, setEdlevel] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingOptions, setLoadingOptions] = useState(true);
  const [error, setError] = useState("");

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

  const toggleValue = (value, setValues) => {
    setValues((previous) =>
      previous.includes(value)
        ? previous.filter((item) => item !== value)
        : [...previous, value],
    );
  };

  const handleCompare = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const comparisons = await Promise.all(
        selectedCountries.map(async (country) => {
          const data = await fetchJson("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              years,
              country,
              edlevel,
              langages: selectedLanguages,
            }),
          });
          return { pays: country, salaire: data.prediction };
        }),
      );
      setResults(comparisons);
    } catch (requestError) {
      setError(requestError.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container">
      <section className="page-intro">
        <p className="eyebrow">Comparaison géographique</p>
        <h1>Comparer les estimations par pays</h1>
        <p>
          Les profils comparés partagent la même expérience, le même niveau
          d’études et les mêmes compétences.
        </p>
      </section>

      <form className="panel prediction-form" onSubmit={handleCompare}>
        {loadingOptions ? (
          <p role="status">Chargement des options du modèle…</p>
        ) : (
          <>
            <label htmlFor="compare-years">
              Années d’expérience professionnelle
            </label>
            <input
              id="compare-years"
              type="number"
              min="0"
              max="60"
              step="0.5"
              value={years}
              onChange={(event) => setYears(event.target.value)}
              required
            />

            <label htmlFor="compare-education">Niveau d’études</label>
            <select
              id="compare-education"
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
                      checked={selectedLanguages.includes(language)}
                      onChange={() =>
                        toggleValue(language, setSelectedLanguages)
                      }
                    />
                    {language}
                  </label>
                ))}
              </div>
            </fieldset>

            <fieldset>
              <legend>Pays à comparer</legend>
              <div className="checkboxes">
                {options.countries.map((country) => (
                  <label key={country} className="checkbox-item">
                    <input
                      type="checkbox"
                      checked={selectedCountries.includes(country)}
                      onChange={() =>
                        toggleValue(country, setSelectedCountries)
                      }
                    />
                    {country}
                  </label>
                ))}
              </div>
            </fieldset>

            <button
              type="submit"
              disabled={loading || selectedCountries.length === 0}
            >
              {loading ? "Comparaison en cours…" : "Comparer les pays"}
            </button>
          </>
        )}
      </form>

      {error && (
        <p className="message message-error" role="alert">
          {error}
        </p>
      )}

      {results.length > 0 && (
        <section className="panel chart-panel">
          <h2>Salaires annuels estimés (USD)</h2>
          <ResponsiveContainer width="100%" height={360}>
            <BarChart data={results} margin={{ top: 20, right: 20, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="pays" interval={0} angle={-20} textAnchor="end" height={70} />
              <YAxis />
              <Tooltip formatter={(value) => `${Number(value).toLocaleString("fr-FR")} USD`} />
              <Bar dataKey="salaire" name="Estimation annuelle" fill="#3157d5" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <p className="chart-note">
            Comparaison indicative issue du modèle, et non d’une enquête
            représentative du marché de chaque pays.
          </p>
        </section>
      )}
    </main>
  );
}

export default Compare;
