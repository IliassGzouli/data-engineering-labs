# E-commerce Analytics Warehouse

Pipeline Data Engineering et Analytics Warehouse construit à partir du **Brazilian E-Commerce Public Dataset by Olist**.

Le projet transforme progressivement les données sources CSV en données analytiques structurées selon une architecture **Raw -> Bronze -> Silver -> Gold**. Le socle d’ingestion Bronze est terminé, trois pipelines Silver sont disponibles et une première couche Gold est construite avec DuckDB et dbt Core.

## Objectifs du projet

- Construire un pipeline de données reproductible et testable.
- Fiabiliser les données Olist grâce à des contrôles de qualité génériques.
- Standardiser les datasets dans des fichiers Parquet organisés par couche.
- Construire une architecture analytique locale avec DuckDB et dbt Core.
- Produire des marts Gold documentés et adaptés à l’analyse métier.
- Préparer la future visualisation des données avec Metabase.

## Architecture

```text
data/raw/                    Fichiers CSV Olist
	|
	v
Ingestion Polars : extraction + validation
	|
	v
data/bronze/                 Données validées au format Parquet
	|
	v
Transformation Silver
	|
	v
data/silver/                 Données nettoyées et enrichies
	|
	v
DuckDB + dbt staging         Modèles intermédiaires matérialisés en vues
	|
	v
dbt marts / Gold             Modèles analytiques matérialisés en tables
	|
	v
Metabase                     À connecter
```

La stack actuelle comprend Python, Polars, Parquet, pytest, DuckDB, dbt Core et `dbt-duckdb`. Metabase, Docker et GitHub Actions font partie des prochaines étapes.

## État actuel du projet

### Terminé

- Les 9 fichiers CSV Olist sont présents dans `data/raw/`.
- Extraction des CSV avec Polars.
- Validation générique des DataFrames.
- Schémas de validation définis pour les 9 datasets.
- Contrôles des colonnes requises, des valeurs nulles et de l’unicité.
- Pipeline d’ingestion Raw -> Bronze.
- Écriture des 9 datasets au format Parquet dans `data/bronze/`.
- Tests pytest pour l’ingestion et les transformations Python disponibles.
- Pipelines Bronze -> Silver pour `customers`, `orders` et `order_items`.
- Génération des trois fichiers Parquet Silver correspondants.
- Détection de 23 anomalies réelles de dates de livraison dans les données `orders`.
- Intégration de DuckDB comme moteur analytique local.
- Configuration de dbt Core avec `dbt-duckdb` dans `ecommerce_analytics/`.
- Création de trois modèles staging matérialisés en vues.
- Création de deux marts Gold matérialisés en tables.
- Documentation des modèles Gold et de leurs principales colonnes.
- Mise en place de cinq tests dbt, tous passants (`PASS=5`, `ERROR=0`).

### En cours

- Développement des transformations Silver des autres datasets Olist.
- Généralisation du pipeline Bronze -> Silver à l’ensemble des datasets.
- Structuration des `quality_reports` et du traitement des données rejetées.
- Enrichissement progressif de la couche Gold avec de nouveaux marts.

### À venir

- Ajout de tests dbt supplémentaires, notamment des tests `relationships`.
- Connexion de Metabase.
- Dockerisation du projet.
- Mise en place de GitHub Actions.

## Couches de données

| Couche | Emplacement | Rôle | État |
| --- | --- | --- | --- |
| Raw | `data/raw/` | Données CSV originales provenant d’Olist | Disponible : 9 datasets |
| Bronze | `data/bronze/` | Données extraites, validées et stockées en Parquet | Terminé : 9 datasets |
| Silver | `data/silver/` | Données nettoyées, standardisées et enrichies | Partiel : `customers`, `orders`, `order_items` |
| Gold | `ecommerce_analytics/models/marts/` | Marts analytiques construits avec dbt dans DuckDB | Disponible : `dim_customers`, `fct_orders` |

Les répertoires `data/quality_reports/` et `data/rejected/` sont prévus pour les rapports de qualité et les données rejetées. Leur traitement complet reste à implémenter.

## Règles de qualité implémentées

La validation est pilotée par les schémas centralisés dans `ingestion/schemas.py`. Les règles actuellement disponibles sont :

- vérification qu’un DataFrame n’est pas vide ;
- vérification de la présence des colonnes requises ;
- vérification de l’absence de valeurs nulles sur les colonnes critiques ;
- vérification de l’unicité d’une colonne ou d’une clé composite ;
- vérification de l’existence des colonnes utilisées par les règles de validation ;
- association du bon schéma au dataset à partir du nom du fichier CSV.

Lorsqu’une validation échoue, le pipeline signale l’erreur. L’isolement automatique des fichiers ou lignes rejetés dans `data/rejected/` n’est pas encore implémenté.

## Transformations Silver disponibles

### `customers`

La transformation `transform_customers` convertit `customer_zip_code_prefix` en chaîne de caractères et complète la valeur à gauche afin d’obtenir cinq caractères. Les zéros initiaux sont ainsi conservés.

### `orders`

La transformation `transform_orders` ajoute le champ booléen `has_delivery_date_anomaly`.

Ce flag vaut `true` lorsqu’une commande au statut `delivered` présente au moins une des dates importantes suivantes manquante :

- `order_approved_at` ;
- `order_delivered_carrier_date` ;
- `order_delivered_customer_date`.

Cette règle a permis de détecter 23 anomalies réelles dans le dataset.

### `order_items`

La transformation `transform_order_items` ajoute la colonne `item_total_value`, calculée selon la formule suivante :

```text
item_total_value = price + freight_value
```

Chaque pipeline lit le Parquet Bronze correspondant, applique sa transformation et écrit le résultat dans `data/silver/`.

## DuckDB et dbt

DuckDB est utilisé comme moteur analytique local. Le projet dbt est configuré dans `ecommerce_analytics/` avec l’adaptateur `dbt-duckdb`.

La couche dbt est organisée en deux niveaux :

- `staging`, matérialisé en vues, prépare les données Silver pour les transformations analytiques ;
- `marts`, matérialisé en tables, constitue la couche Gold destinée à l’analyse métier.

### Modèles staging

- `stg_customers`
- `stg_orders`
- `stg_order_items`

### Modèles marts / Gold

#### `dim_customers`

Dimension construite à partir de `stg_customers`. Elle contient notamment :

- `customer_id`
- `customer_unique_id`
- `customer_zip_code_prefix`
- `customer_city`
- `customer_state`

#### `fct_orders`

Table de faits construite à partir de `stg_orders` et `stg_order_items`. Elle contient notamment :

- `order_id`
- `customer_id`
- `order_status`
- les dates de commande, d’approbation et de livraison
- `has_delivery_date_anomaly`
- `item_count`
- `products_value`
- `freight_value`
- `order_total_value`

## Tests dbt

Les tests dbt sont déclarés dans `ecommerce_analytics/models/marts/schema.yml` :

| Modèle | Colonne | Tests |
| --- | --- | --- |
| `dim_customers` | `customer_id` | `not_null`, `unique` |
| `dim_customers` | `customer_unique_id` | `not_null` |
| `fct_orders` | `order_id` | `not_null`, `unique` |

Le résultat actuel est de cinq tests réussis : `PASS=5`, `ERROR=0`.

Le fichier `schema.yml` documente également les modèles Gold et leurs principales colonnes. La documentation et le lineage peuvent être générés et consultés avec `dbt docs generate` puis `dbt docs serve`.

## Structure du projet

```text
.
├── data/
│   ├── raw/                         # 9 CSV sources Olist
│   ├── bronze/                      # 9 Parquet validés
│   ├── silver/                      # Parquet transformés
│   ├── quality_reports/             # Rapports qualité à finaliser
│   └── rejected/                    # Traitement à implémenter
├── ingestion/
│   ├── extract.py                   # Extraction CSV avec Polars
│   ├── validate.py                  # Validation générique
│   ├── schemas.py                   # Schémas des 9 datasets
│   ├── load.py                      # Chargement vers Bronze
│   └── pipeline.py                  # Pipeline Raw -> Bronze
├── transformation/
│   ├── silver.py                    # Transformations Silver
│   ├── load.py                      # Chargement vers Silver
│   └── pipeline.py                  # Pipelines Bronze -> Silver
├── ecommerce_analytics/             # Projet dbt et base DuckDB locale
│   ├── models/
│   │   ├── staging/                 # Modèles staging matérialisés en vues
│   │   └── marts/                   # Modèles Gold matérialisés en tables
│   └── dbt_project.yml              # Configuration du projet dbt
├── tests/                           # Tests pytest
├── dashboards/                      # Espace réservé aux dashboards
├── requirements.txt                 # Dépendances Python
└── README.md
```

## Installation

Pré-requis : Python 3.10 ou version ultérieure.

```bash
git clone <URL_DU_REPOSITORY>
cd ecommerce-dbt-analytics-warehouse

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install dbt-core dbt-duckdb
```

Sous Windows, l’activation de l’environnement virtuel peut être effectuée avec :

```powershell
.venv\Scripts\activate
```

## Lancer l’ingestion Bronze

Depuis la racine du projet :

```bash
python -m ingestion.pipeline
```

La commande lit les fichiers CSV de `data/raw/`, applique le schéma correspondant à chaque dataset et écrit un fichier Parquet dans `data/bronze/`.

## Lancer les pipelines Silver disponibles

Les pipelines `customers`, `orders` et `order_items` peuvent être exécutés depuis Python :

```python
from transformation.pipeline import (
    run_customers_silver_pipeline,
    run_orders_silver_pipeline,
    run_order_items_silver_pipeline,
)

run_customers_silver_pipeline(
    bronze_file_path="data/bronze/olist_customers_dataset.parquet",
    silver_data_dir="data/silver",
)

run_orders_silver_pipeline(
    bronze_file_path="data/bronze/olist_orders_dataset.parquet",
    silver_data_dir="data/silver",
)

run_order_items_silver_pipeline(
    bronze_file_path="data/bronze/olist_order_items_dataset.parquet",
    silver_data_dir="data/silver",
)
```

## Exécuter dbt

Depuis le répertoire du projet dbt :

```bash
cd ecommerce_analytics
dbt run
dbt test
```

Pour générer puis consulter la documentation et le lineage :

```bash
dbt docs generate
dbt docs serve
```

## Tests Python

Pour exécuter l’ensemble des tests pytest depuis la racine du projet :

```bash
pytest -q
```

Les tests Python couvrent notamment l’extraction de fichiers CSV, les erreurs de format et de contenu, les règles de validation, l’écriture Parquet et les transformations Silver.

## Roadmap

1. Terminer les transformations Silver des autres datasets Olist.
2. Généraliser le pipeline Bronze -> Silver.
3. Finaliser les `quality_reports`.
4. Implémenter le traitement de `data/rejected/`.
5. Enrichir la couche Gold avec d’autres marts.
6. Ajouter des tests dbt supplémentaires, notamment des tests `relationships`.
7. Connecter Metabase.
8. Dockeriser le projet.
9. Ajouter GitHub Actions.

## Limites actuelles

- La couche Silver officiellement disponible est partielle et couvre `customers`, `orders` et `order_items`.
- Le pipeline Bronze -> Silver n’est pas encore généralisé à tous les datasets.
- La couche Gold est limitée à `dim_customers` et `fct_orders`.
- Les tests dbt ne couvrent pas encore les relations entre les modèles.
- Les `quality_reports` ne sont pas finalisés.
- Les fichiers ou lignes invalides ne sont pas encore isolés automatiquement dans `data/rejected/`.
- Metabase n’est pas encore connecté.
- Docker et GitHub Actions ne sont pas encore implémentés.

## Données Olist

Le projet utilise le **Brazilian E-Commerce Public Dataset by Olist**, un dataset public décrivant une activité e-commerce brésilienne. Il contient notamment des informations sur les clients, commandes, produits, vendeurs, paiements, avis, lignes de commande, géolocalisation et catégories de produits.

Les données présentes dans `data/raw/` sont utilisées dans le cadre de ce projet d’apprentissage et d’expérimentation Data Engineering. Leur utilisation et leur redistribution restent soumises aux conditions applicables à leur source d’origine.
