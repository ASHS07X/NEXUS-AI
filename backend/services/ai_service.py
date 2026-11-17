
import os
import json
import ollama
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:4b")
HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

client = ollama.Client(host=HOST)


SYSTEM_PROMPT = """
You are NEXUS AI, an enterprise IT service management assistant.

Your responsibilities:
1. Understand employee IT problems.
2. Provide safe, practical troubleshooting instructions.
3. Classify IT support tickets.
4. Recommend ticket priority.

Categories:
Network, Hardware, Software, Account Access,
Security, Email, Other.

Priority levels:
Low, Medium, High, Critical.

Always provide clear, concise and professional answers.
Never expose internal reasoning.
Never claim that a problem has been fixed without confirmation.
For suspicious security incidents, advise contacting IT support
instead of attempting risky fixes.
"""


def generate_response(issue: str):

    response = client.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
                Analyze this employee IT issue:

                {issue}

                Return:
                1. Issue summary
                2. Possible cause
                3. Troubleshooting steps
                4. Category
                5. Priority
                """
            }
        ],
        options={"temperature": 0.3}
    )

    return response.message.content


def classify_ticket(issue: str):

    prompt = f"""
    Classify this IT support issue:

    {issue}

    Return ONLY valid JSON:
    {{
        "category": "Network",
        "priority": "Medium",
        "summary": "Short issue description"
    }}

    Category must be one of:
    Network, Hardware, Software, Account Access,
    Security, Email, Other.

    Priority must be one of:
    Low, Medium, High, Critical.
    """

    response = client.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        format="json",
        options={"temperature": 0.1}
    )

    try:
        return json.loads(response.message.content)
    except (json.JSONDecodeError, TypeError):
        return {
            "category": "Other",
            "priority": "Medium",
            "summary": issue[:150]
        }
