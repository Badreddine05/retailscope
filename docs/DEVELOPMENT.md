# Développer et reconstruire RetailScope

## Application

Il faut Node.js 22.12 ou plus récent, compatible avec Vite 7. Les agrégats sont déjà dans le dépôt.

```sh
npm ci
npm run dev
```

Vite affiche l'adresse locale. Pour vérifier la version de production :

```sh
npm test
npm run build
npm run preview
```

`dist/` est un site statique. La configuration `base: './'` permet de le servir sous `/retailscope/` dans le portfolio ; les chemins de données restent relatifs, et aucune requête ne part vers une API pendant l'exploration. Arrêter le serveur Vite avant un `npm ci` : sous Windows, il verrouille `esbuild.exe`.

Une image Docker sert le site avec Nginx :

```sh
docker build -t retailscope .
docker run --rm -p 8080:80 retailscope
```

## Données

Le pipeline lit le fichier XLSX officiel avec la seule bibliothèque standard de Python 3.11 ou plus récent. Le premier lancement télécharge l'archive UCI (environ 23 Mo) ; les suivants la réutilisent après avoir vérifié son SHA-256 contre le manifeste. Prévoir quelques centaines de Mo pour l'archive, la base et les CSV. En cas de changement de source, inspecter le fichier avant d'utiliser `--refresh`.

```sh
python pipeline/build.py
python -m unittest discover -s tests -p "test_*.py"
npm test
```

| Sortie | Usage |
| --- | --- |
| `data/raw/online-retail.zip` | Archive source, non versionnée |
| `data/warehouse/retailscope.sqlite` | Modèle en étoile, non versionné |
| `data/warehouse/exports/*.csv` | Tables complètes pour Power BI, non versionnées |
| `public/data/analytics.json` | Agrégats et factures d'achat pseudonymisées pour l'application |
| `public/data/manifest.json` | Provenance, empreintes, comptages et schéma des tableaux compacts |

Les montants sont calculés en millièmes de livre, sous forme d'entiers, pour garder exacts les quelques prix à trois décimales de la source ; la division par 1 000 n'intervient qu'à l'affichage. Les lignes sans identifiant client restent dans les totaux commerciaux et sortent des analyses par client. Le navigateur reçoit des agrégats par pays, mois et produit et les factures d'achat, pas les 534 129 lignes brutes (environ 4,3 Mo de JSON avant compression).

| Contrôle | Résultat |
| --- | ---: |
| Lignes originales | 541 909 |
| Doublons exacts retirés | 5 268 |
| Lignes à prix nul ou négatif exclues | 2 512 |
| Lignes retenues | 534 129 |
| Lignes retenues sans identifiant client | 132 565 |
| Factures d'achat distinctes | 19 960 |
| Chiffre d'affaires net sur toute la source | 9 748 131,074 GBP |

## Organisation du code

| Chemin | Rôle |
| --- | --- |
| `pipeline/build.py` | Lecture XML du XLSX, contrôles, dédoublonnage, entrepôt et agrégats |
| `sql/schema.sql`, `sql/measures.sql` | Modèle en étoile (`fact_line`, dimensions date, pays, produit, client) et mesures |
| `src/analytics.js` | Filtres, indicateurs, RFM et cohortes |
| `src/main.jsx`, `src/style.css`, `src/tokens.css` | Interface React, graphiques Recharts et identité graphique |
| `tests/` | Tests JavaScript et Python |

## Tests

`npm test` contrôle la réconciliation exacte des montants, les comptes de factures, la cohérence des filtres entre vues, les cas vides, la partition RFM, la censure des cohortes et l'échappement CSV. Les tests Python couvrent les conversions monétaires, les avoirs, les identifiants manquants et les valeurs invalides. GitHub Actions exécute les deux suites puis construit l'application, avec les agrégats versionnés et sans téléchargement.

Après une reconstruction, `sql/measures.sql` vérifie l'entrepôt avec SQLite : `PRAGMA foreign_key_check` ne doit renvoyer aucune ligne.

Voir aussi la [méthodologie](METHODOLOGY.md) et le [guide Power BI](POWER_BI.md), qui décrit les exports du modèle en étoile et les mesures DAX ; aucun fichier `.pbix` n'est livré.
