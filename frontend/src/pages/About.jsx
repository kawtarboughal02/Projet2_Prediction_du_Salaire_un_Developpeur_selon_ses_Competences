const technologies = [
  {
    name: "Python, Pandas et NumPy",
    role: "Préparation et manipulation des données",
    reason: "Nettoyage reproductible du jeu d’enquête et préparation des variables.",
  },
  {
    name: "Matplotlib et Seaborn",
    role: "Analyse exploratoire",
    reason: "Visualisation des distributions et relations dans les notebooks.",
  },
  {
    name: "Scikit-learn",
    role: "Modèles de référence et évaluation",
    reason: "Régression linéaire, Random Forest, encodage et métriques communes.",
  },
  {
    name: "XGBoost",
    role: "Modèle principal de l’application",
    reason: "Algorithme de gradient boosting évalué sur des données tabulaires.",
  },
  {
    name: "TensorFlow / Keras",
    role: "Comparaison expérimentale",
    reason: "Réseau de neurones comparé aux modèles tabulaires, sans présumer qu’il gagne.",
  },
  {
    name: "Flask et Flask-CORS",
    role: "API REST de prédiction",
    reason: "Expose les options, estimations et métriques consommées par le navigateur.",
  },
  {
    name: "React et Vite",
    role: "Interface web interactive",
    reason: "Quatre écrans : prédiction, comparateur, tableau de bord et présentation.",
  },
  {
    name: "Recharts",
    role: "Visualisation interactive dans React",
    reason: "Affiche les performances, importances et salaires descriptifs dans le navigateur.",
  },
];

function About() {
  const repositoryUrl =
    import.meta.env.VITE_REPOSITORY_URL ||
    "https://github.com/kawtarboughal02/Projet2_Prediction_du_Salaire_un_Developpeur_selon_ses_Competences";
  const reportUrl = `${repositoryUrl.replace(/\/$/, "")}/blob/main/rapport_final.md`;

  return (
    <main className="container about-page">
      <section className="page-intro">
        <p className="eyebrow">Projet de Data Science et d’intelligence artificielle</p>
        <h1>À propos du projet</h1>
        <p>
          Prédiction du salaire d’un développeur selon ses compétences,
          son expérience, son pays et son niveau d’études.
        </p>
      </section>

      <section className="panel about-section">
        <h2>Contexte</h2>
        <p>
          Les rémunérations des développeurs varient selon les marchés, les
          compétences déclarées, l’expérience et le parcours d’études. Ce projet
          exploite les réponses publiques du Stack Overflow Developer Survey
          2018 pour étudier ces écarts et construire un outil de prédiction
          démonstratif.
        </p>
        <p>
          Le jeu utilisé regroupe les profils disposant des informations
          nécessaires et d’un salaire annuel converti en dollars US. Il s’agit
          d’une enquête volontaire en ligne, non d’un échantillon représentatif
          de tous les développeurs ou de tous les pays.
        </p>
      </section>

      <section className="panel about-section">
        <h2>Objectif et problématique</h2>
        <p>
          L’objectif est de mesurer dans quelle mesure les compétences
          techniques, l’expérience professionnelle, le pays et le niveau
          d’études permettent d’estimer un salaire annuel, puis de comparer
          plusieurs familles de modèles selon leur précision.
        </p>
        <p>
          L’application transforme les résultats du travail analytique en un
          service utilisable : l’API Flask sert le modèle XGBoost et l’interface
          React présente une simulation, une comparaison entre pays et les
          résultats de l’évaluation.
        </p>
      </section>

      <section className="panel about-section">
        <h2>Méthodologie</h2>
        <ol className="method-list">
          <li>
            <strong>Exploration :</strong> inspection de l’enquête Stack
            Overflow et de ses variables.
          </li>
          <li>
            <strong>Nettoyage :</strong> sélection des colonnes pertinentes,
            conversion de l’expérience et filtrage des salaires atypiques.
          </li>
          <li>
            <strong>Analyse exploratoire :</strong> distributions, expérience,
            pays, niveaux d’études et salaires observés par langage.
          </li>
          <li>
            <strong>Préparation :</strong> encodage multi-label des langages et
            encodage des catégories de pays et d’études.
          </li>
          <li>
            <strong>Évaluation :</strong> Régression Linéaire, Random Forest,
            XGBoost et réseau de neurones TensorFlow sont comparés avec MAE,
            RMSE et R².
          </li>
          <li>
            <strong>Application :</strong> sauvegarde des artefacts, API REST,
            interface React et visualisations interactives.
          </li>
        </ol>
        <p>
          Le partage entraînement/test utilisé par les notebooks est aléatoire
          (80/20, graine fixe) et non temporel. Les métriques représentent donc
          cette partition et ne garantissent pas les performances futures.
        </p>
      </section>

      <section className="panel about-section">
        <h2>Technologies, rôle et justification</h2>
        <div className="table-scroll">
          <table className="technology-table">
            <thead>
              <tr>
                <th scope="col">Technologie</th>
                <th scope="col">Rôle</th>
                <th scope="col">Justification</th>
              </tr>
            </thead>
            <tbody>
              {technologies.map((technology) => (
                <tr key={technology.name}>
                  <th scope="row">{technology.name}</th>
                  <td>{technology.role}</td>
                  <td>{technology.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel about-section">
        <h2>Résultats et interprétation</h2>
        <p>
          Dans les métriques enregistrées, XGBoost présente la plus faible
          erreur absolue moyenne (MAE : environ 22&nbsp;649 USD) et un R²
          d’environ 0,362. Ces valeurs résument une expérience sur une enquête
          donnée ; elles ne permettent ni de garantir une estimation
          individuelle ni d’établir une relation causale.
        </p>
        <p>
          Le tableau de bord expose les scores des quatre modèles, les variables
          importantes pour XGBoost et les salaires médians observés par langage.
        </p>
      </section>

      <section className="panel about-section">
        <h2>Limites et usage responsable</h2>
        <ul className="detail-list">
          <li>
            Les salaires sont auto-déclarés et la population répondante n’est
            pas représentative de l’ensemble du marché mondial.
          </li>
          <li>
            Le modèle peut reproduire des écarts géographiques ou sociaux
            présents dans les données ; ses prédictions ne sont pas des
            références normatives de rémunération.
          </li>
          <li>
            Les catégories inconnues ne sont pas extrapolées : l’API demande
            une valeur parmi les modalités apprises.
          </li>
          <li>
            Une validation temporelle, une analyse de biais plus complète et
            des données plus récentes seraient nécessaires avant tout usage
            professionnel.
          </li>
        </ul>
      </section>

      <section className="panel about-section">
        <h2>Documentation et auteure</h2>
        <ul className="detail-list">
          <li>
            <a href={repositoryUrl} target="_blank" rel="noreferrer">
              Dépôt GitHub du projet
            </a>
          </li>
          <li>
            <a href={reportUrl} target="_blank" rel="noreferrer">
              Rapport final complet
            </a>
          </li>
          <li>
            <a
              href="https://lnkd.in/p/ewqEGkZQ"
              target="_blank"
              rel="noreferrer"
            >
              Démonstration complète — LinkedIn
            </a>
          </li>
          <li>
            <a
              href="https://www.linkedin.com/in/kawtar-boughal02"
              target="_blank"
              rel="noreferrer"
            >
              Kawtar Boughal — profil LinkedIn
            </a>
          </li>
        </ul>
      </section>
    </main>
  );
}

export default About;
