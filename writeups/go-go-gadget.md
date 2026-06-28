# Go Go Gadget

- Catégorie : Sandbox / Linux
- Difficulté : Non précisée
- Flag : `SHLK{l4_ch3ff3_3st_L-D}`

## Démarche

Challenge AppArmor avec profils imbriqués. player_shell interdisait /opt/mission/briefing, mais /usr/bin/gaget transitionnait vers gaget_domain, autorisé à lire /opt/mission/**. La résolution utilisait LD_PRELOAD : une bibliothèque partagée avec constructeur s'exécute dans le domaine AppArmor de gaget, puis lit le briefing.

## Commandes et scripts pertinents

Aucun script public associé.

```bash
LD_PRELOAD=/tmp/g.so /usr/bin/gaget
```

## Conclusion

Un binaire passerelle vers un profil plus permissif doit neutraliser les variables d'environnement dangereuses.
