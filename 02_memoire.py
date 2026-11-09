"""
ÉTAPE 2 : la "mémoire" d'un chatbot.

Le LLM ne se souvient de RIEN entre deux appels.
ChatGPT donne l'impression de se souvenir parce qu'il te renvoie TOUTE
la conversation à chaque message. La mémoire, c'est juste une liste Python.

Lance :  python 02_memoire.py
"""

from rich import print
from rich.rule import Rule

from llm import get_client

client, modele = get_client()


def demander(messages):
    r = client.chat.completions.create(model=modele, messages=messages)
    return r.choices[0].message.content


# --- Essai 1 : chaque appel est indépendant ---------------------------------
print(Rule("Sans mémoire : deux appels séparés"))
print("[cyan]Toi :[/] Salut, je m'appelle Yasmine")
print("[green]LLM :[/]", demander([{"role": "user", "content": "Salut, je m'appelle Yasmine"}]))
print("[cyan]Toi :[/] Comment je m'appelle ?")
print("[green]LLM :[/]", demander([{"role": "user", "content": "Comment je m'appelle ?"}]))

# --- Essai 2 : on renvoie l'historique ----------------------------------------
print(Rule("Avec mémoire : on renvoie tout l'historique"))
historique = [{"role": "user", "content": "Salut, je m'appelle Yasmine"}]
reponse = demander(historique)
historique.append({"role": "assistant", "content": reponse})
print("[cyan]Toi :[/] Salut, je m'appelle Yasmine")
print("[green]LLM :[/]", reponse)

historique.append({"role": "user", "content": "Comment je m'appelle ?"})
print("[cyan]Toi :[/] Comment je m'appelle ?")
print("[green]LLM :[/]", demander(historique))

print(f"\n[dim]Ce qu'on a vraiment envoyé au LLM au 2e message : {len(historique)} messages.[/]")
