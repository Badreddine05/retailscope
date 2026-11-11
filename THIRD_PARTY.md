# Sources et licences tierces

Le code original du projet est distribué sous licence MIT. Les données ne changent pas de licence du fait de leur présence dans ce dépôt.

Les textes intégraux des licences et attributions des dépendances réellement incluses dans le bundle de production sont reproduits dans [public/THIRD_PARTY_NOTICES.txt](public/THIRD_PARTY_NOTICES.txt). Ce fichier est également distribué à la racine du site compilé. L'inventaire repose sur les modules du build Vite et les polices locales ; les outils de compilation et les paquets contenant seulement des déclarations TypeScript en sont exclus.

- **Données** : Chen, D. (2015). *Online Retail*. UCI Machine Learning Repository. DOI : [10.24432/C5BW33](https://doi.org/10.24432/C5BW33). Source : [UCI, jeu 352](https://archive.ics.uci.edu/dataset/352/online+retail). Licence : [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Les fichiers `public/data/analytics.json` et `manifest.json` sont des adaptations : déduplication, exclusion documentée de prix, pseudonymisation et agrégation. L'attribution est conservée dans l'application.
- **React / React DOM** : MIT. **Vite** et **@vitejs/plugin-react** : MIT. **Recharts** : MIT. **Lucide** : ISC. Versions résolues et dépendances transitives dans `package-lock.json` ; leurs notices restent dans les paquets installés.
- **Animations** : les snippets d'accordéon et de chiffres de `src/transitions.css` proviennent des instructions locales [Transitions.dev](https://transitions.dev), intégrés selon la procédure d'installation fournie. Cette mention est une attribution ; aucune propriété exclusive de ces snippets n'est revendiquée.
- **Polices** : Newsreader (variable), IBM Plex Sans (variable) et IBM Plex Mono (graisses 400 et 500), sous SIL Open Font License 1.1. Les fichiers WOFF2 sont versionnés dans `src/fonts/` et inclus dans le build ; les textes de licence sont distribués dans `public/licenses/` et repris dans `public/THIRD_PARTY_NOTICES.txt`. Aucune police n'est chargée depuis un CDN.

Le code et la documentation ont été produits avec l'assistance d'un agent de développement. Les commits portent leurs dates réelles. Le projet est une étude de portfolio, pas une mission pour le commerçant du jeu de données.
