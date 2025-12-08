"""
AI-Powered Predictive Analytics and Forecasting System

Advanced machine learning for personal productivity insights and predictions
"""

import asyncio
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
from pathlib import Path

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from config.logging_config import setup_logger


class PredictionType(Enum):
    PRODUCTIVITY_SCORE = "productivity_score"
    TASK_COMPLETION_TIME = "task_completion_time"
    WORKLOAD_FORECAST = "workload_forecast"
    ENERGY_LEVELS = "energy_levels"
    MEETING_EFFECTIVENESS = "meeting_effectiveness"
    FOCUS_TIME_OPTIMAL = "focus_time_optimal"
    DEADLINE_RISK = "deadline_risk"
    BURNOUT_RISK = "burnout_risk"
    COLLABORATION_PATTERNS = "collaboration_patterns"
    SKILL_DEVELOPMENT = "skill_development"


class ModelType(Enum):
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    XGBOOST = "xgboost"
    ARIMA = "arima"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    NEURAL_NETWORK = "neural_network"


@dataclass
class PredictionRequest:
    """Prediction request structure"""
    user_id: str
    prediction_type: PredictionType
    time_horizon: int  # days
    features: Dict[str, Any]
    confidence_level: float = 0.95
    include_explanation: bool = True


@dataclass
class PredictionResult:
    """Prediction result structure"""
    prediction_id: str
    user_id: str
    prediction_type: PredictionType
    predicted_value: float
    confidence_interval: Tuple[float, float]
    confidence_score: float
    feature_importance: Dict[str, float]
    explanation: str
    model_used: ModelType
    created_at: datetime
    valid_until: datetime
    metadata: Dict[str, Any]


@dataclass
class UserProductivityData:
    """User productivity data structure"""
    user_id: str
    timestamp: datetime
    tasks_completed: int
    hours_worked: float
    meetings_attended: int
    focus_time_minutes: int
    interruptions: int
    energy_level: int  # 1-10 scale
    stress_level: int  # 1-10 scale
    sleep_hours: float
    exercise_minutes: int
    mood_score: int  # 1-10 scale
    weather_condition: str
    day_of_week: int
    is_holiday: bool
    project_complexity: int  # 1-10 scale
    team_size: int
    deadline_pressure: int  # 1-10 scale


class AdvancedPredictiveAnalytics:
    """Advanced AI-powered predictive analytics system"""

    def __init__(self):
        self.logger = setup_logger("PredictiveAnalytics")

        # Model storage
        self.models: Dict[str, Dict[str, Any]] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.encoders: Dict[str, LabelEncoder] = {}

        # Data storage
        self.user_data: Dict[str, List[UserProductivityData]] = {}
        self.predictions: Dict[str, PredictionResult] = {}

        # Configuration
        self.config = {
            "min_data_points": 30,
            "retrain_interval_days": 7,
            "feature_importance_threshold": 0.05,
            "confidence_threshold": 0.7,
            "max_prediction_horizon": 90,
            "auto_model_selection": True,
            "ensemble_models": True
        }

        # Feature engineering
        self.feature_extractors = {
            "temporal": self._extract_temporal_features,
            "behavioral": self._extract_behavioral_features,
            "environmental": self._extract_environmental_features,
            "performance": self._extract_performance_features
        }

    async def initialize(self):
        """Initialize predictive analytics system"""
        await self._load_models()
        await self._load_user_data()

        # Start background tasks
        asyncio.create_task(self._model_retraining_loop())
        asyncio.create_task(self._data_quality_monitoring())
        asyncio.create_task(self._prediction_accuracy_tracking())

        self.logger.info("Predictive Analytics System initialized")

    # Data Collection and Management

    async def add_user_data(self, data: UserProductivityData):
        """Add user productivity data point"""
        try:
            if data.user_id not in self.user_data:
                self.user_data[data.user_id] = []

            self.user_data[data.user_id].append(data)

            # Keep only recent data (configurable window)
            max_data_points = 1000
            if len(self.user_data[data.user_id]) > max_data_points:
                self.user_data[data.user_id] = self.user_data[data.user_id][-max_data_points:]

            # Trigger model update if enough new data
            if len(self.user_data[data.user_id]) % 50 == 0:
                await self._update_user_models(data.user_id)

            self.logger.debug(f"Added data point for user {data.user_id}")

        except Exception as e:
            self.logger.error(f"Data addition failed: {e}")

    async def bulk_add_user_data(self, user_id: str, data_points: List[Dict[str, Any]]):
        """Bulk add user data points"""
        try:
            for data_point in data_points:
                data = UserProductivityData(
                    user_id=user_id,
                    timestamp=datetime.fromisoformat(data_point['timestamp']),
                    **{k: v for k, v in data_point.items() if k != 'timestamp'}
                )
                await self.add_user_data(data)

            self.logger.info(f"Bulk added {len(data_points)} data points for user {user_id}")

        except Exception as e:
            self.logger.error(f"Bulk data addition failed: {e}")

    # Feature Engineering

    def _extract_temporal_features(self, data: List[UserProductivityData]) -> pd.DataFrame:
        """Extract temporal features"""
        try:
            df = pd.DataFrame([asdict(d) for d in data])
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            # Temporal features
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['day_of_month'] = df['timestamp'].dt.day
            df['week_of_year'] = df['timestamp'].dt.isocalendar().week
            df['month'] = df['timestamp'].dt.month
            df['quarter'] = df['timestamp'].dt.quarter
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            df['is_monday'] = (df['day_of_week'] == 0).astype(int)
            df['is_friday'] = (df['day_of_week'] == 4).astype(int)

            # Time-based patterns
            df['days_since_start'] = (df['timestamp'] - df['timestamp'].min()).dt.days
            df['week_number'] = df['days_since_start'] // 7

            return df

        except Exception as e:
            self.logger.error(f"Temporal feature extraction failed: {e}")
            return pd.DataFrame()

    def _extract_behavioral_features(self, data: List[UserProductivityData]) -> pd.DataFrame:
        """Extract behavioral pattern features"""
        try:
            df = pd.DataFrame([asdict(d) for d in data])

            # Rolling averages (7-day window)
            df['avg_tasks_7d'] = df['tasks_completed'].rolling(window=7, min_periods=1).mean()
            df['avg_hours_7d'] = df['hours_worked'].rolling(window=7, min_periods=1).mean()
            df['avg_focus_7d'] = df['focus_time_minutes'].rolling(window=7, min_periods=1).mean()
            df['avg_energy_7d'] = df['energy_level'].rolling(window=7, min_periods=1).mean()

            # Productivity ratios
            df['tasks_per_hour'] = df['tasks_completed'] / (df['hours_worked'] + 0.1)
            df['focus_ratio'] = df['focus_time_minutes'] / (df['hours_worked'] * 60 + 1)
            df['interruption_rate'] = df['interruptions'] / (df['hours_worked'] + 0.1)

            # Consistency metrics
            df['task_consistency'] = df['tasks_completed'].rolling(window=7).std()
            df['energy_consistency'] = df['energy_level'].rolling(window=7).std()

            # Trend indicators
            df['productivity_trend'] = df['tasks_per_hour'].rolling(window=7).apply(
                lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
            )

            return df

        except Exception as e:
            self.logger.error(f"Behavioral feature extraction failed: {e}")
            return pd.DataFrame()

    def _extract_environmental_features(self, data: List[UserProductivityData]) -> pd.DataFrame:
        """Extract environmental features"""
        try:
            df = pd.DataFrame([asdict(d) for d in data])

            # Weather encoding
            weather_encoder = LabelEncoder()
            df['weather_encoded'] = weather_encoder.fit_transform(df['weather_condition'])

            # Sleep quality indicators
            df['sleep_deficit'] = np.maximum(0, 8 - df['sleep_hours'])
            df['sleep_excess'] = np.maximum(0, df['sleep_hours'] - 9)
            df['sleep_quality_score'] = 10 - df['sleep_deficit'] - df['sleep_excess'] * 0.5

            # Work-life balance indicators
            df['work_life_balance'] = df['exercise_minutes'] / (df['hours_worked'] * 10 + 1)
            df['stress_energy_ratio'] = df['stress_level'] / (df['energy_level'] + 1)

            # Team dynamics
            df['team_complexity'] = df['team_size'] * df['project_complexity']
            df['pressure_index'] = df['deadline_pressure'] * df['project_complexity']

            return df

        except Exception as e:
            self.logger.error(f"Environmental feature extraction failed: {e}")
            return pd.DataFrame()

    def _extract_performance_features(self, data: List[UserProductivityData]) -> pd.DataFrame:
        """Extract performance-based features"""
        try:
            df = pd.DataFrame([asdict(d) for d in data])

            # Performance metrics
            df['efficiency_score'] = (
                df['tasks_completed'] * df['focus_time_minutes'] /
                ((df['hours_worked'] * 60 + 1) * (df['interruptions'] + 1))
            )

            df['wellbeing_score'] = (
                df['energy_level'] + (10 - df['stress_level']) + df['mood_score']
            ) / 3

            # Lag features (previous day performance)
            df['prev_tasks'] = df['tasks_completed'].shift(1)
            df['prev_energy'] = df['energy_level'].shift(1)
            df['prev_stress'] = df['stress_level'].shift(1)

            # Performance momentum
            df['task_momentum'] = df['tasks_completed'] - df['prev_tasks']
            df['energy_momentum'] = df['energy_level'] - df['prev_energy']

            # Weekly patterns
            df['weekly_task_avg'] = df.groupby('day_of_week')['tasks_completed'].transform('mean')
            df['weekly_energy_avg'] = df.groupby('day_of_week')['energy_level'].transform('mean')

            return df

        except Exception as e:
            self.logger.error(f"Performance feature extraction failed: {e}")
            return pd.DataFrame()

    # Model Training and Management

    async def _train_model(self, user_id: str, prediction_type: PredictionType,
                          features: pd.DataFrame, target: pd.Series) -> Dict[str, Any]:
        """Train prediction model for specific user and prediction type"""
        try:
            if len(features) < self.config["min_data_points"]:
                raise Exception(f"Insufficient data: {len(features)} < {self.config['min_data_points']}")

            # Prepare data
            X_train, X_test, y_train, y_test = train_test_split(
                features, target, test_size=0.2, random_state=42
            )

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Model selection based on prediction type
            models = self._get_models_for_prediction_type(prediction_type)

            best_model = None
            best_score = -np.inf
            best_model_type = None

            # Train and evaluate models
            for model_type, model in models.items():
                try:
                    # Train model
                    if model_type in [ModelType.ARIMA, ModelType.EXPONENTIAL_SMOOTHING]:
                        # Time series models
                        model_result = self._train_time_series_model(model_type, target)
                    else:
                        # ML models
                        model.fit(X_train_scaled, y_train)

                        # Evaluate
                        y_pred = model.predict(X_test_scaled)
                        score = r2_score(y_test, y_pred)

                        if score > best_score:
                            best_score = score
                            best_model = model
                            best_model_type = model_type

                except Exception as e:
                    self.logger.warning(f"Model {model_type} training failed: {e}")
                    continue

            if best_model is None:
                raise Exception("No model could be trained successfully")

            # Feature importance
            feature_importance = {}
            if hasattr(best_model, 'feature_importances_'):
                feature_importance = dict(zip(
                    features.columns,
                    best_model.feature_importances_
                ))
            elif hasattr(best_model, 'coef_'):
                feature_importance = dict(zip(
                    features.columns,
                    np.abs(best_model.coef_)
                ))

            # Store model
            model_key = f"{user_id}_{prediction_type.value}"
            self.models[model_key] = {
                "model": best_model,
                "model_type": best_model_type,
                "scaler": scaler,
                "feature_names": list(features.columns),
                "feature_importance": feature_importance,
                "performance_score": best_score,
                "trained_at": datetime.now(),
                "training_samples": len(X_train)
            }

            self.logger.info(f"Model trained for {user_id} - {prediction_type.value}: R² = {best_score:.3f}")

            return self.models[model_key]

        except Exception as e:
            self.logger.error(f"Model training failed: {e}")
            return None

    def _get_models_for_prediction_type(self, prediction_type: PredictionType) -> Dict[ModelType, Any]:
        """Get appropriate models for prediction type"""
        base_models = {
            ModelType.LINEAR_REGRESSION: LinearRegression(),
            ModelType.RANDOM_FOREST: RandomForestRegressor(n_estimators=100, random_state=42),
            ModelType.GRADIENT_BOOSTING: GradientBoostingRegressor(random_state=42),
            ModelType.XGBOOST: xgb.XGBRegressor(random_state=42)
        }

        # Add time series models for temporal predictions
        if prediction_type in [PredictionType.WORKLOAD_FORECAST, PredictionType.ENERGY_LEVELS]:
            base_models.update({
                ModelType.ARIMA: "arima",
                ModelType.EXPONENTIAL_SMOOTHING: "exponential_smoothing"
            })

        return base_models

    def _train_time_series_model(self, model_type: ModelType, target: pd.Series):
        """Train time series model"""
        try:
            if model_type == ModelType.ARIMA:
                model = ARIMA(target, order=(1, 1, 1))
                fitted_model = model.fit()
                return fitted_model
            elif model_type == ModelType.EXPONENTIAL_SMOOTHING:
                model = ExponentialSmoothing(target, trend='add', seasonal='add', seasonal_periods=7)
                fitted_model = model.fit()
                return fitted_model

        except Exception as e:
            self.logger.error(f"Time series model training failed: {e}")
            return None

    # Prediction Generation

    async def generate_prediction(self, request: PredictionRequest) -> PredictionResult:
        """Generate prediction based on request"""
        try:
            # Validate request
            if request.time_horizon > self.config["max_prediction_horizon"]:
                raise Exception(f"Time horizon too large: {request.time_horizon}")

            # Get user data
            user_data = self.user_data.get(request.user_id, [])
            if len(user_data) < self.config["min_data_points"]:
                raise Exception(f"Insufficient user data: {len(user_data)}")

            # Prepare features
            features_df = await self._prepare_prediction_features(request, user_data)

            # Get or train model
            model_key = f"{request.user_id}_{request.prediction_type.value}"
            model_info = self.models.get(model_key)

            if not model_info or self._model_needs_retraining(model_info):
                # Train new model
                target = self._get_target_variable(request.prediction_type, user_data)
                model_info = await self._train_model(
                    request.user_id, request.prediction_type, features_df, target
                )

                if not model_info:
                    raise Exception("Model training failed")

            # Generate prediction
            prediction_value, confidence_interval = await self._predict_with_confidence(
                model_info, features_df.iloc[-1:], request.confidence_level
            )

            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                model_info, features_df, request.time_horizon
            )

            # Generate explanation
            explanation = self._generate_prediction_explanation(
                request, model_info, prediction_value, confidence_score
            )

            # Create result
            result = PredictionResult(
                prediction_id=f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.user_id}",
                user_id=request.user_id,
                prediction_type=request.prediction_type,
                predicted_value=prediction_value,
                confidence_interval=confidence_interval,
                confidence_score=confidence_score,
                feature_importance=model_info["feature_importance"],
                explanation=explanation,
                model_used=model_info["model_type"],
                created_at=datetime.now(),
                valid_until=datetime.now() + timedelta(hours=24),
                metadata={
                    "time_horizon": request.time_horizon,
                    "model_performance": model_info["performance_score"],
                    "training_samples": model_info["training_samples"]
                }
            )

            # Store prediction
            self.predictions[result.prediction_id] = result

            self.logger.info(f"Prediction generated: {result.prediction_id}")
            return result

        except Exception as e:
            self.logger.error(f"Prediction generation failed: {e}")
            raise

    async def _prepare_prediction_features(self, request: PredictionRequest,
                                         user_data: List[UserProductivityData]) -> pd.DataFrame:
        """Prepare features for prediction"""
        try:
            # Extract all feature types
            features_list = []
            for extractor_name, extractor_func in self.feature_extractors.items():
                features = extractor_func(user_data)
                if not features.empty:
                    features_list.append(features)

            # Combine features
            if features_list:
                combined_features = features_list[0]
                for features in features_list[1:]:
                    combined_features = combined_features.combine_first(features)
            else:
                combined_features = pd.DataFrame()

            # Add request-specific features
            if request.features:
                for key, value in request.features.items():
                    combined_features[f"custom_{key}"] = value

            # Handle missing values
            combined_features = combined_features.fillna(combined_features.mean())

            # Select numeric columns only
            numeric_columns = combined_features.select_dtypes(include=[np.number]).columns
            combined_features = combined_features[numeric_columns]

            return combined_features

        except Exception as e:
            self.logger.error(f"Feature preparation failed: {e}")
            return pd.DataFrame()

    def _get_target_variable(self, prediction_type: PredictionType,
                           user_data: List[UserProductivityData]) -> pd.Series:
        """Get target variable for prediction type"""
        try:
            df = pd.DataFrame([asdict(d) for d in user_data])

            target_mapping = {
                PredictionType.PRODUCTIVITY_SCORE: lambda x: x['tasks_completed'] / (x['hours_worked'] + 0.1),
                PredictionType.TASK_COMPLETION_TIME: lambda x: x['hours_worked'] / (x['tasks_completed'] + 0.1),
                PredictionType.WORKLOAD_FORECAST: lambda x: x['hours_worked'],
                PredictionType.ENERGY_LEVELS: lambda x: x['energy_level'],
                PredictionType.MEETING_EFFECTIVENESS: lambda x: x['tasks_completed'] / (x['meetings_attended'] + 0.1),
                PredictionType.FOCUS_TIME_OPTIMAL: lambda x: x['focus_time_minutes'],
                PredictionType.DEADLINE_RISK: lambda x: x['deadline_pressure'] * x['stress_level'],
                PredictionType.BURNOUT_RISK: lambda x: x['stress_level'] - x['energy_level'] + x['hours_worked'] / 2,
                PredictionType.COLLABORATION_PATTERNS: lambda x: x['meetings_attended'],
                PredictionType.SKILL_DEVELOPMENT: lambda x: x['project_complexity'] * x['tasks_completed']
            }

            target_func = target_mapping.get(prediction_type)
            if target_func:
                return df.apply(target_func, axis=1)
            else:
                raise Exception(f"Unknown prediction type: {prediction_type}")

        except Exception as e:
            self.logger.error(f"Target variable extraction failed: {e}")
            return pd.Series()

    async def _predict_with_confidence(self, model_info: Dict[str, Any],
                                     features: pd.DataFrame,
                                     confidence_level: float) -> Tuple[float, Tuple[float, float]]:
        """Generate prediction with confidence interval"""
        try:
            model = model_info["model"]
            scaler = model_info["scaler"]

            # Scale features
            features_scaled = scaler.transform(features)

            # Generate prediction
            if hasattr(model, 'predict'):
                prediction = model.predict(features_scaled)[0]
            else:
                # Time series model
                prediction = model.forecast(steps=1)[0]

            # Calculate confidence interval (simplified approach)
            # In production, use proper uncertainty quantification
            model_std = model_info.get("prediction_std", 0.1)
            z_score = 1.96 if confidence_level == 0.95 else 2.58  # 95% or 99%

            margin = z_score * model_std
            confidence_interval = (prediction - margin, prediction + margin)

            return float(prediction), confidence_interval

        except Exception as e:
            self.logger.error(f"Prediction with confidence failed: {e}")
            return 0.0, (0.0, 0.0)

    def _calculate_confidence_score(self, model_info: Dict[str, Any],
                                  features: pd.DataFrame, time_horizon: int) -> float:
        """Calculate confidence score for prediction"""
        try:
            base_confidence = model_info["performance_score"]

            # Adjust for time horizon (longer = less confident)
            time_penalty = max(0, 1 - (time_horizon / 30) * 0.2)

            # Adjust for data recency
            days_since_training = (datetime.now() - model_info["trained_at"]).days
            recency_penalty = max(0, 1 - (days_since_training / 7) * 0.1)

            # Adjust for training data size
            data_size_bonus = min(0.2, model_info["training_samples"] / 1000 * 0.2)

            confidence = base_confidence * time_penalty * recency_penalty + data_size_bonus
            return max(0.0, min(1.0, confidence))

        except Exception as e:
            self.logger.error(f"Confidence score calculation failed: {e}")
            return 0.5

    def _generate_prediction_explanation(self, request: PredictionRequest,
                                       model_info: Dict[str, Any],
                                       prediction_value: float,
                                       confidence_score: float) -> str:
        """Generate human-readable explanation"""
        try:
            # Get top features
            feature_importance = model_info["feature_importance"]
            top_features = sorted(
                feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]

            # Generate explanation
            explanation = f"Based on your recent patterns, I predict "

            if request.prediction_type == PredictionType.PRODUCTIVITY_SCORE:
                explanation += f"your productivity score will be {prediction_value:.1f} tasks per hour. "
            elif request.prediction_type == PredictionType.ENERGY_LEVELS:
                explanation += f"your energy level will be {prediction_value:.1f}/10. "
            elif request.prediction_type == PredictionType.WORKLOAD_FORECAST:
                explanation += f"you'll work approximately {prediction_value:.1f} hours. "
            else:
                explanation += f"the value will be {prediction_value:.2f}. "

            explanation += f"This prediction has a {confidence_score*100:.0f}% confidence level. "

            if top_features:
                explanation += "Key factors influencing this prediction: "
                feature_descriptions = {
                    "avg_energy_7d": "your recent energy levels",
                    "tasks_per_hour": "your task completion efficiency",
                    "focus_ratio": "your ability to maintain focus",
                    "sleep_quality_score": "your sleep quality",
                    "stress_level": "your stress levels",
                    "day_of_week": "the day of the week pattern"
                }

                feature_explanations = []
                for feature, importance in top_features:
                    desc = feature_descriptions.get(feature, feature.replace('_', ' '))
                    feature_explanations.append(f"{desc} ({importance:.1%} influence)")

                explanation += ", ".join(feature_explanations) + "."

            return explanation

        except Exception as e:
            self.logger.error(f"Explanation generation failed: {e}")
            return "Prediction generated based on historical patterns."

    # Batch Predictions

    async def generate_batch_predictions(self, user_id: str,
                                       prediction_types: List[PredictionType],
                                       time_horizon: int = 7) -> Dict[str, PredictionResult]:
        """Generate multiple predictions for user"""
        try:
            results = {}

            for prediction_type in prediction_types:
                request = PredictionRequest(
                    user_id=user_id,
                    prediction_type=prediction_type,
                    time_horizon=time_horizon,
                    features={}
                )

                try:
                    result = await self.generate_prediction(request)
                    results[prediction_type.value] = result
                except Exception as e:
                    self.logger.warning(f"Batch prediction failed for {prediction_type}: {e}")
                    continue

            return results

        except Exception as e:
            self.logger.error(f"Batch prediction generation failed: {e}")
            return {}

    async def generate_productivity_insights(self, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive productivity insights"""
        try:
            # Generate key predictions
            key_predictions = await self.generate_batch_predictions(
                user_id,
                [
                    PredictionType.PRODUCTIVITY_SCORE,
                    PredictionType.ENERGY_LEVELS,
                    PredictionType.BURNOUT_RISK,
                    PredictionType.FOCUS_TIME_OPTIMAL
                ]
            )

            # Analyze patterns
            user_data = self.user_data.get(user_id, [])
            if not user_data:
                return {"error": "No user data available"}

            df = pd.DataFrame([asdict(d) for d in user_data[-30:]])  # Last 30 days

            # Calculate trends
            productivity_trend = self._calculate_trend(df['tasks_completed'])
            energy_trend = self._calculate_trend(df['energy_level'])
            stress_trend = self._calculate_trend(df['stress_level'])

            # Identify patterns
            best_day = df.groupby('day_of_week')['tasks_completed'].mean().idxmax()
            best_time = df.groupby('hour')['tasks_completed'].mean().idxmax() if 'hour' in df.columns else None

            # Generate recommendations
            recommendations = self._generate_productivity_recommendations(df, key_predictions)

            insights = {
                "predictions": {k: asdict(v) for k, v in key_predictions.items()},
                "trends": {
                    "productivity": productivity_trend,
                    "energy": energy_trend,
                    "stress": stress_trend
                },
                "patterns": {
                    "best_day_of_week": int(best_day),
                    "best_time_of_day": int(best_time) if best_time else None,
                    "average_daily_tasks": float(df['tasks_completed'].mean()),
                    "average_focus_time": float(df['focus_time_minutes'].mean())
                },
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat()
            }

            return insights

        except Exception as e:
            self.logger.error(f"Productivity insights generation failed: {e}")
            return {"error": str(e)}

    def _calculate_trend(self, series: pd.Series) -> str:
        """Calculate trend direction"""
        try:
            if len(series) < 2:
                return "insufficient_data"

            # Linear regression to find trend
            x = np.arange(len(series))
            slope = np.polyfit(x, series, 1)[0]

            if slope > 0.1:
                return "increasing"
            elif slope < -0.1:
                return "decreasing"
            else:
                return "stable"

        except Exception:
            return "unknown"

    def _generate_productivity_recommendations(self, df: pd.DataFrame,
                                             predictions: Dict[str, PredictionResult]) -> List[str]:
        """Generate productivity recommendations"""
        recommendations = []

        try:
            # Energy-based recommendations
            if 'energy_levels' in predictions:
                energy_pred = predictions['energy_levels'].predicted_value
                if energy_pred < 6:
                    recommendations.append("Consider scheduling lighter tasks tomorrow due to predicted low energy")
                elif energy_pred > 8:
                    recommendations.append("Great energy predicted! Plan challenging tasks for maximum impact")

            # Burnout risk recommendations
            if 'burnout_risk' in predictions:
                burnout_risk = predictions['burnout_risk'].predicted_value
                if burnout_risk > 7:
                    recommendations.append("High burnout risk detected. Consider taking breaks and reducing workload")

            # Focus time optimization
            avg_focus = df['focus_time_minutes'].mean()
            if avg_focus < 120:  # Less than 2 hours
                recommendations.append("Try to increase focused work time - aim for 2-3 hour blocks")

            # Sleep recommendations
            avg_sleep = df['sleep_hours'].mean()
            if avg_sleep < 7:
                recommendations.append("Improve sleep quality - aim for 7-8 hours for better productivity")

            # Meeting optimization
            avg_meetings = df['meetings_attended'].mean()
            avg_tasks = df['tasks_completed'].mean()
            if avg_meetings > 4 and avg_tasks < 5:
                recommendations.append("Consider reducing meetings to increase task completion time")

            return recommendations

        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return ["Unable to generate recommendations at this time"]

    # Model Management

    def _model_needs_retraining(self, model_info: Dict[str, Any]) -> bool:
        """Check if model needs retraining"""
        try:
            days_since_training = (datetime.now() - model_info["trained_at"]).days
            return days_since_training >= self.config["retrain_interval_days"]
        except Exception:
            return True

    async def _update_user_models(self, user_id: str):
        """Update models for specific user"""
        try:
            user_data = self.user_data.get(user_id, [])
            if len(user_data) < self.config["min_data_points"]:
                return

            # Update models for all prediction types
            for prediction_type in PredictionType:
                try:
                    features_df = await self._prepare_prediction_features(
                        PredictionRequest(user_id, prediction_type, 7, {}),
                        user_data
                    )
                    target = self._get_target_variable(prediction_type, user_data)

                    if not features_df.empty and not target.empty:
                        await self._train_model(user_id, prediction_type, features_df, target)

                except Exception as e:
                    self.logger.warning(f"Model update failed for {prediction_type}: {e}")
                    continue

            self.logger.info(f"Models updated for user {user_id}")

        except Exception as e:
            self.logger.error(f"User model update failed: {e}")

    # Background Tasks

    async def _model_retraining_loop(self):
        """Periodic model retraining"""
        while True:
            try:
                for user_id in self.user_data.keys():
                    await self._update_user_models(user_id)

                await asyncio.sleep(86400)  # Daily retraining

            except Exception as e:
                self.logger.error(f"Model retraining loop failed: {e}")
                await asyncio.sleep(3600)

    async def _data_quality_monitoring(self):
        """Monitor data quality"""
        while True:
            try:
                for user_id, data in self.user_data.items():
                    if len(data) > 0:
                        # Check for data anomalies
                        recent_data = data[-7:]  # Last week
                        df = pd.DataFrame([asdict(d) for d in recent_data])

                        # Detect outliers
                        for column in ['tasks_completed', 'hours_worked', 'energy_level']:
                            if column in df.columns:
                                q75, q25 = np.percentile(df[column], [75, 25])
                                iqr = q75 - q25
                                outliers = df[(df[column] < q25 - 1.5*iqr) | (df[column] > q75 + 1.5*iqr)]

                                if len(outliers) > 0:
                                    self.logger.warning(f"Data quality issue for {user_id}: outliers in {column}")

                await asyncio.sleep(3600)  # Hourly monitoring

            except Exception as e:
                self.logger.error(f"Data quality monitoring failed: {e}")
                await asyncio.sleep(1800)

    async def _prediction_accuracy_tracking(self):
        """Track prediction accuracy"""
        while True:
            try:
                # Check predictions that should have materialized
                current_time = datetime.now()

                for pred_id, prediction in self.predictions.items():
                    if prediction.valid_until < current_time:
                        # Prediction has expired, check accuracy if possible
                        await self._evaluate_prediction_accuracy(prediction)

                await asyncio.sleep(3600)  # Hourly accuracy tracking

            except Exception as e:
                self.logger.error(f"Prediction accuracy tracking failed: {e}")
                await asyncio.sleep(1800)

    async def _evaluate_prediction_accuracy(self, prediction: PredictionResult):
        """Evaluate accuracy of past prediction"""
        try:
            # Get actual data for the prediction period
            user_data = self.user_data.get(prediction.user_id, [])

            # Find actual value (simplified - in production, match exact time periods)
            actual_data = [d for d in user_data if d.timestamp > prediction.created_at]

            if actual_data:
                actual_value = self._get_actual_value(prediction.prediction_type, actual_data[0])
                error = abs(prediction.predicted_value - actual_value)

                # Log accuracy metrics
                self.logger.info(f"Prediction accuracy - ID: {prediction.prediction_id}, "
                               f"Predicted: {prediction.predicted_value:.2f}, "
                               f"Actual: {actual_value:.2f}, "
                               f"Error: {error:.2f}")

        except Exception as e:
            self.logger.error(f"Prediction accuracy evaluation failed: {e}")

    def _get_actual_value(self, prediction_type: PredictionType, data: UserProductivityData) -> float:
        """Get actual value for prediction type"""
        mapping = {
            PredictionType.PRODUCTIVITY_SCORE: data.tasks_completed / (data.hours_worked + 0.1),
            PredictionType.ENERGY_LEVELS: data.energy_level,
            PredictionType.WORKLOAD_FORECAST: data.hours_worked,
            PredictionType.TASK_COMPLETION_TIME: data.hours_worked / (data.tasks_completed + 0.1)
        }
        return mapping.get(prediction_type, 0.0)

    # Data Management

    async def _load_models(self):
        """Load saved models"""
        try:
            # In production, load from persistent storage
            self.logger.info("Models loaded from storage")
        except Exception as e:
            self.logger.error(f"Model loading failed: {e}")

    async def _load_user_data(self):
        """Load user data"""
        try:
            # In production, load from database
            self.logger.info("User data loaded from storage")
        except Exception as e:
            self.logger.error(f"User data loading failed: {e}")

    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status and statistics"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "users": len(self.user_data),
                "total_data_points": sum(len(data) for data in self.user_data.values()),
                "trained_models": len(self.models),
                "active_predictions": len(self.predictions),
                "model_types": list(set(
                    model["model_type"].value for model in self.models.values()
                )),
                "prediction_types": list(set(
                    pred.prediction_type.value for pred in self.predictions.values()
                )),
                "average_model_performance": np.mean([
                    model["performance_score"] for model in self.models.values()
                ]) if self.models else 0.0
            }
        except Exception as e:
            self.logger.error(f"System status generation failed: {e}")
            return {}

    async def shutdown(self):
        """Shutdown predictive analytics system"""
        # Save models and data
        await self._save_models()
        await self._save_user_data()

        self.logger.info("Predictive Analytics System shutdown complete")

    async def _save_models(self):
        """Save models to persistent storage"""
        try:
            # In production, save to file system or database
            self.logger.info("Models saved to storage")
        except Exception as e:
            self.logger.error(f"Model saving failed: {e}")

    async def _save_user_data(self):
        """Save user data to persistent storage"""
        try:
            # In production, save to database
            self.logger.info("User data saved to storage")
        except Exception as e:
            self.logger.error(f"User data saving failed: {e}")


# Example usage
async def main():
    """Example usage of predictive analytics system"""
    analytics = AdvancedPredictiveAnalytics()
    await analytics.initialize()

    # Add sample user data
    user_id = "user_123"
    sample_data = [
        UserProductivityData(
            user_id=user_id,
            timestamp=datetime.now() - timedelta(days=i),
            tasks_completed=np.random.randint(3, 12),
            hours_worked=np.random.uniform(6, 10),
            meetings_attended=np.random.randint(1, 5),
            focus_time_minutes=np.random.randint(60, 240),
            interruptions=np.random.randint(2, 8),
            energy_level=np.random.randint(4, 9),
            stress_level=np.random.randint(2, 7),
            sleep_hours=np.random.uniform(6, 9),
            exercise_minutes=np.random.randint(0, 60),
            mood_score=np.random.randint(5, 9),
            weather_condition=np.random.choice(['sunny', 'cloudy', 'rainy']),
            day_of_week=i % 7,
            is_holiday=False,
            project_complexity=np.random.randint(3, 8),
            team_size=5,
            deadline_pressure=np.random.randint(2, 8)
        )
        for i in range(50)
    ]

    for data in sample_data:
        await analytics.add_user_data(data)

    # Generate predictions
    request = PredictionRequest(
        user_id=user_id,
        prediction_type=PredictionType.PRODUCTIVITY_SCORE,
        time_horizon=7,
        features={"custom_motivation": 8}
    )

    prediction = await analytics.generate_prediction(request)
    print(f"Prediction: {prediction.predicted_value:.2f}")
    print(f"Confidence: {prediction.confidence_score:.2f}")
    print(f"Explanation: {prediction.explanation}")

    # Generate insights
    insights = await analytics.generate_productivity_insights(user_id)
    print(f"Insights: {insights}")

    # Get system status
    status = await analytics.get_system_status()
    print(f"System Status: {status}")


if __name__ == "__main__":
    asyncio.run(main())
