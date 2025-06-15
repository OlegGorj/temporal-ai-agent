from fastapi import FastAPI
from typing import Optional
from temporalio.client import Client
from temporalio.exceptions import TemporalError
from temporalio.api.enums.v1 import WorkflowExecutionStatus
from fastapi import HTTPException
from dotenv import load_dotenv
import asyncio
import os

from workflows.agent_goal_workflow import AgentGoalWorkflow
from models.data_types import CombinedInput, AgentGoalWorkflowParams
from tools.goal_registry import goal_match_train_invoice, goal_event_flight_invoice
from fastapi.middleware.cors import CORSMiddleware
from shared.config import get_temporal_client, TEMPORAL_TASK_QUEUE

app = FastAPI()
# temporal_client: Optional[Client] = None

# Load environment variables
load_dotenv()

_workflow_id = os.getenv("WORKFLOW_ID", "agent-workflow")
if not _workflow_id:
    raise ValueError(
        "WORKFLOW_ID environment variable is not set. Please set it to the desired workflow name."
    )

def get_agent_goal():
    """Get the agent goal from environment variables."""
    goal_name = os.getenv("AGENT_GOAL", "goal_match_train_invoice")
    goals = {
        "goal_match_train_invoice": goal_match_train_invoice,
        "goal_event_flight_invoice": goal_event_flight_invoice,
    }
    return goals.get(goal_name, goal_event_flight_invoice)


@app.on_event("startup")
async def startup_event():
    app.state.temporal_client = await get_temporal_client()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Temporal AI Agent!"}


@app.get("/tool-data")
async def get_tool_data():
    """Calls the workflow's 'get_tool_data' query."""
    try:
        # Get workflow handle
        handle = temporal_client.get_workflow_handle(_workflow_id)

        # Check if the workflow is completed
        workflow_status = await handle.describe()
        if workflow_status.status == 2:
            # Workflow is completed; return an empty response
            return {}

        # Query the workflow
        tool_data = await handle.query("get_tool_data")
        return tool_data
    except TemporalError as e:
        # Workflow not found; return an empty response
        print(e)
        return {}


@app.get("/history")
async def history():
    """Calls the workflow's 'get_history' query."""
    try:
        handle = temporal_client.get_workflow_handle(_workflow_id)
        failed_states = [
            WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_TERMINATED,
            WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_CANCELED,
            WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_FAILED,
        ]

        description = await handle.describe()
        if description.status in failed_states:
            print("Workflow is in a failed state. Returning empty history.")
            return []

        # Set a timeout for the query
        try:
            _history = await asyncio.wait_for(
                handle.query("get_history"),
                timeout=5,  # Timeout after 5 seconds
            )
            return _history
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=404,
                detail="Temporal query timed out (worker may be unavailable).",
            )
    except TemporalError as e:
        error_message = str(e)
        print(f"Temporal error: {error_message}")
        # If worker is down or no poller is available, return a 404
        if "no poller seen for task queue recently" in error_message:
            raise HTTPException(
                status_code=404, detail="Workflow worker unavailable or not found."
            )

        # For other Temporal errors, return a 500
        raise HTTPException(
            status_code=500, detail="Internal server error while querying workflow."
        )


@app.post("/send-prompt")
async def send_prompt(prompt: str):
    # Create combined input with goal from environment
    combined_input = CombinedInput(
        tool_params=AgentGoalWorkflowParams(None, None),
        agent_goal=get_agent_goal(),
    )

    # Start (or signal) the workflow
    await temporal_client.start_workflow(
        AgentGoalWorkflow.run,
        combined_input,
        id=_workflow_id,
        task_queue=TEMPORAL_TASK_QUEUE,
        start_signal="user_prompt",
        start_signal_args=[prompt],
    )

    return {"message": f"Prompt '{prompt}' sent to workflow {_workflow_id}."}


@app.post("/confirm")
async def send_confirm():
    """Sends a 'confirm' signal to the workflow."""
    handle = temporal_client.get_workflow_handle(_workflow_id)
    await handle.signal("confirm")
    return {"message": "Confirm signal sent."}


@app.post("/end-chat")
async def end_chat():
    """Sends a 'end_chat' signal to the workflow."""
    try:
        handle = temporal_client.get_workflow_handle(_workflow_id)
        await handle.signal("end_chat")
        return {"message": "End chat signal sent."}
    except TemporalError as e:
        print(e)
        # Workflow not found; return an empty response
        return {}


@app.post("/start-workflow")
async def start_workflow():
    # Get the configured goal
    agent_goal = get_agent_goal()

    # Create combined input
    combined_input = CombinedInput(
        tool_params=AgentGoalWorkflowParams(None, None),
        agent_goal=agent_goal,
    )

    # Start the workflow with the starter prompt from the goal
    await temporal_client.start_workflow(
        AgentGoalWorkflow.run,
        combined_input,
        id=_workflow_id,
        task_queue=TEMPORAL_TASK_QUEUE,
        start_signal="user_prompt",
        start_signal_args=["### " + agent_goal.starter_prompt],
    )

    return {
        "message": f"Workflow started with goal's starter prompt: {agent_goal.starter_prompt}."
    }
