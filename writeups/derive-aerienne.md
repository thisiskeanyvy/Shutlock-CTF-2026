# Dérive Aérienne

- Catégorie : Forensic / Drone
- Difficulté : Non précisée
- Flag : `SHLK{L3_C13L_35T_4_N0U5}`

## Démarche

Les scripts publiés documentent une analyse MAVLink : 828 messages GLOBAL_POSITION_INT, 83 HEARTBEAT, port UDP 14550, trajectoire autour de la Tour Eiffel, environ 82,7 secondes de vol, 2532 m de chemin et 1113 m de déplacement net. Plusieurs candidats coordonnées/durées ont été rejetés avant qu'une validation retient le flag final.

## Commandes et scripts pertinents

- `../scripts/drone_analyze.py`

```bash
python3 scripts/drone_analyze.py
```

## Conclusion

Le script conservé explique les hypothèses GPS, mais ne relie pas entièrement le flag à une étape reproductible.
