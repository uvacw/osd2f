from .config import Production
from .server import app

app.config.from_object(Production)
