# RIPOSTE

- Catégorie : DEV
- Difficulté : 500 points dans l'état du challenge
- Flag : `SHLK{Cub3_Str1k3s_B4ck}`

## Démarche

`RIPOSTE` est un challenge interactif autour d'un cube de Rubik. La résolution utilise un solveur de cube, par exemple `kociemba`, pour produire une séquence de coups depuis l'état reçu.

La contrainte pratique venait de l'échange avec le service : les coups sont envoyés par paquets de 3, puis les réponses `RIPOSTE` du serveur doivent être compensées dans l'état local avant de calculer ou poursuivre la séquence suivante. En gardant ce modèle synchronisé, le solveur atteint l'état final et récupère :

```text
SHLK{Cub3_Str1k3s_B4ck}
```

## Commandes et scripts pertinents

Exemple de dépendance utile côté solveur :

```bash
python3 -m pip install kociemba
```

## Conclusion

Résolution documentée avec solveur Rubik, envoi par paquets de 3 coups et compensation des ripostes serveur.
