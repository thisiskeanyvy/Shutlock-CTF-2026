# Cache-Cache

- Catégorie : Web / Ruby
- Difficulté : Non précisée
- Flag : `SHLK{c4ch3_c4ch3_r14l1z3r_35t_d4ng3r3ux}`

## Démarche

Challenge web avec désérialisation Ruby. La source contenait une chaîne de gadgets autour de Marshal.load : DocumentNode -> Dispatcher -> Formatter -> Locator -> DataStore. L'exploitation téléversait un avatar avec saveas=../../../tmp/cache/pwn.cache, puis déclenchait GET /report/pwn pour lire /flag.txt.

## Commandes et scripts pertinents

- `../scripts/cache_cache_solve.py`

```bash
python3 scripts/cache_cache_solve.py
```

## Conclusion

Marshal.load ne doit jamais traiter une donnée contrôlée par l'utilisateur. Note : un rejet CTFd historique est mentionné malgré ce flag exact ; il est donc conservé avec réserve.
