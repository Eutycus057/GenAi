include "llm_bindings.jac";
include "helpers.jac";

with entry {
    # any module-level init (logger, config) can go here
}

# Use LLM to generate slides, store them in session, and request PPTX creation
def generate_and_prepare_slides(topic: str, session: Session) {
    slides = generate_slides(topic);
    session.topic = topic;
    session.slides = slides;
    session.current_idx = 0;

    # ask backend to create a downloadable PPTX (backend must implement /api/pptx/create)
    external_call("/api/pptx/create", {"session_id": session.id, "slides": slides}) -> ppt_resp;
    # safe-guard: check resp shape depending on your backend
    if (ppt_resp and ppt_resp.json and ("url" in ppt_resp.json)) {
        session.pptx_url = ppt_resp.json.url;
    } else {
        session.pptx_url = "";
    }

    emit_event(session, "slides_ready", {"slides_count": len(slides)});
}

# Present next slide: push slide to frontend and request TTS narration
def present_next_slide(session: Session) {
    if (session.current_idx < len(session.slides)) {
        slide = session.slides[session.current_idx];
        emit_event(session, "present_slide", slide);

        # request backend to speak the slide notes (backend implements /api/tts/speak)
        text_to_speak = "";
        if ("notes" in slide and slide.notes) {
            text_to_speak = slide.notes;
        } else if ("bullets" in slide) {
            text_to_speak = " ".join(slide.bullets);
        } else {
            text_to_speak = slide.title;
        }

        external_call("/api/tts/speak", {"session_id": session.id, "text": text_to_speak}) -> tts_resp;

        # advance pointer
        session.current_idx = session.current_idx + 1;
    } else {
        emit_event(session, "lecture_finished", {});
    }
}

# Handle an incoming student question (LLM + logging)
def handle_question(session: Session, student_id: str, question_text: str) -> str {
    # Build a compact context for the LLM
    ctx = {
        "current_slide": (session.slides[session.current_idx] if (session.current_idx < len(session.slides)) else {}),
        "transcript": session.transcript
    };

    answer_text = answer_question(question_text, ctx);

    # persist in-session transcript
    session.transcript.append({"student": student_id, "question": question_text, "answer": answer_text});

    # emit QA event to frontend / logging endpoint
    emit_event(session, "qa", {"student_id": student_id, "question": question_text, "answer": answer_text});

    # log to backend DB if you have /api/db/log_question implemented
    external_call("/api/db/log_question", {"session_id": session.id, "student_id": student_id, "question": question_text, "answer": answer_text}) -> log_resp;

    return answer_text;
}

# End lecture and produce summary
def end_lecture(session: Session) -> str {
    summary = summarize_discussion(session.transcript);

    emit_event(session, "summary", {"text": summary});

    return summary;
}
