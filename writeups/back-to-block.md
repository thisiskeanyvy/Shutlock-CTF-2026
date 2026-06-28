# Back to Block

- Catégorie : Cryptographie
- Difficulté : 500 points
- Flag : `SHLK{1nTegr4l_fTw_ae98ba56}`

## Démarche

Le script publié implémente une attaque intégrale de type Square sur AES. Le service fuit la diagonale de la master key `k[0]`, `k[5]`, `k[10]`, `k[15]`. Deux structures de 256 plaintexts permettent de récupérer la dernière clé de round, puis le script inverse le key schedule AES-128 pour reconstruire la clé maître.

Le dépôt contient aussi un serveur de démonstration avec `FLAG=SHLK{test}` par défaut. Cette valeur est un placeholder de test, pas un flag CTFd.

Sur l'instance dynamique du challenge, la même attaque a été exécutée avec le solveur local. Les deux structures de 256 plaintexts consomment le budget complet de 512 requêtes, récupèrent la clé maître AES `7bebc245dce4620b819a4f816c5a93e1`, puis la soumission de cette clé au service renvoie le flag.

## Commandes et scripts pertinents

- `../scripts/back_to_block/solve_back_to_block.py`
- `../scripts/back_to_block/aes_given.py`
- `../scripts/back_to_block/server.py`

```bash
python3 scripts/back_to_block/solve_back_to_block.py --self-test
python3 scripts/back_to_block/solve_back_to_block.py --host <host> --port <port> --submit
```

Résultat du self-test :

```text
self-test key=00112233445566778899aabbccddeeff ok=True
```

Ce test confirme que l'attaque intégrale et l'inversion du key schedule fonctionnent sur l'oracle de démonstration. Il ne récupère pas le flag CTF, car celui-ci n'est renvoyé qu'après soumission de la clé à une instance dynamique du challenge.

Résultat sur l'instance du challenge :

```text
queries=512
key=7bebc245dce4620b819a4f816c5a93e1
SHLK{1nTegr4l_fTw_ae98ba56}
```

## Conclusion

Attaque documentée et reproductible en self-test, puis validée sur l'instance dynamique avec récupération de la clé maître et retour du flag exact :

```text
SHLK{1nTegr4l_fTw_ae98ba56}
```
