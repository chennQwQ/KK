import unittest

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


if __name__ == "__main__":
    unittest.main()
