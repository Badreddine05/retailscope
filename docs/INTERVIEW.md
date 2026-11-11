# Présenter RetailScope en entretien

## Le problème traité

Un responsable commercial veut comprendre l'évolution des ventes et savoir si les clients reviennent. Le projet transforme un classeur de transactions en un outil d'exploration : nettoyage, modèle de données, calcul des indicateurs et visualisation cohérente.

## Démonstration en cinq minutes

1. Ouvrir la vue d'ensemble. Expliquer pourquoi le défaut contient douze mois complets et pourquoi les livres sterling ne sont pas converties en euros.
2. Choisir la France puis quelques mois. Montrer que courbe, indicateurs, produits et export appliquent le même périmètre.
3. Passer aux clients. Distinguer clients identifiés et couverture des commandes ; expliquer les cinq segments, leurs seuils et leurs limites.
4. Lire une cohorte. Comparer une cellule zéro à une cellule non observable. Expliquer pourquoi « premier achat observé » ne signifie pas acquisition réelle.
5. Ouvrir la méthode. Montrer les comptages source, le SHA-256 et un test de réconciliation.

## Choix techniques à savoir expliquer

**Pourquoi un modèle étoile ?** Le grain de la table de faits est la ligne de facture retenue. Les dimensions regroupent les produits, dates, pays et clients. Cette séparation rend les agrégations et les exports Power BI lisibles.

**Pourquoi les entiers milli-GBP ?** Certains prix contiennent trois décimales. Les entiers évitent les dérives d'arrondi binaire dans les sommes ; la présentation en monnaie ne modifie pas les données sous-jacentes.

**Pourquoi une application statique ?** Le jeu historique est figé et modeste. Les agrégats réduisent le volume transmis, et un hébergement statique suffit à la démonstration. Avec des données privées ou des millions de clients, il faudrait une API avec contrôle d'accès, pagination et calculs serveur.

**Pourquoi pas un taux de retours ?** Les avoirs ne sont pas liés à leur facture d'origine. Diviser les montants de crédit d'une période par les ventes de cette même période est un ratio financier descriptif, pas une probabilité de retour d'un produit.

**Comment tester autrement que par une capture ?** Vérifier des invariants : même CA net entre faits et agrégats, même nombre de factures entre exports et vues, absence de client dans plusieurs segments, null pour les horizons non observables. Puis contrôler les interactions et la lisibilité dans le navigateur.

## Formulation possible pour un CV

> RetailScope, projet personnel de BI : pipeline Python et modèle étoile SQLite sur 541 909 transactions UCI ; application React avec filtres, cohortes de fidélisation, segmentation RFM, exports et tests de réconciliation.

Cette phrase décrit les livrables. Elle ne revendique pas de gain de revenu, d'expérience chez le commerçant ni d'ancienneté inventée. Les composants du projet ont été développés avec l'assistance d'un agent ; préparer une explication personnelle des choix, des limites et du code avant de le présenter.

## Prolongements possibles

Un suivi incrémental avec contrats de schéma, une version authentifiée pour données privées, ou une évaluation de segments sur plusieurs fenêtres seraient des évolutions distinctes. La prédiction de réachat demanderait une validation temporelle et des variables connues avant la date de prédiction ; elle n'est pas implémentée ici.
