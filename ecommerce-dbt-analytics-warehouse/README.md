# E-commerce Analytics Warehouse

Pipeline Data Engineering et Analytics Warehouse construit à partir du **Brazilian E-Commerce Public Dataset by Olist**.

Le projet transforme progressivement les données sources CSV en données analytiques structurées selon une architecture **Raw -> Bronze -> Silver -> Gold**. Le socle d’ingestion Bronze est terminé ; la couche Silver est actuellement en cours de développement.

## Objectifs du projet

- Construire un pipeline de données reproductible et testable.
- Fiabiliser les données Olist grâce à des contrôles de qualité génériques.
- Standardiser les datasets dans des fichiers Parquet organisés par couche.
- Préparer une architecture analytique exploitable avec DuckDB, dbt Core et Metabase.
- Produire à terme des marts Gold documentés et adaptés à l’analyse métier.

## Architecture

```text
data/raw/                    Fichiers CSV Olist
	|
	v
Ingestion: extraction + validation
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
Gold / marts analytiques     À construire avec dbt Core
	|
	v
Metabase                     À connecter
```

La stack cible comprend Python, Polars, Parquet, DuckDB, dbt Core, pytest, les tests dbt, Docker, GitHub Actions et Metabase. À ce stade, seuls Python, Polars, Parquet et pytest sont utilisés dans le code actuel ; les autres composants restent à intégrer.

## État actuel du projet

### Terminé

- Les 9 fichiers CSV Olist sont présents dans `data/raw/`.
- Extraction des CSV avec Polars.
- Validation générique des DataFrames.
- Schémas de validation définis pour les 9 datasets.
- Contrôles des colonnes requises, des valeurs nulles et de l’unicité.
- Pipeline d’ingestion Raw -> Bronze.
- Écriture des 9 datasets au format Parquet dans `data/bronze/`.
- Tests pytest pour l’extraction, la validation, le chargement et les transformations déjà disponibles.
- Pipeline Bronze -> Silver pour `customers`.
- Pipeline Bronze -> Silver pour `orders`.
- Génération des fichiers Parquet Silver pour `customers` et `orders`.
- Détection de 23 anomalies réelles de dates de livraison dans les données `orders`.

### En cours

- Développement des transformations Silver des autres datasets Olist.
- Généralisation du pipeline Bronze -> Silver à l’ensemble des datasets.
- Structuration des quality reports et du traitement des données rejetées.

### À venir

- Intégration de DuckDB.
- Initialisation de dbt Core.
- Construction des modèles dbt et de la couche Gold.
- Ajout des tests et de la documentation dbt.
- Connexion de Metabase.
- Dockerisation du projet.
- Mise en place de GitHub Actions.

## Couches de données

| Couche | Emplacement | Rôle | État |
| --- | --- | --- | --- |
| Raw | `data/raw/` | Données CSV originales provenant d’Olist | Disponible |
| Bronze | `data/bronze/` | Données extraites, validées et stockées en Parquet | Terminé |
| Silver | `data/silver/` | Données nettoyées, standardisées et enrichies | En cours |
| Gold | À définir | Marts analytiques prêts pour la consommation métier | À venir |

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

Le pipeline associé lit le Parquet Bronze, applique la transformation et écrit le résultat dans `data/silver/`.

### `orders`

La transformation `transform_orders` ajoute le champ booléen `has_delivery_date_anomaly`.

Ce flag est activé lorsqu’une commande est au statut `delivered` et qu’au moins une des dates suivantes est manquante :

- `order_approved_at` ;
- `order_delivered_carrier_date` ;
- `order_delivered_customer_date`.

Les autres datasets ne disposent pas encore de transformation Silver dédiée.

## Structure du projet

```text
.
├── data/
│   ├── raw/                 # CSV sources Olist
│   ├── bronze/              # Parquet validés
│   ├── silver/              # Parquet transformés
│   ├── quality_reports/     # Rapports qualité à venir
│   └── rejected/            # Données rejetées à venir
├── ingestion/
│   ├── extract.py           # Extraction CSV avec Polars
│   ├── validate.py          # Validation générique
│   ├── schemas.py           # Schémas des 9 datasets
│   ├── load.py              # Chargement vers Bronze
│   └── pipeline.py          # Pipeline Raw -> Bronze
├── transformation/
│   ├── silver.py            # Transformations Silver
│   ├── load.py              # Chargement vers Silver
│   └── pipeline.py          # Pipelines Silver disponibles
├── tests/                   # Tests pytest
├── dashboards/              # Espace réservé aux dashboards
├── requirements.txt         # Dépendances actuelles
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
```

Sous Windows, l’activation de l’environnement virtuel peut être effectuée avec :

```powershell
.venv\Scripts\activate
```

Les dépendances actuellement déclarées sont limitées à Polars. DuckDB, dbt Core, Docker et Metabase ne sont pas encore configurés dans le projet.

## Lancer l’ingestion Bronze

Depuis la racine du projet :

```bash
python -m ingestion.pipeline
```

La commande lit les fichiers CSV de `data/raw/`, applique le schéma correspondant à chaque dataset et écrit un fichier Parquet dans `data/bronze/`.

## Lancer les pipelines Silver disponibles

Les pipelines `customers` et `orders` peuvent être exécutés depuis Python :

```python
from transformation.pipeline import (
    run_customers_silver_pipeline,
    run_orders_silver_pipeline,
)

run_customers_silver_pipeline(
    bronze_file_path="data/bronze/olist_customers_dataset.parquet",
    silver_data_dir="data/silver",
)

run_orders_silver_pipeline(
    bronze_file_path="data/bronze/olist_orders_dataset.parquet",
    silver_data_dir="data/silver",
)
```

## Tests

Pour exécuter l’ensemble des tests :

```bash
pytest -q
```

Les tests couvrent notamment l’extraction de fichiers CSV, les erreurs de format et de contenu, les règles de validation, l’écriture Parquet et les transformations Silver de `customers` et `orders`.

## Roadmap

1. Terminer les transformations Silver des datasets restants.
2. Généraliser le pipeline Bronze -> Silver.
3. Finaliser les `quality_reports` et le traitement de `rejected`.
4. Intégrer DuckDB.
5. Initialiser dbt Core.
6. Construire les modèles dbt et la couche Gold.
7. Ajouter les tests et la documentation dbt.
8. Connecter Metabase.
9. Dockeriser le projet.
10. Ajouter GitHub Actions.

## Limites actuelles

- La couche Silver est partielle et ne couvre que `customers` et `orders`.
- Le pipeline Bronze -> Silver n’est pas encore généralisé à tous les datasets.
- DuckDB n’est pas encore intégré.
- dbt Core n’est pas encore initialisé.
- La couche Gold et les marts analytiques ne sont pas encore construits.
- Metabase n’est pas encore connecté.
- Docker et GitHub Actions ne sont pas encore implémentés.
- Les fichiers ou lignes invalides ne sont pas encore isolés automatiquement dans `data/rejected/`.

## Données Olist

Le projet utilise le **Brazilian E-Commerce Public Dataset by Olist**, un dataset public décrivant une activité e-commerce brésilienne. Il contient notamment des informations sur les clients, commandes, produits, vendeurs, paiements, avis, lignes de commande, géolocalisation et catégories de produits.

Les données présentes dans `data/raw/` sont utilisées dans le cadre de ce projet d’apprentissage et d’expérimentation Data Engineering. Leur utilisation et leur redistribution restent soumises aux conditions applicables à leur source d’origine.
