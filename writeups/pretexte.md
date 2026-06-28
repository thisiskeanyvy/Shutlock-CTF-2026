# Pretexte

- Catégorie : Reverse
- Difficulté : Non précisée
- Flag : `SHLK{c0n5TrucTor-oVer_h3RriNg}`

## Démarche

Challenge reverse ARM64 avec faux chemin de succès. Le binaire affichait nope. reverse harder même quand l'analyse avançait. Le solve reconstruit le JIT natif et corrige la compréhension de la fonction clé : x0 pointe vers un buffer local, x1 vers un curseur du buffer principal. Deux offsets utilisent une table XOR du buffer de référence sur les données principales. La donnée décisive est le mot de passe attendu à l'offset +0xb0.

## Commandes et scripts pertinents

- `../scripts/pretexte_solve.py`

```bash
python3 scripts/pretexte_solve.py
```

## Conclusion

La sortie affichée était trompeuse ; il fallait suivre la donnée vérifiée par le checkeur.
