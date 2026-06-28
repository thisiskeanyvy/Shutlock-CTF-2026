# EdDéjàVu

- Catégorie : Cryptographie
- Difficulté : 500 points dans l'état du challenge
- Flag : `Non repris ici`

## Démarche

L'énoncé indique un challenge de signature Ed25519 avec source C fournie. Le service génère une seed privée, affiche la clé publique et permet de signer des messages. La fonction de signature tronque le message à `SIGN_LIMIT = 128` octets pour le calcul de nonce, mais calcule aussi une somme sur la longueur complète du message et applique `clamp(k_scalar)` seulement si cette somme est impaire.

Le point `déjà vu` vient donc d'un comportement de signature réutilisable ou malléable selon la parité et la troncature. Le fichier source est publié pour analyse, mais aucun script de solve final ni flag exact n'est repris ici.

## Commandes et scripts pertinents

- `../scripts/eddeja-vu/EdDejaVu.c`

```bash
gcc -o EdDejaVu scripts/eddeja-vu/EdDejaVu.c -lsodium -O2
```

## Conclusion

Challenge résolu, mais flag exact non repris ici. Aucun flag inventé.
