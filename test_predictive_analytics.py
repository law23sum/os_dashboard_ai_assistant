#!/usr/bin/env python3
"""
Test script for the Predictive Analytics System
"""

import asyncio
import sys
import os

# Add current directory to path for proper imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

try:
    from assistant_core.predictive_analytics import AdvancedPredictiveAnalytics, PredictionType, PredictionRequest, UserProductivityData
    from datetime import datetime, timedelta
    import numpy as np

    async def test_predictive_analytics():
        """Test the predictive analytics system"""
        print("🔧 Testing Predictive Analytics System...")

        # Initialize the system
        analytics = AdvancedPredictiveAnalytics()
        await analytics.initialize()

        print("✅ Predictive Analytics System initialized")

        # Add sample user data
        user_id = "test_user"
        print("\n📊 Adding sample user data...")

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
            for i in range(60)  # 60 days of data
        ]

        for data in sample_data:
            await analytics.add_user_data(data)

        print(f"✅ Added {len(sample_data)} data points for user {user_id}")

        # Test prediction generation
        print("\n🔮 Testing prediction generation...")
        request = PredictionRequest(
            user_id=user_id,
            prediction_type=PredictionType.PRODUCTIVITY_SCORE,
            time_horizon=7,
            features={"custom_motivation": 8}
        )

        try:
            prediction = await analytics.generate_prediction(request)
            print("✅ Prediction generated:")
            print(f"   Value: {prediction.predicted_value:.2f}")
            print(f"   Confidence: {prediction.confidence_score:.2f}")
            print(f"   Explanation: {prediction.explanation[:100]}...")
        except Exception as e:
            print(f"❌ Prediction generation failed: {e}")

        # Test insights generation
        print("\n📈 Testing productivity insights...")
        try:
            insights = await analytics.generate_productivity_insights(user_id)
            print("✅ Productivity insights generated:")
            print(f"   Predictions: {len(insights.get('predictions', {}))}")
            print(f"   Recommendations: {len(insights.get('recommendations', []))}")
        except Exception as e:
            print(f"❌ Insights generation failed: {e}")

        # Test system status
        print("\n📊 Testing system status...")
        status = await analytics.get_system_status()
        print("✅ System status retrieved:")
        print(f"   Users: {status['users']}")
        print(f"   Data points: {status['total_data_points']}")
        print(f"   Models: {status['trained_models']}")

        # Shutdown
        await analytics.shutdown()
        print("\n🛑 Predictive Analytics System shutdown complete")

        print("\n🎉 All predictive analytics tests completed!")

    if __name__ == "__main__":
        asyncio.run(test_predictive_analytics())

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("The predictive analytics system requires ML dependencies:")
    print("  - scikit-learn")
    print("  - xgboost")
    print("  - statsmodels")
    print("These should be installed via: pip install scikit-learn xgboost statsmodels")
