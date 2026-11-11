# Reproduire les mesures dans Power BI

Le pipeline produit cinq CSV dans `data/warehouse/exports/`. Importer chaque table dans Power BI Desktop, avec l'encodage UTF-8 et la virgule comme séparateur. Les types attendus sont : date pour `dim_date[date]` et `fact_line[date]`, entier pour les quantités/montants, texte pour les codes et identifiants.

Créer les relations un-à-plusieurs suivantes, avec filtre à sens unique depuis la dimension :

- `dim_date[date]` → `fact_line[date]`
- `dim_product[stock_code]` → `fact_line[stock_code]`
- `dim_country[country]` → `fact_line[country]`
- `dim_customer[customer]` → `fact_line[customer]`

Les clients manquants de la table de faits restent vides. Ils ne doivent pas être supprimés lors de l'import ou du filtrage commercial. La dimension date contient les jours présents dans les transactions ; créer une table calendrier continue séparée pour les fonctions DAX de time intelligence, puis la marquer comme table de dates.

```dax
CA brut GBP =
DIVIDE(
    CALCULATE(SUM(fact_line[amount_milli]), fact_line[is_credit] = 0),
    1000,
    0
)

Avoirs GBP =
DIVIDE(
    -CALCULATE(SUM(fact_line[amount_milli]), fact_line[is_credit] = 1),
    1000,
    0
)

CA net GBP = DIVIDE(SUM(fact_line[amount_milli]), 1000, 0)

Commandes =
CALCULATE(DISTINCTCOUNT(fact_line[invoice]), fact_line[is_credit] = 0)

Panier moyen GBP = DIVIDE([CA brut GBP], [Commandes])

Ratio avoirs ventes = DIVIDE([Avoirs GBP], [CA brut GBP])

Clients identifiés =
CALCULATE(
    DISTINCTCOUNT(fact_line[customer]),
    fact_line[is_credit] = 0,
    fact_line[customer] <> BLANK()
)
```

Formater les montants en GBP et le ratio en pourcentage. Pour réconcilier précisément le total complet, conserver trois décimales : **9 748 131,074 GBP**. Le défaut visuel de l'application arrondit seulement l'affichage.

Pour reproduire l'écran d'ouverture, filtrer décembre 2010 à novembre 2011. Un graphique de courbe utilise `dim_date[month]` et `[CA net GBP]` ; un tableau produit utilise la description, le code et cette même mesure. Les cohortes et segments de l'application sont définis dans `METHODOLOGY.md` : ils nécessitent une table d'achats clients ou des calculs supplémentaires, pas seulement ces mesures de base.

Ce document et les exports constituent un point de départ reproductible. Aucun rapport `.pbix` n'a été produit ou validé dans Power BI Desktop dans ce dépôt.
