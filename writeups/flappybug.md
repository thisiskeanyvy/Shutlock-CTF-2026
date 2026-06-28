# FlappyBug

- Catégorie : Reverse
- Difficulté : Non précisée
- Flag : `SHLK{Wh4t_E_Us3leSs_b1rD}`

## Démarche

Challenge Unity/IL2CPP. L'archive contenait un StreamingAssets/flag.dat chiffré. La clé XOR réelle était dans les métadonnées Mono, plus précisément dans la fieldDefaultValue du champ entier 6C8AD818..., champ 38106, TypeDef 8879. Le script parse les métadonnées v39, lit dataIndex=584888, extrait les quatre octets 23 7a b1 4f, puis déchiffre par XOR périodique.

## Commandes et scripts pertinents

- `../scripts/flappy_extract_key.py`
- `../scripts/flappy_brute.py`

```bash
python3 scripts/flappy_extract_key.py
python3 scripts/flappy_brute.py
```

## Conclusion

Le plaintext obtenu est un PNG de 607x213 contenant le flag.
