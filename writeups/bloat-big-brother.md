# Bloat Big Brother

- Catégorie : Cryptographie / Reverse
- Difficulté : 498 points dans l'état du challenge
- Flag : `Non repris ici`

## Démarche

Les notes de résolution documentent une piste Blowfish. La fuite utile est un P-array de 18 mots 32 bits. Un bug initial de comparaison a été corrigé : l'implémentation du script stocke `P` en 9 paires `(L, R)`, donc il faut aplatir la structure avant de comparer aux entiers fuités.

La piste `schneierfacts #1605` mentionne `One Fish, Twofish, Red Fish, Blowfish`. Des wordlists disponibles, phrases dérivées et `rockyou-top20k` ont été testées sans retrouver la clé. Le flag attendu serait probablement de la forme `SHLK{clé}` une fois la clé retrouvée, mais aucun candidat n'est validé.

## Commandes et scripts pertinents

- `../scripts/bloat_big_brother/bf.py`
- `../scripts/bloat_big_brother/blowfish_lib.py`
- `../scripts/bloat_big_brother/blowfish_recover.py`
- `../scripts/bloat_big_brother/blowfish_rockyou.py`

```bash
python3 scripts/bloat_big_brother/blowfish_recover.py
python3 scripts/bloat_big_brother/blowfish_rockyou.py
```

Résultats des scripts :

```text
$ python3 scripts/bloat_big_brother/blowfish_recover.py
done (wordlist only)

$ python3 scripts/bloat_big_brother/blowfish_rockyou.py
# aucun match trouvé avec les wordlists disponibles
```

## Conclusion

Le challenge est documenté jusqu'à la piste Blowfish/P-array, mais aucun flag fiable n'est publié ici.
