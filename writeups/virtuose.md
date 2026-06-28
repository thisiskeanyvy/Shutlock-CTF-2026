# Virtuose

- Catégorie : Forensic / ML
- Difficulté : Non précisée
- Flag : `SHLK{sp4ti4l_fr3qu3nci3s_4s_fun_4s_67!}`

## Démarche

Challenge combinant image et modèle machine learning. model.pkl contenait un MLPClassifier, un StandardScaler et une taille d'image 64. microfilms_board.png mesurait 1216x1024, soit une grille de 19x16 tuiles. En classifiant les tuiles ligne par ligne puis en convertissant les bits en ASCII, on obtenait le flag avec l'accolade finale à rétablir.

## Commandes et scripts pertinents

Aucun script public associé.

```bash
Aucun script final compact n'a été retrouvé pour publication.
```

## Conclusion

Il fallait reproduire le découpage et la normalisation utilisés à l'entraînement.
