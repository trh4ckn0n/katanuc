# katanuc trhacknon FuzzScanner
katanuc by trhacknon .Just a script for use katana and nuclei for find urls with query params usable with nuclei

🛠️ Outil de scan automatique combinant Katana et Nuclei, ciblant les paramètres vulnérables à l'aide de templates de fuzzing.

## Fonctionnalités

- Scan via Katana
- Fuzzing via Nuclei
- Choix interactif du fichier de domaines (.txt)
- Affichage coloré des vulnérabilités (info, low, medium, high, critical)
- Export des résultats dans output/nuclei/
- Multithreadé (via ThreadPoolExecutor)

## Installation

```bash
https://github.com/trh4ckn0n/katanuc
```

1. Installer les dépendances Python :

```bash
pip install -r requirements.txt
```

2. Installer Katana et Nuclei :

```bash
GO111MODULE=on go install -v github.com/projectdiscovery/katana/cmd/katana@latest
GO111MODULE=on go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
```

Ajouter ensuite $GOPATH/bin à ton PATH :

```
export PATH=$PATH:$(go env GOPATH)/bin
```

3. Télécharger les templates fuzzing de Nuclei :

```bash
git clone https://github.com/projectdiscovery/fuzzing-templates ~/nuclei-templates-fuzzing
```

> Adapter le chemin dans la variable TEMPLATES_PATH si besoin.

## Utilisation

```bash
python fuzzscanner.py
```

- Choisir un fichier .txt contenant les domaines (ex: list1.txt)
- Choisir le nombre de threads
- L’outil scanne avec Katana → filtre les URL avec paramètres → exécute Nuclei
- Résultats affichés dans la console et sauvegardés dans output/nuclei/

## Structure

.
├── output/
│   ├── katana/
│   └── nuclei/
├── fuzzscanner.py
├── requirements.txt
└── README.md
