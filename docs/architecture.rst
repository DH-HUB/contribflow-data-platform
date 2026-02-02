Architecture
============

Vue d’ensemble
--------------

ContribFlow met en œuvre un pipeline data « production-like » :

- **Ingestion** (Python) : chargement des fichiers CSV (données synthétiques) en couche *Raw*.
- **Contrôles de qualité** : validations de schéma et règles simples (Pandera) avant consolidation.
- **ELT** (dbt) : transformation vers une couche *Staging* puis *Marts*.
- **Orchestration** (Airflow) : enchaînement des tâches, relançabilité et observabilité.
- **Auditabilité** : journalisation des runs et des incidents qualité dans des tables dédiées.

Flux de données (logique)
-------------------------

.. code-block:: text

   Source (CSV quotidien)
          |
          v
     Airflow (DAG daily)
   - init_db
   - generate_source / pick_latest
   - ingest_validate (Pandera)
   - dbt run / dbt test
          |
          v
   PostgreSQL Warehouse
   raw.*  -> staging.*  -> marts.*
          |
          v
        meta.* (audit, qualité)

Schémas PostgreSQL
------------------

Le warehouse PostgreSQL est organisé par schémas afin de séparer clairement les responsabilités.

**raw (ingestion brute)**
- Objectif : conserver une représentation fidèle et rejouable des données source.
- Caractéristiques : append-only, dédoublonnage (hash), colonnes techniques pour traçabilité.

**staging (standardisation)**
- Objectif : normaliser les types, noms de colonnes et conventions.
- Caractéristiques : vues dbt (typage et sélection des champs utiles).

**marts (consommation analytique)**
- Objectif : exposer des tables prêtes pour l’analyse (BI / data products).
- Caractéristiques : tables dbt matérialisées, modèle en faits/dimensions.

**meta (opérations & audit)**
- Objectif : suivi des exécutions, incidents, métriques techniques.
- Caractéristiques : tables alimentées par le pipeline pour audit et troubleshooting.

Tables principales
------------------

raw.contributions_raw
^^^^^^^^^^^^^^^^^^^^^
Couche brute (ingestion).

- `ingestion_ts` : timestamp d’ingestion
- `source_file` : fichier source
- `record_hash` : hash de la ligne (dédoublonnage / idempotence)
- colonnes métier : `declaration_id`, `taxpayer_id`, `event_date`, `amount`, `currency`, `contribution_type`, `status`, `country`
- `payload` : JSON brut (optionnel) pour audit

staging.stg_contributions
^^^^^^^^^^^^^^^^^^^^^^^^^
Vue dbt de standardisation.

- Normalisation des types (date, numeric, text)
- Base stable pour toutes les transformations aval

marts.dim_taxpayer
^^^^^^^^^^^^^^^^^^
Dimension contribuable (pseudo-anonymisée).

- `taxpayer_key` : clé hachée (surrogate key)
- `country` : attribut de dimension
- Objectif : limiter l’exposition d’identifiants sensibles

marts.fct_contributions
^^^^^^^^^^^^^^^^^^^^^^^
Table de faits des contributions.

- `declaration_id` : identifiant de déclaration
- `taxpayer_key` : clé de jointure vers la dimension
- `event_date`, `amount`, `currency`, `contribution_type`, `status`, `country`
- `ingestion_ts`, `source_file` : traçabilité

meta.etl_run
^^^^^^^^^^^^
Audit des exécutions.

- `run_id`, `dag_id`, `task_id`
- `started_at`, `finished_at`
- `status`, `rows_loaded`, `error_message`

meta.data_quality_issue
^^^^^^^^^^^^^^^^^^^^^^^
Journal des incidents qualité.

- `issue_id`, `run_id`, `detected_at`
- `rule_name`, `severity`
- `sample` (exemples), `details`

Qualité des données (DQ) & contrôles
------------------------------------

Contrôles ingestion (Pandera)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Les validations à l’ingestion sécurisent l’entrée du pipeline :

- schéma attendu (types, champs obligatoires)
- règles simples : montants >= 0, identifiants non nuls, dates parseables
- rejet / journalisation des anomalies dans `meta.data_quality_issue`

Tests ELT (dbt)
^^^^^^^^^^^^^^^
Les tests dbt valident la cohérence des modèles :

- **not_null** / **unique** sur les clés (ex : `declaration_id`, `taxpayer_key`)
- **relationships** entre tables (ex : `fct_contributions.taxpayer_key` référence `dim_taxpayer.taxpayer_key`)

Ces tests garantissent la stabilité des *marts* avant exposition à des usages analytiques.

Observabilité & relançabilité
-----------------------------

- Les chargements sont **idempotents** (hash + insert sans duplication).
- Les logs et artefacts dbt sont produits dans un chemin **writable** (`/opt/airflow/...`) pour éviter les problèmes de permissions en environnement Docker/WSL.
- Les tables `meta.*` permettent d’expliquer « quoi / quand / combien / pourquoi » lors d’un incident.




