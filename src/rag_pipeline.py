from src.answer_pipeline import AnswerPipeline


def ask_question(db, question, memory):
    return AnswerPipeline().answer(db, question, memory)
