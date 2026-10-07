import { lazy, Suspense, useState } from "react";
import "./App.css";

const Prediction = lazy(() => import("./pages/Prediction"));
const Compare = lazy(() => import("./pages/Compare"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const About = lazy(() => import("./pages/About"));

function App() {
  const [page, setPage] = useState("prediction");

  const pages = {
    prediction: <Prediction />,
    compare: <Compare />,
    dashboard: <Dashboard />,
    about: <About />,
  };

  return (
    <>
      <header className="site-header">
        <p className="site-title">
          Prédiction du salaire d’un développeur selon ses compétences
        </p>
        <p className="site-subtitle">Stack Overflow Developer Survey 2018</p>
        <nav className="navbar" aria-label="Navigation principale">
          <button
            type="button"
            className={page === "prediction" ? "active" : ""}
            aria-current={page === "prediction" ? "page" : undefined}
            onClick={() => setPage("prediction")}
          >
            Prédiction
          </button>
          <button
            type="button"
            className={page === "compare" ? "active" : ""}
            aria-current={page === "compare" ? "page" : undefined}
            onClick={() => setPage("compare")}
          >
            Comparateur
          </button>
          <button
            type="button"
            className={page === "dashboard" ? "active" : ""}
            aria-current={page === "dashboard" ? "page" : undefined}
            onClick={() => setPage("dashboard")}
          >
            Tableau de bord
          </button>
          <button
            type="button"
            className={page === "about" ? "active" : ""}
            aria-current={page === "about" ? "page" : undefined}
            onClick={() => setPage("about")}
          >
            À propos
          </button>
        </nav>
      </header>
      <Suspense
        fallback={
          <main className="container">
            <p role="status">Chargement de la page…</p>
          </main>
        }
      >
        {pages[page]}
      </Suspense>
    </>
  );
}

export default App;