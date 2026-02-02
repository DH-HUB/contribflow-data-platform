Sécurité
=========

Sécurité (contexte de démonstration)
-----------------------------------

ContribFlow est documenté dans un contexte **local et pédagogique**.

- Données entièrement **synthétiques** (aucune donnée réelle).
- Services (Airflow, PostgreSQL) exposés **uniquement en local**.
- Secrets injectés via **variables d’environnement**.
- Séparation des rôles et schémas pour limiter l’exposition des données.

En environnement de production, ces principes s’étendent naturellement à
l’usage d’un gestionnaire de secrets, à un réseau privé et à des contrôles
d’accès renforcés.