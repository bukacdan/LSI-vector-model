import os
import logging

import numpy as np
import pandas as pd

from kneed import KneeLocator
from scipy.sparse.linalg import svds
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class LSI:
    def __init__(self):
        self.k = 200


    def fetch_dataset(self, data_dir: str = "sklearn-data", remove: tuple = ("headers", "footers", "quotes")):
        logging.info("Fetching dataset.")
        self.dataset = fetch_20newsgroups(subset="all", data_home=os.path.join(".", data_dir), remove=remove)
        self.df = pd.DataFrame({"documents": self.dataset.data})


    def clean_documents(self, min_word_length: int = 1):
        logging.info("Cleaning documents.")
        self.df['documents_cleaned'] = pd.Series(self.df["documents"])
        self.df['documents_cleaned'] = (
            self.df['documents_cleaned']
                .pipe(lambda x: x.str.lower())  # make all letters lowercase 
                .pipe(lambda x: x.str.replace("\S*@\S*\s?", "", regex=True)) # remove email addresses
                .pipe(lambda x: x.str.replace("[^a-zA-Z#]", " ", regex=True)) # remove non-alphabetical characters
                .pipe(lambda x: pd.Series([' '.join([w for w in line if len(w) >= min_word_length]) for line in x.str.split()])) # get rid of short words
            )


    def create_tdm(self):
        logging.info("Creating term-by-document matrix from the dataset.")
        self.tfidf = TfidfVectorizer(stop_words="english")

        # tdm matrix: shape(number_of_documents, number_of_terms) <==> term-by-document matrix
        self.tdm = self.tfidf.fit_transform(self.df["documents_cleaned"])


    def svd_optimal_k(self):
        logging.info("Searching for optimal number of concepts.")
        _, s, _ = svds(self.tdm, self.k)
        
        x = range(1, len(s) + 1)
        y = sorted(s, reverse=True)
        self.k = KneeLocator(x, y, curve="convex", direction="decreasing").knee
        logging.info(f"The optimal number of concepts is {self.k}.")


    def svd_dataset(self):
        self.svd_optimal_k()

        logging.info("Applying SVD to the dataset.")
        """
        u  matrix: shape(number_of_documents, number_of_concepts) <==> concept-by-document matrix
        s  vector: shape(number_of_concepts,) <=> concepts
        vt matrix: shape(number_of_concepts, number_of_terms) <=> concept-by-term matrix
        """
        self.u, self.s, self.vt = svds(self.tdm, k=self.k)


    def process_query(self, query: str, limit: int = -1) -> list:
        logging.info(f"Processing query \"{query}\".")
        query = query.split()
        query_tdm = self.tfidf.transform(query)
        query_concepts = query_tdm @ np.transpose(self.vt)  # query projection to the space of concepts --> concept-by-query
        sim = cosine_similarity(self.u, query_concepts)  # cosine similarity between concept-by-documents and concept-by-query
        acos = np.arccos(sim)

        values_indexes = []
        for i in range(acos.shape[1]):
            for j, val in enumerate(acos[:, i]):
                values_indexes.append({"query": query[i], "angle": val, "document_index": j})
        values_indexes.sort(key=lambda x: x["angle"])

        if limit == -1:
          limit = acos.shape[1]

        return values_indexes[:limit]



    """
    Example of the pipeline:

    lsi = LSI()
    lsi.fetch_dataset()
    lsi.clean_documents(min_word_length=3)
    lsi.create_tdm()
    lsi.svd_dataset()

    lsi.process_query("windows dos", 10)
    """
