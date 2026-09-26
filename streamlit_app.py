import streamlit as st
import pandas as pd

from app.agent import run_agent


# ---------------------------------
# PAGE CONFIG
# ---------------------------------

st.set_page_config(
    page_title="DataPilot",
    page_icon="🤖",
    layout="wide"
)


# ---------------------------------
# SESSION STATE
# ---------------------------------

if "history" not in st.session_state:

    st.session_state.history = []


# ---------------------------------
# HEADER
# ---------------------------------

st.title(
    "🤖 DataPilot"
)

st.subheader(
    "Agentic AI Data Analysis Assistant"
)

st.write(
    """
Upload a CSV file and ask a natural-language
question. DataPilot will plan the task, select
analysis tools, execute them, observe the results,
and generate a final answer.
"""
)


# ---------------------------------
# SIDEBAR
# ---------------------------------

with st.sidebar:

    st.header(
        "⚙️ How DataPilot Works"
    )

    st.write(
        """
    1. Understand the task
    2. Create a plan
    3. Select tools
    4. Execute analysis
    5. Observe results
    6. Decide next action
    7. Generate final answer
    """
    )

    st.divider()

    st.subheader(
        "🗂️ Previous Questions"
    )

    if not st.session_state.history:

        st.caption(
            "No previous questions."
        )

    else:

        for item in reversed(
            st.session_state.history
        ):

            st.write(
                f"**Q:** {item['question']}"
            )

            st.write(
                f"**A:** {item['answer']}"
            )

            st.divider()


# ---------------------------------
# CSV UPLOAD
# ---------------------------------

uploaded_file = st.file_uploader(
    "📁 Upload CSV Dataset",
    type=["csv"]
)


if uploaded_file is None:

    st.info(
        "Upload a CSV file to begin."
    )

    st.stop()


# ---------------------------------
# LOAD DATASET
# ---------------------------------

try:

    df = pd.read_csv(
        uploaded_file
    )

except Exception as error:

    st.error(
        f"Unable to read CSV: {error}"
    )

    st.stop()


# ---------------------------------
# DATASET SUMMARY
# ---------------------------------

st.success(
    f"Dataset loaded successfully: "
    f"{len(df):,} rows × "
    f"{len(df.columns)} columns"
)


with st.expander(
    "👀 Preview Dataset"
):

    st.dataframe(
        df.head(10),
        use_container_width=True
    )


# ---------------------------------
# DATASET INFORMATION
# ---------------------------------

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Rows",
        f"{len(df):,}"
    )


with col2:

    st.metric(
        "Columns",
        len(df.columns)
    )


with col3:

    st.metric(
        "Missing Values",
        int(df.isna().sum().sum())
    )


# ---------------------------------
# QUESTION
# ---------------------------------

st.divider()

question = st.text_area(
    "💬 What would you like to analyze?",
    placeholder=(
        "Example: Compare average yield "
        "across states and check whether "
        "rainfall is correlated with yield."
    ),
    height=100
)


# ---------------------------------
# RUN AGENT
# ---------------------------------

run_button = st.button(
    "🚀 Run Agent",
    type="primary",
    use_container_width=True
)


if run_button:

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

        st.stop()

    try:

        with st.spinner(
            "🤖 Agent is planning and analyzing..."
        ):

            state = run_agent(
                question,
                df
            )

    except Exception as error:

        st.error(
            f"Agent error: {error}"
        )

        st.stop()


    # ---------------------------------
    # SAVE HISTORY
    # ---------------------------------

    st.session_state.history.append({

        "question": question,

        "answer": state.final_answer

    })


    # ---------------------------------
    # AGENT STATUS
    # ---------------------------------

    if state.status == "completed":

        st.success(
            "Agent completed the analysis."
        )

    else:

        st.warning(
            f"Agent status: {state.status}"
        )


    # ---------------------------------
    # PLAN
    # ---------------------------------

    st.subheader(
        "🧠 Agent Plan"
    )

    for index, step in enumerate(
        state.plan,
        start=1
    ):

        st.write(
            f"**Step {index}:** {step}"
        )


    # ---------------------------------
    # AGENT DECISIONS
    # ---------------------------------

    st.subheader(
        "🔎 Agent Decisions"
    )

    for item in state.tool_history:

        iteration = item.get(
            "iteration",
            "-"
        )

        action = item.get(
            "action"
        )

        reason = item.get(
            "reason",
            ""
        )

        with st.expander(
            f"Iteration {iteration}"
        ):

            st.write(
                "**Action:**"
            )

            if isinstance(
                action,
                dict
            ):

                st.code(
                    action["tool"]
                )

                st.write(
                    "**Arguments:**"
                )

                st.json(
                    action.get(
                        "arguments",
                        {}
                    )
                )

            else:

                st.write(
                    action
                )

            st.write(
                "**Reason:**"
            )

            st.write(
                reason
            )


    # ---------------------------------
    # OBSERVATIONS
    # ---------------------------------

    st.subheader(
        "🔧 Tool Observations"
    )

    for observation in (
        state.observations
    ):

        iteration = observation[
            "iteration"
        ]

        tool = observation[
            "tool"
        ]

        with st.expander(
            f"Iteration {iteration} — {tool}"
        ):

            st.write(
                "**Arguments:**"
            )

            st.json(
                observation["arguments"]
            )

            st.write(
                "**Result:**"
            )

            st.json(
                observation["result"]
            )


    # ---------------------------------
    # VISUALIZATION
    # ---------------------------------

    visualization_found = False

    for observation in (
        state.observations
    ):

        if observation["tool"] != (
            "visualization"
        ):

            continue

        result = observation[
            "result"
        ]

        if "data" not in result:

            continue

        chart_data = result["data"]

        chart_df = pd.DataFrame(
            {
                result["value_column"]:
                    chart_data
            }
        )

        st.subheader(
            "📊 Visualization"
        )

        st.bar_chart(
            chart_df
        )

        visualization_found = True


    # ---------------------------------
    # FINAL ANSWER
    # ---------------------------------

    st.divider()

    st.subheader(
        "💡 Final Answer"
    )

    st.write(
        state.final_answer
    )