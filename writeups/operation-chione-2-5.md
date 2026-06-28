# Opération Chioné - 2/5

- Catégorie : OSINT
- Difficulté : 500 points
- Flag : `Non repris ici`

## Démarche

Cette étape demandait de trouver le lieu et l'heure de la transaction de Léna Kingsley, avec un format de type `SHLK{12.858S,28.294E_15h30}`.

Les pistes documentées sont :

- l'écosystème fictif `kriosdynamics.site`, `lk-blog.site`, `vaultdrop.site`, `eumelopos.shutlock.fr` et `search.shutlock.fr` ;
- une piste MiShell/accessCode pour accéder au profil détaillé de Lena ;
- un Google Doc Eumelopos avec une section courrier tronquée autour de `DPO - Place` ;
- une image calendrier/horloge contenant notamment `TLEN`, `AYS`, `RPS`, `WS`, `ANS`, des marques sur les jours `10`, `19`, `20`, `25`, `26` et l'indication `PERMANENT` ;
- une piste Instagram indiquant une montre autour de `15h30` et un lieu probable autour de `La Belle Tortue`, Silhouette Island, Seychelles.

Deux candidats importants ont été rejetés ou non validés :

```text
SHLK{4.46579S,55.22673E_15h30}
SHLK{4.486S,55.253E_15h30}
```

Le second candidat corrige les coordonnées vers La Belle Tortue (`4.486S,55.253E`), mais il n'est pas validé. Il ne doit donc pas être publié comme flag.

## Commandes et scripts pertinents

- `../scripts/chione/calendar_decode.py`
- `../scripts/chione/calendar_decode2.py`

Ces helpers servent à explorer la grille calendrier, pas à produire un flag validé.

## Conclusion

Aucun flag exact validé n'est publié ici. La meilleure piste reste La Belle Tortue / 15h30, mais elle est explicitement non résolue.
