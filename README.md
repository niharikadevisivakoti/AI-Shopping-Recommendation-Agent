# Product Recommendation System

Portfolio-ready full-stack recommendation system using **React + FastAPI + Python + Pandas + NumPy + scikit-learn**.

## Features
- Product catalog, search and categories
- Product details and similar products
- Personalized recommendations from recently viewed products
- Cold-start fallback using rating/review popularity
- Responsive UI
- FastAPI REST API with Swagger docs
- Local CSV dataset; no database required
- TF-IDF + cosine similarity content-based filtering

## Architecture
React UI → FastAPI REST API → RecommendationEngine → TF-IDF + Cosine Similarity → products.csv

## Run backend
From the project root:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn backend.app:app --reload
```

API: http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs

## Run frontend
Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally http://localhost:5173.

## Algorithm
Product name, category, description and tags are combined into text. `TfidfVectorizer` converts this text into vectors. Cosine similarity ranks similar products. For personalization, vectors of recently viewed products are averaged to create a simple user profile; candidates closest to that profile are ranked. With no history, highly rated products are returned.

## API endpoints
- `GET /api/health`
- `GET /api/categories`
- `GET /api/products?q=...&category=...`
- `GET /api/products/{id}`
- `GET /api/products/{id}/similar?limit=6`
- `POST /api/recommendations`

## Interview explanation
The system solves product discovery using content-based filtering. TF-IDF provides an interpretable text representation and cosine similarity measures product similarity. Recent views provide lightweight personalization without requiring authentication or a database. A cold-start fallback handles users with no history.

## Future improvements
Collaborative filtering from ratings, hybrid ranking, embeddings/vector databases, authentication, feedback loops, evaluation metrics and A/B testing.

## Structure
```text
product-recommendation-system/
├── backend/app.py
├── recommendation_engine/recommender.py
├── data/products.csv
├── frontend/src/main.jsx
├── frontend/src/styles.css
├── frontend/package.json
├── requirements.txt
├── .gitignore
└── README.md
```
