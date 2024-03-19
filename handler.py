import json
import sqlalchemy
from serpapi import GoogleSearch
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Float, ARRAY, Text
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

engine = sqlalchemy.create_engine(os.environ['POSTGRES_URL'])
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

API_KEY = os.environ['API_KEY']

store_ids = [
    # EXEMPLOS DE RESTAURANTES.
    'ChIJW43Oz8JxGZURggGzEv4NNSw', # N1 CHICKEN - 22 Reviews.
    'ChIJSXGmKWlwGZUR7W-PMNcKFfw', # RESTAURANTE LANCHERIA DO GORDO - 19 Reviews.
    'ChIJd21ozb1xGZURpnuOii5KvHg', # LASANHA GOURMET - 7 Reviews.
    # Adicionar os IDs da Lojas que desejar aqui.
]


class Review(Base):
    __tablename__ = 'reviews_serpapi'

    id = Column(String(100), primary_key=True)
    store_id = Column(String(100))
    author_name = Column(String(100))
    author_id = Column(String(100))
    author_photo_url = Column(String(200))
    relative_time = Column(String(50))
    rating = Column(Float)
    text = Column(Text)
    attachments = Column(ARRAY(String(255)))


def add_reviews_to_database(stores_data):

    Base.metadata.create_all(engine)

    for store in stores_data:

        store_id = store.get('search_parameters').get('place_id')

        logger.info(f"Store ID: {store_id} - Adding reviews to the database...")

        for review_data in store['reviews']:
            existing_review = session.query(Review).filter_by(id=review_data['review_id']).first()

            if existing_review is None:
                new_review = Review(
                    id = review_data.get('review_id'),
                    store_id = store_id,
                    author_name = review_data.get('user').get('name'),
                    author_id = review_data.get('user').get('contributor_id'),
                    author_photo_url = review_data.get('user').get('thumbnail'), 
                    relative_time= review_data.get('date'),
                    rating = review_data.get('rating'),
                    text = review_data.get('snippet'),
                    attachments = review_data.get('images', []),
                )

                session.add(new_review)
                session.commit()


def get_store_reviews(event, context):
    data = []
    
    try:
        for store in store_ids:

            logger.info(f"Store ID: {store} - Searching reviews...")

            store_data = {}

            params = {
                "engine": "google_maps_reviews",
                "place_id": store,
                "api_key": API_KEY
            }
            search = GoogleSearch(params)
            results = search.get_json()

            store_data = results

            next_page_token = results.get('serpapi_pagination', {}).get('next_page_token')

            while next_page_token:
                params['next_page_token'] = next_page_token
                search = GoogleSearch(params)
                results = search.get_json()
                reviews = results.get('reviews', [])

                store_data['reviews'].extend(reviews)

                next_page_token = results.get('serpapi_pagination', {}).get('next_page_token')

            data.append(store_data)
        
        add_reviews_to_database(data)

        return {
            'statusCode': 200,
            'body': json.dumps("Reviews successfully collected using SerpApi and saved to the database.")
        }
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps("Something went wrong collecting reviews with SerpApi.")
        }
