
from sqlalchemy import create_engine, inspect
from core.config import settings

engine = create_engine(settings.database_url)
inspector = inspect(engine)
columns = inspector.get_columns('newsletter_campaigns')
for c in columns:
    if c['name'] in ['scheduled_at', 'sent_at']:
        print(f"Column {c['name']}: {c['type']}")
