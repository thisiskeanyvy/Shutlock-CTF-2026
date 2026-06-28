# Sneaky

- Catégorie : PWN / Kernel
- Difficulté : 500 points
- Flag : `Non repris ici`

## Démarche

Les éléments disponibles contiennent des scripts de lancement/debug kernel et une clé de déchiffrement `5ne4-Key`. Une image de démonstration contient `SHLK{THE_FLAG}`, mais les notes précisent que cette valeur est un placeholder évident, pas un flag CTFd.

La piste utile est donc l'environnement kernel/QEMU et le déchiffrement de l'image, pas la chaîne placeholder.

## Commandes et scripts pertinents

- `../scripts/sneaky/run_kernel.sh`
- `../scripts/sneaky/run_gdb.sh`
- `../scripts/sneaky/send_keys.sh`

## Conclusion

Aucun flag CTF retrouvé. `SHLK{THE_FLAG}` est explicitement traité comme placeholder.
