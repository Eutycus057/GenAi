import random;
import json;

with entry {
    # module-level initialisation if needed
}

obj Session {
    has id: str;
    has topic: str = "";
    has slides: list = [];
    has current_idx: int = 0;
    has transcript: list = [];
    has pptx_url: str = "";
}

# Emit events to the backend/frontend router (backend must implement /api/session/emit)
def emit_event(session: Session, event_type: str, payload: map) {
    external_call("/api/session/emit", {"session_id": session.id, "event": event_type, "payload": payload}) -> resp;
}
