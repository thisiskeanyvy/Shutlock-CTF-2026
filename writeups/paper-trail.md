# Paper Trail

- Catégorie : Forensic / Réseau
- Difficulté : Non précisée
- Flag : `SHLK{PJL_M4st3r_H4ck3r}`

## Démarche

Le service renvoyait une PCAP loopback contenant un flux JetDirect TCP/9100. La résolution consistait à reconstituer le payload client vers le port d'impression, découper les blocs PJL/UEL, puis extraire un PostScript flag.ps. La reconstruction manuelle de la colormap et des indices pixels permettait de produire une image 600x100.

## Commandes et scripts pertinents

Aucun script public associé.

```bash
Extraction du flux TCP/9100 puis reconstruction PostScript en image.
```

## Conclusion

Les flux d'impression PJL encapsulent souvent des documents à reconstruire avant interprétation.
