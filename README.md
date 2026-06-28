# Shutlock CTF 2026 - Write-ups

Ce dossier rassemble des write-ups et notes de résolution Shutlock CTF 2026. Il est conçu comme un dépôt GitHub autonome : un fichier Markdown par challenge couvert, plus les scripts utiles qui peuvent être publiés sans gros binaires, archives originales ni secrets.

## Avertissement CTF et éthique

Ces notes sont destinées à documenter un CTF dans un cadre légal et pédagogique. Les techniques décrites doivent rester limitées aux environnements autorisés, challenges, labs ou systèmes pour lesquels vous avez une permission explicite. Aucun scan agressif ni soumission automatisée n'est inclus dans ce dépôt.

## État des flags et limites

Les flags ci-dessous sont uniquement ceux dont la valeur exacte est reprise de façon fiable. Les autres challenges sont marqués `Non repris ici` afin d'éviter toute invention.

Au total, 31 résolutions sont documentées, dont 21 avec flag exact publié. Pour les autres, la note reste volontairement limitée : certains challenges exigent une instance dynamique, un binaire original ou une archive qui ne fait pas partie de ce dépôt.

| Challenge | Flag |
|---|---|
| [Opération Chioné - Préambule](writeups/operation-chione-preambule.md) | `SHLK{HateDeCommencer}` |
| [Opération Chioné - 1/5](writeups/operation-chione-1-5.md) | `SHLK{Lena_KINGSLEY}` |
| [Pretexte](writeups/pretexte.md) | `SHLK{c0n5TrucTor-oVer_h3RriNg}` |
| [FlappyBug](writeups/flappybug.md) | `SHLK{Wh4t_E_Us3leSs_b1rD}` |
| [Hisser Les Drapeaux](writeups/hisser-les-drapeaux.md) | `SHLK{Hoisted_The_Flag_Captain_ABDE8981}` |
| [Frozen Love](writeups/frozen-love.md) | `SHLK{F1aT_Sh4m1r_TR4nsF0rM_21aebc78}` |
| [Pomme de reinette et pomme d'API](writeups/pomme-api.md) | `SHLK{R4C3_C0nd1t10n_1S_CO0l}` |
| [AppArmor-cé](writeups/apparmor-ce.md) | `SHLK{s3cr3t_4g3nt_n4m3_1s_4pp4rm0r}` |
| [Archives à couches multiples (1/3)](writeups/archives-couches-1.md) | `SHLK{4583}` |
| [Archives à couches multiples (2/3)](writeups/archives-couches-2.md) | `SHLK{D0n7_r3inv3n7_7h3_wh33l}` |
| [Go Go Gadget](writeups/go-go-gadget.md) | `SHLK{l4_ch3ff3_3st_L-D}` |
| [Virtuose](writeups/virtuose.md) | `SHLK{sp4ti4l_fr3qu3nci3s_4s_fun_4s_67!}` |
| [Chute libre!](writeups/chute-libre.md) | `SHLK{secret.evilcorp-0123456789}` |
| [Paper Trail](writeups/paper-trail.md) | `SHLK{PJL_M4st3r_H4ck3r}` |
| [Liaisons dangereuses](writeups/liaisons-dangereuses.md) | `SHLK{d0_n07_f0rg37_70_v3r1fy_3v3ry7h1ng}` |
| [RISCy Business](writeups/riscy-business.md) | `SHLK{M4k3_YouR_MoV3}` |
| [CARMEN](writeups/carmen.md) | `SHLK{carmen_rings_restored}` |
| [Dérive Aérienne](writeups/derive-aerienne.md) | `SHLK{L3_C13L_35T_4_N0U5}` |
| [Extra Bon Pour Fouiller](writeups/extra-bon-pour-fouiller.md) | `SHLK{trust.shutlook.fr}` |
| [Cache-Cache](writeups/cache-cache.md) | `SHLK{c4ch3_c4ch3_r14l1z3r_35t_d4ng3r3ux}` |
| [Union Art Festival](writeups/union-art-festival.md) | `SHLK{J3m4ll0c_Thr34d_UAF_1s_R34l}` |

## Index des challenges

- [Opération Chioné - Préambule](writeups/operation-chione-preambule.md) - OSINT - flag : `SHLK{HateDeCommencer}`
- [Opération Chioné - 1/5](writeups/operation-chione-1-5.md) - OSINT - flag : `SHLK{Lena_KINGSLEY}`
- [Opération Chioné - 2/5](writeups/operation-chione-2-5.md) - OSINT - flag : `Non repris ici`
- [Pretexte](writeups/pretexte.md) - Reverse - flag : `SHLK{c0n5TrucTor-oVer_h3RriNg}`
- [FlappyBug](writeups/flappybug.md) - Reverse - flag : `SHLK{Wh4t_E_Us3leSs_b1rD}`
- [Hisser Les Drapeaux](writeups/hisser-les-drapeaux.md) - Web - flag : `SHLK{Hoisted_The_Flag_Captain_ABDE8981}`
- [Frozen Love](writeups/frozen-love.md) - Cryptographie - flag : `SHLK{F1aT_Sh4m1r_TR4nsF0rM_21aebc78}`
- [Pomme de reinette et pomme d'API](writeups/pomme-api.md) - Web - flag : `SHLK{R4C3_C0nd1t10n_1S_CO0l}`
- [AppArmor-cé](writeups/apparmor-ce.md) - Sandbox / Linux - flag : `SHLK{s3cr3t_4g3nt_n4m3_1s_4pp4rm0r}`
- [Archives à couches multiples (1/3)](writeups/archives-couches-1.md) - Cryptographie / Format - flag : `SHLK{4583}`
- [Archives à couches multiples (2/3)](writeups/archives-couches-2.md) - Pwn / Format - flag : `SHLK{D0n7_r3inv3n7_7h3_wh33l}`
- [Go Go Gadget](writeups/go-go-gadget.md) - Sandbox / Linux - flag : `SHLK{l4_ch3ff3_3st_L-D}`
- [Virtuose](writeups/virtuose.md) - Forensic / ML - flag : `SHLK{sp4ti4l_fr3qu3nci3s_4s_fun_4s_67!}`
- [Chute libre!](writeups/chute-libre.md) - Forensic / Réseau - flag : `SHLK{secret.evilcorp-0123456789}`
- [Paper Trail](writeups/paper-trail.md) - Forensic / Réseau - flag : `SHLK{PJL_M4st3r_H4ck3r}`
- [Liaisons dangereuses](writeups/liaisons-dangereuses.md) - Web / mTLS - flag : `SHLK{d0_n07_f0rg37_70_v3r1fy_3v3ry7h1ng}`
- [RISCy Business](writeups/riscy-business.md) - Reverse - flag : `SHLK{M4k3_YouR_MoV3}`
- [CARMEN](writeups/carmen.md) - Programmation / Puzzle - flag : `SHLK{carmen_rings_restored}`
- [Dérive Aérienne](writeups/derive-aerienne.md) - Forensic / Drone - flag : `SHLK{L3_C13L_35T_4_N0U5}`
- [Extra Bon Pour Fouiller](writeups/extra-bon-pour-fouiller.md) - Forensic / Mémoire - flag : `SHLK{trust.shutlook.fr}`
- [Cache-Cache](writeups/cache-cache.md) - Web / Ruby - flag : `SHLK{c4ch3_c4ch3_r14l1z3r_35t_d4ng3r3ux}`
- [Union Art Festival](writeups/union-art-festival.md) - Pwn / UAF jemalloc - flag : `SHLK{J3m4ll0c_Thr34d_UAF_1s_R34l}`
- [Camera_Intro](writeups/camera-intro.md) - Introduction - flag : `Non repris ici`
- [Checkpoint charlie](writeups/checkpoint-charlie.md) - Système - flag : `Non repris ici`
- [RIPOSTE](writeups/riposte.md) - DEV - flag : `Non repris ici`
- [speedcoding](writeups/speedcoding.md) - Programmation - flag : `Non repris ici`
- [ELF_bien_nourri](writeups/elf-bien-nourri.md) - Reverse - flag : `Non repris ici`
- [Pareidolia](writeups/pareidolia.md) - Reverse / VM - flag : `Non repris ici`
- [Coffee Break](writeups/coffee-break.md) - Pwn - flag : `Non repris ici`
- [Bloat Big Brother](writeups/bloat-big-brother.md) - Cryptographie / Reverse - flag : `Non repris ici`
- [EdDéjàVu](writeups/eddeja-vu.md) - Cryptographie - flag : `Non repris ici`
- [Back to Block](writeups/back-to-block.md) - Cryptographie - flag : `Non repris ici`
- [AXICrypt](writeups/axicrypt.md) - Cryptographie / Hardware - flag : `Non repris ici`
- [Substix](writeups/substix.md) - Reverse / Malware - flag : `Non repris ici`
- [Sneaky](writeups/sneaky.md) - PWN / Kernel - flag : `Non repris ici`
- [Ladycoop](writeups/ladycoop.md) - PWN - flag : `Non repris ici`
- [Esther](writeups/esther.md) - Web - flag : `Non repris ici`

## Limites connues

- 31 résolutions sont documentées, dont 21 flags exacts publiés.
- Les flags encore manquants ne sont pas reconstruits artificiellement.
- Certains challenges nécessitent une instance distante, un binaire original ou une archive non publiée ; leur flag exact est donc simplement non repris ici.
- Les candidats explicitement non validés, placeholders et flags de développement ne sont pas présentés comme flags réels.
- Les gros éléments, binaires, archives originales, captures et répertoires de build/vendor ne sont pas copiés.
- Plusieurs scripts exigent les fichiers originaux du challenge ou une instance CTF ; ils documentent la démarche mais ne sont pas toujours exécutables seuls dans ce dépôt.
- Les sources de services vulnérables ne sont pas recopiées lorsqu'elles ne sont pas nécessaires au solve public.

## Utiliser les scripts

Les scripts sont dans `scripts/`. Depuis la racine du dépôt :

```bash
python3 scripts/pretexte_solve.py
python3 scripts/frozen_solve.py <host> <port>
python3 scripts/back_to_block/solve_back_to_block.py --self-test
python3 scripts/esther_solve.py http://host:port
python3 scripts/bloat_big_brother/blowfish_recover.py
```

Installez les dépendances éventuelles dans un environnement Python isolé si un script l'exige. Les fichiers de challenge originaux ne sont pas inclus volontairement. Les scripts de soumission CTFd et tokens privés ne sont pas publiés.
