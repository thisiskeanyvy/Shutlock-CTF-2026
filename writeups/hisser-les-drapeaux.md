# Hisser Les Drapeaux

- Catégorie : Web
- Difficulté : Non précisée
- Flag : `SHLK{Hoisted_The_Flag_Captain_ABDE8981}`

## Démarche

Challenge web basé sur une XSS déclenchée par un bot interne. Un identifiant inconnu injectait ship.name avec le filtre safe dans du JavaScript. La subtilité venait du bot : le cookie FLAG était posé après navigation si le hostname était web. Il fallait donc reporter une URL interne du type http://web:5000/ship?id=..., pas seulement l'URL exposée depuis l'extérieur.

## Commandes et scripts pertinents

- `../scripts/hisser_solve.py`

```bash
python3 scripts/hisser_solve.py
```

## Conclusion

Le filtre safe sur une donnée métier contrôlable a rendu possible l'exfiltration du cookie bot.
