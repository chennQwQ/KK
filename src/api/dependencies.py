_db = None


def get_knowledge_base():
    global _db
    if _db is None:
        from src.vector_db import initialize_knowledge_base

        _db = initialize_knowledge_base()
    return _db


def get_answer_pipeline():
    from src.answer_pipeline import AnswerPipeline

    return AnswerPipeline()


def get_memory():
    from langchain_classic.memory import ConversationBufferWindowMemory

    return ConversationBufferWindowMemory(
        k=3,
        memory_key="chat_history",
        return_messages=True,
    )
