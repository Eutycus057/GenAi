import from byllm { Model };

with entry {
    # binding to the LLM model (adjust model_name as needed)
}

glob llm = Model(model_name = "gpt-4");

# LLM-backed functions using `by llm()` style
# The Jac runtime will route these to the configured Model instance.

def generate_slides(topic: str) -> list by llm();
def answer_question(question: str, context: map) -> str by llm();
def summarize_discussion(transcript: list) -> str by llm();
