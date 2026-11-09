# Cours : introduction aux LLM et aux agents

## Les tokens
Un LLM ne lit pas des mots mais des tokens : des morceaux de mots. "Bonjour" peut faire 1 token, un mot rare en fait plusieurs. Les modèles sont facturés et limités en tokens (fenêtre de contexte).

## Comment un LLM génère du texte
Le modèle reçoit une suite de tokens et calcule, pour chaque token possible, la probabilité qu'il vienne ensuite. Il en choisit un, l'ajoute au texte, et recommence. La température règle le hasard : basse = réponses stables, haute = réponses plus créatives.

## Entraînement
1. Pré-entraînement : le modèle lit une énorme quantité de textes et apprend à prédire le token suivant.
2. Fine-tuning : on l'entraîne sur des exemples de conversations pour qu'il suive des instructions.
3. RLHF : des humains notent les réponses, et le modèle apprend à préférer les meilleures.

## Limites
- Hallucinations : le modèle peut inventer des faits avec assurance.
- Pas de mémoire entre deux appels : l'application renvoie l'historique.
- Connaissances figées à la date de fin d'entraînement.
- Mauvais en calcul exact.

## Les agents
Un agent est un LLM qui peut appeler des outils (fonctions, API, code) et qui tourne en boucle : il réfléchit, agit avec un outil, observe le résultat, puis recommence jusqu'à finir la tâche. Le protocole MCP (Model Context Protocol) standardise la façon de brancher des outils sur un agent.

## RAG
Le RAG (Retrieval-Augmented Generation) consiste à chercher les passages pertinents dans des documents, puis à les donner au LLM avec la question. Le modèle répond alors à partir de sources, ce qui réduit les hallucinations.
