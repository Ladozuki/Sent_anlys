from sqlalchemy import Column, String, Float, Date, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class FreightRate(Base):
    __tablename__ = "freight_rates"
    id = Column(Integer, primary_key=True)
    route = Column(String, nullable=False)  # Route code, e.g., 'TD2'
    description = Column(String, nullable=False)  # Route description
    laydays = Column(String)  # Laydays/cancelling period, e.g., '20/30 days'
    cargo_type = Column(String, nullable=False)  # Type of cargo, e.g., 'Crude Oil'
    volume = Column(Integer, nullable=False)  # Volume in metric tons
    hull_type = Column(String)  # Hull type, e.g., 'Double hull'
    age_max = Column(Integer)  # Maximum vessel age in years
    commission = Column(Float)  # Total commission as a percentage

class NewsSentiment(Base):
    __tablename__ = "news_sentiment"
    id = Column(Integer, primary_key=True)
    topic = Column(String, nullable=False)
    source = Column(String)
    author = Column(String)
    title = Column(String)
    description = Column(String)
    content = Column(String)
    published_at = Column(Date)
    url = Column(String)
    sentiment_score = Column(Float)

class MacroData(Base):
    __tablename__ = "macro_data"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    metric = Column(String, nullable=False)
    value = Column(Float, nullable=False)


