import unittest

import src.persistence_schema as persistence_schema
from src.persistence_schema import TABLES, required_tables


class PersistenceSchemaTests(unittest.TestCase):
    def test_required_tables_cover_product_memory_design(self):
        self.assertEqual(
            required_tables(),
            {
                "users",
                "knowledge_bases",
                "documents",
                "ingestion_manifests",
                "chat_categories",
                "chat_tags",
                "chat_tag_links",
                "virtual_agents",
                "chats",
                "chat_participants",
                "messages",
                "citations",
                "memory_items",
                "jobs",
                "module_settings",
            },
        )

    def test_memory_items_include_scope_and_agent_columns(self):
        memory_columns = TABLES["memory_items"]
        self.assertIn("scope", memory_columns)
        self.assertIn("user_id", memory_columns)
        self.assertIn("agent_id", memory_columns)
        self.assertIn("chat_id", memory_columns)
        self.assertIn("importance", memory_columns)

    def test_schema_inventory_is_documented_as_planning_contract(self):
        self.assertIn("planning contract", persistence_schema.__doc__)
        self.assertIn("not an executable migration", persistence_schema.__doc__)

    def test_chat_agent_and_message_columns_preserve_extension_concepts(self):
        chat_columns = TABLES["chats"]
        self.assertIn("category_id", chat_columns)
        self.assertIn("category_source", chat_columns)
        self.assertIn("agent_id", chat_columns)
        self.assertIn("knowledge_base_id", chat_columns)

        agent_columns = TABLES["virtual_agents"]
        self.assertIn("system_prompt", agent_columns)
        self.assertIn("style_prompt", agent_columns)
        self.assertIn("memory_policy_id", agent_columns)
        self.assertIn("retrieval_policy_id", agent_columns)

        message_columns = TABLES["messages"]
        self.assertIn("chat_id", message_columns)
        self.assertIn("sender_type", message_columns)
        self.assertIn("sender_id", message_columns)
        self.assertIn("role", message_columns)
        self.assertIn("content", message_columns)


if __name__ == "__main__":
    unittest.main()
