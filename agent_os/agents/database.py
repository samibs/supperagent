from .base import Agent, LLMModel

class DatabaseAgent(Agent):
    """
    The Database Agent designs the database schema, queries, and ensures
    data integrity based on the application's data models.
    """
    def __init__(self):
        super().__init__("DatabaseAgent")

    def execute_task(self, data_model_description: str) -> str:
        """
        Generates a database schema and sample queries for a given data model.

        Args:
            data_model_description (str): A description of the data models.

        Returns:
            str: SQL DDL for the schema and example queries.
        """
        self.log.info("Generating database schema...")
        self.log.debug(f"Data Model: {data_model_description}")

        # A model with strong logical and structured data capabilities is ideal.
        prompt = (
            "Based on the following data models, design a normalized SQL database "
            "schema (DDL). Also, provide example SELECT, INSERT, UPDATE, and "
            "DELETE queries for the primary tables."
            f"\n\n--- Data Models ---\n{data_model_description}"
        )

        db_schema = self._invoke_llm(model="gemini", prompt=prompt)

        self.log.info("Database schema generated.")
        return db_schema