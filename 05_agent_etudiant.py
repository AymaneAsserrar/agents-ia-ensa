"""
ÉTAPE 5 : un vrai agent qui fait une vraie tâche.

L'agent peut : lister des fichiers, les lire, écrire des fichiers,
et ÉCRIRE PUIS EXÉCUTER SON PROPRE CODE PYTHON.
Avant d'exécuter du code, il demande la permission à l'humain (toi).

Lance :  python 05_agent_etudiant.py
Options : --mock  (sans internet, réponses pré-enregistrées)
          --oui   (accepte automatiquement l'exécution de code)
"""

import json
import sys
import time

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax

from llm import get_client, message_vers_dict
from outils import ecrire_fichier, executer_python, lire_fichier, lister_fichiers

console = Console()
client, modele = get_client()
AUTO_OUI = "--oui" in sys.argv

SYSTEME = """Tu es un agent assistant pour étudiants ingénieurs.
Tu travailles dans un dossier de projet avec des sous-dossiers data/ (entrées) et sortie/ (résultats).
Avant d'agir, annonce en une phrase courte ce que tu vas faire.
Pour tout calcul sur des données, écris un script Python et exécute-le plutôt que de calculer de tête.
Les graphiques matplotlib doivent utiliser matplotlib.use("Agg") et être enregistrés dans sortie/.
Réponds en français, de façon concise."""

TACHE_DEMO = (
    "Analyse les notes dans le dossier data. Calcule la moyenne de chaque étudiant, "
    "dis qui doit passer au rattrapage (moyenne < 12), fais un graphique, "
    "et écris un rapport en Markdown dans sortie/rapport.md."
)


def schema(nom, description, **params):
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
    schema("lister_fichiers", "Liste les fichiers d'un dossier du projet", dossier="ex: data"),
    schema("lire_fichier", "Lit le contenu d'un fichier texte", chemin="ex: data/notes.csv"),
    schema("ecrire_fichier", "Crée ou remplace un fichier", chemin="ex: sortie/rapport.md", contenu="texte du fichier"),
    schema("executer_python", "Exécute un script Python dans le dossier du projet et renvoie ce qu'il affiche", code="code Python complet"),
]
FONCTIONS = {
    "lister_fichiers": lister_fichiers,
    "lire_fichier": lire_fichier,
    "ecrire_fichier": ecrire_fichier,
    "executer_python": executer_python,
}


def autoriser_code(code):
    console.print(Panel(Syntax(code, "python", line_numbers=True), title="🐍 L'agent veut exécuter ce code", border_style="red"))
    if AUTO_OUI:
        console.print("[dim](--oui : accepté automatiquement)[/]")
        return True
    return console.input("[bold red]Tu autorises ? (o/n) [/]").strip().lower() in ("o", "oui", "y", "yes", "")


def lancer_agent(tache, max_tours=15):
    messages = [{"role": "system", "content": SYSTEME}, {"role": "user", "content": tache}]
    console.print(Panel(tache, title="🎯 Tâche", border_style="cyan"))

    for tour in range(1, max_tours + 1):
        with console.status(f"[bold]L'agent réfléchit… (tour {tour})"):
            reponse = client.chat.completions.create(model=modele, messages=messages, tools=OUTILS)
            if modele == "mock":
                time.sleep(0.8)  # pour que le public ait le temps de suivre
        msg = reponse.choices[0].message
        messages.append(message_vers_dict(msg))

        if not msg.tool_calls:
            console.print(Panel(Markdown(msg.content or ""), title=f"✅ Réponse finale (en {tour} tours)", border_style="green"))
            return

        if msg.content:
            console.print(f"🧠 [italic]{msg.content}[/]")

        for appel in msg.tool_calls:
            nom = appel.function.name
            args = json.loads(appel.function.arguments or "{}")

            if nom == "executer_python" and not autoriser_code(args.get("code", "")):
                resultat = "L'utilisateur a refusé l'exécution de ce code."
            elif nom in FONCTIONS:
                apercu = {k: (v[:60] + "…" if isinstance(v, str) and len(v) > 60 else v) for k, v in args.items()}
                console.print(f"🔧 [yellow]{nom}[/]({apercu})")
                resultat = FONCTIONS[nom](**args)
            else:
                resultat = f"Outil inconnu : {nom}"

            court = resultat if len(resultat) < 400 else resultat[:400] + "\n…"
            console.print(Panel(court, title=f"📦 Résultat de {nom}", border_style="magenta", expand=False))
            messages.append({"role": "tool", "tool_call_id": appel.id, "content": resultat})

    console.print("[red]Nombre maximum de tours atteint.[/]")


if __name__ == "__main__":
    console.print(Panel.fit(f"Agent étudiant 🤖  ·  modèle : [bold]{modele}[/]", border_style="blue"))
    console.print("Idées : [dim]« Fais une fiche de révision de data/cours_ia.md »  ·  « Combien d'étudiants ont plus de 15 en maths ? »[/]")
    while True:
        tache = console.input("\n[bold cyan]Tâche[/] (Entrée = démo des notes, q = quitter) : ").strip()
        if tache.lower() in ("q", "quit", "exit"):
            break
        lancer_agent(tache or TACHE_DEMO)
        if modele == "mock" or not sys.stdin.isatty():
            break
