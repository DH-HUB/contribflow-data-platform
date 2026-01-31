Dépannage
=========

WSL / Docker Desktop (permissions)
----------------------------------
Si Airflow/dbt n’arrive pas à écrire dans certains dossiers montés, vérifier les permissions
sur les volumes Docker (UID airflow souvent 50000) et préférer /opt/airflow/... pour logs/artefacts.
