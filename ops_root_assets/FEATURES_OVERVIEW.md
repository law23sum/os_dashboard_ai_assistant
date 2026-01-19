# AI OS — Features Overview

## TOC
- Sessions are appended below in chronological order.

## Session 20251211T223456Z

- Generated at: `2025-12-11T22:34:59Z`
- Repo count (manifest): **1**
- Unhealthy repos: **1** (dirty=1, missing=0)

### Current capabilities (this OS Dashboard repo)
- **Unified launcher**: `start_ui.py` runs React (web/Electron) + FastAPI backend.
- **Backend APIs**: primary `assistant_hub/api/server.py` (SPA + API); legacy/alt `backend_api/main.py` (router-heavy).
- **Automation**: `scripts/ai_auto_fix.py` log watcher + patch applier; `scripts/codex_sentinel.py` multi-repo inspection + reports.
- **Ops hub**: `~/OS_Dashboard_AI_Assistant/` for logs + reports + TODO curation.

### Repo registry snapshot
- **os_dashboard_ai_assistant** `/Users/chrisdixon/Projects/os_dashboard_ai_assistant` (python, fastapi, react) | git: dirty | todos: 245

### Changes / deltas (auto-detected)
- **Note**: Sentinel detects deltas via git status changes; it does not snapshot file contents.
- **os_dashboard_ai_assistant**: `M assistant_hub.db  M assistant_hub_gui/autofix_monitor.py  M docs/future_supreme.html  M frontend/electron/main.cjs  M frontend/electron/main.js  M frontend/public/docs/future_supreme.html  M frontend/src/pages/Project…`
## Session 20251211T223848Z

- Generated at: `2025-12-11T22:39:07Z`
- Repo count (manifest): **26**
- Unhealthy repos: **18** (dirty=18, missing=0)

### Current capabilities (this OS Dashboard repo)
- **Unified launcher**: `start_ui.py` runs React (web/Electron) + FastAPI backend.
- **Backend APIs**: primary `assistant_hub/api/server.py` (SPA + API); legacy/alt `backend_api/main.py` (router-heavy).
- **Automation**: `scripts/ai_auto_fix.py` log watcher + patch applier; `scripts/codex_sentinel.py` multi-repo inspection + reports.
- **Ops hub**: `~/OS_Dashboard_AI_Assistant/` for logs + reports + TODO curation.

### Repo registry snapshot
- **os_dashboard_ai_assistant** `/Users/chrisdixon/Projects/os_dashboard_ai_assistant` (python, fastapi, react) | git: dirty | todos: 245
- **portfolio_strategist** `/Users/chrisdixon/Projects/portfolio_strategist` (python, django, react) | git: dirty | todos: 340
- **idea_trade_exchange** `/Users/chrisdixon/IdeaProjects/trade-exchange` (kotlin, android) | git: dirty | todos: 1
- **portfolio_ref_budget_app** `/Users/chrisdixon/Projects/portfolio_strategist/reference/budget_app` (python, django) | git: clean | todos: 0
- **portfolio_ref_financia** `/Users/chrisdixon/Projects/portfolio_strategist/reference/financia` (python, flask) | git: dirty | todos: 0
- **trader_exchange** `/Users/chrisdixon/PycharmProjects/trader_exchange` (python, fastapi) | git: dirty | todos: 0
- **codenest** `/Users/chrisdixon/PycharmProjects/codenest` (python, django) | git: dirty | todos: 391
- **idea_budget_app** `/Users/chrisdixon/IdeaProjects/budget_app` (kotlin, android) | git: clean | todos: 0
- **matlab_mathematica** `/Users/chrisdixon/MATLAB/Project/Projects/mathematica` (matlab) | git: dirty | todos: 33
- **research_papers_energy** `/Users/chrisdixon/Projects/research_papers/energy/latex-paper` (latex) | git: dirty | todos: 0
- **research_papers_force** `/Users/chrisdixon/Projects/research_papers/force/latex-paper` (latex) | git: dirty | todos: 0
- **research_papers_light** `/Users/chrisdixon/Projects/research_papers/light` (latex, python) | git: dirty | todos: 0
- **research_papers_matter** `/Users/chrisdixon/Projects/research_papers/matter/latex-paper` (latex) | git: dirty | todos: 0
- **idea_java_project** `/Users/chrisdixon/IdeaProjects/JavaProject` (java) | git: clean | todos: 0
- **idea_java_tutorial** `/Users/chrisdixon/IdeaProjects/JavaTutorial` (java) | git: clean | todos: 0
- **idea_repositories** `/Users/chrisdixon/IdeaProjects/Repositories` (java, gradle) | git: dirty | todos: 18
- **manim_core** `/Users/chrisdixon/PycharmProjects/external/manim` (python, cairo) | git: clean | todos: 126
- **manim_tutorial** `/Users/chrisdixon/PycharmProjects/external/manim_tutorial` (python, manim) | git: clean | todos: 0
- **matlab_fundamentals** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Fundamentals-of-Programming` (matlab) | git: dirty | todos: 0
- **matlab_prog_starter** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Programming-A-Starter-Project-Using-MATLAB-and-Python` (matlab, python) | git: dirty | todos: 0
- **matlab_programming_data** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Programming-Organizing-Data` (matlab) | git: dirty | todos: 0
- **matlab_real_space** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Matlab_Real_Space` (matlab) | git: clean | todos: 0
- **matlab_structuring_code** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Programming-Structuring-Code` (matlab) | git: dirty | todos: 0
- **matlab_treasure_hunt** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Treasure-Hunt` (matlab) | git: clean | todos: 0
- **media_videos** `/Users/chrisdixon/PycharmProjects/external/videos` (python) | git: dirty | todos: 141
- **python_tutorial** `/Users/chrisdixon/PycharmProjects/python_tutorial` (python) | git: dirty | todos: 8

### Changes / deltas (auto-detected)
- **Note**: Sentinel detects deltas via git status changes; it does not snapshot file contents.
- **os_dashboard_ai_assistant**: `M assistant_hub.db  M assistant_hub_gui/autofix_monitor.py  M docs/future_supreme.html  M frontend/electron/main.cjs  M frontend/electron/main.js  M frontend/public/docs/future_supreme.html  M frontend/src/App.tsx  M fr…`
- **portfolio_strategist**: `M apps/chat/management/commands/test_openai.py  M apps/content/migrations/0004_bootstrap_initial_blog_content.py  M apps/records/financial_aggregation.py  M apps/stock_analysis/resources/offline_data/nvda_fundamentals.j…`
- **portfolio_ref_financia**: `M stock_analyzer/README.md  M stock_analyzer/main.py  M stock_analyzer/stock_fetcher.py  M stock_analyzer/stock_gui.py  M stock_analyzer/stock_statistics.py ?? stock_analyzer/investment_utils.py ?? stock_analyzer/notifi…`
- **research_papers_light**: `M latex_paper/paper.log  M latex_paper/paper.pdf  M texput.log`
- **research_papers_energy**: `D arxiv/figures.pdf`
- **research_papers_matter**: `D appendix.pdf  D arxiv/figures.pdf  D bibliography.bst  D figures.pdf  D paper.pdf`
- **research_papers_force**: `D appendix.pdf  D arxiv/figures.pdf  D bibliography.bst  D figures.pdf  D paper.pdf`
- **trader_exchange**: `M .DS_Store  M backend/.DS_Store  M backend/target/classes/com/tradeexchange/JavaBackendApplication.class  M backend/target/classes/com/tradeexchange/api/AdminController.class  M backend/target/classes/com/tradeexchange…`
- **python_tutorial**: `D sample_code/application/automate_online-materials/dictionary.txt ?? apps/finance_documents/ ?? assets/javascript/finance_documents/ ?? templates/web/finance_documents/`
- **codenest**: `D assets/images/about-page-images/about-banner.webp  D assets/images/about-page-images/about-team-image.webp  D assets/images/contact-page-images/contact-banner.webp  D assets/images/home-page-images/hero-background.web…`
- **media_videos**: `M _2015/complex_multiplication_article.py  M _2015/counting_in_binary.py  M _2015/eulers_characteristic_formula.py  M _2015/generate_logo.py  M _2015/inventing_math.py  M _2015/inventing_math_images.py  D _2015/ka_playg…`
- **idea_trade_exchange**: `M .DS_Store  M backend/.DS_Store  M backend/pom.xml  M backend/src/main/java/com/tradeexchange/JavaBackendApplication.java  M backend/src/main/java/com/tradeexchange/api/AdminController.java  M backend/src/main/java/com…`
- **idea_repositories**: `?? .idea/`
- **matlab_mathematica**: `M .venv/bin/Activate.ps1  M .venv/bin/activate  M .venv/bin/activate.csh  M .venv/bin/activate.fish  M .venv/bin/pip  M .venv/bin/pip3  M .venv/lib/python3.11/site-packages/__pycache__/argparse.cpython-311.pyc  M .venv/…`
- **matlab_prog_starter**: `D Images/SeaSurfaceTemps.png  D Images/windTokyo.gif`
- **matlab_programming_data**: `D Images/TokyoWindPrediction.gif  D Images/sst.png`
- **matlab_fundamentals**: `D Images/TokyoWindMap.gif  D Images/sst.png`
- **matlab_structuring_code**: `D Images/turkeys1.jpg`
## Session 20251211T224137Z

- Generated at: `2025-12-11T22:41:40Z`
- Repo count (manifest): **1**
- Unhealthy repos: **1** (dirty=1, missing=0)

### Current capabilities (this OS Dashboard repo)
- **Unified launcher**: `start_ui.py` runs React (web/Electron) + FastAPI backend.
- **Backend APIs**: primary `assistant_hub/api/server.py` (SPA + API); legacy/alt `backend_api/main.py` (router-heavy).
- **Automation**: `scripts/ai_auto_fix.py` log watcher + patch applier; `scripts/codex_sentinel.py` multi-repo inspection + reports.
- **Ops hub**: `~/OS_Dashboard_AI_Assistant/` for logs + reports + TODO curation.

### Repo registry snapshot
- **os_dashboard_ai_assistant** `/Users/chrisdixon/Projects/os_dashboard_ai_assistant` (python, fastapi, react) | git: dirty | todos: 245

### Changes / deltas (auto-detected)
- **Note**: Sentinel detects deltas via git status changes; it does not snapshot file contents.
- **os_dashboard_ai_assistant**: `M assistant_core/ai.py  M assistant_hub.db  M assistant_hub_gui/autofix_monitor.py  M docs/future_supreme.html  M frontend/electron/main.cjs  M frontend/electron/main.js  M frontend/public/docs/future_supreme.html  M fr…`
## Session 20251211T232211Z

- Generated at: `2025-12-11T23:22:42Z`
- Repo count (manifest): **26**
- Unhealthy repos: **18** (dirty=18, missing=0)

### Current capabilities (this OS Dashboard repo)
- **Unified launcher**: `start_ui.py` runs React (web/Electron) + FastAPI backend.
- **Backend APIs**: primary `assistant_hub/api/server.py` (SPA + API); legacy/alt `backend_api/main.py` (router-heavy).
- **Automation**: `scripts/ai_auto_fix.py` log watcher + patch applier; `scripts/codex_sentinel.py` multi-repo inspection + reports.
- **Ops hub**: `~/OS_Dashboard_AI_Assistant/` for logs + reports + TODO curation.

### Repo registry snapshot
- **os_dashboard_ai_assistant** `/Users/chrisdixon/Projects/os_dashboard_ai_assistant` (python, fastapi, react) | git: dirty | todos: 286
- **portfolio_strategist** `/Users/chrisdixon/Projects/portfolio_strategist` (python, django, react) | git: dirty | todos: 208
- **idea_trade_exchange** `/Users/chrisdixon/IdeaProjects/trade-exchange` (kotlin, android) | git: dirty | todos: 1
- **portfolio_ref_budget_app** `/Users/chrisdixon/Projects/portfolio_strategist/reference/budget_app` (python, django) | git: clean | todos: 0
- **portfolio_ref_financia** `/Users/chrisdixon/Projects/portfolio_strategist/reference/financia` (python, flask) | git: dirty | todos: 0
- **trader_exchange** `/Users/chrisdixon/PycharmProjects/trader_exchange` (python, fastapi) | git: dirty | todos: 0
- **codenest** `/Users/chrisdixon/PycharmProjects/codenest` (python, django) | git: dirty | todos: 356
- **idea_budget_app** `/Users/chrisdixon/IdeaProjects/budget_app` (kotlin, android) | git: clean | todos: 0
- **matlab_mathematica** `/Users/chrisdixon/MATLAB/Project/Projects/mathematica` (matlab) | git: dirty | todos: 33
- **research_papers_energy** `/Users/chrisdixon/Projects/research_papers/energy/latex-paper` (latex) | git: dirty | todos: 0
- **research_papers_force** `/Users/chrisdixon/Projects/research_papers/force/latex-paper` (latex) | git: dirty | todos: 0
- **research_papers_light** `/Users/chrisdixon/Projects/research_papers/light` (latex, python) | git: dirty | todos: 0
- **research_papers_matter** `/Users/chrisdixon/Projects/research_papers/matter/latex-paper` (latex) | git: dirty | todos: 0
- **idea_java_project** `/Users/chrisdixon/IdeaProjects/JavaProject` (java) | git: clean | todos: 0
- **idea_java_tutorial** `/Users/chrisdixon/IdeaProjects/JavaTutorial` (java) | git: clean | todos: 0
- **idea_repositories** `/Users/chrisdixon/IdeaProjects/Repositories` (java, gradle) | git: dirty | todos: 18
- **manim_core** `/Users/chrisdixon/PycharmProjects/external/manim` (python, cairo) | git: clean | todos: 126
- **manim_tutorial** `/Users/chrisdixon/PycharmProjects/external/manim_tutorial` (python, manim) | git: clean | todos: 0
- **matlab_fundamentals** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Fundamentals-of-Programming` (matlab) | git: dirty | todos: 0
- **matlab_prog_starter** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Programming-A-Starter-Project-Using-MATLAB-and-Python` (matlab, python) | git: dirty | todos: 0
- **matlab_programming_data** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Programming-Organizing-Data` (matlab) | git: dirty | todos: 0
- **matlab_real_space** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Matlab_Real_Space` (matlab) | git: clean | todos: 0
- **matlab_structuring_code** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Programming-Structuring-Code` (matlab) | git: dirty | todos: 0
- **matlab_treasure_hunt** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Treasure-Hunt` (matlab) | git: clean | todos: 0
- **media_videos** `/Users/chrisdixon/PycharmProjects/external/videos` (python) | git: dirty | todos: 141
- **python_tutorial** `/Users/chrisdixon/PycharmProjects/python_tutorial` (python) | git: dirty | todos: 51

### Changes / deltas (auto-detected)
- **Note**: Sentinel detects deltas via git status changes; it does not snapshot file contents.
- **os_dashboard_ai_assistant**: `M assistant_core/ai.py  M assistant_hub.db  M assistant_hub/ai.py  M assistant_hub/db.py  M assistant_hub_gui/assistant_hub/ai.py  M assistant_hub_gui/autofix_monitor.py  M backend_api/main.py  M backend_api/routers/__i…`
- **portfolio_strategist**: `M apps/chat/management/commands/test_openai.py  M apps/content/migrations/0004_bootstrap_initial_blog_content.py  M apps/records/financial_aggregation.py  M apps/stock_analysis/resources/offline_data/nvda_fundamentals.j…`
- **portfolio_ref_financia**: `M stock_analyzer/README.md  M stock_analyzer/main.py  M stock_analyzer/stock_fetcher.py  M stock_analyzer/stock_gui.py  M stock_analyzer/stock_statistics.py ?? stock_analyzer/investment_utils.py ?? stock_analyzer/notifi…`
- **research_papers_light**: `M latex_paper/paper.log  M latex_paper/paper.pdf  M texput.log`
- **research_papers_energy**: `D arxiv/figures.pdf`
- **research_papers_matter**: `D appendix.pdf  D arxiv/figures.pdf  D bibliography.bst  D figures.pdf  D paper.pdf`
- **research_papers_force**: `D appendix.pdf  D arxiv/figures.pdf  D bibliography.bst  D figures.pdf  D paper.pdf`
- **trader_exchange**: `M .DS_Store  M backend/.DS_Store  M backend/target/classes/com/tradeexchange/JavaBackendApplication.class  M backend/target/classes/com/tradeexchange/api/AdminController.class  M backend/target/classes/com/tradeexchange…`
- **python_tutorial**: `D sample_code/application/automate_online-materials/dictionary.txt ?? apps/finance_documents/ ?? assets/javascript/finance_documents/ ?? templates/web/finance_documents/`
- **codenest**: `D assets/images/about-page-images/about-banner.webp  D assets/images/about-page-images/about-team-image.webp  D assets/images/contact-page-images/contact-banner.webp  D assets/images/home-page-images/hero-background.web…`
- **media_videos**: `M _2015/complex_multiplication_article.py  M _2015/counting_in_binary.py  M _2015/eulers_characteristic_formula.py  M _2015/generate_logo.py  M _2015/inventing_math.py  M _2015/inventing_math_images.py  D _2015/ka_playg…`
- **idea_trade_exchange**: `M .DS_Store  M backend/.DS_Store  M backend/pom.xml  M backend/src/main/java/com/tradeexchange/JavaBackendApplication.java  M backend/src/main/java/com/tradeexchange/api/AdminController.java  M backend/src/main/java/com…`
- **idea_repositories**: `?? .idea/`
- **matlab_mathematica**: `M .venv/bin/Activate.ps1  M .venv/bin/activate  M .venv/bin/activate.csh  M .venv/bin/activate.fish  M .venv/bin/pip  M .venv/bin/pip3  M .venv/lib/python3.11/site-packages/__pycache__/argparse.cpython-311.pyc  M .venv/…`
- **matlab_prog_starter**: `D Images/SeaSurfaceTemps.png  D Images/windTokyo.gif`
- **matlab_programming_data**: `D Images/TokyoWindPrediction.gif  D Images/sst.png`
- **matlab_fundamentals**: `D Images/TokyoWindMap.gif  D Images/sst.png`
- **matlab_structuring_code**: `D Images/turkeys1.jpg`
## Session 20251211T233147Z

- Generated at: `2025-12-11T23:32:19Z`
- Repo count (manifest): **26**
- Unhealthy repos: **18** (dirty=18, missing=0)

### Current capabilities (this OS Dashboard repo)
- **Unified launcher**: `start_ui.py` runs React (web/Electron) + FastAPI backend.
- **Backend APIs**: primary `assistant_hub/api/server.py` (SPA + API); legacy/alt `backend_api/main.py` (router-heavy).
- **Automation**: `scripts/ai_auto_fix.py` log watcher + patch applier; `scripts/codex_sentinel.py` multi-repo inspection + reports.
- **Ops hub**: `~/OS_Dashboard_AI_Assistant/` for logs + reports + TODO curation.

### Repo registry snapshot
- **os_dashboard_ai_assistant** `/Users/chrisdixon/Projects/os_dashboard_ai_assistant` (python, fastapi, react) | git: dirty | todos: 286
- **portfolio_strategist** `/Users/chrisdixon/Projects/portfolio_strategist` (python, django, react) | git: dirty | todos: 208
- **idea_trade_exchange** `/Users/chrisdixon/IdeaProjects/trade-exchange` (kotlin, android) | git: dirty | todos: 1
- **portfolio_ref_budget_app** `/Users/chrisdixon/Projects/portfolio_strategist/reference/budget_app` (python, django) | git: clean | todos: 0
- **portfolio_ref_financia** `/Users/chrisdixon/Projects/portfolio_strategist/reference/financia` (python, flask) | git: dirty | todos: 0
- **trader_exchange** `/Users/chrisdixon/PycharmProjects/trader_exchange` (python, fastapi) | git: dirty | todos: 0
- **codenest** `/Users/chrisdixon/PycharmProjects/codenest` (python, django) | git: dirty | todos: 356
- **idea_budget_app** `/Users/chrisdixon/IdeaProjects/budget_app` (kotlin, android) | git: clean | todos: 0
- **matlab_mathematica** `/Users/chrisdixon/MATLAB/Project/Projects/mathematica` (matlab) | git: dirty | todos: 33
- **research_papers_energy** `/Users/chrisdixon/Projects/research_papers/energy/latex-paper` (latex) | git: dirty | todos: 0
- **research_papers_force** `/Users/chrisdixon/Projects/research_papers/force/latex-paper` (latex) | git: dirty | todos: 0
- **research_papers_light** `/Users/chrisdixon/Projects/research_papers/light` (latex, python) | git: dirty | todos: 0
- **research_papers_matter** `/Users/chrisdixon/Projects/research_papers/matter/latex-paper` (latex) | git: dirty | todos: 0
- **idea_java_project** `/Users/chrisdixon/IdeaProjects/JavaProject` (java) | git: clean | todos: 0
- **idea_java_tutorial** `/Users/chrisdixon/IdeaProjects/JavaTutorial` (java) | git: clean | todos: 0
- **idea_repositories** `/Users/chrisdixon/IdeaProjects/Repositories` (java, gradle) | git: dirty | todos: 18
- **manim_core** `/Users/chrisdixon/PycharmProjects/external/manim` (python, cairo) | git: clean | todos: 126
- **manim_tutorial** `/Users/chrisdixon/PycharmProjects/external/manim_tutorial` (python, manim) | git: clean | todos: 0
- **matlab_fundamentals** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Fundamentals-of-Programming` (matlab) | git: dirty | todos: 0
- **matlab_prog_starter** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Programming-A-Starter-Project-Using-MATLAB-and-Python` (matlab, python) | git: dirty | todos: 0
- **matlab_programming_data** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Programming-Organizing-Data` (matlab) | git: dirty | todos: 0
- **matlab_real_space** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Matlab_Real_Space` (matlab) | git: clean | todos: 0
- **matlab_structuring_code** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Programming-Structuring-Code` (matlab) | git: dirty | todos: 0
- **matlab_treasure_hunt** `/Users/chrisdixon/MATLAB/Project/ExternalProjects/Treasure-Hunt` (matlab) | git: clean | todos: 0
- **media_videos** `/Users/chrisdixon/PycharmProjects/external/videos` (python) | git: dirty | todos: 141
- **python_tutorial** `/Users/chrisdixon/PycharmProjects/python_tutorial` (python) | git: dirty | todos: 51

### Changes / deltas (auto-detected)
- **Note**: Sentinel detects deltas via git status changes; it does not snapshot file contents.
- **os_dashboard_ai_assistant**: `M assistant_core/ai.py  M assistant_hub.db  M assistant_hub/ai.py  M assistant_hub/db.py  M assistant_hub_gui/assistant_hub/ai.py  M assistant_hub_gui/autofix_monitor.py  M backend_api/main.py  M backend_api/routers/__i…`
- **portfolio_strategist**: `M apps/chat/management/commands/test_openai.py  M apps/content/migrations/0004_bootstrap_initial_blog_content.py  M apps/records/financial_aggregation.py  M apps/stock_analysis/resources/offline_data/nvda_fundamentals.j…`
- **portfolio_ref_financia**: `M stock_analyzer/README.md  M stock_analyzer/main.py  M stock_analyzer/stock_fetcher.py  M stock_analyzer/stock_gui.py  M stock_analyzer/stock_statistics.py ?? stock_analyzer/investment_utils.py ?? stock_analyzer/notifi…`
- **research_papers_light**: `M latex_paper/paper.log  M latex_paper/paper.pdf  M texput.log`
- **research_papers_energy**: `D arxiv/figures.pdf`
- **research_papers_matter**: `D appendix.pdf  D arxiv/figures.pdf  D bibliography.bst  D figures.pdf  D paper.pdf`
- **research_papers_force**: `D appendix.pdf  D arxiv/figures.pdf  D bibliography.bst  D figures.pdf  D paper.pdf`
- **trader_exchange**: `M .DS_Store  M backend/.DS_Store  M backend/target/classes/com/tradeexchange/JavaBackendApplication.class  M backend/target/classes/com/tradeexchange/api/AdminController.class  M backend/target/classes/com/tradeexchange…`
- **python_tutorial**: `D sample_code/application/automate_online-materials/dictionary.txt ?? apps/finance_documents/ ?? assets/javascript/finance_documents/ ?? templates/web/finance_documents/`
- **codenest**: `D assets/images/about-page-images/about-banner.webp  D assets/images/about-page-images/about-team-image.webp  D assets/images/contact-page-images/contact-banner.webp  D assets/images/home-page-images/hero-background.web…`
- **media_videos**: `M _2015/complex_multiplication_article.py  M _2015/counting_in_binary.py  M _2015/eulers_characteristic_formula.py  M _2015/generate_logo.py  M _2015/inventing_math.py  M _2015/inventing_math_images.py  D _2015/ka_playg…`
- **idea_trade_exchange**: `M .DS_Store  M backend/.DS_Store  M backend/pom.xml  M backend/src/main/java/com/tradeexchange/JavaBackendApplication.java  M backend/src/main/java/com/tradeexchange/api/AdminController.java  M backend/src/main/java/com…`
- **idea_repositories**: `?? .idea/`
- **matlab_mathematica**: `M .venv/bin/Activate.ps1  M .venv/bin/activate  M .venv/bin/activate.csh  M .venv/bin/activate.fish  M .venv/bin/pip  M .venv/bin/pip3  M .venv/lib/python3.11/site-packages/__pycache__/argparse.cpython-311.pyc  M .venv/…`
- **matlab_prog_starter**: `D Images/SeaSurfaceTemps.png  D Images/windTokyo.gif`
- **matlab_programming_data**: `D Images/TokyoWindPrediction.gif  D Images/sst.png`
- **matlab_fundamentals**: `D Images/TokyoWindMap.gif  D Images/sst.png`
- **matlab_structuring_code**: `D Images/turkeys1.jpg`
