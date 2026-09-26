import json
import os

from dotenv import load_dotenv
from groq import Groq


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found in .env"
    )


# =========================================================
# GROQ CLIENT
# =========================================================

client = Groq(
    api_key=GROQ_API_KEY
)


# =========================================================
# CREATE PLAN
# =========================================================

def create_plan(
    user_task: str,
    dataset_columns=None
):

    if dataset_columns is None:
        dataset_columns = []

    prompt = f"""
You are the planning component of an
agentic data analysis system.

Your job is to create a short, logical
step-by-step plan for answering the
user's question.

==================================================
USER QUESTION
==================================================

{user_task}


==================================================
ACTUAL DATASET COLUMNS
==================================================

{dataset_columns}


==================================================
STRICT RULES
==================================================

1. Use ONLY columns that actually exist
   in the dataset.

2. Never invent columns.

3. Never mention variables such as:
   soil properties,
   irrigation,
   temperature,
   humidity,
   planting density,
   pest incidence,
   or other variables unless
   they actually exist in the dataset.

4. The plan must be specific to the
   user's question.

5. Do not create unnecessary steps.

6. If the question asks for average
   by category, plan a group-by operation.

7. If the question asks for highest
   or lowest value by category,
   plan a group-by operation followed
   by comparison.

8. If the question asks for correlation,
   plan correlation calculations using
   numeric columns that actually exist.

9. If the user requests a chart,
   graph, plot, or visualization,
   include a visualization step.

10. The plan should describe what the
    agent will actually execute.

==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

Format:

{{
    "plan": [
        {{
            "step": 1,
            "description": "..."
        }},
        {{
            "step": 2,
            "description": "..."
        }}
    ]
}}
"""

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            temperature=0.2,

            response_format={
                "type": "json_object"
            },

            messages=[

                {
                    "role": "system",
                    "content": (
                        "You are a precise data "
                        "analysis planner. "
                        "Never invent dataset columns."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ]
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        result = json.loads(
            content
        )

        return result.get(
            "plan",
            []
        )

    except Exception as error:

        return [
            {
                "step": 1,
                "description": (
                    "Analyze the uploaded dataset "
                    "using only the available columns "
                    "to answer the user's question."
                )
            }
        ]