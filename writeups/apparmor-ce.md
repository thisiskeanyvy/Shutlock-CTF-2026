# AppArmor-cé

- Catégorie : Sandbox / Linux
- Difficulté : Non précisée
- Flag : `SHLK{s3cr3t_4g3nt_n4m3_1s_4pp4rm0r}`

## Démarche

L'archive source contenait des profils AppArmor. Le shell player_shell interdisait /secure_data/agents.txt, mais le scanner exécutait des fichiers déposés dans /var/scan/ sous le profil var_scan_binary, autorisé à lire /secure_data/**. La chaîne consistait à déposer un script exécutable dans /var/scan/, attendre le daemon, puis copier le contenu confidentiel vers /tmp/.

## Commandes et scripts pertinents

- `../scripts/apparmor_solve.py`

```bash
python3 scripts/apparmor_solve.py
```

## Conclusion

Une transition de profil peut devenir une élévation de privilège si un service privilégié exécute un chemin contrôlé.
