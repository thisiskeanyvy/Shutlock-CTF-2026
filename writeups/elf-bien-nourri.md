# ELF_bien_nourri

- Catégorie : Reverse
- Difficulté : 498 points dans l'état du challenge
- Flag : `Non repris ici`

## Démarche

Le binaire est un ELF Linux x86-64 stripé. Les chaînes visibles incluent `Your try:`, `Not yet :(`, `Nice, you got it !` et `Don't forget to add SHLK{...} before submititing`. L'analyse statique indique un mécanisme anti-debug ou de tracing : une grosse zone `.data` est copiée en mémoire exécutable, avec des blocs marqués, et le parent redirige l'exécution de l'enfant vers des offsets internes après certains signaux.

Un candidat faible `SHLK{42}` a été envisagé dans les notes, mais explicitement jugé non fiable. Docker/qemu n'était pas utilisable dans l'environnement disponible, donc le dump runtime n'a pas été finalisé.

## Commandes et scripts pertinents

Aucun solve final propre n'a été retrouvé. Les helpers exploratoires de reverse/JIT publiés pour Pretexte peuvent servir de modèle, mais ne constituent pas un solve ELF_bien_nourri.

## Conclusion

Aucun flag exact retrouvé. Le candidat `SHLK{42}` n'est pas publié comme flag.
