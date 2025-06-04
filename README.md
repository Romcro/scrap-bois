# goodforest Scraper

Un outil de scraping cross-plateforme pour collecter automatiquement les résultats Google et Google Scholar sur les scolytes, le prix du bois et les pathogènes du bois.

---

## Fonctionnalités

- **Interface graphique ** (Tkinter)
- **Scraping Google et Google Scholar**
- **Filtrage des résultats récents** (moins de 2 semaines)
- **Export des résultats en CSV sur le bureau**
- **Logs détaillés et progression visuelle**
- **Arrêt propre du processus**

---

## Prérequis

- **Python 3.8+**
- **pip**
- **Google Chrome installé**

---

## Installation

1. **Clone le dépôt :**
```

git clone https://github.com/ton-utilisateur/goodforest-scraper.git
cd goodforest-scraper

```

2. **Crée et active un environnement virtuel (optionnel mais recommandé) :**
```

python -m venv .venv
source .venv/bin/activate # Sur Linux/Mac

# .venv\Scripts\activate # Sur Windows

```

3. **Installe les dépendances :**
```

pip install selenium webdriver-manager

```

---

## Utilisation

1. **Lance l’application :**
```

python script.py

```

2. **Clique sur « Lancer la collecte » pour démarrer le scraping.**

3. **Les résultats sont sauvegardés sur le bureau sous forme de fichiers CSV.**

4. **Les logs s’affichent en temps réel dans la fenêtre.**

---

## Configuration

- **Modifie les requêtes dans la liste `protocol_steps` dans le code pour changer les sujets de recherche.**
- **Le mode headless est désactivé par défaut pour faciliter le débogage.**

---

## Fichiers générés

- **Fichiers CSV sur le bureau :**
- `GF_scolytes_YYYYMMDD_HHMM.csv`
- `GF_prix_bois_YYYYMMDD_HHMM.csv`
- `GF_pathogenes_YYYYMMDD_HHMM.csv`
- **Logs HTML (en cas de blocage Google) :**
- `last_page.html`
- `last_page_scholar.html`

---

## Dépannage

- **Si Google bloque l’accès :**
- Vérifie le fichier `last_page.html` pour voir si un CAPTCHA s’affiche.
- Désactive le mode headless dans le code pour voir ce qui se passe dans le navigateur.
- **Si aucun résultat n’est trouvé :**
- Vérifie que Google Chrome est bien installé.
- Mets à jour ChromeDriver avec `webdriver-manager`.

---

## Licence



---

## Auteur

**[Romuald CROCHAT]**

---

```
