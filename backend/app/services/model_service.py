"""
model_service.py

Wraps the EXISTING ML implementation from the original model.py 1:1:
- clean_text()          -> ModelService.clean_text()
- predict_message()     -> ModelService.predict()
- get_top_toxic_words() -> ModelService.top_toxic_words()
- train_cyberbullying_model() -> ModelService.retrain()

The trained model + vectorizer are loaded ONCE at startup and kept in memory
(self._model_data). Nothing here changes the prediction behavior of the
original project - the TF-IDF + Logistic Regression pipeline, the lexicon
fallback, and the toxic-word matching logic are preserved exactly.
"""
import os
import pickle
import re
import threading
import unicodedata
from typing import Dict, List, Optional, Tuple

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from app.core.config import settings
from app.core.logging import logger

# Same lexicon as the original model.py (used for the fallback / OOV boost path)
VULGAR_WORDS = {
    'stupid', 'ugly', 'loser', 'trash', 'dumb', 'idiot', 'pathetic', 'hate',
    'useless', 'freak', 'kill', 'destroy', 'beat', 'leak', 'monster', 'coward',
    'clown', 'liar', 'garbage', 'disgrace', 'uneducated', 'parasite', 'crybaby',
    'hideous', 'irritating', 'shut up', 'get lost', 'hate you', 'chomu', 'gadha',
    'fattu', 'pagal', 'jerk', 'bastard', 'suck', 'sucks', 'dumbass', 'hell',
    'fuck', 'fucking', 'fucker', 'bitch', 'asshole', 'shit'
}
MULTI_WORD_PHRASES = ['shut up', 'get lost', 'hate you', 'watch your back', 'ruin your life']

METHOD_ML = "TF-IDF + Logistic Regression"
METHOD_FALLBACK = "Fallback Lexicon Rules"


class ModelService:
    """Singleton-style service. Instantiated once in main.py's startup event."""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self._model_data: Optional[dict] = None
        self._lock = threading.Lock()
        self.load()

    # ---------------------------------------------------------------- load
    def load(self) -> bool:
        """Load the pickle file into memory. Safe to call again after retraining."""
        if not os.path.exists(self.model_path):
            logger.warning(f"Model file not found at '{self.model_path}'. Using lexicon fallback.")
            self._model_data = None
            return False

        try:
            with open(self.model_path, "rb") as f:
                data = pickle.load(f)

            with self._lock:
                self._model_data = data
            logger.info(f"Model loaded from '{self.model_path}' (accuracy={data.get('accuracy')})")
            return True
        except Exception as e:
            logger.error(f"Failed to load model file at '{self.model_path}': {e}. Using lexicon fallback.")
            with self._lock:
                self._model_data = None
            return False

    @property
    def is_loaded(self) -> bool:
        return self._model_data is not None

    # ------------------------------------------------------------ clean_text
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize the input text (removing special characters, websites, normalization)."""
        if not isinstance(text, str):
            return ""
        # Normalize Unicode characters (e.g., handles homoglyphs and accents)
        text = unicodedata.normalize("NFKC", text)
        text = text.lower()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'[^\w\s]', '', text)
        text = " ".join(text.split())
        return text

    # -------------------------------------------------------------- predict
    def predict(self, message: str) -> Dict:
        """Identical behavior to the original predict_message(), including
        the lexicon fallback and the out-of-vocabulary boosting logic."""
        cleaned = self.clean_text(message)

        if not self.is_loaded:
            return self._predict_fallback(cleaned)

        model_data = self._model_data
        model = model_data['model']
        vectorizer = model_data['vectorizer']

        matched = [w for w in cleaned.split() if w in VULGAR_WORDS]
        for phrase in MULTI_WORD_PHRASES:
            if phrase in cleaned:
                matched.append(phrase)
        matched = list(set(matched))

        try:
            features = vectorizer.transform([cleaned])

            if features.nnz == 0:
                if len(matched) > 0:
                    prediction = 1
                    confidence = 0.70 + (0.05 * min(len(matched), 5))
                    method = METHOD_FALLBACK
                else:
                    prediction = 0
                    confidence = 0.95
                    method = METHOD_ML
            else:
                prediction = int(model.predict(features)[0])
                probabilities = model.predict_proba(features)[0]
                confidence = float(probabilities[prediction])
                method = METHOD_ML
        except Exception as e:
            logger.error(f"Error predicting with ML model, falling back to lexicon rules: {e}")
            return self._predict_fallback(cleaned)

        return {
            'label': int(prediction),
            'confidence': float(confidence),
            'matched_words': matched,
            'method': method,
        }

    def _predict_fallback(self, cleaned: str) -> Dict:
        words = set(cleaned.split())
        matched = list(words.intersection(VULGAR_WORDS))
        if len(matched) > 0:
            return {
                'label': 1,
                'confidence': 0.70 + (0.05 * min(len(matched), 5)),
                'matched_words': matched,
                'method': METHOD_FALLBACK,
            }
        return {
            'label': 0,
            'confidence': 0.90,
            'matched_words': [],
            'method': METHOD_FALLBACK,
        }

    # ------------------------------------------------------ top toxic words
    def top_toxic_words(self, top_n: int = 10) -> List[Tuple[str, float]]:
        if not self.is_loaded:
            # same mock fallback weights used in the original get_top_toxic_words()
            return [
                ("ugly", 2.8), ("stupid", 2.5), ("loser", 2.3), ("threat", 2.1),
                ("kill", 2.0), ("destroy", 1.9), ("hate", 1.8), ("trash", 1.7),
                ("dumb", 1.6), ("useless", 1.5)
            ]
        model = self._model_data['model']
        vectorizer = self._model_data['vectorizer']
        coefficients = model.coef_[0]
        feature_names = vectorizer.get_feature_names_out()
        word_weights = list(zip(feature_names, coefficients))
        word_weights.sort(key=lambda x: x[1], reverse=True)
        return [(w, float(c)) for w, c in word_weights[:top_n]]

    # ----------------------------------------------------------------- meta
    @property
    def accuracy(self) -> Optional[float]:
        if not self.is_loaded:
            return None
        return self._model_data.get('accuracy')

    @property
    def confusion_matrix(self):
        if not self.is_loaded:
            return None
        return self._model_data.get('confusion_matrix')

    @property
    def classification_report(self):
        if not self.is_loaded:
            return None
        return self._model_data.get('classification_report')

    # -------------------------------------------------------------- retrain
    def retrain(self, dataset_path: str) -> Dict:
        """Identical pipeline to the original train_cyberbullying_model():
        80/20 stratified split, TF-IDF(max_features=1000, ngram_range=(1,2),
        stop_words='english'), LogisticRegression(class_weight='balanced').
        Saves the new model to self.model_path and hot-swaps it into memory.
        """
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found at {dataset_path}")

        df = pd.read_csv(dataset_path)
        if 'text' not in df.columns or 'label' not in df.columns:
            raise ValueError(
                "dataset.csv must contain 'text' and 'label' columns (matching the "
                "original training pipeline's expected schema)."
            )

        df['cleaned_text'] = df['text'].apply(self.clean_text)
        X = df['cleaned_text']
        y = df['label']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000, ngram_range=(1, 2))
        X_train_tfidf = vectorizer.fit_transform(X_train)
        X_test_tfidf = vectorizer.transform(X_test)

        model = LogisticRegression(class_weight='balanced', C=1.0, random_state=42)
        model.fit(X_train_tfidf, y_train)

        y_pred = model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        class_report = classification_report(y_test, y_pred, output_dict=True)

        model_data = {
            'model': model,
            'vectorizer': vectorizer,
            'accuracy': accuracy,
            'confusion_matrix': conf_matrix.tolist(),
            'classification_report': class_report,
        }

        os.makedirs(os.path.dirname(self.model_path) or ".", exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)

        with self._lock:
            self._model_data = model_data

        logger.info(f"Model retrained. accuracy={accuracy:.4f}, rows={len(df)}")

        return {
            'success': True,
            'accuracy': float(accuracy),
            'training_rows': len(X_train),
            'testing_rows': len(X_test),
            'message': 'Model retrained and hot-swapped into memory successfully.',
        }


# Module-level singleton, created on first import; main.py re-creates/reloads
# it explicitly on startup so MODEL_PATH from settings is respected.
model_service = ModelService(settings.MODEL_PATH)
