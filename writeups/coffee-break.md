# Coffee Break

- Catégorie : PWN
- Difficulté : 499 points dans l'état du challenge
- Flag : `SHLK{J3m4ll0c_N3v3r_F0rg3ts}`

## Démarche

Le binaire x86-64 exposait un symbole `secret` qui appelle `system("/bin/sh")`. Sur l'instance distante, l'exploitation de la primitive mémoire autour de `jemalloc` permettait de détourner l'exécution vers cette fonction et d'obtenir un shell.

Une fois le shell obtenu, le flag était lisible dans le fichier prévu par l'environnement du challenge :

```bash
cat /ctf/flag.txt
```

Résultat :

```text
SHLK{J3m4ll0c_N3v3r_F0rg3ts}
```

## Commandes et scripts pertinents

Aucun script final publiable n'est repris pour ce challenge. La chaîne de résolution repose sur l'exploitation distante de la primitive mémoire, puis sur l'appel à `secret`.

## Conclusion

Challenge résolu sur instance distante ; le flag exact confirmé est `SHLK{J3m4ll0c_N3v3r_F0rg3ts}`.
