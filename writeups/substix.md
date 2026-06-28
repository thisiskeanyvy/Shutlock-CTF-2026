# Substix

- Catégorie : Reverse / Malware / Forensique
- Difficulté : 500 points
- Flag : `Non repris ici`

## Démarche

Substix porte sur un binaire Go malveillant remplaçant `jq` dans une chaîne Nix. Les notes de résolution identifient le package compromis `0q85yfxd70aq8iv4n43hqcmh2dbyb80z-jq-1.7.1-bin`, un binaire Go statique, et un C2 `https://nixos-community.me/update`.

La fonction `deriveKey` reconstituée XOR deux slices globales de 22 octets et produit la clé :

```text
N1X_SUBST1TUT3R_P01S0N
```

Cette clé est envoyée en User-Agent. Le format attendu par l'énoncé est `SHLK{md5(package:key:c2)}`. De nombreuses variantes de package, clé et C2 ont été testées et rejetées dans les notes ; aucun flag fiable ne doit être publié.

## Commandes et scripts pertinents

- `../scripts/substix_derive.py`
- `../scripts/substix_brute.py`
- `../scripts/run_substix_docker.py`
- `../scripts/mock_c2.py`
- `../scripts/substix/analyze_jq.py`
- `../scripts/substix/reverse_jq.py`

```bash
python3 scripts/substix_derive.py
python3 scripts/substix_brute.py
python3 scripts/mock_c2.py
```

## Conclusion

Reverse solide, mais pas de résolution validée. Les scripts de brute force publiés servent à reproduire les candidats, pas à affirmer un flag.
