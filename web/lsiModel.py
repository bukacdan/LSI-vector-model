import os
import time
import nltk
import logging

import numpy as np
import pandas as pd

from kneed import KneeLocator
from nltk.stem import WordNetLemmatizer
from scipy.sparse.linalg import svds
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class LSI:
    def __init__(self):
        self.prepared = False
        self.k = 200
        self.last_query_results = []
        self.last_query_execution_time = 0
        self.NLTK_DATA_PATH = "./nltk_data"
        self.lemmatizer = WordNetLemmatizer()

        #logging.info("LSI: Downloading nltk data.")
        #nltk.download(['porter_test', 'rslp'], download_dir=os.path.abspath(self.NLTK_DATA_PATH))
        nltk.data.path.append(os.path.abspath(self.NLTK_DATA_PATH))


    def fetch_dataset(self, data_dir: str = "sklearn-data", remove: tuple = ("headers", "footers", "quotes")):
        logging.info("LSI: Fetching dataset.")
        self.dataset = fetch_20newsgroups(subset="all", data_home=os.path.join(".", data_dir), remove=remove)
        self.df = pd.DataFrame({"documents": self.dataset.data})


    def clean_documents(self, min_word_length: int = 1):
        logging.info("LSI: Cleaning documents.")
        self.df['documents_cleaned'] = pd.Series(self.df["documents"])
        self.df['documents_cleaned'] = (
            self.df['documents_cleaned']
                .pipe(lambda x: x.str.lower())  # make all letters lowercase 
                .pipe(lambda x: x.str.replace("\S*@\S*\s?", "", regex=True)) # remove email addresses
                .pipe(lambda x: x.str.replace("[^a-zA-Z#]", " ", regex=True)) # remove non-alphabetical characters
                .pipe(lambda x: pd.Series([' '.join([self.lemmatizer.lemmatize(w) for w in line]) for line in x.str.split()])) # lemmatization
                .pipe(lambda x: pd.Series([' '.join([w for w in line if len(w) >= min_word_length]) for line in x.str.split()])) # get rid of short words
            )


    def create_tdm(self):
        logging.info("LSI: Creating term-by-document matrix from the dataset.")
        self.tfidf = TfidfVectorizer(stop_words="english")

        # tdm matrix: shape(number_of_documents, number_of_terms) <==> term-by-document matrix
        self.tdm = self.tfidf.fit_transform(self.df["documents_cleaned"])


    def svd_optimal_k(self):
        logging.info("LSI: Searching for optimal number of concepts.")
        _, s, _ = svds(self.tdm, self.k)
        
        x = range(1, len(s) + 1)
        y = sorted(s, reverse=True)
        self.k = KneeLocator(x, y, curve="convex", direction="decreasing").knee
        logging.info(f"LSI: The optimal number of concepts is {self.k}.")


    def svd_dataset(self):
        self.svd_optimal_k()

        logging.info("LSI: Applying SVD to the dataset.")
        """
        u  matrix: shape(number_of_documents, number_of_concepts) <==> concept-by-document matrix
        s  vector: shape(number_of_concepts,) <=> concepts
        vt matrix: shape(number_of_concepts, number_of_terms) <=> concept-by-term matrix
        """
        self.u, self.s, self.vt = svds(self.tdm, k=self.k)

    
    def prepare(self):
        self.fetch_dataset()
        self.clean_documents(min_word_length=1)
        self.create_tdm()
        self.svd_dataset()

        self.prepared = True


    def process_query(self, query: str, limit: int = -1) -> list:
        start = time.time()
        logging.info(f"LSI: Processing query \"{query}\".")
        query = query.split()
        query_lemmatized = query
        for i, q in enumerate(query_lemmatized):
            query_lemmatized[i] = self.lemmatizer.lemmatize(q)
        query_lemmatized_tdm = self.tfidf.transform(query_lemmatized)
        query_lemmatized_concepts = query_lemmatized_tdm @ np.transpose(self.vt)  # query projection to the space of concepts --> concept-by-query
        sim = cosine_similarity(self.u, query_lemmatized_concepts)  # cosine similarity between concept-by-documents and concept-by-query
        acos = np.arccos(sim)

        values_indexes = []
        for i in range(acos.shape[1]):
            for j, val in enumerate(acos[:, i]):
                values_indexes.append({
                    "query": query[i],
                    "query_lemmatized": query_lemmatized[i],
                    "angle": val,
                    "document_index": j,
                    "document_category": self.dataset.target_names[self.dataset.target[j]]
                })
        values_indexes.sort(key=lambda x: x["angle"])

        if limit == -1:
          #limit = acos.shape[0]
          limit = 100
          
        for v in values_indexes[:limit]:
            v["document"] = self.df.iloc[v["document_index"]]["documents"]
        end = time.time()
        self.last_query_results = values_indexes[:limit]
        self.last_query_execution_time = end - start


    def process_query_seq(self, query, limit=-1):
        start = time.time()
        self.terms = self.tfidf.get_feature_names()
        logging.info(f'LSI: Processing query \"{query}\".')
        query = query.split()
        query_lemmatized = query
        for i, q in enumerate(query_lemmatized):
            query_lemmatized[i] = self.lemmatizer.lemmatize(q)
        res = []
        for i, word in enumerate(query_lemmatized):
            try:
                indice = self.terms.index(word)
            except ValueError:
                self.last_query_results=res
                end = time.time()
                self.last_query_execution_time = end - start
                return
            col = self.tdm[:, indice]
            docs = [
                {
                    "query": query[i],
                    "query_lemmatized": query_lemmatized[i],
                    "document_index": index,
                    "document": self.df.loc[index, "documents"],
                    "document_category": self.dataset.target_names[self.dataset.target[index]]
                }
                for index, tfidf in enumerate(col)
                if tfidf > 0]
            res = [*res, *docs]
        
        if limit == -1:
            limit = 100

        end = time.time()
        self.last_query_results = res[:limit]
        self.last_query_execution_time = end - start
