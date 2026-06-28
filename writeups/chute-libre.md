# Chute libre!

- Catégorie : Forensic / Réseau
- Difficulté : Non précisée
- Flag : `SHLK{secret.evilcorp-0123456789}`

## Démarche

La PCAP contenait un échange IKEv1 aggressive mode. Ce mode expose assez de matière pour attaquer le PSK à partir de la capture. Les notes conservent notamment ID_USER_FQDN secret.evilcorp et les paramètres nécessaires au HMAC-SHA1. Le dictionnaire rockyou-top20k a retrouvé le PSK 0123456789.

## Commandes et scripts pertinents

Aucun script public associé.

```bash
Attaque hors ligne HMAC-SHA1 sur les paramètres IKE extraits de la capture.
```

## Conclusion

IKE aggressive mode avec PSK faible permet une compromission rapide par attaque hors ligne.
