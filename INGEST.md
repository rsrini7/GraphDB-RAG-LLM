# GraphRAG Data Ingestion CLI

This CLI tool allows you to ingest data files into the GraphRAG system, preprocess them, generate embeddings, and store them for retrieval-augmented generation.

---

## Usage

Activate your virtual environment, then run:

```bash
python src/data_ingestion/cli.py --data-path <path_to_data> [options]
```

---

## Required Argument

- `--data-path`  
  Path to a data file or directory to ingest.

---

## Optional Arguments

- `--file-type {csv,json,txt}`  
  Filter files by type when ingesting a directory.

- `--chunk-size <int>`  
  Maximum size of text chunks in characters (default: 512).

- `--chunk-overlap <int>`  
  Overlap between chunks in characters (default: 50).

- `--embedding-model <model_name>`  
  Name of the SentenceTransformer model to use for embeddings.

- `--clear-existing`  
  Clear existing data before ingestion.

- `--verbose`  
  Enable verbose logging output.

---

## Examples

Ingest a single CSV file:

```bash
python src/data_ingestion/cli.py --data-path data/myfile.csv --file-type csv
```

Ingest all JSON files in a directory, clearing existing data:

```bash
python src/data_ingestion/cli.py --data-path data/ --file-type json --clear-existing
```

Use a specific embedding model with verbose logging:

```bash
python src/data_ingestion/cli.py --data-path data/ --embedding-model all-MiniLM-L6-v2 --verbose
```

---

## Description

- The CLI will preprocess the data files, splitting large texts into manageable chunks.
- It generates embeddings for each chunk using the specified or default model.
- Embeddings and metadata are stored in the system's database for efficient retrieval.
- You can clear existing data before ingestion using `--clear-existing`.
- Verbose mode provides detailed logs for debugging and monitoring.

---

## Notes

- Ensure your virtual environment is activated before running the CLI.
- Supported file types are CSV, JSON, and TXT.
- The embedding model defaults to the one configured in your environment if not specified.
