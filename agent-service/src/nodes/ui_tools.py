"""UI tool definitions for generative UI components."""

UI_TOOLS = [
    {
        "name": "show_approval_card",
        "description": "Display an approval card with options for the user to approve, edit, or reject",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the approval card"},
                "description": {"type": "string", "description": "Description or content to show"},
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of action options (e.g., ['Approve', 'Edit', 'Reject'])",
                },
            },
            "required": ["title", "description", "options"],
        },
    },
    {
        "name": "show_editable_value",
        "description": "Display an editable value field that the user can modify",
        "input_schema": {
            "type": "object",
            "properties": {
                "label": {"type": "string", "description": "Label for the field"},
                "value": {"type": "string", "description": "Current value"},
                "field_type": {
                    "type": "string",
                    "enum": ["text", "number", "date"],
                    "description": "Type of input field",
                },
            },
            "required": ["label", "value"],
        },
    },
    {
        "name": "show_document",
        "description": "Display a document or content summary with optional metadata",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Document title"},
                "content": {"type": "string", "description": "Main content to display"},
                "metadata": {"type": "object", "description": "Optional metadata key-value pairs"},
            },
            "required": ["title", "content"],
        },
    },
    {
        "name": "show_options",
        "description": "Display multiple choice options for the user to select from",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "The question to ask"},
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of options to choose from",
                },
            },
            "required": ["question", "options"],
        },
    },
    {
        "name": "show_research_summary",
        "description": "Display a formatted research summary with findings",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Summary title"},
                "findings": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key findings or insights",
                },
            },
            "required": ["title", "findings"],
        },
    },
]
