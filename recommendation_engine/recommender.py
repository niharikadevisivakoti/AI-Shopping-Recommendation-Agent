from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RecommendationEngine:

    def __init__(self, csv_path: Path):
        self.df = pd.read_csv(csv_path)
        self.df['id'] = self.df['id'].astype(int)

        self.df['text'] = (
            self.df['name'].fillna('')
            + ' '
            + self.df['category'].fillna('')
            + ' '
            + self.df['description'].fillna('')
            + ' '
            + self.df['tags'].fillna('')
        ).str.lower()

        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )

        self.matrix = self.vectorizer.fit_transform(
            self.df['text']
        )

        self.similarity = cosine_similarity(self.matrix)

        self.id_to_index = {
            int(v): i
            for i, v in enumerate(self.df['id'])
        }

    def _records(self, f):
        return f[
            [
                'id',
                'name',
                'category',
                'price',
                'rating',
                'reviews',
                'description',
                'image'
            ]
        ].to_dict('records')

    def categories(self):
        return {
            'categories': sorted(
                self.df['category'].unique().tolist()
            )
        }

    def products(self, q=None, category=None):
        f = self.df

        if q:
            f = f[
                f['text'].str.contains(
                    q.lower(),
                    regex=False,
                    na=False
                )
            ]

        if category:
            f = f[
                f['category'].str.lower()
                == category.lower()
            ]

        return {
            'products': self._records(f)
        }

    def product(self, pid):
        f = self.df[self.df.id == pid]

        return (
            self._records(f)[0]
            if not f.empty
            else None
        )

    def similar(self, pid, limit=6):
        i = self.id_to_index[pid]

        selected_category = self.df.iloc[i]['category']

        category_indices = self.df[
            self.df['category'].str.lower()
            == str(selected_category).lower()
        ].index.tolist()

        category_indices.sort(
            key=lambda x: self.similarity[i][x],
            reverse=True
        )

        category_indices = [
            x for x in category_indices
            if x != i
        ][:limit]

        return {
            'products': self._records(
                self.df.iloc[category_indices]
            )
        }

    def personalized(
        self,
        viewed_ids,
        category=None,
        limit=6
    ):
        valid = [
            self.id_to_index[i]
            for i in viewed_ids
            if i in self.id_to_index
        ]

        f = self.df.copy()

        if category:
            f = f[
                f['category'].str.lower()
                == category.lower()
            ]

        if valid:
            profile = np.asarray(
                self.matrix[valid].mean(axis=0)
            )

            scores = cosine_similarity(
                profile,
                self.matrix
            ).ravel()

            f['_score'] = [
                scores[
                    self.id_to_index[int(i)]
                ]
                for i in f.id
            ]

            f = f[
                ~f.id.isin(viewed_ids)
            ].sort_values(
                ['_score', 'rating', 'reviews'],
                ascending=False
            )

        else:
            f = f.sort_values(
                ['rating', 'reviews'],
                ascending=False
            )

        return {
            'products': self._records(
                f.head(limit)
            )
        }