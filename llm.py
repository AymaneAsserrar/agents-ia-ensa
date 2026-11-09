"""
Connexion au LLM.

On utilise le SDK `openai` parce que presque tous les fournisseurs parlent ce "langage" :
Gemini (gratuit), Groq, Ollama (en local sur ton PC), OpenAI...
Tu changes de fournisseur en modifiant juste le fichier .env.

Si aucune clé n'est configurée (ou avec --mock), on passe en MODE DÉMO :
un faux LLM qui rejoue des réponses écrites à l'avance. Pratique si internet lâche en plein live.
"""

import json
import os
import re
import sys
import uuid
from datetime import date

from dotenv import load_dotenv

load_dotenv()

FOURNISSEURS = {
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "cle": "GEMINI_API_KEY",
        "modele": "gemini-3.8-flash",
    },
    "groq": {"base_url": "https://api.groq.com/openai/v1", "cle": "GROQ_API_KEY", "modele": None},
    "ollama": {"base_url": "http://localhost:11434/v1", "cle": None, "modele": None},
    "openai": {"base_url": None, "cle": "OPENAI_API_KEY", "modele": None},
}


def get_client():
    """Renvoie (client, nom_du_modele). Bascule en mode démo si besoin."""
    fournisseur = os.getenv("PROVIDER", "gemini").lower()
    conf = FOURNISSEURS.get(fournisseur)
    if conf is None:
        sys.exit(f"PROVIDER inconnu : {fournisseur}. Choix : {', '.join(FOURNISSEURS)}")

    cle = os.getenv(conf["cle"]) if conf["cle"] else "ollama"
    if "--mock" in sys.argv or os.getenv("MOCK") == "1" or not cle:
        if not cle and "--mock" not in sys.argv:
            print("⚠️  Pas de clé API trouvée dans .env : passage en MODE DÉMO (réponses pré-enregistrées).\n")
        return MockClient(), "mock"

    from openai import OpenAI

    modele = os.getenv("MODEL") or conf["modele"]
    if not modele:
        sys.exit(f"Ajoute MODEL=... dans ton .env pour le fournisseur {fournisseur}.")
    return OpenAI(api_key=cle, base_url=conf["base_url"]), modele


def message_vers_dict(msg):
    """Transforme la réponse du LLM en dict qu'on peut remettre dans l'historique.

    On garde les tool_calls tels quels (model_dump) : Gemini y ajoute une
    "thought signature" qu'il faut lui renvoyer, sinon il refuse la suite.
    """
    d = {"role": "assistant", "content": msg.content or ""}
    if msg.tool_calls:
        d["tool_calls"] = []
        for tc in msg.tool_calls:
            tc_dict = tc.model_dump(exclude_none=True) if hasattr(tc, "model_dump") else tc
            if not tc_dict.get("id"):
                tc_dict["id"] = "call_" + uuid.uuid4().hex[:8]
                tc.id = tc_dict["id"]
            d["tool_calls"].append(tc_dict)
    return d


# ---------------------------------------------------------------------------
# MODE DÉMO : un faux LLM qui imite les réponses du vrai, sans internet.
# (Tu n'as pas besoin de lire cette partie pendant le talk.)
# ---------------------------------------------------------------------------


class _Obj:
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def model_dump(self, exclude_none=False):
        out = {}
        for k, v in self.__dict__.items():
            out[k] = v.model_dump() if isinstance(v, _Obj) else v
        return out


def _appel_outil(nom, **args):
    return _Obj(
        id="call_" + uuid.uuid4().hex[:8],
        type="function",
        function=_Obj(name=nom, arguments=json.dumps(args, ensure_ascii=False)),
    )


def _reponse(content=None, tool_calls=None):
    msg = _Obj(content=content, tool_calls=tool_calls or None)
    return _Obj(choices=[_Obj(message=msg, finish_reason="tool_calls" if tool_calls else "stop")])


CODE_ANALYSE = '''import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

with open("data/notes.csv", encoding="utf-8") as f:
    lignes = list(csv.DictReader(f))

matieres = [c for c in lignes[0] if c != "etudiant"]
resultats = []
for l in lignes:
    moy = sum(float(l[m]) for m in matieres) / len(matieres)
    resultats.append((l["etudiant"], round(moy, 2)))
resultats.sort(key=lambda r: r[1], reverse=True)

for nom, moy in resultats:
    statut = "Validé" if moy >= 12 else "Rattrapage"
    print(f"{nom};{moy};{statut}")

noms = [r[0] for r in resultats]
moys = [r[1] for r in resultats]
couleurs = ["#2e7d32" if m >= 12 else "#c62828" for m in moys]
plt.figure(figsize=(8, 4))
plt.bar(noms, moys, color=couleurs)
plt.axhline(12, linestyle="--", color="gray")
plt.title("Moyenne par étudiant (seuil de validation : 12)")
plt.ylim(0, 20)
plt.tight_layout()
plt.savefig("sortie/moyennes.png")
print("GRAPHIQUE: sortie/moyennes.png")
'''


class MockClient:
    """Imite client.chat.completions.create(...) du SDK openai."""

    def __init__(self):
        self.chat = _Obj(completions=_Obj(create=self._create))

    def _create(self, model=None, messages=None, tools=None, **kw):
        user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
        derniere = user_msgs[-1].lower() if user_msgs else ""
        resultats = [m["content"] for m in messages if m.get("role") == "tool"]
        outils = {t["function"]["name"] for t in (tools or [])}

        # 02 - mémoire : retrouver un prénom donné plus tôt dans la conversation
        if "comment je m'appelle" in derniere:
            tout = " ".join(user_msgs)
            m = re.search(r"je m'appelle (\w+)", tout, re.I)
            if m:
                return _reponse(f"Tu t'appelles {m.group(1)} 😊")
            return _reponse("Je ne sais pas, tu ne me l'as pas dit. Je n'ai aucun souvenir des messages précédents.")
        if "je m'appelle" in derniere:
            m = re.search(r"je m'appelle (\w+)", derniere, re.I)
            return _reponse(f"Enchanté {m.group(1).capitalize()} ! Comment je peux t'aider ?")

        # 05 - l'agent étudiant
        if "lire_fichier" in outils:
            return self._agent_etudiant(derniere, resultats)

        # 04 - boucle agent avec dates
        if "date_du_jour" in outils:
            if len(resultats) == 0:
                return _reponse(tool_calls=[_appel_outil("date_du_jour")])
            if len(resultats) == 1:
                return _reponse(tool_calls=[_appel_outil("jours_entre", date1=resultats[0], date2="2027-01-01")])
            return _reponse(f"Nous sommes le {resultats[0]}. Il reste {resultats[1]} jours avant le 1er janvier 2027.")

        # 03 - un seul outil : la calculatrice
        if "calculer" in outils:
            if not resultats:
                return _reponse(tool_calls=[_appel_outil("calculer", expression="48756 * 9321")])
            return _reponse(f"48 756 × 9 321 = {int(float(resultats[0])):,}".replace(",", " "))

        # 01 - appel simple
        if "agent" in derniere:
            return _reponse(
                "Un agent IA, c'est un LLM qui ne se contente pas de répondre : il peut utiliser des outils "
                "(lire un fichier, chercher sur le web, exécuter du code), observer le résultat, puis décider "
                "de la prochaine étape, en boucle, jusqu'à finir la tâche."
            )
        return _reponse("(mode démo) Je suis un faux LLM. Configure une clé API dans .env pour discuter vraiment !")

    def _agent_etudiant(self, tache, resultats):
        etape = len(resultats)
        if etape == 0:
            return _reponse("Je commence par regarder quels fichiers sont disponibles.", [_appel_outil("lister_fichiers", dossier="data")])
        if etape == 1:
            return _reponse("Il y a un fichier de notes, je le lis.", [_appel_outil("lire_fichier", chemin="data/notes.csv")])
        if etape == 2:
            return _reponse(
                "J'ai les notes. Je vais écrire un petit script Python pour calculer les moyennes et faire un graphique.",
                [_appel_outil("executer_python", code=CODE_ANALYSE)],
            )
        if etape == 3:
            sortie = resultats[2]
            lignes = [l.split(";") for l in sortie.splitlines() if l.count(";") == 2]
            if not lignes:
                return _reponse("Le script n'a rien donné (exécution refusée ?). Je m'arrête là.")
            tableau = "\n".join(f"| {n} | {m} | {s} |" for n, m, s in lignes)
            rattrapage = [n for n, _, s in lignes if s == "Rattrapage"]
            rapport = (
                "# Rapport des moyennes\n\n"
                f"Major de promo : **{lignes[0][0]}** avec {lignes[0][1]}/20.\n\n"
                "| Étudiant | Moyenne | Statut |\n|---|---|---|\n"
                f"{tableau}\n\n"
                f"Étudiants en rattrapage : {', '.join(rattrapage) if rattrapage else 'aucun'}.\n\n"
                "![Moyennes](moyennes.png)\n"
            )
            return _reponse("J'écris le rapport final.", [_appel_outil("ecrire_fichier", chemin="sortie/rapport.md", contenu=rapport)])
        return _reponse(
            "C'est fait ✅ J'ai lu les notes, calculé les moyennes avec Python, généré un graphique "
            "(sortie/moyennes.png) et écrit le rapport dans sortie/rapport.md."
        )
