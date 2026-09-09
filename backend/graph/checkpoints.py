import logging
from typing import Dict, Any, Optional
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)

# Primary in-memory checkpoint saver for LangGraph thread persistence
memory_checkpointer = MemorySaver()

# Secondary state store for instant API access
STATE_SNAPSHOTS: Dict[str, Dict[str, Any]] = {}


def save_state_snapshot(run_id: str, state: Dict[str, Any]) -> None:
    STATE_SNAPSHOTS[run_id] = dict(state)


def get_state_snapshot(run_id: str) -> Optional[Dict[str, Any]]:
    return STATE_SNAPSHOTS.get(run_id)
