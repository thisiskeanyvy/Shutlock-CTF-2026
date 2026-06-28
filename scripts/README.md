# Scripts

Scripts de résolution, d'analyse ou de reproduction recopiés depuis les éléments disponibles Shutlock 2026.

Ils sont fournis comme support de write-up : certains exigent les fichiers de challenge originaux ou une instance CTF, qui ne sont pas inclus ici. Les scripts de soumission de flags et les tokens disponibles ont été exclus volontairement.

## Chemins configurables

- `CACHE_CACHE_SOURCE_DIR` : dossier source Ruby contenant `lib/gadgets` pour `cache_cache_solve.py` ; défaut `cache-cache`.
- `DRONE_PCAP` : chemin de la capture pour `drone_analyze.py` ; défaut `drone.pcap`.
- `FLAPPY_FLAG_DAT` : chemin de `flag.dat` pour `flappy_brute.py` ; défaut `flag.dat`.
- `DOCKER_HOST_OVERRIDE` : socket Docker optionnel pour `run_substix_docker.py`.

## Scripts principaux

- `apparmor_solve.py` — exploitation AppArmor-cé via transition de profil scanner.
- `axicrypt_decode_capture.py`, `axicrypt_scan_direct_keys.py` — analyse AXICrypt / capture AXI-Lite.
- `back_to_block/solve_back_to_block.py` — attaque intégrale AES ; `back_to_block/aes_given.py` et `back_to_block/server.py` servent à la reproduction disponible.
- `cache_cache_solve.py` — exploitation Ruby Marshal pour Cache-Cache.
- `drone_analyze.py` — analyse MAVLink pour Dérive Aérienne.
- `esther_solve.py` — récupération tech + tentative d'exfil CSS pour E.S.T.H.E.R, sans soumission automatique.
- `flappy_extract_key.py`, `flappy_brute.py` — extraction/déchiffrement FlappyBug.
- `frozen_solve.py` — forge Schnorr pour Frozen Love.
- `hisser_solve.py` — XSS/bot interne pour Hisser Les Drapeaux.
- `liaisons_solve.py` — mTLS + injection LDAP dans certificat client.
- `pomme_solve.py` — course GraphQL pour Pomme d'API.
- `pretexte_solve.py` — solve final Pretexte ; `pretexte/` contient les helpers JIT/reverse exploratoires.
- `substix_derive.py`, `substix_brute.py`, `run_substix_docker.py`, `mock_c2.py`, `substix/` — reverse Substix et reproduction C2.
- `bloat_big_brother/` — scripts Blowfish/P-array pour Bloat Big Brother, non résolu.
- `speedcoding/` — source et documentation Fortran90 Lite récupérés dans cette note.
- `eddeja-vu/EdDejaVu.c` — source C du challenge EdDéjàVu récupérée dans cette note.
- `chione/` — helpers de décodage calendrier pour Opération Chioné 2/5.
- `sneaky/` — scripts de lancement/debug kernel disponibles pour Sneaky.

## Exclusions volontaires

- `submit_flags.py` et `submit_batch.py` : scripts de soumission/validation CTFd, non publiés.
- `blowfish_lib.py` : fichier de démonstration invalide contenant seulement `404: Not Found`, non publié.
- `pretexte_emulate.py` : brouillon exploratoire syntaxiquement invalide, non publié.
- Dossiers `archives3/MLA/MLA/vendor`, `target`, caches et builds : trop volumineux et non nécessaires.
- Binaires, PCAP, archives originales, images générées et outputs de reverse : exclus par `.gitignore`.
- Sources complètes de services vulnérables contenant des placeholders ou flags de dev : non publiées sauf extrait/source nécessaire au write-up.
