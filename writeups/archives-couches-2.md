# Archives à couches multiples (2/3)

- Catégorie : Pwn / Format
- Difficulté : Non précisée
- Flag : `SHLK{D0n7_r3inv3n7_7h3_wh33l}`

## Démarche

La deuxième étape exposait SSH admin:admin et un mécanisme d'update MLA exécuté par cron root. updater.py vérifiait une signature Ed25519, mais calculate_hash() ignorait le contenu des blocs BLOCK_TYPE_ENTRY_CONTENT en faisant un seek(content_len, 1). La forge remplaçait update.sh par un payload de même longueur pour conserver les métadonnées signées.

## Commandes et scripts pertinents

Aucun script public associé.

```bash
Aucun script final compact n'a été retenu pour publication.
```

## Conclusion

Une signature d'archive doit couvrir les octets réellement extraits ou exécutés.
