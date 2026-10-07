export const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export async function fetchJson(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, options);
  } catch (error) {
    const isLocalApi =
      /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?(?:\/|$)/.test(API_URL);
    const guidance = isLocalApi
      ? "Vérifiez que l’API Flask est démarrée avec « .\\venv\\Scripts\\python.exe app\\app.py »."
      : "Vérifiez l’URL de l’API et que le service est disponible.";
    throw new Error(
      `Impossible de joindre l’API (${API_URL}). ${guidance}`,
      { cause: error },
    );
  }

  let data;
  try {
    data = await response.json();
  } catch (error) {
    throw new Error("L’API a renvoyé une réponse illisible.", { cause: error });
  }

  if (!response.ok) {
    throw new Error(data.error || `Erreur HTTP ${response.status}.`);
  }

  return data;
}