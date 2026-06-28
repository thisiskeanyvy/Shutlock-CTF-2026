# Esther

- Catégorie : Web
- Difficulté : 500 points
- Flag : `Non repris ici`

## Démarche

Les notes de résolution décrivent `E.S.T.H.E.R` comme un challenge web avec bypass de recovery et exfiltration côté bot. La route `GET /tech/recovery?` renvoie un `tech_pass` parce que le middleware compare une URI exacte et ne traite pas pareil `?` ou `?x=1`. Après connexion tech, une zone CSS est injectée dans `<style>{{ css }}</style>` sur `/discussion`.

Un bot consulte `/discussion` puis poste périodiquement. Les tentatives d'exfiltration via propriétés CSS à URL n'ont pas généré de requêtes exploitables dans les journaux de test. La piste restante était un breakout CSS/HTML et l'exfiltration de l'attribut `checker`.

Les sources de démonstration contiennent des placeholders : `secret_website.db` inclut `SHLK{local_flag}` et le bot de développement contient des valeurs `CTF{...}`. Ces valeurs ne sont pas des flags CTF.

## Commandes et scripts pertinents

- `../scripts/esther_solve.py`

```bash
python3 scripts/esther_solve.py http://host:port
```

Le script publié ne soumet rien automatiquement ; il affiche seulement un candidat s'il en reconstruit un.

## Conclusion

Aucun flag CTF repris ici. Les placeholders ne doivent pas être publiés comme flags.
