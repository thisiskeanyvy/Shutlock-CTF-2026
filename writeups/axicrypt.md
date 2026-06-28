# AXICrypt

- Catégorie : Reverse / Crypto / Hardware
- Difficulté : 500 points
- Flag : `Non repris ici`

## Démarche

Les éléments disponibles contiennent une capture de transactions AXI-Lite et des scripts d'analyse. Les notes mentionnent 8 écritures aux registres `0x10..0x2c`, un démarrage via le registre `0x00`, un status final `0x03` et une sortie de 128 bits :

```text
fd8b0a7e 65036ded 8162c20f be3c80f2
```

Les essais AES-128 ECB AES-128 ECB avec les conventions endian usuelles n'ont pas produit de texte flag. Une note mémoire séparée autour de `support.AXICrypt` documente aussi une piste TLS/vhost, mais sans flag explicite.

## Commandes et scripts pertinents

- `../scripts/axicrypt_decode_capture.py`
- `../scripts/axicrypt_scan_direct_keys.py`

```bash
python3 scripts/axicrypt_decode_capture.py
python3 scripts/axicrypt_scan_direct_keys.py
```

## Conclusion

Analyse partielle conservée, aucun flag exact retrouvé dans les éléments ou notes.
