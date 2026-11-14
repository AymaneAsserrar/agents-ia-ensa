# De ChatGPT aux agents IA

Code de la session IEEE ENSA Fès du 14 novembre 2026, par Aymane Asserrar ([@aymane.ai_](https://instagram.com/aymane.ai_) sur Instagram).

Les slides de la session : [slides/De_ChatGPT_aux_agents_IA.pdf](slides/De_ChatGPT_aux_agents_IA.pdf).

On construit un agent IA à partir de zéro, en 5 petits scripts Python, sans framework. L'idée : comprendre ce qui se passe vraiment derrière ChatGPT, Claude ou Gemini quand ils "utilisent des outils".

```
Agent = LLM + outils + une boucle
```

## Installation (5 minutes)

Il te faut Python 3.10 ou plus.

```bash
git clone https://github.com/AymaneAsserrar/agents-ia-ensa.git
cd agents-ia-ensa
pip install -r requirements.txt
cp .env.example .env
```

Ensuite, mets une clé API dans `.env`. Pendant la session, la démo tourne avec Claude (clé sur la [console Anthropic](https://console.anthropic.com), crédits payants). Pour refaire la démo gratuitement, prends une clé Gemini sur [Google AI Studio](https://aistudio.google.com/apikey) et mets `PROVIDER=gemini`.

Pas de clé ? Tout marche quand même en mode démo (réponses pré-enregistrées) : ajoute `--mock` à la fin de la commande.

## Les 5 étapes

| Script | Ce que tu apprends |
|---|---|
| `01_appel_llm.py` | Un LLM prend du texte et prédit la suite. C'est tout. |
| `02_memoire.py` | Le LLM n'a aucune mémoire : l'application lui renvoie tout l'historique à chaque message. |
| `03_premier_outil.py` | Le function calling. Le LLM ne calcule pas, il demande à ton code de le faire. |
| `04_boucle_agent.py` | La boucle d'agent : le LLM enchaîne plusieurs outils et décide seul de l'ordre. |
| `05_agent_etudiant.py` | Un vrai agent qui lit des fichiers, écrit et exécute son propre code Python, puis rédige un rapport. |

Lance-les dans l'ordre :

```bash
python 01_appel_llm.py
python 02_memoire.py
python 03_premier_outil.py
python 04_boucle_agent.py
python 05_agent_etudiant.py
```

Dans le script 5, appuie sur Entrée pour la démo (analyse de `data/notes.csv`), ou donne ta propre tâche, par exemple :

- « Fais une fiche de révision de data/cours_ia.md dans sortie/fiche.md »
- « Combien d'étudiants ont plus de 15 en maths ? »
- « Fais un graphique des notes d'informatique »

Avant d'exécuter du code, l'agent te montre ce qu'il veut lancer et attend ton accord. Garde ce réflexe dans tes propres projets : un agent qui exécute du code sans contrôle humain peut faire n'importe quoi sur ta machine.

## Les fichiers

```
llm.py       connexion au LLM (Claude, Gemini, Groq, Ollama, OpenAI) + mode démo
outils.py    les fonctions que les agents peuvent appeler
data/        les fichiers d'entrée (notes, cours)
sortie/      ce que l'agent produit
```

## Changer de modèle

Le code utilise le format de l'API OpenAI, que la plupart des fournisseurs acceptent. Pour changer, modifie seulement `.env` :

- `PROVIDER=claude` : Claude d'Anthropic, le modèle de la démo (clé payante)
- `PROVIDER=gemini` : gratuit avec une clé AI Studio (utilisé si `PROVIDER` est absent)
- `PROVIDER=ollama` : un modèle qui tourne sur ton PC, sans internet ni clé ([ollama.com](https://ollama.com))
- `PROVIDER=groq` ou `PROVIDER=openai` : avec leur clé et `MODEL=...`

## Pour aller plus loin

- Ajoute un outil dans `outils.py` (météo, recherche web, envoi de mail) et décris-le dans `05_agent_etudiant.py`.
- Regarde le protocole MCP (Model Context Protocol), qui standardise la façon de brancher des outils sur un agent.
- Essaie un framework une fois que tu as compris la boucle : LangGraph, OpenAI Agents SDK, Claude Agent SDK, Google ADK.

Questions ou idées : écris-moi sur Instagram [@aymane.ai_](https://instagram.com/aymane.ai_), où j’explique l’IA en darija.
