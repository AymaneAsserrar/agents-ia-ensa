"""
Les outils que nos agents peuvent utiliser.

Ce sont des fonctions Python normales. Le LLM ne voit que leur description,
jamais leur code. Chaque outil renvoie du texte, que l'on redonne au LLM.
"""

import ast
import operator
import subprocess
import sys
from datetime import date
from pathlib import Path

RACINE = Path(__file__).parent.resolve()


# --- Calcul -----------------------------------------------------------------

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.FloorDiv: operator.floordiv,
}


def calculer(expression: str) -> str:
    """Calcule une expression sans utiliser eval() (plus sûr)."""

    def _eval(noeud):
        if isinstance(noeud, ast.Constant) and isinstance(noeud.value, (int, float)):
            return noeud.value
        if isinstance(noeud, ast.BinOp):
            return _OPS[type(noeud.op)](_eval(noeud.left), _eval(noeud.right))
        if isinstance(noeud, ast.UnaryOp):
            return _OPS[type(noeud.op)](_eval(noeud.operand))
        raise ValueError("expression non autorisée")

    try:
        expression = expression.replace("×", "*").replace("÷", "/").replace(" ", "")
        return str(_eval(ast.parse(expression, mode="eval").body))
    except Exception as e:
        return f"Erreur : {e}"


# --- Dates ------------------------------------------------------------------

def date_du_jour() -> str:
    return date.today().isoformat()


def jours_entre(date1: str, date2: str) -> str:
    try:
        return str((date.fromisoformat(date2) - date.fromisoformat(date1)).days)
    except ValueError as e:
        return f"Erreur : {e} (format attendu AAAA-MM-JJ)"


# --- Fichiers (limités au dossier du projet) ----------------------------------

def _chemin_sur(chemin: str) -> Path:
    p = (RACINE / chemin).resolve()
    if RACINE not in p.parents and p != RACINE:
        raise PermissionError("accès refusé en dehors du dossier du projet")
    return p


def lister_fichiers(dossier: str = ".") -> str:
    try:
        p = _chemin_sur(dossier)
        fichiers = sorted(f.name + ("/" if f.is_dir() else "") for f in p.iterdir() if not f.name.startswith("."))
        return "\n".join(fichiers) or "(dossier vide)"
    except Exception as e:
        return f"Erreur : {e}"


def lire_fichier(chemin: str) -> str:
    try:
        texte = _chemin_sur(chemin).read_text(encoding="utf-8")
        return texte[:8000] + ("\n...(tronqué)" if len(texte) > 8000 else "")
    except Exception as e:
        return f"Erreur : {e}"


def ecrire_fichier(chemin: str, contenu: str) -> str:
    try:
        p = _chemin_sur(chemin)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(contenu, encoding="utf-8")
        return f"Fichier écrit : {chemin} ({len(contenu)} caractères)"
    except Exception as e:
        return f"Erreur : {e}"


# --- Exécution de code ------------------------------------------------------

def executer_python(code: str) -> str:
    """Exécute du code Python dans le dossier du projet (20 s max).

    Attention : l'agent écrit ce code lui-même. Dans 05_agent_etudiant.py,
    on demande TOUJOURS la permission à l'humain avant de lancer cet outil.
    """
    (RACINE / "sortie").mkdir(exist_ok=True)
    try:
        r = subprocess.run(
            [sys.executable, "-c", code], cwd=RACINE, capture_output=True, text=True, timeout=20
        )
        sortie = (r.stdout + ("\nERREUR:\n" + r.stderr if r.returncode else "")).strip()
        return sortie[:4000] or "(aucune sortie)"
    except subprocess.TimeoutExpired:
        return "Erreur : le code a pris plus de 20 secondes."
