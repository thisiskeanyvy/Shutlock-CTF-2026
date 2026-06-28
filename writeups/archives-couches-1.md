# Archives à couches multiples (1/3)

- Catégorie : Cryptographie / Format
- Difficulté : Non précisée
- Flag : `SHLK{4583}`

## Démarche

Le fichier codepin_corrupted.mla ne contenait que 252 octets, mais le format MLA révélait un bloc MAEB ff suivi d'un SHA-256. L'archive ne protégeait qu'un PIN de quatre chiffres. Une recherche hors ligne de 0000 à 9999 sur le hash suffisait à retrouver 4583.

## Commandes et scripts pertinents

Aucun script public associé.

```bash
Aucun script dédié n'a été conservé dans le dossier public.
```

## Conclusion

Un PIN court hashé sans sel ni facteur de coût résiste très peu à une recherche exhaustive.
