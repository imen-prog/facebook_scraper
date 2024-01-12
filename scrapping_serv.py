from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

app = FastAPI()

# Set up the database and initialize it
engine = create_engine('sqlite:///posts.db')
Base = declarative_base()

try:
    Base.metadata.create_all(engine)
    print("Tables created successfully!")
except Exception as e:
    print(f"Error creating tables: {e}")

Session = sessionmaker(bind=engine)

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    content = Column(String)
    date = Column(String)
    likes = Column(Integer)

# Scraping function
def scrape_nasa_page():
    url = 'https://www.facebook.com/NASA/'
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad responses (e.g., 404)

    soup = BeautifulSoup(response.text, 'html.parser')
    posts = []
    for post in soup.find_all('div', class_='clearfix relative lfloat'):
        content = post.find('div', class_='userContent').p.text
        date = post.find('abbr', class_='timestamp').text
        likes = int(post.find('span', class_='_50f6').text.strip(' likes'))
        posts.append({'content': content, 'date': date, 'likes': likes})
    return posts

# Data saving functions
def save_to_database(posts):
    with Session() as session:
        try:
            for post in posts:
                new_post = Post(content=post['content'], date=post['date'], likes=post['likes'])
                session.add(new_post)
            session.commit()
            print("Data saved to the database successfully!")
        except Exception as e:
            print(f"Error saving data to the database: {e}")


# FastAPI route
@app.get('/scrape')
def scrape():
    try:
        posts = scrape_nasa_page()
        print(f"Number of posts scraped: {len(posts)}")
        
        if posts:
            save_to_database(posts)
            
            
            return {'message': 'Scraped and saved NASA posts'}
        else:
            return {'message': 'No posts scraped'}
    except Exception as e:
        print(f"Error during scraping: {e}")
        return {'error': str(e)}
