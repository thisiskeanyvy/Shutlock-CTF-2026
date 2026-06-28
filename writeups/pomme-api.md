# Pomme de reinette et pomme d'API

- Catégorie : Web
- Difficulté : Non précisée
- Flag : `SHLK{R4C3_C0nd1t10n_1S_CO0l}`

## Démarche

API GraphQL protégée par un filtrage naïf. Le WAF bloquait __type et __schema lorsqu'ils apparaissaient en premier champ, mais l'introspection restait possible après un champ autorisé. Cela révélait getClassifiedIntel. Une mutation promoteAgent sans argument ouvrait ensuite une courte fenêtre de privilège Handler, exploitable par course entre promotion et requête sensible.

## Commandes et scripts pertinents

- `../scripts/pomme_solve.py`

```bash
python3 scripts/pomme_solve.py
```

## Conclusion

L'introspection ne doit pas être filtrée par recherche de chaîne et les promotions temporaires doivent être atomiques.
