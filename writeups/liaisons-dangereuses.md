# Liaisons dangereuses

- Catégorie : Web / mTLS
- Difficulté : Non précisée
- Flag : `SHLK{d0_n07_f0rg37_70_v3r1fy_3v3ry7h1ng}`

## Démarche

Le service HTTPS exigeait une authentification mTLS. Un certificat client CN=supervisor.liaisons.local était accepté, mais l'autorisation applicative reposait ensuite sur un mapping LDAP. Une injection dans OU, par exemple /CN=supervisor.liaisons.local/OU=*)|(role=admin, cassait le filtre LDAP et faisait matcher un rôle admin.

## Commandes et scripts pertinents

- `../scripts/liaisons_solve.py`

```bash
python3 scripts/liaisons_solve.py
```

## Conclusion

Les champs de certificat sont aussi des entrées utilisateur et doivent être échappés avant usage LDAP.
