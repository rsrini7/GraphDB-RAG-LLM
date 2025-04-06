import logging
from typing import List, Dict, Any, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from ..config import EMBEDDING_MODEL, EMBEDDING_DIMENSION

class EmbeddingGenerator:
    """Generates vector embeddings for text chunks.
    
    This class is responsible for using a pre-trained model to generate
    vector embeddings for preprocessed text chunks.
    """
    
    def __init__(self, model_name: str = None):
        """Initialize the EmbeddingGenerator.
        
        Args:
            model_name: Name of the SentenceTransformer model to use
        """
        self.model_name = model_name or EMBEDDING_MODEL
        self.dimension = EMBEDDING_DIMENSION
        self.logger = logging.getLogger(__name__)
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model."""
        try:
            self.logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.logger.info(f"Embedding model loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for a single text.
        
        Args:
            text: The text to generate an embedding for
            
        Returns:
            List of floats representing the embedding vector
        """
        if not self.model:
            self._load_model()
        
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            self.logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embedding vectors (each as a list of floats)
        """
        if not self.model:
            self._load_model()
        
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            self.logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    def process_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a list of text chunks and add embeddings.
        
        Args:
            chunks: List of chunk dictionaries with 'text' key
            
        Returns:
            List of chunk dictionaries with added 'embedding' key
        """
        texts = [chunk["text"] for chunk in chunks]
        
        try:
            embeddings = self.generate_embeddings(texts)
            
            # Add embeddings to the chunks
            for i, chunk in enumerate(chunks):
                chunk["embedding"] = embeddings[i]
            
            self.logger.info(f"Generated embeddings for {len(chunks)} chunks")
            return chunks
        except Exception as e:
            self.logger.error(f"Error processing chunks: {str(e)}")
            raise

# Create a singleton instance
embedding_generator = EmbeddingGenerator()