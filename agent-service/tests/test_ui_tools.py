"""Tests for UI tool definitions."""


from src.nodes.ui_tools import UI_TOOLS


def test_ui_tools_list_exists():
    """Test that UI_TOOLS list is defined."""
    assert UI_TOOLS is not None
    assert isinstance(UI_TOOLS, list)


def test_ui_tools_count():
    """Test that we have the expected number of UI tools."""
    assert len(UI_TOOLS) == 5


def test_all_tools_have_required_fields():
    """Test that all tools have required fields."""
    for tool in UI_TOOLS:
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
        assert isinstance(tool["name"], str)
        assert isinstance(tool["description"], str)
        assert isinstance(tool["input_schema"], dict)


def test_show_approval_card_schema():
    """Test show_approval_card tool schema."""
    tool = next(t for t in UI_TOOLS if t["name"] == "show_approval_card")

    assert tool["description"] == (
        "Display an approval card with options for the user to approve, edit, or reject"
    )

    schema = tool["input_schema"]
    assert schema["type"] == "object"
    assert "title" in schema["properties"]
    assert "description" in schema["properties"]
    assert "options" in schema["properties"]
    assert schema["required"] == ["title", "description", "options"]


def test_show_editable_value_schema():
    """Test show_editable_value tool schema."""
    tool = next(t for t in UI_TOOLS if t["name"] == "show_editable_value")

    assert "editable value field" in tool["description"].lower()

    schema = tool["input_schema"]
    assert "label" in schema["properties"]
    assert "value" in schema["properties"]
    assert "field_type" in schema["properties"]
    assert schema["required"] == ["label", "value"]

    # Check field_type enum
    field_type_prop = schema["properties"]["field_type"]
    assert field_type_prop["enum"] == ["text", "number", "date"]


def test_show_document_schema():
    """Test show_document tool schema."""
    tool = next(t for t in UI_TOOLS if t["name"] == "show_document")

    assert "document" in tool["description"].lower()

    schema = tool["input_schema"]
    assert "title" in schema["properties"]
    assert "content" in schema["properties"]
    assert "metadata" in schema["properties"]
    assert schema["required"] == ["title", "content"]


def test_show_options_schema():
    """Test show_options tool schema."""
    tool = next(t for t in UI_TOOLS if t["name"] == "show_options")

    assert "multiple choice" in tool["description"].lower()

    schema = tool["input_schema"]
    assert "question" in schema["properties"]
    assert "options" in schema["properties"]
    assert schema["required"] == ["question", "options"]


def test_show_research_summary_schema():
    """Test show_research_summary tool schema."""
    tool = next(t for t in UI_TOOLS if t["name"] == "show_research_summary")

    assert "research summary" in tool["description"].lower()

    schema = tool["input_schema"]
    assert "title" in schema["properties"]
    assert "findings" in schema["properties"]
    assert schema["required"] == ["title", "findings"]


def test_all_tool_names_unique():
    """Test that all tool names are unique."""
    names = [tool["name"] for tool in UI_TOOLS]
    assert len(names) == len(set(names))


def test_tool_schemas_are_valid_json_schema():
    """Test that all input_schemas follow JSON Schema format."""
    for tool in UI_TOOLS:
        schema = tool["input_schema"]
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert isinstance(schema["properties"], dict)
        assert "required" in schema
        assert isinstance(schema["required"], list)
