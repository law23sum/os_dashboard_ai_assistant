"""Re-export database models and helpers from ``assistant_hub.db``.

The project includes a mature database layer under ``assistant_hub``.
For ``assistant_core`` modules we provide a lightweight shim that
forwards all attributes, ensuring imports like ``from .db import ...``
continue to work without duplicating logic.
"""

from assistant_hub.db import *  # noqa: F401,F403
