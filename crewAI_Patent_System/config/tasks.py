# config/tasks.py

# Define the tasks configuration
tasks = [
    {
        "name": "initial_idea_task",
        "description": """
            Help conceptualize and refine Mercedes-Benz's initial patent idea. 
            The core problem to solve involves [describe the specific problem]. 
            Provide at least three specific improvement suggestions, each with detailed explanations and potential technical implementation methods.
        """,
        "expected_output": "Refined ideas with three potential improvements, including implementation methods and technical depth.",
        "output_file": "initial_ideas.md"
    },
    {
        "name": "innovation_task",
        "description": """
            Identify and mine new patentable innovations. Propose effective questions and provide at least three new patent innovation points. 
            For each, describe its uniqueness, background, and potential applications. Evaluate and select the most relevant innovations for Mercedes-Benz.
        """,
        "expected_output": "Three innovative points with clear descriptions, uniqueness, and applications.",
        "output_file": "innovations.md"
    },
    {
        "name": "qa_task",
        "description": """
            Answer standard patent-related questions in detail, ensuring technical accuracy. 
            Questions should cover the work done for the invention, its technical problems, existing related technologies, solutions, advantages, and a concise summary of the invention.
        """,
        "expected_output": "Complete, detailed answers to each question using professional terminology.",
        "output_file": "qa_answers.md"
    },
    {
        "name": "customization_task",
        "description": """
            Draft the patent document with technical details, including mathematical formulas and deep learning algorithms. 
            Ensure the formulas are in a format that can be directly pasted into Word (no LaTeX), and use symbols like ∑, xᵢ, yⱼ, ∫, ⊕, ⊗, etc. Provide technical implementation details and algorithm descriptions, ensuring the content is highly actionable and professional.
        """,
        "expected_output": "A professional patent document in Chinese, including technical details, mathematical formulas, and algorithm descriptions.",
        "output_file": "patent_draft.md"
    },
    {
        "name": "deep_improvement_task",
        "description": """
            Perform deep improvements on the technical details, mathematical principles, and deep learning algorithms. 
            Compare with existing technologies, highlight novelty, and enhance the patent document structure, including Background Technology, Invention Content, Specific Implementation Methods, and Claims.
        """,
        "expected_output": "Final improved patent document, exceeding 4000 words, with refined technical details, better logical structure, and improved patentability.",
        "output_file": "final_patent.md"
    }
]
