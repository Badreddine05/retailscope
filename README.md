# RetailScope

Une application de Business Intelligence pour explorer les ventes, les clients et la fidélisation d'un commerce en ligne. Elle s'appuie sur les transactions réelles **UCI Online Retail**, avec un pipeline Python reproductible, un entrepôt SQLite en étoile et une interface React.

[Démo dans le portfolio](https://Badreddine05.github.io/retailscope/) · [Source des données](https://archive.ics.uci.edu/dataset/352/online+retail) · [Méthodologie](docs/METHODOLOGY.md) · [Préparation entretien](docs/INTERVIEW.md)

## Ce que l'on peut explorer

- **Activité** : chiffre d'affaires net, commandes, panier moyen, avoirs, évolution mensuelle et marchés principaux.
- **Clients** : couverture des identifiants, achats récurrents, segmentation RFM explicite et cohortes mensuelles avec périodes non observables laissées vides.
- **Catalogue** : recherche par référence ou description, tri, pagination et export CSV.
- **Méthode** : contrôles qualité, règles de calcul, source, licence et empreinte du fichier téléchargé.

Les filtres pays et mois s'appliquent aux indicateurs, graphiques, tableaux et exports. Les chiffres et graphiques s'animent lors des changements ; le réglage système de réduction des animations est respecté. L'application fonctionne sans compte, clé API ni service payant.

## Démarrer

Prérequis : Node.js 22 ou version ultérieure compatible avec Vite 7. Python 3.11+ est nécessaire uniquement pour reconstruire les données. Les agrégats sont déjà présents dans le dépôt.

```bash
npm ci
npm run dev
```

Ouvrir l'adresse locale affichée par Vite. Pour vérifier la version de production :

```bash
npm test
npm run build
npm run preview
```

Le dossier `dist/` est un site statique. La configuration `base: './'` permet de le servir sous `/retailscope/` dans le portfolio. Les chemins de données restent relatifs ; aucune requête ne part vers une API pendant l'exploration.

## Reconstruire les données

```bash
python pipeline/build.py
python -m unittest discover -s tests -p 'test_*.py'
npm test
```

Le premier appel télécharge l'archive officielle UCI d'environ 23 Mo. Le traitement XLSX, SQLite et les exports utilisent seulement la bibliothèque standard Python. Prévoir de l'espace pour l'archive, la base et les CSV (quelques centaines de Mo). Les exécutions suivantes réutilisent l'archive et vérifient son SHA-256 contre le manifeste. En cas de changement de source, inspecter le fichier avant d'utiliser `--refresh`.

Fichiers produits :

| Sortie | Usage |
| --- | --- |
| `data/raw/online-retail.zip` | Archive source, ignorée par Git |
| `data/warehouse/retailscope.sqlite` | Modèle étoile, ignoré par Git |
| `data/warehouse/exports/*.csv` | Tables complètes pour Power BI, ignorées par Git |
| `public/data/analytics.json` | Agrégats et factures positives pseudonymisées pour l'application |
| `public/data/manifest.json` | Provenance, empreintes, comptages et schéma des tableaux compacts |

Les montants sont calculés en **millièmes entiers de livre sterling** pour conserver les quelques prix à trois décimales de la source. La division par 1 000 intervient à l'affichage. Les clients sans identifiant sont conservés dans les totaux commerciaux et exclus des analyses individuelles.

## Résultats vérifiés sur la source

| Contrôle | Résultat |
| --- | ---: |
| Lignes originales | 541 909 |
| Doublons exacts retirés | 5 268 |
| Lignes à prix nul ou négatif exclues | 2 512 |
| Lignes retenues | 534 129 |
| Lignes retenues sans identifiant client | 132 565 |
| Factures d'achat distinctes | 19 960 |
| CA net sur toute la source | 9 748 131,074 GBP |

Ces chiffres décrivent le traitement et les données, pas un impact économique du projet. Le tableau de bord s'ouvre par défaut sur décembre 2010 à novembre 2011, soit les douze mois complets. Le dernier mois de la source s'arrête au 9 décembre 2011 ; on peut l'afficher dans les ventes, mais il est exclu des cohortes pour éviter de comparer un mois partiel à des mois complets.

## Architecture

```text
Archive UCI XLSX
    -> pipeline/build.py : lecture XML, contrôles, déduplication
    -> SQLite : fact_line + dimensions date, pays, produit, client
    -> agrégats JSON + exports CSV
    -> src/analytics.js : filtres, métriques, RFM et cohortes
    -> React + Recharts : exploration et exports
```

Le navigateur utilise des agrégats pays/mois/produit et les factures positives, pas les 534 129 lignes brutes. Le fichier JSON fait environ 4,3 Mo avant compression. Les calculs clients restent dans le navigateur ; les pseudonymes sont des identifiants de démonstration issus des IDs anonymes du jeu UCI, pas une garantie d'anonymisation cryptographique.

## Vérification et intégration continue

`npm test` contrôle la réconciliation exacte des montants, les comptes de factures, la cohérence des filtres entre vues, les cas vides, la partition RFM, le censurage des cohortes et l'échappement CSV. Les tests Python couvrent les conversions monétaires, les avoirs, les identifiants manquants et les valeurs invalides. Le workflow GitHub Actions exécute les deux suites puis construit l'application. Il utilise les agrégats versionnés et ne dépend pas d'un téléchargement externe à chaque commit.

Pour vérifier l'entrepôt après reconstruction, exécuter `sql/measures.sql` avec SQLite. Le `PRAGMA foreign_key_check` doit ne retourner aucune ligne.

```bash
docker build -t retailscope .
docker run --rm -p 8080:80 retailscope
```

Le Dockerfile est fourni pour un service statique Nginx. Son exécution dépend de la présence de Docker ; les contrôles de développement portent sur le pipeline Python et le build Node.

## Power BI

Les exports du modèle étoile et les mesures DAX sont documentés dans [docs/POWER_BI.md](docs/POWER_BI.md). Ils permettent de reconstruire un rapport avec les mêmes règles. Aucun fichier `.pbix` n'est livré ni présenté comme réalisé.

## Limites et attribution

Le jeu couvre un seul commerçant britannique en 2010–2011, avec de nombreux grossistes. Il ne fournit ni coûts, ni stocks, ni marge. Les avoirs ne sont pas reliés à leur achat d'origine ; le ratio avoirs/ventes n'est donc pas un taux de retours produits. Le premier achat observé n'est pas nécessairement la première acquisition réelle. Les segments RFM utilisent des seuils lisibles, sans modèle prédictif ni recommandation causale.

Données : **Chen, D. (2015). Online Retail. UCI Machine Learning Repository. DOI:10.24432/C5BW33**, sous [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Les agrégats sont une adaptation documentée. Code : [MIT](LICENSE). Autres composants : [THIRD_PARTY.md](THIRD_PARTY.md).

Projet de portfolio de Badreddine Channoufi, réalisé avec l'assistance d'un agent de développement. Les commits correspondent aux étapes réelles de réalisation et portent leurs dates réelles. Ce projet n'est pas une prestation pour l'entreprise du jeu de données.
