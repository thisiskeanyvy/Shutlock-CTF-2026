# Frozen Love

- Catégorie : Cryptographie
- Difficulté : Non précisée
- Flag : `SHLK{F1aT_Sh4m1r_TR4nsF0rM_21aebc78}`

## Démarche

Challenge autour d'une signature de type Schnorr. L'exploitation repose sur une forge algébrique : choisir une relation entre la clé publique Y, la réponse s, le point R et le challenge c. Les notes résument la forge par Y = (s*G - R) / c, ce qui permet de produire une signature acceptée sans connaître la clé privée attendue.

## Commandes et scripts pertinents

- `../scripts/frozen_solve.py`

```bash
python3 scripts/frozen_solve.py <host> <port>
```

## Conclusion

La clé publique, le message et l'engagement doivent être liés correctement dans le challenge de signature.
