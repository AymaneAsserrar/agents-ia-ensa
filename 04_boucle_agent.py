"""
ÉTAPE 4 : la boucle d'agent.

Un agent = un LLM + des outils + une BOUCLE.

    tant que le LLM demande des outils :
        on exécute les outils
        on lui renvoie les résultats
    quand il ne demande plus rien -> c'est sa réponse finale

Ici, l'agent a besoin de DEUX outils, l'un après l'autre : il doit d'abord
connaître la date du jour avant de pouvoir compter les jours. Personne ne lui
dit dans quel ordre faire les choses : il décide seul.

Lance :  python 04_boucle_agent.py
"""

import json

from rich import print

from llm import get_client, message_vers_dict
from outils import date_du_jour, jours_entre

client, modele = get_client()


def outil(nom, description, **params):
    """Petit raccourci pour décrire un outil au format attendu par l'API."""
    return {
        "type": "function",
        "function": {
            "name": nom,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {p: {"type": "string", "description": d} for p, d in params.items()},
                "required": list(params),
            },
        },
    }


OUTILS = [
    outil("date_du_jour", "Renvoie la date d'aujourd'hui au format AAAA-MM-JJ"),
    outil("jours_entre", "Nombre de jours entre deux dates", date1="AAAA-MM-JJ", date2="AAAA-MM-JJ"),
]
FONCTIONS = {"date_du_jour": date_du_jour, "jours_entre": jours_entre}

question = "Combien de jours reste-t-il avant le 1er janvier 2027 ?"
messages = [{"role": "user", "content": question}]
print(f"[bold cyan]Toi :[/] {question}\n")

for tour in range(1, 11):  # sécurité : 10 tours maximum
    reponse = client.chat.completions.create(model=modele, messages=messages, tools=OUTILS)
    msg = reponse.choices[0].message
    messages.append(message_vers_dict(msg))

    if not msg.tool_calls:  # plus d'outil demandé : c'est la réponse finale
        print(f"[bold green]Agent (tour {tour}) :[/] {msg.content}")
        break

    for appel in msg.tool_calls:
        args = json.loads(appel.function.arguments or "{}")
        resultat = FONCTIONS[appel.function.name](**args)
        print(f"[yellow]Tour {tour} 🔧 {appel.function.name}({args})[/] -> [magenta]{resultat}[/]")
        messages.append({"role": "tool", "tool_call_id": appel.id, "content": resultat})
