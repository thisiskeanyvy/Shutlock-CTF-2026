# speedcoding

- Catégorie : Programmation
- Difficulté : 500 points dans l'état du challenge
- Flag : `SHLK{F4812r851Nx9MzK7}`

## Démarche

La documentation disponible décrit un mini Fortran90 Lite. Le solve implémente un interpréteur supportant déclarations entières, affectations, `if/else`, boucles `do`, fonctions et une sémantique spéciale où `print` devient le retour attendu.

La documentation précise que les tests publics sont indicatifs et que la validation lance des tests avec des valeurs différentes. La soumission attendue envoie le programme au endpoint `/submit` en JSON :

```json
{"code": "..."}
```

Une fois l'interpréteur suffisamment fidèle à la sémantique Fortran-lite du challenge, la validation renvoie le flag :

```text
SHLK{F4812r851Nx9MzK7}
```

## Commandes et scripts pertinents

- `../scripts/speedcoding/documentation.md`
- `../scripts/speedcoding/challenge.py`
- [`scripts/speedcoding/documentation.md`](https://github.com/thisiskeanyvy/Shutlock-CTF-2026/blob/main/scripts/speedcoding/documentation.md)
- [`scripts/speedcoding/challenge.py`](https://github.com/thisiskeanyvy/Shutlock-CTF-2026/blob/main/scripts/speedcoding/challenge.py)

## Conclusion

Documentation source présente et flag exact publié.
