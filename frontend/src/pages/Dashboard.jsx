import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchJson } from "../api";

function Dashboard() {
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    fetchJson("/api/metrics")
      .then((data) => {
        if (active) setResults(data);
      })
      .catch((requestError) => {
        if (active) setError(requestError.message);
      });

    return () => {
      active = false;
    };
  }, []);

  if (error) {
    return (
      <main className="container">
        <p className="message message-error" role="alert">
          {error}
        </p>
      </main>
    );
  }

  if (!results) {
    return (
      <main className="container">
        <p role="status">Chargement des résultats du modèle…</p>
      </main>
    );
  }

  const modelMetrics = Object.entries(results.metriques).map(([name, metrics]) => ({
    nom: name,
    MAE: metrics.mae,
    RMSE: metrics.rmse,
  }));
  const modelRows = Object.entries(results.metriques);
  const featureImportance = Object.entries(results.importance)
    .sort((left, right) => right[1] - left[1])
    .slice(0, 10)
    .map(([variable, importance]) => ({ variable, importance }));
  const salaryByLanguage = results.salaire_par_langage || [];

  return (
    <main className="container">
      <section className="page-intro">
        <p className="eyebrow">Évaluation et interprétation</p>
        <h1>Résultats de l’analyse des modèles</h1>
        <p>
          Les scores sont calculés sur le jeu de test du notebook de
          modélisation. Une erreur plus faible est préférable ; R² complète
          cette lecture.
        </p>
      </section>

      <section className="panel chart-panel">
        <h2>Comparaison des modèles — MAE et RMSE</h2>
        <ResponsiveContainer width="100%" height={360}>
          <BarChart data={modelMetrics} margin={{ top: 20, right: 20, left: 10, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="nom" interval={0} angle={-12} textAnchor="end" height={70} />
            <YAxis />
            <Tooltip formatter={(value) => `${Number(value).toLocaleString("fr-FR")} USD`} />
            <Legend />
            <Bar dataKey="MAE" fill="#3157d5" radius={[5, 5, 0, 0]} />
            <Bar dataKey="RMSE" fill="#e0783d" radius={[5, 5, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <p className="chart-note">
          MAE et RMSE sont exprimées en USD par an. La RMSE pénalise davantage
          les grandes erreurs.
        </p>
      </section>

      <section className="panel">
        <h2>Tableau des métriques</h2>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th scope="col">Modèle</th>
                <th scope="col">MAE (USD)</th>
                <th scope="col">RMSE (USD)</th>
                <th scope="col">R²</th>
              </tr>
            </thead>
            <tbody>
              {modelRows.map(([name, metrics]) => (
                <tr key={name}>
                  <th scope="row">{name}</th>
                  <td>{Number(metrics.mae).toLocaleString("fr-FR")}</td>
                  <td>{Number(metrics.rmse).toLocaleString("fr-FR")}</td>
                  <td>{Number(metrics.r2).toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel chart-panel">
        <h2>Variables les plus importantes — XGBoost</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart
            data={featureImportance}
            layout="vertical"
            margin={{ top: 10, right: 20, left: 40, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="variable" type="category" width={130} />
            <Tooltip />
            <Bar dataKey="importance" name="Importance" fill="#16816b" radius={[0, 5, 5, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <p className="chart-note">
          L’importance des variables décrit leur contribution dans le modèle ;
          elle ne prouve pas une relation de causalité.
        </p>
      </section>

      {salaryByLanguage.length > 0 && (
        <section className="panel chart-panel">
          <h2>Salaire médian observé par langage</h2>
          <ResponsiveContainer width="100%" height={420}>
            <BarChart
              data={salaryByLanguage}
              layout="vertical"
              margin={{ top: 10, right: 20, left: 35, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="language" type="category" width={120} />
              <Tooltip
                formatter={(value) => `${Number(value).toLocaleString("fr-FR")} USD`}
              />
              <Bar
                dataKey="median_salary"
                name="Salaire médian annuel"
                fill="#7952b3"
                radius={[0, 5, 5, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
          <p className="chart-note">
            Données descriptives des répondants filtrés du jeu de données, avec
            au moins 50 réponses par langage ; elles ne mesurent pas l’effet
            causal du langage sur le salaire.
          </p>
        </section>
      )}
    </main>
  );
}

export default Dashboard;
