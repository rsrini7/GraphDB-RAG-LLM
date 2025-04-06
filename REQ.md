# Requirements for GraphRAG Localhost Implementation

## 1. Overview

This document outlines the requirements for building a local Graph-based Retrieval-Augmented Generation (GraphRAG) system. The system will allow users to ask natural language questions via a Streamlit interface. It will leverage a Langchain orchestrator to process the question, potentially perform vector searches and structured graph queries against a local Neo4j database (containing both graph data and vector indexes), and use an LLM (via OpenRouter) to generate Cypher queries and synthesize final natural language answers. The system includes data ingestion, preprocessing, embedding generation, caching, error handling, and basic monitoring capabilities, all designed to run locally using Docker Compose for Neo4j and potentially LocalStack for S3 emulation.

## 2. Core Technologies & Components

*   **User Interface:** Streamlit
*   **Orchestration:** Langchain (Python)
*   **LLM Interface:** OpenRouter API
*   **Graph Database:** Neo4j (running via Docker Compose)
    *   Includes Neo4j Vector Index functionality
*   **Database Driver:** Neo4j Python Driver
*   **Data Storage (Source):** Local Files (e.g., CSV, JSON)
*   **Cloud Emulation (Optional):** LocalStack (for S3 emulation)
*   **Containerization:** Docker Compose (for Neo4j, potentially LocalStack)
*   **Programming Language:** Python

## 3. Functional Requirements

### 3.1. User Interface (Streamlit)

*   **FR-UI-01:** Provide a web interface using Streamlit.
*   **FR-UI-02:** Accept natural language questions as text input from the user (Label: "1. User Question (NL)").
*   **FR-UI-03:** Display the final generated natural language answer to the user (Label: "10. Final Answer").
*   **FR-UI-04:** Interact with the Langchain Orchestrator to send questions and receive answers.

### 3.2. Langchain Orchestrator

*   **FR-ORCH-01:** Act as the central controller for the RAG process.
*   **FR-ORCH-02:** Receive the user's question from the Streamlit UI.
*   **FR-ORCH-03:** Implement caching logic:
    *   Check the `Response Cache` for existing results based on the question ("Retrieve Cached").
    *   If a cache hit occurs, return the cached result directly to the UI.
    *   If a cache miss occurs, proceed with the full RAG flow.
    *   Store newly generated results in the `Response Cache` ("Cache Results").
*   **FR-ORCH-04:** Initiate vector search (if applicable) by interacting with the `Document Preprocessor` / `Embedding Generator` pathway or directly querying the `Vector DB` for similar documents based on the user query ("Vector Search" -> Preprocessor; "Similar Documents" <- Vector DB).
*   **FR-ORCH-05:** Prepare and send prompts to the `Query Translator` to generate a Cypher query based on the user question and potentially context from vector search (Label: "2. Generate Cypher Prompt").
*   **FR-ORCH-06:** Receive the generated Cypher query from the `Query Translator` (Label: "4. Generate Cypher Query").
*   **FR-ORCH-07:** Execute the generated Cypher query against the Neo4j database via the `Neo4j Python Driver` (Label: "5. Execute Cypher Query").
*   **FR-ORCH-08:** Receive query results from the `Neo4j Python Driver` (Label: "7. Results" - *Note: Diagram shows this going to Ingestion Script, but logically the orchestrator needs results too. Assuming orchestrator gets results from Driver after execution*).
*   **FR-ORCH-09:** Prepare and send prompts (including the original question, retrieved graph data, and potentially similar documents from vector search) to the `Answer Generator` (Label: "8. Prepare Answer Prompt").
*   **FR-ORCH-10:** Receive the final natural language answer from the `Answer Generator` (Label: "9. Generate Final Answer").
*   **FR-ORCH-11:** Return the final answer to the Streamlit UI.
*   **FR-ORCH-12:** Interact with the `Error Handler` to manage exceptions during the process ("Handle Errors", "Error Recovery").
*   **FR-ORCH-13:** Log key activities and metrics to the `Monitoring Dashboard` ("Log Activity").

### 3.3. Query Translator (LLM-based)

*   **FR-QT-01:** Receive prompts (including user question, potentially schema info, context) from the Orchestrator.
*   **FR-QT-02:** Interact with the configured LLM via the `OpenRouter API` ("Uses").
*   **FR-QT-03:** Generate a valid Neo4j Cypher query designed to retrieve relevant information from the graph database.
*   **FR-QT-04:** Return the generated Cypher query to the Orchestrator.
*   **FR-QT-05:** Implicitly require access to or information about the Neo4j graph schema (indicated by "3. Query Schema Info" flow originating from Neo4j Instance, likely consumed during prompt preparation by Orchestrator or directly by Translator).

### 3.4. Answer Generator (LLM-based)

*   **FR-AG-01:** Receive prompts (including original question, retrieved graph data/context, potentially vector search results) from the Orchestrator.
*   **FR-AG-02:** Interact with the configured LLM via the `OpenRouter API` ("Uses").
*   **FR-AG-03:** Synthesize a coherent, human-readable natural language answer based on the provided information.
*   **FR-AG-04:** Return the generated natural language answer to the Orchestrator.

### 3.5. LLM Interface (OpenRouter API)

*   **FR-LLM-01:** Provide a standardized interface to call various LLMs available through OpenRouter.
*   **FR-LLM-02:** Handle authentication with the OpenRouter API (API Key).
*   **FR-LLM-03:** Allow configuration of the specific LLM model to be used for translation and answer generation.

### 3.6. Data Ingestion & Processing

*   **FR-DI-01:** `Data Ingestion Script`:
    *   Read data from source `Raw Data` files (CSV, JSON) (Label: "a. Read").
    *   Optionally interact with `LocalStack` S3 emulation (potentially reading data stored via "Store Documents", and using it for "c. Populate Database" via the Driver). *Clarification needed on exact LocalStack workflow based on diagram labels.*
    *   Coordinate with `Document Preprocessor` and `Embedding Generator`.
    *   Use the `Neo4j Python Driver` to write structured graph data to the `Neo4j Instance` (Label: "b. Write Graph Data").
    *   Use the `Neo4j Python Driver` to store generated vectors in the `Vector DB (Neo4j Vector Index)` (Label: "Store Vectors").
    *   Must be runnable as a standalone process.
*   **FR-DI-02:** `Document Preprocessor`:
    *   Receive raw text data (likely from the Ingestion Script).
    *   Perform necessary preprocessing steps (e.g., cleaning, chunking) suitable for the `Embedding Generator`.
    *   Pass processed data to the `Embedding Generator`.
*   **FR-DI-03:** `Embedding Generator`:
    *   Receive preprocessed text chunks.
    *   Use a configured embedding model (e.g., SentenceTransformers, API call) to generate vector embeddings for each chunk.
    *   Provide the generated vectors (and associated text/metadata) for storage.

### 3.7. Database Interaction (Neo4j Python Driver)

*   **FR-DB-01:** Provide connectivity to the local `Neo4j Instance`.
*   **FR-DB-02:** Execute arbitrary Cypher queries received from the Orchestrator or Ingestion Script.
*   **FR-DB-03:** Return query results.
*   **FR-DB-04:** Fetch graph schema information (Label: "3. Query Schema Info").
*   **FR-DB-05:** Handle writing/updating graph nodes and relationships.
*   **FR-DB-06:** Handle writing vector embeddings and metadata to the `Vector DB (Neo4j Vector Index)`.
*   **FR-DB-07:** Manage database connections and sessions appropriately.

### 3.8. Caching (Response Cache)

*   **FR-CACHE-01:** Store key-value pairs, where the key is likely related to the user question and the value is the generated response (or intermediate data).
*   **FR-CACHE-02:** Provide methods for retrieving (`Retrieve Cached`) and storing (`Cache Results`) entries.
*   **FR-CACHE-03:** Implement a cache invalidation strategy (e.g., TTL, manual clear - *not specified in diagram, needs definition*).
*   **FR-CACHE-04:** Use a simple local mechanism (e.g., Python dictionary, file-based cache, potentially Redis if added).

### 3.9. Error Handling (Error Handler)

*   **FR-ERR-01:** Provide centralized logic to catch and handle exceptions occurring during the RAG process.
*   **FR-ERR-02:** Implement basic error recovery strategies if feasible (e.g., retry LLM call, return a fallback message).
*   **FR-ERR-03:** Log errors appropriately (likely interacting with the Monitoring Dashboard/logging system).

### 3.10. Monitoring (Monitoring Dashboard)

*   **FR-MON-01:** Provide a mechanism to view logs and potentially basic metrics generated by the Orchestrator and other components.
*   **FR-MON-02:** Could range from simple console output/log file aggregation to a basic dashboard integrated into Streamlit. *Implementation detail needs definition.*

## 4. Non-Functional Requirements

*   **NFR-01:** **Local Execution:** The entire system (UI, Processing Layer, Data Layer including DB) must run on a single local machine.
*   **NFR-02:** **Containerization:** Neo4j and LocalStack must be managed via Docker Compose for easy setup and teardown.
*   **NFR-03:** **Configuration:** Sensitive information (API Keys like OpenRouter, DB credentials) and key parameters (LLM model names, embedding model names) must be configurable via environment variables or a configuration file (e.g., `.env`).
*   **NFR-04:** **Modularity:** Python code should be organized into logical modules representing the different components in the diagram.
*   **NFR-05:** **Security:** API keys must not be hardcoded in the source code.

## 5. Data Requirements

*   **DR-01:** **Input Data:** Define the expected format(s) (CSV, JSON) and schema of the raw input data files.
*   **DR-02:** **Neo4j Graph Schema:** Define the target node labels, relationship types, and properties for the structured graph data in Neo4j.
*   **DR-03:** **Neo4j Vector Index:** Define the configuration for the Neo4j vector index (e.g., index name, node label, property storing the embedding, dimensions, similarity metric).

## 6. Key Interactions & Flows (Summary)

*   **Main Query Flow:** UI -> Orchestrator -> [Cache Check] -> [Cache Hit -> UI] / [Cache Miss -> Query Translator -> LLM -> Orchestrator -> Driver -> Neo4j -> Driver -> Orchestrator -> Answer Generator -> LLM -> Orchestrator -> Cache Store -> UI].
*   **Vector Search Integration:** Query potentially triggers vector search via Orchestrator -> Preprocessor/Embedding pathway or direct query to Vector DB -> Results ("Similar Documents") inform Query Translator and/or Answer Generator prompts.
*   **Data Ingestion Flow:** Raw Data/LocalStack -> Ingestion Script -> Preprocessor -> Embedding Generator -> Driver -> Neo4j Instance & Vector DB.