import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a document Q&A assistant. Answer the user's question using ONLY the information in the provided chunks.

Rules:
- If the answer is not in the chunks, say "I couldn't find that in the document" — never guess.
- Write in plain, direct prose. Do not use Markdown, asterisks, bold, or bullet points.
- Keep answers short and clear. Get straight to the point — no preamble like "Based on the chunks provided."
- After each claim, cite the chunk you used like this: [1] or [1, 3].
- If listing multiple items, write them as a simple sentence, not a formatted list."""

def build_context(chunks: list[dict]) -> str:
    return "\n\n".join(
        f'<chunk id="{i+1}" source="{c["filename"]}" page="{c["page"]}">\n{c["text"]}\n</chunk>'
        for i, c in enumerate(chunks)
    )

def answer_question(question: str, chunks: list[dict]) -> str:
    context = build_context(chunks)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Here are the relevant document chunks:\n\n{context}\n\nQuestion: {question}"
        }]
    )
    return response.content[0].text