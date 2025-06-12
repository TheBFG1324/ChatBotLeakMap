# File: neo4j_driver.py
# This File handles all neo4j interactions for the exploitation script
from neo4j import GraphDatabase
import logging
from utils.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

logger = logging.getLogger(__name__)

# Neo4jDriver class holds all functionality to interact and get information from local Neo4j database
class Neo4jDriver:
    def __init__(self):
        self._driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    # Closes the connection with database
    def close(self):
        self._driver.close()

    # Executes a given cypher query
    def _execute(self, cypher: str, **params):
        with self._driver.session() as session:
            return session.run(cypher, params)

    # Inserts a given chatbot
    def insert_bot(self, bot_id: str, name: str, type_: str, url: str):
        cypher = '''
        MERGE (b:Bot {id: $bot_id})
        SET b.name = $name,
            b.type = $type,
            b.url = $url
        '''
        self._execute(cypher, bot_id=bot_id, name=name, type=type_, url=url)
        logger.debug(f"Upserted Bot {{id={bot_id}}}")

    # Creates a exploitation chain on a given bot
    def create_chain(self, chain_id: str, bot_id: str, timestamp: str, temperature: float, mode: str):
        cypher = '''
        CREATE (c:Chain {
            id: $chain_id,
            timestamp: datetime($timestamp),
            temperature: $temperature,
            mode: $mode,
            success: false
        })
        WITH c
        MATCH (b:Bot {id: $bot_id})
        CREATE (b)-[:TARGETED_IN]->(c)
        '''
        self._execute(
            cypher,
            chain_id=chain_id,
            bot_id=bot_id,
            timestamp=timestamp,
            temperature=temperature,
            mode=mode
        )
        logger.debug(f"Created Chain {{id={chain_id}}} for Bot {{id={bot_id}}}")

    # Gets a given prompt
    def get_or_create_prompt(self, prompt_id: str, text: str):
        cypher = '''
        MERGE (p:Prompt {id: $prompt_id})
        SET p.text = $text
        RETURN p.id AS id
        '''
        result = self._execute(cypher, prompt_id=prompt_id, text=text)
        return result.single()["id"]

    def get_or_create_response(self, response_id: str, text: str, timestamp: str, embedding: list):
        cypher = '''
        MERGE (r:Response {id: $response_id})
        SET r.text = $text,
            r.timestamp = datetime($timestamp),
            r.embedding = $embedding
        RETURN r.id AS id
        '''
        result = self._execute(
            cypher,
            response_id=response_id,
            text=text,
            timestamp=timestamp,
            embedding=embedding
        )
        return result.single()["id"]

    def link_step(self, chain_id: str, prompt_id: str, step_number: int):
        cypher = '''
        MATCH (c:Chain {id: $chain_id}), (p:Prompt {id: $prompt_id})
        CREATE (c)-[:STEP {step_number: $step_number}]->(p)
        '''
        self._execute(cypher, chain_id=chain_id, prompt_id=prompt_id, step_number=step_number)
        logger.debug(f"Linked Chain {{id={chain_id}}} -> Prompt {{id={prompt_id}}} at step {step_number}")

    def link_result(self, prompt_id: str, response_id: str):
        cypher = '''
        MATCH (p:Prompt {id: $prompt_id}), (r:Response {id: $response_id})
        MERGE (p)-[:RESULTED_IN]->(r)
        '''
        self._execute(cypher, prompt_id=prompt_id, response_id=response_id)
        logger.debug(f"Linked Prompt {{id={prompt_id}}} -> Response {{id={response_id}}}")

    def mark_chain_success(self, chain_id: str, response_id: str):
        cypher = '''
        MATCH (c:Chain {id: $chain_id}), (r:Response {id: $response_id})
        MERGE (c)-[:ENDED_IN_SUCCESS]->(r)
        SET c.success = true
        '''
        self._execute(cypher, chain_id=chain_id, response_id=response_id)
        logger.info(f"Chain {{id={chain_id}}} marked successful at Response {{id={response_id}}}")

    def find_best_match(self, embedding: list, threshold: float, bot_type: str, limit: int = 1):
        cypher = '''
        WITH $embedding AS emb, $threshold AS t, $bot_type AS bt
        CALL db.index.vector.cosineSimilarity(
            'responseEmbeddingIdx', emb
        ) YIELD node AS r, similarity
        MATCH (r)<-[:RESULTED_IN]-(p:Prompt)<-[:STEP]-(c:Chain)
        WHERE similarity > t
          AND (c)-[:TARGETED_IN]->(:Bot {type: bt})
          AND c.success = true
        RETURN p.id AS prompt_id, similarity
        ORDER BY similarity DESC
        LIMIT $limit
        '''
        result = self._execute(
            cypher,
            embedding=embedding,
            threshold=threshold,
            bot_type=bot_type,
            limit=limit
        )
        record = result.single()
        return dict(record) if record else None


# File: neo4j/embed.py
import openai
from utils.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    """
    Generate and return a 1536-dimensional embedding for the given text.
    """
    response = openai.Embedding.create(
        model=model,
        input=[text]
    )
    # Embedding API returns a list of embeddings; we provided one input
    embedding = response['data'][0]['embedding']
    return embedding
