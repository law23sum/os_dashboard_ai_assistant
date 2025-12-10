python main.py                             # Main application
python_os assistant_hub_gui/main.py        # Web dashboard
pytest tests/                              # Run tests


python security_monitor.py dashboard
python security_monitor.py compliance gdpr
python security_monitor.py analyze-threats /var/log/auth.log

python -m compileall assistant_hub
pytest tests/
python neural_architecture_search.py
python_os assistant_hub_gui/main.py 

# Run all tests
python -m unittest discover tests

# Run specific components
python -m unittest tests.test_ai_assistant
python -m unittest tests.test_database
python -m unittest tests.test_task_automation

# Run with verbose output
python -m unittest discover tests -v


python -c "from os_dashboard_orchestrator import OSDashboard; print('Import successful')"
# Output: Import successful