import logging
from typing import List, Dict, Any, Union, Optional
import re
import nltk
from nltk.tokenize import sent_tokenize

class DocumentPreprocessor:
    """Preprocesses documents for embedding generation.
    
    This class is responsible for cleaning, chunking, and preparing text data
    for embedding generation.
    """
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """Initialize the DocumentPreprocessor.
        
        Args:
            chunk_size: Maximum size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.logger = logging.getLogger(__name__)
        
        # Download NLTK resources if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    def preprocess(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Preprocess a text document into chunks suitable for embedding.
        
        Args:
            text: The raw text to preprocess
            metadata: Optional metadata to associate with the document
            
        Returns:
            List of dictionaries containing processed chunks and metadata
        """
        # Clean the text
        cleaned_text = self._clean_text(text)
        
        # Split into chunks
        chunks = self._chunk_text(cleaned_text)
        
        # Prepare result with metadata
        result = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                "text": chunk,
                "chunk_id": i,
                "total_chunks": len(chunks)
            }
            
            # Add metadata if provided
            if metadata:
                chunk_data["metadata"] = metadata
            
            result.append(chunk_data)
        
        self.logger.info(f"Preprocessed document into {len(chunks)} chunks")
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean the text by removing extra whitespace and special characters.
        
        Args:
            text: The text to clean
            
        Returns:
            Cleaned text
        """
        # Replace multiple newlines with a single newline
        text = re.sub(r'\n+', '\n', text)
        
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s.,;:!?\-\'\"\(\)\[\]{}]', '', text)
        
        return text.strip()
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks of specified size.
        
        Args:
            text: The text to split into chunks
            
        Returns:
            List of text chunks
        """
        # First split by sentences to avoid cutting in the middle of a sentence
        sentences = sent_tokenize(text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed the chunk size, save the current chunk and start a new one
            if len(current_chunk) + len(sentence) > self.chunk_size:
                if current_chunk:  # Only append if not empty
                    chunks.append(current_chunk.strip())
                
                # Start a new chunk with overlap from the previous chunk if possible
                if self.chunk_overlap > 0 and current_chunk:
                    # Get the last few characters from the previous chunk for overlap
                    words = current_chunk.split()
                    overlap_text = " ".join(words[-min(len(words), self.chunk_overlap//5):])  # Approximate word count
                    current_chunk = overlap_text + " " + sentence
                else:
                    current_chunk = sentence
            else:
                # Add the sentence to the current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        # Add the last chunk if it's not empty
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

# Create a singleton instance
document_preprocessor = DocumentPreprocessor()