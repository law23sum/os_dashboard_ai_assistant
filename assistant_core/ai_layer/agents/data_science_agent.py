"""
Data Science Agent - Advanced MLOps and Machine Learning Operations

Provides comprehensive machine learning capabilities including:
- Dataset management and analysis
- Automated ML experiments and hyperparameter optimization
- Model training, validation, and deployment
- Performance monitoring and data drift detection
- Feature engineering and pipeline automation
"""

import asyncio
import json
import uuid
import time
import pickle
import joblib
from typing import Dict, Any, List, Optional, Tuple, Set, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import heapq
import hashlib
import os
import shutil

# ML Libraries
import sklearn
from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    GridSearchCV,
    RandomizedSearchCV,
)
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    LabelEncoder,
    OneHotEncoder,
)
from sklearn.feature_selection import SelectKBest, RFE, RFECV
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA, TruncatedSVD, FactorAnalysis
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline

import xgboost as xgb
import lightgbm as lgb

# Deep Learning (optional)
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from ...logger import setup_logger


class ModelType(Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    DEEP_LEARNING = "deep_learning"
    ENSEMBLE = "ensemble"


class PipelineStage(Enum):
    DATA_INGESTION = "data_ingestion"
    DATA_VALIDATION = "data_validation"
    DATA_PREPROCESSING = "data_preprocessing"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_TRAINING = "model_training"
    MODEL_VALIDATION = "model_validation"
    MODEL_DEPLOYMENT = "model_deployment"
    MONITORING = "monitoring"


class ExperimentStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelStatus(Enum):
    TRAINING = "training"
    TRAINED = "trained"
    VALIDATED = "validated"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"


@dataclass
class Dataset:
    """Dataset metadata and information"""

    dataset_id: str
    name: str
    description: str
    file_path: str
    format: str  # csv, json, parquet, etc.
    size_bytes: int
    rows: int
    columns: int
    target_column: Optional[str]
    feature_columns: List[str]
    categorical_columns: List[str]
    numerical_columns: List[str]
    missing_values: Dict[str, int]
    data_types: Dict[str, str]
    statistics: Dict[str, Any]
    created_at: datetime
    last_modified: datetime
    metadata: Dict[str, Any]


@dataclass
class Experiment:
    """ML experiment tracking"""

    experiment_id: str
    name: str
    description: str
    model_type: ModelType
    dataset_id: str
    parameters: Dict[str, Any]
    metrics: Dict[str, float]
    artifacts: Dict[str, str]  # artifact_name -> file_path
    status: ExperimentStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    error_message: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class Model:
    """ML model metadata"""

    model_id: str
    name: str
    model_type: ModelType
    algorithm: str
    experiment_id: str
    dataset_id: str
    version: str
    parameters: Dict[str, Any]
    metrics: Dict[str, float]
    feature_importance: Dict[str, float]
    model_path: str
    preprocessing_path: Optional[str]
    status: ModelStatus
    created_at: datetime
    deployed_at: Optional[datetime]
    performance_history: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@dataclass
class Pipeline:
    """ML pipeline definition"""

    pipeline_id: str
    name: str
    description: str
    stages: List[PipelineStage]
    configuration: Dict[str, Any]
    schedule: Optional[str]  # cron expression
    is_active: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    run_history: List[Dict[str, Any]]
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class DataDrift:
    """Data drift detection result"""

    drift_id: str
    model_id: str
    feature_name: str
    drift_score: float
    threshold: float
    is_drift: bool
    detection_method: str
    reference_period: Tuple[datetime, datetime]
    current_period: Tuple[datetime, datetime]
    detected_at: datetime
    metadata: Dict[str, Any]


@dataclass
class ModelPerformance:
    """Model performance monitoring"""

    performance_id: str
    model_id: str
    metrics: Dict[str, float]
    predictions_count: int
    accuracy_degradation: float
    latency_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    measured_at: datetime
    metadata: Dict[str, Any]


class DataScienceAgent:
    """Data Science Agent - Advanced MLOps and Machine Learning Operations"""

    def __init__(self):
        self.logger = setup_logger("DataScienceAgent")

        # Core storage
        self.datasets: Dict[str, Dataset] = {}
        self.experiments: Dict[str, Experiment] = {}
        self.models: Dict[str, Model] = {}
        self.pipelines: Dict[str, Pipeline] = {}

        # Monitoring and drift detection
        self.data_drift_results: Dict[str, List[DataDrift]] = defaultdict(list)
        self.performance_history: Dict[str, List[ModelPerformance]] = defaultdict(list)

        # Model registry and versioning
        self.model_registry: Dict[str, List[str]] = defaultdict(
            list
        )  # model_name -> model_ids
        self.deployed_models: Dict[str, str] = {}  # endpoint -> model_id

        # Feature store
        self.feature_store: Dict[str, Dict[str, Any]] = {}
        self.feature_metadata: Dict[str, Dict[str, Any]] = {}

        # AutoML and hyperparameter optimization
        self.automl_jobs: Dict[str, Dict[str, Any]] = {}
        self.hyperparameter_searches: Dict[str, Dict[str, Any]] = {}

        # Real-time monitoring
        self.prediction_logs: deque = deque(maxlen=10000)
        self.performance_metrics: Dict[str, Any] = {}

        # Configuration
        self.config = {
            "data_directory": "ml_data/",
            "models_directory": "ml_models/",
            "experiments_directory": "ml_experiments/",
            "artifacts_directory": "ml_artifacts/",
            "max_experiment_history": 1000,
            "drift_detection_threshold": 0.1,
            "performance_degradation_threshold": 0.05,
            "auto_retrain_threshold": 0.1,
            "model_validation_split": 0.2,
            "cross_validation_folds": 5,
            "hyperparameter_search_iterations": 50,
            "feature_selection_k": 10,
            "ensemble_models_count": 3,
            "monitoring_interval_minutes": 15,
            "cleanup_interval_hours": 24,
        }

        # ML algorithms registry
        self.algorithms = {
            ModelType.CLASSIFICATION: {
                "random_forest": RandomForestClassifier,
                "gradient_boosting": GradientBoostingClassifier,
                "logistic_regression": LogisticRegression,
                "svm": SVC,
                "mlp": MLPClassifier,
                "xgboost": xgb.XGBClassifier,
                "lightgbm": lgb.LGBMClassifier,
            },
            ModelType.REGRESSION: {
                "random_forest": RandomForestClassifier,  # Note: Using classifier for now, would need regressor
                "gradient_boosting": GradientBoostingClassifier,
                "linear_regression": LinearRegression,
                "ridge": Ridge,
                "lasso": Lasso,
                "svr": SVR,
                "mlp": MLPRegressor,
                "xgboost": xgb.XGBRegressor,
                "lightgbm": lgb.LGBMRegressor,
            },
            ModelType.CLUSTERING: {
                "kmeans": KMeans,
                "dbscan": DBSCAN,
                "agglomerative": AgglomerativeClustering,
            },
            ModelType.DIMENSIONALITY_REDUCTION: {
                "pca": PCA,
                "truncated_svd": TruncatedSVD,
                "factor_analysis": FactorAnalysis,
            },
        }

        # Preprocessing components
        self.preprocessors = {
            "standard_scaler": StandardScaler,
            "minmax_scaler": MinMaxScaler,
            "label_encoder": LabelEncoder,
            "onehot_encoder": OneHotEncoder,
        }

        # Feature selection methods
        self.feature_selectors = {
            "select_k_best": SelectKBest,
            "rfe": RFE,
            "rfecv": RFECV,
        }

    async def initialize(self):
        """Initialize Data Science Agent"""
        await self._setup_directories()
        await self._load_existing_data()
        await self._initialize_feature_store()

        # Start background tasks
        asyncio.create_task(self._model_monitoring())
        asyncio.create_task(self._drift_detection())
        asyncio.create_task(self._pipeline_scheduler())
        asyncio.create_task(self._performance_tracker())
        asyncio.create_task(self._cleanup_manager())
        asyncio.create_task(self._auto_retraining())

        self.logger.info("Data Science Agent initialized")

    async def process_request(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> str:
        """Process user requests for data science and ML operations"""
        try:
            user_input_lower = user_input.lower()

            # Route requests to appropriate methods
            if "dataset" in user_input_lower and (
                "register" in user_input_lower or "upload" in user_input_lower
            ):
                return await self._handle_dataset_registration(user_input, context)
            elif "experiment" in user_input_lower and (
                "create" in user_input_lower or "run" in user_input_lower
            ):
                return await self._handle_experiment_creation(user_input, context)
            elif "model" in user_input_lower and (
                "train" in user_input_lower or "build" in user_input_lower
            ):
                return await self._handle_model_training(user_input, context)
            elif "predict" in user_input_lower or "inference" in user_input_lower:
                return await self._handle_prediction(user_input, context)
            elif "automl" in user_input_lower or "auto ml" in user_input_lower:
                return await self._handle_automl(user_input, context)
            elif "dashboard" in user_input_lower or "status" in user_input_lower:
                return await self._handle_dashboard_request(user_input, context)
            elif "deploy" in user_input_lower:
                return await self._handle_model_deployment(user_input, context)
            else:
                return self._get_help_message()

        except Exception as e:
            self.logger.error(f"Request processing failed: {e}")
            return f"Error processing request: {str(e)}"

    async def _handle_dataset_registration(
        self, user_input: str, context: Dict[str, Any]
    ) -> str:
        """Handle dataset registration requests"""
        try:
            # Extract dataset information from user input or context
            dataset_info = context.get("dataset_info", {})

            if not dataset_info:
                return "Please provide dataset information (file path, name, target column, etc.)"

            dataset_id = await self.register_dataset(dataset_info)

            dataset = self.datasets[dataset_id]
            return f"""Dataset registered successfully!

📊 Dataset: {dataset.name}
🆔 ID: {dataset_id}
📁 File: {dataset.file_path}
📈 Rows: {dataset.rows}, Columns: {dataset.columns}
🎯 Target: {dataset.target_column or 'Not specified'}
📊 Features: {len(dataset.feature_columns)}

The dataset is ready for ML experiments!"""

        except Exception as e:
            return f"Dataset registration failed: {str(e)}"

    async def _handle_experiment_creation(
        self, user_input: str, context: Dict[str, Any]
    ) -> str:
        """Handle experiment creation requests"""
        try:
            experiment_info = context.get("experiment_info", {})

            if not experiment_info:
                return "Please provide experiment information (dataset_id, model_type, etc.)"

            experiment_id = await self.create_experiment(experiment_info)

            # Auto-run the experiment
            result = await self.run_experiment(experiment_id)

            return f"""Experiment completed successfully!

🧪 Experiment: {experiment_info['name']}
🆔 ID: {experiment_id}
🤖 Algorithm: {result['algorithm']}
📊 Accuracy: {result['metrics'].get('accuracy', 'N/A'):.4f}
⏱️ Duration: {result['duration_seconds']:.1f}s

Model ID: {result['model_id']}"""

        except Exception as e:
            return f"Experiment creation failed: {str(e)}"

    async def _handle_model_training(
        self, user_input: str, context: Dict[str, Any]
    ) -> str:
        """Handle model training requests"""
        try:
            training_info = context.get("training_info", {})

            if not training_info:
                return (
                    "Please provide training information (dataset_id, algorithm, etc.)"
                )

            # Create experiment
            experiment_data = {
                "name": f"Training_{training_info.get('algorithm', 'unknown')}",
                "description": "User-initiated model training",
                "model_type": training_info.get("model_type", "classification"),
                "dataset_id": training_info["dataset_id"],
                "parameters": training_info.get("parameters", {}),
            }

            experiment_id = await self.create_experiment(experiment_data)

            # Run experiment
            result = await self.run_experiment(
                experiment_id,
                algorithm=training_info.get("algorithm"),
                hyperparameters=training_info.get("hyperparameters"),
            )

            return f"""Model training completed!

🎯 Algorithm: {result['algorithm']}
📊 Performance: {result['metrics']}
🧠 Model ID: {result['model_id']}

Ready for deployment or further evaluation."""

        except Exception as e:
            return f"Model training failed: {str(e)}"

    async def _handle_prediction(self, user_input: str, context: Dict[str, Any]) -> str:
        """Handle prediction requests"""
        try:
            prediction_info = context.get("prediction_info", {})

            if not prediction_info:
                return "Please provide prediction information (endpoint, input_data)"

            result = await self.predict(
                prediction_info["endpoint"], prediction_info["input_data"]
            )

            return f"""Prediction completed!

🎯 Prediction: {result['prediction']}
📊 Confidence: {result.get('prediction_proba', 'N/A')}
⚡ Latency: {result['prediction_time_ms']:.1f}ms"""

        except Exception as e:
            return f"Prediction failed: {str(e)}"

    async def _handle_automl(self, user_input: str, context: Dict[str, Any]) -> str:
        """Handle AutoML requests"""
        try:
            automl_info = context.get("automl_info", {})

            if not automl_info:
                return "Please provide AutoML information (dataset_id, target_column, model_type)"

            result = await self.run_automl(
                automl_info["dataset_id"],
                automl_info["target_column"],
                ModelType(automl_info["model_type"]),
                time_limit_minutes=automl_info.get("time_limit", 10),
            )

            return f"""AutoML completed!

🤖 Best Algorithm: {result['best_algorithm']}
📊 Best Score: {result['metrics']['accuracy'] if 'accuracy' in result['metrics'] else result['metrics']}
🧠 Model ID: {result['model_id']}
⏱️ Duration: {result['duration_seconds']:.1f}s

The optimal model has been trained and is ready for deployment!"""

        except Exception as e:
            return f"AutoML failed: {str(e)}"

    async def _handle_dashboard_request(
        self, user_input: str, context: Dict[str, Any]
    ) -> str:
        """Handle dashboard requests"""
        try:
            dashboard = await self.get_ml_dashboard()

            return f"""📊 ML Operations Dashboard

📈 Summary:
• Datasets: {dashboard['summary']['total_datasets']}
• Experiments: {dashboard['summary']['total_experiments']}
• Models: {dashboard['summary']['total_models']}
• Deployed Models: {dashboard['summary']['deployed_models']}

📊 Recent Activity (24h):
• Experiments: {dashboard['recent_activity']['experiments_24h']}
• Predictions: {dashboard['recent_activity']['predictions_1h']}
• Completed: {dashboard['recent_activity']['completed_experiments']}
• Failed: {dashboard['recent_activity']['failed_experiments']}

🚨 Alerts: {dashboard['drift_alerts']} drift detection alerts"""

        except Exception as e:
            return f"Dashboard retrieval failed: {str(e)}"

    async def _handle_model_deployment(
        self, user_input: str, context: Dict[str, Any]
    ) -> str:
        """Handle model deployment requests"""
        try:
            deployment_info = context.get("deployment_info", {})

            if not deployment_info:
                return "Please provide deployment information (model_id, endpoint)"

            endpoint = await self.deploy_model(
                deployment_info["model_id"], deployment_info.get("endpoint")
            )

            return f"""🚀 Model deployed successfully!

🧠 Model: {deployment_info['model_id']}
🌐 Endpoint: {endpoint}
📊 Status: Ready for predictions

You can now make predictions using this endpoint."""

        except Exception as e:
            return f"Model deployment failed: {str(e)}"

    def _get_help_message(self) -> str:
        """Get help message for available operations"""
        return """🤖 Data Science Agent - Available Operations:

📊 **Dataset Management:**
• Register datasets for ML operations
• Analyze data quality and statistics

🧪 **Experiment Tracking:**
• Create and run ML experiments
• Compare different algorithms and hyperparameters

🤖 **Model Training:**
• Train models with various algorithms
• Automated hyperparameter optimization

🎯 **AutoML:**
• Automated machine learning pipelines
• Find optimal models automatically

🚀 **Model Deployment:**
• Deploy trained models as APIs
• Real-time prediction endpoints

📈 **Monitoring & Analytics:**
• Performance tracking and drift detection
• ML operations dashboard

💡 **Usage Examples:**
• "Register this dataset for ML training"
• "Run an experiment with random forest on dataset X"
• "Deploy model Y for predictions"
• "Show me the ML dashboard"
• "Run AutoML on this classification problem"

Provide specific parameters in the context for detailed operations."""

    # Core MLOps Methods (adapted from the provided code)

    async def register_dataset(self, dataset_data: Dict[str, Any]) -> str:
        """Register dataset for ML operations"""
        try:
            dataset_id = str(uuid.uuid4())
            file_path = dataset_data["file_path"]

            # Load and analyze dataset
            df = await self._load_dataset(file_path)

            # Extract metadata
            dataset_stats = await self._analyze_dataset(df)

            dataset = Dataset(
                dataset_id=dataset_id,
                name=dataset_data["name"],
                description=dataset_data.get("description", ""),
                file_path=file_path,
                format=dataset_data.get("format", "csv"),
                size_bytes=os.path.getsize(file_path)
                if os.path.exists(file_path)
                else 0,
                rows=len(df),
                columns=len(df.columns),
                target_column=dataset_data.get("target_column"),
                feature_columns=dataset_data.get("feature_columns", list(df.columns)),
                categorical_columns=dataset_stats["categorical_columns"],
                numerical_columns=dataset_stats["numerical_columns"],
                missing_values=dataset_stats["missing_values"],
                data_types=dataset_stats["data_types"],
                statistics=dataset_stats["statistics"],
                created_at=datetime.now(),
                last_modified=datetime.now(),
                metadata=dataset_data.get("metadata", {}),
            )

            self.datasets[dataset_id] = dataset

            # Store features in feature store
            await self._update_feature_store(dataset_id, df)

            self.logger.info(f"Dataset registered: {dataset_id}")
            return dataset_id

        except Exception as e:
            self.logger.error(f"Dataset registration failed: {e}")
            raise

    async def create_experiment(self, experiment_data: Dict[str, Any]) -> str:
        """Create ML experiment"""
        try:
            experiment_id = str(uuid.uuid4())

            experiment = Experiment(
                experiment_id=experiment_id,
                name=experiment_data["name"],
                description=experiment_data.get("description", ""),
                model_type=ModelType(experiment_data["model_type"]),
                dataset_id=experiment_data["dataset_id"],
                parameters=experiment_data.get("parameters", {}),
                metrics={},
                artifacts={},
                status=ExperimentStatus.CREATED,
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                duration_seconds=None,
                error_message=None,
                metadata=experiment_data.get("metadata", {}),
            )

            self.experiments[experiment_id] = experiment

            # Create experiment directory
            experiment_dir = os.path.join(
                self.config["experiments_directory"], experiment_id
            )
            os.makedirs(experiment_dir, exist_ok=True)

            self.logger.info(f"Experiment created: {experiment_id}")
            return experiment_id

        except Exception as e:
            self.logger.error(f"Experiment creation failed: {e}")
            raise

    async def run_experiment(
        self,
        experiment_id: str,
        algorithm: str = None,
        hyperparameters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Run ML experiment"""
        try:
            experiment = self.experiments.get(experiment_id)
            if not experiment:
                raise ValueError(f"Experiment not found: {experiment_id}")

            # Update experiment status
            experiment.status = ExperimentStatus.RUNNING
            experiment.started_at = datetime.now()

            # Load dataset
            dataset = self.datasets.get(experiment.dataset_id)
            if not dataset:
                raise ValueError(f"Dataset not found: {experiment.dataset_id}")

            df = await self._load_dataset(dataset.file_path)

            # Prepare data
            X, y = await self._prepare_data(df, dataset, experiment.model_type)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.config["model_validation_split"], random_state=42
            )

            # Select algorithm
            if not algorithm:
                algorithm = await self._select_best_algorithm(
                    X_train, y_train, experiment.model_type
                )

            # Get hyperparameters
            if not hyperparameters:
                hyperparameters = await self._optimize_hyperparameters(
                    X_train, y_train, experiment.model_type, algorithm
                )

            # Train model
            model, preprocessing_pipeline = await self._train_model(
                X_train, y_train, experiment.model_type, algorithm, hyperparameters
            )

            # Evaluate model
            metrics = await self._evaluate_model(
                model, preprocessing_pipeline, X_test, y_test, experiment.model_type
            )

            # Calculate feature importance
            feature_importance = await self._calculate_feature_importance(
                model, X.columns.tolist(), experiment.model_type
            )

            # Save model and artifacts
            model_path, preprocessing_path = await self._save_model_artifacts(
                experiment_id, model, preprocessing_pipeline
            )

            # Create model record
            model_id = await self._create_model_record(
                experiment,
                algorithm,
                hyperparameters,
                metrics,
                feature_importance,
                model_path,
                preprocessing_path,
            )

            # Update experiment
            experiment.metrics = metrics
            experiment.artifacts = {
                "model_path": model_path,
                "preprocessing_path": preprocessing_path,
            }
            experiment.status = ExperimentStatus.COMPLETED
            experiment.completed_at = datetime.now()
            experiment.duration_seconds = (
                experiment.completed_at - experiment.started_at
            ).total_seconds()

            result = {
                "experiment_id": experiment_id,
                "model_id": model_id,
                "algorithm": algorithm,
                "hyperparameters": hyperparameters,
                "metrics": metrics,
                "feature_importance": feature_importance,
                "duration_seconds": experiment.duration_seconds,
            }

            self.logger.info(f"Experiment completed: {experiment_id}")
            return result

        except Exception as e:
            # Update experiment with error
            if experiment_id in self.experiments:
                experiment = self.experiments[experiment_id]
                experiment.status = ExperimentStatus.FAILED
                experiment.error_message = str(e)
                experiment.completed_at = datetime.now()

            self.logger.error(f"Experiment failed: {e}")
            raise

    async def run_automl(
        self,
        dataset_id: str,
        target_column: str,
        model_type: ModelType,
        time_limit_minutes: int = 60,
    ) -> Dict[str, Any]:
        """Run automated machine learning"""
        try:
            automl_id = str(uuid.uuid4())

            # Load dataset
            dataset = self.datasets.get(dataset_id)
            if not dataset:
                raise ValueError(f"Dataset not found: {dataset_id}")

            df = await self._load_dataset(dataset.file_path)

            # Prepare data
            X, y = await self._prepare_data(df, dataset, model_type)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.config["model_validation_split"], random_state=42
            )

            # Get available algorithms
            algorithms = self.algorithms.get(model_type, {})

            best_model = None
            best_score = -np.inf
            best_algorithm = None
            best_params = None

            start_time = time.time()
            time_limit_seconds = time_limit_minutes * 60

            # Try different algorithms
            for algo_name, algo_class in algorithms.items():
                if time.time() - start_time > time_limit_seconds:
                    break

                try:
                    # Quick hyperparameter optimization
                    hyperparameters = await self._optimize_hyperparameters(
                        X_train, y_train, model_type, algo_name
                    )

                    # Train model
                    model, preprocessing_pipeline = await self._train_model(
                        X_train, y_train, model_type, algo_name, hyperparameters
                    )

                    # Evaluate model
                    metrics = await self._evaluate_model(
                        model, preprocessing_pipeline, X_test, y_test, model_type
                    )

                    # Get primary metric
                    if model_type == ModelType.CLASSIFICATION:
                        score = metrics.get("accuracy", 0)
                    elif model_type == ModelType.REGRESSION:
                        score = metrics.get("r2_score", 0)
                    else:
                        score = 0

                    if score > best_score:
                        best_score = score
                        best_model = model
                        best_algorithm = algo_name
                        best_params = hyperparameters

                except Exception as e:
                    self.logger.warning(f"AutoML algorithm {algo_name} failed: {e}")
                    continue

            if not best_model:
                raise ValueError("No successful models in AutoML run")

            # Create experiment for best model
            experiment_data = {
                "name": f"AutoML_{dataset.name}_{model_type.value}",
                "description": f"AutoML experiment for {dataset.name}",
                "model_type": model_type.value,
                "dataset_id": dataset_id,
                "parameters": best_params,
                "metadata": {
                    "automl_id": automl_id,
                    "time_limit_minutes": time_limit_minutes,
                },
            }

            experiment_id = await self.create_experiment(experiment_data)

            # Save best model
            model_path, preprocessing_path = await self._save_model_artifacts(
                experiment_id, best_model, None
            )

            # Calculate feature importance
            feature_importance = await self._calculate_feature_importance(
                best_model, X.columns.tolist(), model_type
            )

            # Evaluate on test set
            final_metrics = await self._evaluate_model(
                best_model, None, X_test, y_test, model_type
            )

            # Create model record
            model_id = await self._create_model_record(
                self.experiments[experiment_id],
                best_algorithm,
                best_params,
                final_metrics,
                feature_importance,
                model_path,
                preprocessing_path,
            )

            # Update experiment
            experiment = self.experiments[experiment_id]
            experiment.status = ExperimentStatus.COMPLETED
            experiment.metrics = final_metrics
            experiment.completed_at = datetime.now()
            experiment.duration_seconds = time.time() - start_time

            result = {
                "automl_id": automl_id,
                "experiment_id": experiment_id,
                "model_id": model_id,
                "best_algorithm": best_algorithm,
                "best_parameters": best_params,
                "metrics": final_metrics,
                "feature_importance": feature_importance,
                "duration_seconds": experiment.duration_seconds,
            }

            self.automl_jobs[automl_id] = result

            self.logger.info(f"AutoML completed: {automl_id}")
            return result

        except Exception as e:
            self.logger.error(f"AutoML failed: {e}")
            raise

    async def deploy_model(self, model_id: str, endpoint: str = None) -> str:
        """Deploy model to serving endpoint"""
        try:
            model = self.models.get(model_id)
            if not model:
                raise ValueError(f"Model not found: {model_id}")

            if not endpoint:
                endpoint = f"model_{model_id[:8]}"

            # Load model
            trained_model = joblib.load(model.model_path)
            preprocessing_pipeline = None
            if model.preprocessing_path:
                preprocessing_pipeline = joblib.load(model.preprocessing_path)

            # Store deployment info
            self.deployed_models[endpoint] = model_id

            # Update model status
            model.status = ModelStatus.DEPLOYED
            model.deployed_at = datetime.now()

            self.logger.info(f"Model deployed: {model_id} -> {endpoint}")
            return endpoint

        except Exception as e:
            self.logger.error(f"Model deployment failed: {e}")
            raise

    async def predict(
        self, endpoint: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make prediction using deployed model"""
        try:
            model_id = self.deployed_models.get(endpoint)
            if not model_id:
                raise ValueError(f"No model deployed at endpoint: {endpoint}")

            model = self.models.get(model_id)
            if not model:
                raise ValueError(f"Model not found: {model_id}")

            # Load model
            trained_model = joblib.load(model.model_path)

            # Prepare input data
            input_df = pd.DataFrame([input_data])

            # Apply preprocessing if available
            if model.preprocessing_path:
                preprocessing_pipeline = joblib.load(model.preprocessing_path)
                input_df = preprocessing_pipeline.transform(input_df)

            # Make prediction
            start_time = time.time()
            prediction = trained_model.predict(input_df)
            prediction_time = (time.time() - start_time) * 1000  # milliseconds

            # Get prediction probability if available
            prediction_proba = None
            if hasattr(trained_model, "predict_proba"):
                try:
                    prediction_proba = trained_model.predict_proba(input_df).tolist()
                except:
                    pass

            # Log prediction
            prediction_log = {
                "model_id": model_id,
                "endpoint": endpoint,
                "input_data": input_data,
                "prediction": prediction.tolist(),
                "prediction_proba": prediction_proba,
                "prediction_time_ms": prediction_time,
                "timestamp": datetime.now(),
            }
            self.prediction_logs.append(prediction_log)

            result = {
                "prediction": prediction.tolist(),
                "prediction_proba": prediction_proba,
                "model_id": model_id,
                "prediction_time_ms": prediction_time,
            }

            return result

        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            raise

    async def get_ml_dashboard(self) -> Dict[str, Any]:
        """Get ML operations dashboard"""
        try:
            # Recent activity
            recent_experiments = [
                exp
                for exp in self.experiments.values()
                if (datetime.now() - exp.created_at).total_seconds() < 86400
            ]

            recent_predictions = [
                log
                for log in self.prediction_logs
                if (datetime.now() - log["timestamp"]).total_seconds() < 3600
            ]

            # Model performance summary
            model_performance_summary = {}
            for model_id, performances in self.performance_history.items():
                if performances:
                    latest = performances[-1]
                    model_performance_summary[model_id] = {
                        "avg_latency_ms": latest.latency_ms,
                        "predictions_count": latest.predictions_count,
                        "last_measured": latest.measured_at.isoformat(),
                    }

            return {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_datasets": len(self.datasets),
                    "total_experiments": len(self.experiments),
                    "total_models": len(self.models),
                    "deployed_models": len(self.deployed_models),
                    "active_pipelines": len(
                        [p for p in self.pipelines.values() if p.is_active]
                    ),
                },
                "recent_activity": {
                    "experiments_24h": len(recent_experiments),
                    "predictions_1h": len(recent_predictions),
                    "completed_experiments": len(
                        [
                            exp
                            for exp in recent_experiments
                            if exp.status == ExperimentStatus.COMPLETED
                        ]
                    ),
                    "failed_experiments": len(
                        [
                            exp
                            for exp in recent_experiments
                            if exp.status == ExperimentStatus.FAILED
                        ]
                    ),
                },
                "model_performance": model_performance_summary,
                "system_metrics": getattr(self, "system_metrics", {}),
                "drift_alerts": len(
                    [
                        drift
                        for drifts in self.data_drift_results.values()
                        for drift in drifts
                        if drift.is_drift
                        and (datetime.now() - drift.detected_at).total_seconds() < 86400
                    ]
                ),
            }

        except Exception as e:
            self.logger.error(f"ML dashboard generation failed: {e}")
            return {"error": str(e)}

    # Supporting methods (simplified versions)
    async def _load_dataset(self, file_path: str) -> pd.DataFrame:
        """Load dataset from file"""
        try:
            if file_path.endswith(".csv"):
                return pd.read_csv(file_path)
            elif file_path.endswith(".json"):
                return pd.read_json(file_path)
            elif file_path.endswith(".xlsx"):
                return pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
        except Exception as e:
            self.logger.error(f"Dataset loading failed: {e}")
            raise

    async def _analyze_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze dataset and extract metadata"""
        try:
            categorical_columns = []
            numerical_columns = []

            for col in df.columns:
                if df[col].dtype in ["object", "category"]:
                    categorical_columns.append(col)
                elif df[col].dtype in ["int64", "float64"]:
                    numerical_columns.append(col)

            missing_values = df.isnull().sum().to_dict()
            data_types = df.dtypes.astype(str).to_dict()

            statistics = {
                "numerical_stats": df.describe().to_dict() if numerical_columns else {},
                "categorical_stats": {},
                "correlation_matrix": df.corr().to_dict() if numerical_columns else {},
            }

            return {
                "categorical_columns": categorical_columns,
                "numerical_columns": numerical_columns,
                "missing_values": missing_values,
                "data_types": data_types,
                "statistics": statistics,
            }
        except Exception as e:
            self.logger.error(f"Dataset analysis failed: {e}")
            return {}

    async def _prepare_data(
        self, df: pd.DataFrame, dataset: Dataset, model_type: ModelType
    ):
        """Prepare data for training"""
        if dataset.target_column and dataset.target_column in df.columns:
            y = df[dataset.target_column]
            X = df.drop(columns=[dataset.target_column])
        else:
            y = None
            X = df

        # Basic preprocessing
        for col in X.columns:
            if X[col].isnull().sum() > 0:
                if X[col].dtype in ["int64", "float64"]:
                    X[col].fillna(X[col].median(), inplace=True)
                else:
                    X[col].fillna(
                        X[col].mode()[0] if len(X[col].mode()) > 0 else "unknown",
                        inplace=True,
                    )

        return X, y

    async def _select_best_algorithm(self, X, y, model_type: ModelType) -> str:
        """Select best algorithm"""
        algorithms = self.algorithms.get(model_type, {})
        return list(algorithms.keys())[0] if algorithms else "random_forest"

    async def _optimize_hyperparameters(
        self, X, y, model_type, algorithm
    ) -> Dict[str, Any]:
        """Basic hyperparameter optimization"""
        return {}

    async def _train_model(self, X, y, model_type, algorithm, hyperparameters):
        """Train a basic model"""
        algorithms = self.algorithms.get(model_type, {})
        algo_class = algorithms.get(algorithm, RandomForestClassifier)
        model = algo_class(**hyperparameters)
        model.fit(X, y)
        return model, None

    async def _evaluate_model(self, model, preprocessing, X_test, y_test, model_type):
        """Basic model evaluation"""
        predictions = model.predict(X_test)
        if model_type == ModelType.CLASSIFICATION:
            accuracy = accuracy_score(y_test, predictions)
            return {"accuracy": accuracy}
        else:
            return {"score": 0.8}  # Placeholder

    async def _calculate_feature_importance(self, model, features, model_type):
        """Basic feature importance"""
        return {}

    async def _save_model_artifacts(self, experiment_id, model, preprocessing):
        """Save model artifacts"""
        model_path = f"ml_experiments/{experiment_id}/model.pkl"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)
        return model_path, None

    async def _create_model_record(
        self,
        experiment,
        algorithm,
        params,
        metrics,
        importance,
        model_path,
        preprocessing_path,
    ):
        """Create model record"""
        model_id = str(uuid.uuid4())
        model = Model(
            model_id=model_id,
            name=f"{experiment.name}_{algorithm}",
            model_type=experiment.model_type,
            algorithm=algorithm,
            experiment_id=experiment.experiment_id,
            dataset_id=experiment.dataset_id,
            version="1.0.0",
            parameters=params,
            metrics=metrics,
            feature_importance=importance,
            model_path=model_path,
            preprocessing_path=preprocessing_path,
            status=ModelStatus.TRAINED,
            created_at=datetime.now(),
            deployed_at=None,
            performance_history=[],
            metadata={},
        )
        self.models[model_id] = model
        return model_id

    async def _update_feature_store(self, dataset_id, df):
        """Update feature store"""
        pass  # Simplified implementation

    # Background tasks (simplified)
    async def _model_monitoring(self):
        """Monitor deployed models"""
        pass

    async def _drift_detection(self):
        """Periodic drift detection"""
        pass

    async def _pipeline_scheduler(self):
        """Schedule and run pipelines"""
        pass

    async def _performance_tracker(self):
        """Track system performance"""
        pass

    async def _cleanup_manager(self):
        """Clean up old data"""
        pass

    async def _auto_retraining(self):
        """Automatic model retraining"""
        pass

    async def _setup_directories(self):
        """Setup required directories"""
        for dir_name in ["ml_data", "ml_models", "ml_experiments", "ml_artifacts"]:
            os.makedirs(dir_name, exist_ok=True)

    async def _load_existing_data(self):
        """Load existing data"""
        pass

    async def _initialize_feature_store(self):
        """Initialize feature store"""
        pass
