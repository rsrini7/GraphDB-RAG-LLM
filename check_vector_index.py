import argparse
import logging
from database.neo4j_driver import neo4j_driver
from config import (
    VECTOR_NODE_LABEL,
    VECTOR_PROPERTY,
    EMBEDDING_DIMENSION,
)
from neo4j.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_neo4j_version():
    try:
        result = neo4j_driver.execute_query("CALL dbms.components() YIELD name, versions RETURN name, versions")
        for r in result or []:
            if r.get("name") == "Neo4j Kernel":
                return r.get("versions", ["unknown"])[0]
    except Exception as e:
        logger.error(f"Could not fetch Neo4j version: {str(e)}")
    return "unknown"

def drop_all_indexes_on_label_property(node_label, property_name):
    try:
        indexes = neo4j_driver.execute_query("SHOW INDEXES YIELD name, labelsOrTypes, properties, type")
        if not indexes:
            logger.warning("SHOW INDEXES returned no results or failed. Cannot drop property indexes.")
            return
        for idx in indexes:
            labels = idx.get("labelsOrTypes", [])
            properties = idx.get("properties", [])
            if not labels or not properties:
                continue
            if node_label in labels and property_name in properties:
                index_name = idx["name"]
                logger.info(f"Dropping index '{index_name}' on :{node_label}({property_name}) (type: {idx.get('type')})")
                try:
                    neo4j_driver.execute_query(f"DROP INDEX {index_name}")
                    logger.info(f"Dropped index '{index_name}'")
                except Exception as e:
                    logger.error(f"Failed to drop index '{index_name}': {str(e)}")
    except Exception as e:
        logger.error(f"Error listing/dropping indexes: {str(e)}")

def main(node_label, property_name, dimension):
    logger.info("Connecting to Neo4j...")
    version = get_neo4j_version()
    logger.info(f"Neo4j version: {version}")

    # Drop all indexes (property or vector) on this label/property
    drop_all_indexes_on_label_property(node_label, property_name)

    # Try to create vector index, but handle missing procedures gracefully
    vector_search = neo4j_driver.vector_search
    try:
        logger.info("Attempting to create vector index...")
        result = vector_search.create_vector_index(node_label=node_label, property_name=property_name, dimension=dimension)
        logger.info(f"Vector index creation result: {result}")
    except ClientError as ce:
        if "ProcedureNotFound" in str(ce) or "no procedure with the name" in str(ce) or "There is no such procedure" in str(ce):
            logger.error("Vector index procedures are not available on this Neo4j instance.")
            logger.error("Vector indexes require Neo4j 5.x+ Enterprise Edition or the vector index plugin.")
            logger.error("Please check your Neo4j version and installation: https://neo4j.com/docs/operations-manual/current/indexes-for-vectors/")
            logger.error("Skipping vector index creation, but property indexes (if any) have been dropped.")
        else:
            logger.error(f"Neo4j ClientError: {str(ce)}")
    except Exception as e:
        logger.error(f"Error creating index: {str(e)}")

    neo4j_driver.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check and (re)create Neo4j vector index.")
    parser.add_argument("--node_label", type=str, default=VECTOR_NODE_LABEL, help="Node label for the vector index")
    parser.add_argument("--property_name", type=str, default=VECTOR_PROPERTY, help="Property name for the vector index")
    parser.add_argument("--dimension", type=int, default=EMBEDDING_DIMENSION, help="Embedding dimension for the vector index")
    args = parser.parse_args()
    main(args.node_label, args.property_name, args.dimension)