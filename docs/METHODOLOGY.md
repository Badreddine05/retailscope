# Méthode et contrats de calcul

## 1. Source et qualité

La source est le fichier `Online Retail.xlsx` du jeu UCI 352, DOI 10.24432/C5BW33. Le manifeste conserve l'URL, le SHA-256 de l'archive et du classeur, l'instant de génération et les comptes de transformation. Aucun jeu synthétique n'est ajouté.

La déduplication utilise toutes les valeurs de la ligne Excel, avant toute conversion. Une ligne répétée à l'identique est retirée. Ce choix peut retirer un achat répété légitime, car la source ne contient pas d'identifiant unique de ligne. Les lignes sans clé obligatoire, à prix non positif, à quantité nulle ou de format numérique illisible sont ensuite écartées et comptées. Sur la version livrée, seules les exclusions de doublons et de prix non positifs sont non nulles.

Les dates Excel sont décodées avec l'époque du 30 décembre 1899. Les heures servent à reconnaître les doublons exacts dans la source, puis l'entrepôt retient le jour. Les dates représentent les dates commerciales de la source ; aucune conversion de fuseau n'est inventée.

Les descriptions produit varient parfois pour un même code. Le libellé publié est le dernier libellé non vide rencontré dans l'ordre source. Le code reste la clé de regroupement. Les codes de frais ou ajustements ne sont pas supprimés par hypothèse.

## 2. Monnaie et transactions

Chaque prix est transformé en entier milli-GBP avec Decimal. Le montant vaut quantité × prix. Une quantité négative ou un numéro de facture préfixé `C` est un avoir ; son montant est forcé négatif. Les agrégations restent entières jusqu'à l'affichage.

| Indicateur | Définition |
| --- | --- |
| CA brut | Somme des montants d'achat positifs retenus |
| Avoirs | Valeur absolue des montants de crédit retenus |
| CA net | CA brut − avoirs |
| Commandes | Factures avec lignes d'achat positives, distinctes |
| Panier moyen | CA brut / commandes, non défini si aucune commande |
| Avoirs / ventes | Avoirs / CA brut, non défini si aucun achat positif |
| Unités positives | Somme des quantités sur les lignes d'achat positives |

Une commande est une facture, pas un panier de navigation. Les avoirs de la période peuvent correspondre à des ventes antérieures. Le ratio peut donc dépasser 100 % sur un périmètre étroit. Un code produit peut avoir un CA net négatif. Les ratios sans dénominateur sont affichés par un tiret, y compris lorsqu'un mois contient seulement des avoirs.

## 3. Segmentation RFM

Les factures positives avec client identifié sont regroupées dans le pays et la période sélectionnés. La récence est le nombre de jours entre le dernier achat et le lendemain de la fin d'observation : premier jour du mois suivant, plafonné au 10 décembre 2011. La fréquence est le nombre de factures positives distinctes. Le montant est le total positif acheté dans la période ; les crédits ne sont pas rattachés arbitrairement à ces achats.

Les règles sont appliquées dans cet ordre :

1. **À réactiver** : récence > 90 jours.
2. **Champions** : récence ≤ 60 jours, fréquence ≥ 3 et montant ≥ valeur du 75e percentile empirique des montants clients de la sélection.
3. **Fidèles** : fréquence ≥ 2.
4. **Nouveaux observés** : récence ≤ 30 jours et une seule commande.
5. **Occasionnels** : autres clients.

Le percentile est l'élément d'indice `floor((n-1)*0.75)` de la liste triée, sans interpolation. Les seuils sont pédagogiques et interprétables, pas des classes apprises ni une estimation de valeur vie client. Une période très courte change mécaniquement les segments : les filtres font partie de leur définition.

## 4. Cohortes et observation incomplète

Le premier mois observé est calculé sur tout l'historique disponible du pays sélectionné, avant application de la borne de début. Cette borne sélectionne les cohortes affichées. La borne de fin limite le suivi, au plus tard en novembre 2011. Décembre 2011 est exclu car il ne contient que neuf jours.

Le dénominateur reste le nombre de clients de la cohorte au premier mois. La cellule M+k indique la proportion de ces clients avec au moins une facture positive dans le mois k. Elle vaut 0 si le mois est observable sans achat, et `null` si le mois est futur ou incomplet. Le tableau affiche ce `null` avec un tiret et un fond hachuré. Il n'est jamais converti en zéro.

La cohorte de décembre 2010 mélange de vrais nouveaux clients et des clients déjà présents avant le début de la source : c'est une limite de troncature à gauche. Les retours non identifiés et les achats anonymes ne peuvent pas alimenter les trajectoires individuelles.

## 5. Contrats de cohérence

- La somme du CA net des produits, des pays et des mois doit égaler celle de l'entrepôt au milli-GBP.
- Les factures positives exportées doivent reproduire le nombre de commandes et le CA brut des agrégats.
- Chaque client identifié appartient à exactement un segment RFM.
- Une cohorte observable vaut 100 % à M+0, et ses ratios restent compris entre 0 et 1.
- Les données absentes ne deviennent pas une prévision ni un zéro de rétention.

Ces propriétés sont exercées par les tests automatisés sur les agrégats réels et par les tests unitaires du normaliseur. Les exports CSV protègent les cellules de texte susceptibles d'être interprétées comme formules par un tableur.
