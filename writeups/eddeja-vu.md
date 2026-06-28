# EdDéjàVu

- Catégorie : Cryptographie
- Difficulté : 500 points dans l'état du challenge
- Flag : `SHLK{t0_cl4mp_0r_n0t_t0_cl4mp_t3ll3_3st_la_qu3st10n}`

## Démarche

L'énoncé indique un challenge de signature Ed25519 avec source C fournie. Le service génère une seed privée, affiche la clé publique et permet de signer des messages. La fonction de signature tronque le message à `SIGN_LIMIT = 128` octets pour le calcul de nonce, mais calcule aussi une somme sur la longueur complète du message et applique `clamp(k_scalar)` seulement si cette somme est impaire.

Le point `déjà vu` vient donc d'un comportement de signature réutilisable ou malléable selon la parité et la troncature. La résolution finale exploite notamment une signature du message vide : elle donne assez d'information pour reconstruire le scalaire privé malgré le clamp conditionnel, puis produire une signature acceptée sur le message attendu.

Le solveur socket reconstruit localement la clé privée à partir des valeurs exposées par le service, puis utilise la clé récupérée pour signer la requête finale. Le flag obtenu est :

```text
SHLK{t0_cl4mp_0r_n0t_t0_cl4mp_t3ll3_3st_la_qu3st10n}
```

## Commandes et scripts pertinents

- `../scripts/eddeja-vu/EdDejaVu.c`
- [`scripts/eddeja-vu/EdDejaVu.c`](https://github.com/thisiskeanyvy/Shutlock-CTF-2026/blob/main/scripts/eddeja-vu/EdDejaVu.c)

```bash
gcc -o EdDejaVu scripts/eddeja-vu/EdDejaVu.c -lsodium -O2
```

## Conclusion

Challenge résolu par récupération du scalaire privé Ed25519 à partir du comportement de signature. Aucun flag inventé.
