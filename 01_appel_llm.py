"""
ÉTAPE 1 : parler à un LLM.

Un LLM (Large Language Model) prend du texte et prédit la suite, mot par mot.
C'est tout. Il n'a pas internet, pas de mémoire, et il n'exécute rien.

Lance :  python 01_appel_llm.py
"""

from rich import print

from llm import get_client

client, modele = get_client()

question = "Explique en 3 phrases ce qu'est un agent IA, pour un étudiant de prépa."

reponse = client.chat.completions.create(
    model=modele,
    messages=[{"role": "user", "content": question}],
)

print(f"[bold cyan]Toi :[/] {question}\n")
print(f"[bold green]LLM :[/] {reponse.choices[0].message.content}")
