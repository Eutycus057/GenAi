# live_agent.jac

import random;
import datetime as dt;

with entry {
    report "AI Teaching Assistant initialized...";
}

# Define an object to represent a teaching session
obj Session {
    has id: str;
    has student_name: str;
    has questions: list = [];
    has answers: list = [];
}

# Walker for handling student questions
walker student_question {
    has student_id: str;
    has question_text: str;
    has answer: str;

    can start with entry {
        report "Student {student_id} asked: {question_text}";
        answer = "This is a placeholder answer for: {question_text}";
        report "Answer: {answer}";
    }
}

# Walker for starting a lecture
walker start_lecture {
    has topic: str;
    has slides: list;
    has pptx_url: str;

    can start with entry {
        report "Starting lecture on {topic}";
        slides = [
            {
                "title": "Introduction to {topic}",
                "bullets": ["Definition of {topic}", "Why it matters", "Real-world applications"],
                "image": null
            },
            {
                "title": "{topic} - Core Concepts",
                "bullets": ["Concept 1", "Concept 2", "Concept 3"],
                "image": null
            },
            {
                "title": "Summary of {topic}",
                "bullets": ["Key points", "Further Reading"],
                "image": null
            }
        ];
        pptx_url = "/downloads/{topic}_slides.pptx";
        report "Slides prepared for {topic}";
    }
}
