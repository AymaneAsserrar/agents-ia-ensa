"""
ÉTAPE 3 : donner un outil au LLM (function calling).

Les LLM sont mauvais en calcul : ils prédisent des chiffres, ils ne calculent pas.
Solution : on lui décrit un outil "calculer". Le LLM ne l'exécute pas lui-même,
il nous DEMANDE de l'appeler. C'est NOTRE code Python qui fait le calcul,
puis on lui renvoie le résultat.

Lance :  python 03_premier_outil.py
"""

import json

from rich import print

from llm import get_client, message_vers_dict
from outils import calculer

client, modele = get_client()

# 1. On décrit l'outil au LLM (nom, à quoi il sert, quels paramètres)
outils = [
    {
        "type": "function",
        "function": {
            "name": "calculer",
            "description": "Calcule une expression mathématique, ex: '12 * (3 + 4)'",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    }
]

question = "Combien font 48756 × 9321 ?"
messages = [{"role": "user", "content": question}]
print(f"[bold cyan]Toi :[/] {question}\n")

# 2. Premier appel : le LLM décide s'il a besoin de l'outil
reponse = client.chat.completions.create(model=modele, messages=messages, tools=outils)
msg = reponse.choices[0].message

if msg.tool_calls:
    appel = msg.tool_calls[0]
    args = json.loads(appel.function.arguments)
    print(f"[yellow]🔧 Le LLM demande :[/] {appel.function.name}({args})")

    # 3. C'est NOUS qui exécutons l'outil
    resultat = calculer(**args)
    print(f"[magenta]📦 Notre code renvoie :[/] {resultat}\n")

    # 4. On renvoie le résultat au LLM pour qu'il formule la réponse
    messages.append(message_vers_dict(msg))
    messages.append({"role": "tool", "tool_call_id": appel.id, "content": resultat})
    reponse = client.chat.completions.create(model=modele, messages=messages, tools=outils)
    msg = reponse.choices[0].message

print(f"[bold green]LLM :[/] {msg.content}")
