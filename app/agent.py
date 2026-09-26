import json
import os

import pandas as pd

from dotenv import load_dotenv
from groq import Groq
from langchain_groq import ChatGroq

from app.state import AgentState
from app.planner import create_plan
from app.tools import TOOLS


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found in .env file."
    )


# =========================================================
# GROQ CLIENTS
# =========================================================

groq_client = Groq(
    api_key=GROQ_API_KEY
)

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.3,
    groq_api_key=GROQ_API_KEY
)


# =========================================================
# HELPER: CLEAN JSON
# =========================================================

def clean_json_response(content: str) -> str:

    if not content:
        return "{}"

    content = content.strip()

    if content.startswith("```json"):
        content = content[len("```json"):]

    elif content.startswith("```"):
        content = content[len("```"):]

    if content.endswith("```"):
        content = content[:-3]

    return content.strip()


# =========================================================
# HELPER: VISUALIZATION REQUESTED?
# =========================================================

def visualization_requested(
    user_task: str
) -> bool:

    task = user_task.lower()

    words = [
        "chart",
        "graph",
        "plot",
        "visualize",
        "visualization",
        "bar chart",
        "show graph",
        "show chart"
    ]

    return any(
        word in task
        for word in words
    )


# =========================================================
# HELPER: TOOL ALREADY USED
# =========================================================

def tool_already_used(
    state: AgentState,
    tool_name: str,
    arguments: dict
) -> bool:

    for observation in state.observations:

        if observation.get("tool") != tool_name:
            continue

        old_arguments = observation.get(
            "arguments",
            {}
        )

        result = observation.get(
            "result",
            {}
        )

        # Only treat successful executions
        # as already completed.
        if (
            isinstance(result, dict)
            and "error" not in result
            and old_arguments == arguments
        ):
            return True

    return False


# =========================================================
# HELPER: GET SUCCESSFUL OBSERVATIONS
# =========================================================

def successful_observations(
    state: AgentState,
    tool_name: str
) -> list:

    results = []

    for observation in state.observations:

        if observation.get("tool") != tool_name:
            continue

        result = observation.get(
            "result",
            {}
        )

        if (
            isinstance(result, dict)
            and "error" not in result
        ):
            results.append(
                observation
            )

    return results


# =========================================================
# CORRELATION CONTROLLER
# =========================================================

def get_next_correlation(
    state: AgentState,
    df: pd.DataFrame
) -> dict | None:

    numeric_columns = (
        df.select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )

    # -----------------------------------------------------
    # Need at least yield + one numeric column
    # -----------------------------------------------------

    if "yield" not in numeric_columns:
        return None

    other_columns = [
        column
        for column in numeric_columns
        if column != "yield"
    ]

    # -----------------------------------------------------
    # Check correlations already completed
    # -----------------------------------------------------

    completed_pairs = set()

    for observation in state.observations:

        if observation.get("tool") != "correlation":
            continue

        result = observation.get(
            "result",
            {}
        )

        if (
            not isinstance(result, dict)
            or "error" in result
        ):
            continue

        arguments = observation.get(
            "arguments",
            {}
        )

        column1 = arguments.get(
            "column1"
        )

        column2 = arguments.get(
            "column2"
        )

        if column1 and column2:

            completed_pairs.add(
                tuple(
                    sorted(
                        [
                            column1,
                            column2
                        ]
                    )
                )
            )

    # -----------------------------------------------------
    # Find next missing correlation
    # -----------------------------------------------------

    for column in other_columns:

        pair = tuple(
            sorted(
                [
                    "yield",
                    column
                ]
            )
        )

        if pair not in completed_pairs:

            return {
                "column1": "yield",
                "column2": column
            }

    return None


# =========================================================
# DECIDE NEXT ACTION
# =========================================================

def decide_next_action(
    state: AgentState,
    df: pd.DataFrame
) -> dict:

    observations = json.dumps(
        state.observations,
        indent=2,
        default=str
    )

    plan = json.dumps(
        state.plan,
        indent=2,
        default=str
    )

    columns = df.columns.tolist()

    numeric_columns = (
        df.select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )

    categorical_columns = (
        df.select_dtypes(
            exclude="number"
        )
        .columns
        .tolist()
    )

    prompt = f"""
You are the decision-making brain of an
agentic data analysis application.

You ONLY decide which Python tool should
run next.

You DO NOT execute tools.

==================================================
USER QUESTION
==================================================

{state.user_task}


==================================================
PLAN
==================================================

{plan}


==================================================
ACTUAL DATASET COLUMNS
==================================================

{columns}


==================================================
NUMERIC COLUMNS
==================================================

{numeric_columns}


==================================================
CATEGORICAL COLUMNS
==================================================

{categorical_columns}


==================================================
PREVIOUS OBSERVATIONS
==================================================

{observations}


==================================================
AVAILABLE TOOLS
==================================================

dataset_info

Arguments:
{{}}


statistics

Arguments:
{{
    "column": "numeric_column"
}}


group_by

Arguments:
{{
    "group_column": "categorical_column",
    "value_column": "numeric_column",
    "operation": "mean"
}}

Allowed operations:
mean
sum
max
min


correlation

Arguments:
{{
    "column1": "numeric_column",
    "column2": "numeric_column"
}}


filter

Arguments:
{{
    "column": "column_name",
    "value": "value"
}}


visualization

Arguments:
{{
    "category_column": "categorical_column",
    "value_column": "numeric_column"
}}


==================================================
RULES
==================================================

1. Use ONLY real dataset columns.

2. Never invent columns.

3. Never invent data.

4. Use previous observations.

5. Do not repeat successful tools.

6. dataset_info only describes the dataset.

7. It does NOT answer the user's question.

8. For:
"Which state has the highest average yield?"

use:

group_by

{{
    "group_column": "state",
    "value_column": "yield",
    "operation": "mean"
}}

9. For average/sum/min/max by category,
use group_by.

10. For correlation questions,
use correlation.

11. If the user asks for relationships
with yield, compare yield with the
other numeric columns.

12. If the user asks for a chart,
graph, plot or visualization:

first perform the required analysis,
then call visualization.

13. Do not finish before the user's
question is answered.

14. Do not call dataset_info repeatedly.

15. Return ONLY JSON.

==================================================
OUTPUT
==================================================

Tool:

{{
    "decision": "USE_TOOL",
    "tool": "tool_name",
    "arguments": {{}},
    "reason": "short reason"
}}

Finish:

{{
    "decision": "FINISH",
    "reason": "short reason"
}}
"""

    try:

        response = groq_client.chat.completions.create(

            model="openai/gpt-oss-20b",

            temperature=0.2,

            response_format={
                "type": "json_object"
            },

            messages=[

                {
                    "role": "system",
                    "content": (
                        "Return ONLY valid JSON. "
                        "Never execute tools."
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

        content = clean_json_response(
            content
        )

        decision = json.loads(
            content
        )

        if not isinstance(
            decision,
            dict
        ):
            return {
                "decision": "ERROR",
                "reason": (
                    "Invalid decision format."
                )
            }

        return decision

    except Exception as error:

        return {
            "decision": "ERROR",
            "reason": (
                "Decision model error: "
                f"{str(error)}"
            )
        }


# =========================================================
# EXECUTE TOOL
# =========================================================

def execute_tool(
    action: dict,
    df: pd.DataFrame
) -> dict:

    tool_name = action.get(
        "tool"
    )

    arguments = action.get(
        "arguments",
        {}
    )

    # -----------------------------------------------------
    # Validate tool
    # -----------------------------------------------------

    if not tool_name:

        return {
            "error": "No tool selected."
        }

    if tool_name not in TOOLS:

        return {
            "error": (
                f"Unknown tool: {tool_name}"
            )
        }

    # -----------------------------------------------------
    # Validate arguments
    # -----------------------------------------------------

    if not isinstance(
        arguments,
        dict
    ):

        return {
            "error": (
                "Tool arguments must be "
                "a dictionary."
            )
        }

    # -----------------------------------------------------
    # Execute
    # -----------------------------------------------------

    try:

        result = TOOLS[tool_name](
            df,
            **arguments
        )

        return result

    except Exception as error:

        return {
            "error": str(error)
        }


# =========================================================
# FINAL ANSWER
# =========================================================

def generate_final_answer(
    state: AgentState
) -> str:

    observations = json.dumps(
        state.observations,
        indent=2,
        default=str
    )

    prompt = f"""
You are the final answer component of
DataPilot.

USER QUESTION:

{state.user_task}


ACTUAL TOOL RESULTS:

{observations}


IMPORTANT:

Use ONLY the actual tool results.

Never invent numbers.

If group_by produced results,
use those exact values.

If correlation results exist,
report the actual correlation values.

For multiple correlation results,
identify the strongest relationship
using the absolute value of Pearson r.

Remember:

Correlation does not prove causation.

If visualization was created,
mention that a visualization was generated.

Give a concise natural answer.

Do not say the dataset has no columns
when actual dataset columns are present.

Do not say data is missing unless the
tool results actually show missing data.
"""

    try:

        response = llm.invoke(
            prompt
        )

        return response.content

    except Exception as error:

        # -------------------------------------------------
        # Safe fallback
        # -------------------------------------------------

        return (
            "Analysis completed.\n\n"
            + observations
            + "\n\n"
            + f"Final answer generation error: {error}"
        )


# =========================================================
# MAIN AGENT
# =========================================================

# =========================================================
# MAIN AGENT
# =========================================================

def run_agent(
    user_task: str,
    df: pd.DataFrame
) -> AgentState:

    # -----------------------------------------------------
    # CREATE STATE
    # -----------------------------------------------------

    state = AgentState(
        user_task=user_task
    )

    # -----------------------------------------------------
    # STEP 1: PLAN
    # -----------------------------------------------------

    state.status = "planning"

    try:

        state.plan = create_plan(
            user_task,
            df.columns.tolist()
        )

    except Exception as error:

        state.plan = [
            {
                "step": 1,
                "description": (
                    "Analyze the available dataset "
                    "to answer the user's question."
                )
            }
        ]

        state.observations.append(
            {
                "iteration": 0,
                "tool": "planner",
                "arguments": {},
                "result": {
                    "error": str(error)
                }
            }
        )

    # -----------------------------------------------------
    # STEP 2: EXECUTING
    # -----------------------------------------------------

    state.status = "executing"

    max_iterations = 10

    # -----------------------------------------------------
    # MAIN LOOP
    # -----------------------------------------------------

    for iteration in range(max_iterations):

        state.current_step = iteration

        # =================================================
        # ASK DECISION MODEL
        # =================================================

        decision = decide_next_action(
            state,
            df
        )

        decision_type = decision.get(
            "decision"
        )

        # =================================================
        # CORRELATION CONTROL
        # =================================================

        task_lower = user_task.lower()

        is_correlation_task = (
            "correlation" in task_lower
            or "relationship" in task_lower
            or "relationships" in task_lower
        )

        if is_correlation_task:

            next_correlation = get_next_correlation(
                state,
                df
            )

            # -------------------------------------------------
            # More correlation calculations required
            # -------------------------------------------------

            if next_correlation:

                decision = {
                    "decision": "USE_TOOL",
                    "tool": "correlation",
                    "arguments": next_correlation,
                    "reason": (
                        "Calculate the next missing "
                        "correlation with yield."
                    )
                }

                decision_type = "USE_TOOL"

            # -------------------------------------------------
            # All required correlations completed
            # -------------------------------------------------

            else:

                decision = {
                    "decision": "FINISH",
                    "reason": (
                        "All required correlations "
                        "with yield have been calculated."
                    )
                }

                decision_type = "FINISH"

        # =================================================
        # DECISION MODEL ERROR
        # =================================================

        if decision_type == "ERROR":

            reason = decision.get(
                "reason",
                "Unknown decision error."
            )

            state.tool_history.append(
                {
                    "iteration": iteration + 1,
                    "action": "ERROR",
                    "reason": reason
                }
            )

            state.observations.append(
                {
                    "iteration": iteration + 1,
                    "tool": "agent_decision",
                    "arguments": {},
                    "result": {
                        "error": reason
                    }
                }
            )

            state.status = "error"

            break

        # =================================================
        # FINISH REQUEST
        # =================================================

        if decision_type == "FINISH":

            # -------------------------------------------------
            # Check analytical tools
            # -------------------------------------------------

            analytical_tools = {
                "statistics",
                "group_by",
                "correlation",
                "filter",
                "visualization"
            }

            tools_used = [
                item.get("tool")
                for item in state.observations
            ]

            has_analysis = any(
                tool in analytical_tools
                for tool in tools_used
            )

            # -------------------------------------------------
            # Do not finish without analysis
            # -------------------------------------------------

            if not has_analysis:

                state.tool_history.append(
                    {
                        "iteration": iteration + 1,
                        "action": "CONTINUE",
                        "reason": (
                            "No analytical tool has "
                            "been executed yet."
                        )
                    }
                )

                continue

            # -------------------------------------------------
            # Visualization check
            # -------------------------------------------------

            if visualization_requested(
                user_task
            ):

                visualization_completed = any(
                    (
                        item.get("tool") == "visualization"
                        and isinstance(
                            item.get("result"),
                            dict
                        )
                        and "error"
                        not in item.get(
                            "result",
                            {}
                        )
                    )
                    for item in state.observations
                )

                if not visualization_completed:

                    state.tool_history.append(
                        {
                            "iteration": iteration + 1,
                            "action": "CONTINUE",
                            "reason": (
                                "Visualization was requested "
                                "but has not been completed."
                            )
                        }
                    )

                    continue

            # -------------------------------------------------
            # Finish successfully
            # -------------------------------------------------

            state.status = "completed"

            state.tool_history.append(
                {
                    "iteration": iteration + 1,
                    "action": "FINISH",
                    "reason": decision.get(
                        "reason",
                        "Analysis completed."
                    )
                }
            )

            break

        # =================================================
        # USE TOOL
        # =================================================

        if decision_type == "USE_TOOL":

            action = {
                "tool": decision.get(
                    "tool"
                ),
                "arguments": decision.get(
                    "arguments",
                    {}
                )
            }

            tool_name = action.get(
                "tool"
            )

            arguments = action.get(
                "arguments",
                {}
            )

            # -------------------------------------------------
            # Validate tool
            # -------------------------------------------------

            if not tool_name:

                state.tool_history.append(
                    {
                        "iteration": iteration + 1,
                        "action": "ERROR",
                        "reason": "No tool selected."
                    }
                )

                continue

            # -------------------------------------------------
            # Prevent duplicate successful calls
            # -------------------------------------------------

            if tool_already_used(
                state,
                tool_name,
                arguments
            ):

                state.tool_history.append(
                    {
                        "iteration": iteration + 1,
                        "action": "SKIP",
                        "reason": (
                            "The same tool with the same "
                            "arguments already succeeded."
                        )
                    }
                )

                continue

            # -------------------------------------------------
            # Execute tool
            # -------------------------------------------------

            result = execute_tool(
                action,
                df
            )

            # -------------------------------------------------
            # Save decision
            # -------------------------------------------------

            state.tool_history.append(
                {
                    "iteration": iteration + 1,
                    "action": action,
                    "reason": decision.get(
                        "reason",
                        ""
                    )
                }
            )

            # -------------------------------------------------
            # Save observation
            # -------------------------------------------------

            state.observations.append(
                {
                    "iteration": iteration + 1,
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": result
                }
            )

            # =================================================
            # GROUP BY SUCCESS
            # =================================================

            if (
                tool_name == "group_by"
                and isinstance(result, dict)
                and "grouped_results" in result
                and "error" not in result
            ):

                # ---------------------------------------------
                # If no visualization is required,
                # group_by already answers the question.
                # ---------------------------------------------

                if not visualization_requested(
                    user_task
                ):

                    state.status = "completed"

                    state.tool_history.append(
                        {
                            "iteration": iteration + 1,
                            "action": "FINISH",
                            "reason": (
                                "group_by produced the "
                                "required analytical result."
                            )
                        }
                    )

                    break

            # -------------------------------------------------
            # Continue loop
            # -------------------------------------------------

            continue

        # =================================================
        # UNKNOWN DECISION
        # =================================================

        state.tool_history.append(
            {
                "iteration": iteration + 1,
                "action": "UNKNOWN",
                "reason": (
                    "The decision model returned "
                    "an unknown decision."
                )
            }
        )

    # =====================================================
    # MAX ITERATIONS
    # =====================================================

    else:

        state.status = "max_iterations_reached"

    # =====================================================
    # STEP 3: FINAL ANSWER
    # =====================================================

    state.final_answer = generate_final_answer(
        state
    )

    return state