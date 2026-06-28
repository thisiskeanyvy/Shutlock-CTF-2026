# Union Art Festival

- Catégorie : PWN
- Difficulté : 499 points dans l'état du challenge
- Flag : `SHLK{J3m4ll0c_Thr34d_UAF_1s_R34l}`

## Démarche

Le fichier `union_art_festival` est un ELF Linux x86-64, non-PIE, non stripé, avec informations de debug, et son SHA-256 est `e9c8df1b9aca22cb4e1702da2af0ce08fae6fb894c6615696c4185b0bd83ac00`, cohérent avec `checksums.txt`.

Les tags enregistrés (`uaf`, `jemalloc`, `pwn`) et le flag indiquent que la résolution reposait sur un use-after-free exploité dans un contexte `jemalloc` multi-thread. La note mentionne une instance dynamique `57.128.112.118:14437` pendant la résolution.

## Commandes et scripts pertinents

Aucun script final publiable n'est repris pour ce challenge. Les binaires et fichiers lourds ne sont pas copiés dans ce dépôt.

## Conclusion

Le flag exact est :

```text
SHLK{J3m4ll0c_Thr34d_UAF_1s_R34l}
```

Limite : la chaîne d'exploitation complète n'est pas reconstruite dans les notes conservées.
