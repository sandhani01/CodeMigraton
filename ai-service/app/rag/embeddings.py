"""Embedding Generator and Vector Math for Semantic Search.

Provides transparent vectorization and cosine similarity calculations using pure NumPy,
avoiding opaque multi-gigabyte blackbox frameworks.
"""

import math
import re
from typing import List, Dict, Any, Tuple
import numpy as np


class LightweightEmbeddingModel:
    """A deterministic TF-IDF and character/subword n-gram vectorizer.
    
    Produces normalized dense embedding vectors capturing both lexical tokens
    and semantic subwords (e.g., 'ajax', 'url', 'timezone', 'deprecated').
    """

    def __init__(self, vocab_size: int = 1024):
        self.vocab_size = vocab_size
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.is_fitted = False

    def _tokenize(self, text: str) -> List[str]:
        """Extract words, dot-separated identifiers, and character 3-grams."""
        text = text.lower()
        # Word tokens
        tokens = re.findall(r"[a-z0-9_.]+", text)
        all_features = list(tokens)
        
        # Subword n-grams for semantic similarity
        for tok in tokens:
            if len(tok) >= 4:
                for i in range(len(tok) - 3):
                    all_features.append(tok[i:i + 4])
                    
        return all_features

    def fit(self, documents: List[str]) -> "LightweightEmbeddingModel":
        """Fits vocabulary and IDF values over the corpus."""
        doc_count = len(documents)
        df: Dict[str, int] = {}

        for doc in documents:
            features = set(self._tokenize(doc))
            for f in features:
                df[f] = df.get(f, 0) + 1

        # Select top most informative features
        sorted_features = sorted(df.items(), key=lambda x: x[1], reverse=True)[:self.vocab_size]
        self.vocab = {feat: idx for idx, (feat, _) in enumerate(sorted_features)}
        
        # Compute smooth IDF: log((N + 1) / (df + 1)) + 1
        for feat, idx in self.vocab.items():
            self.idf[feat] = math.log((doc_count + 1) / (df[feat] + 1)) + 1.0

        self.is_fitted = True
        return self

    def embed_text(self, text: str) -> np.ndarray:
        """Embeds a single string into an L2-normalized vector."""
        vec = np.zeros(self.vocab_size, dtype=np.float32)
        if not self.is_fitted:
            return vec

        features = self._tokenize(text)
        if not features:
            return vec

        tf: Dict[str, int] = {}
        for f in features:
            if f in self.vocab:
                tf[f] = tf.get(f, 0) + 1

        for f, count in tf.items():
            idx = self.vocab[f]
            # TF-IDF calculation
            vec[idx] = count * self.idf.get(f, 1.0)

        # L2 Normalization so dot product equals cosine similarity
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return vec

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Embeds a list of texts into a 2D matrix of shape (N, vocab_size)."""
        return np.array([self.embed_text(t) for t in texts], dtype=np.float32)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Calculates cosine similarity between two 1D normalized vectors."""
    dot = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))
