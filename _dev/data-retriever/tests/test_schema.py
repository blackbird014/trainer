"""Tests for schema validation."""

import pytest

from data_retriever.schema import Field, FieldType, Schema


def test_field_validation_string():
    """Test string field validation."""
    field = Field("name", FieldType.STRING, required=True)
    is_valid, error = field.validate("test")
    assert is_valid
    assert error is None

    is_valid, error = field.validate(123)
    assert not is_valid
    assert "string" in error.lower()


def test_field_validation_integer():
    """Test integer field validation."""
    field = Field("age", FieldType.INTEGER, required=True)
    is_valid, error = field.validate(42)
    assert is_valid

    is_valid, error = field.validate("42")
    assert not is_valid
    assert "integer" in error.lower()


def test_field_validation_optional():
    """Test optional field validation."""
    field = Field("optional", FieldType.STRING, required=False)
    is_valid, error = field.validate(None)
    assert is_valid  # Optional fields can be None

    field = Field("required", FieldType.STRING, required=True)
    is_valid, error = field.validate(None)
    assert not is_valid  # Required fields cannot be None


def test_field_validation_default():
    """Test field with default value."""
    field = Field("status", FieldType.STRING, required=False, default="active")
    assert field.default == "active"


def test_schema_validation():
    """Test schema validation."""
    schema = Schema(
        name="test_schema",
        fields=[
            Field("name", FieldType.STRING, required=True),
            Field("age", FieldType.INTEGER, required=True),
            Field("email", FieldType.STRING, required=False),
        ],
    )

    # Valid data
    is_valid, errors = schema.validate({"name": "John", "age": 30})
    assert is_valid
    assert len(errors) == 0

    # Missing required field
    is_valid, errors = schema.validate({"name": "John"})
    assert not is_valid
    assert any("age" in error.lower() for error in errors)

    # Wrong type
    is_valid, errors = schema.validate({"name": "John", "age": "thirty"})
    assert not is_valid
    assert any("integer" in error.lower() for error in errors)


def test_schema_to_dict():
    """Test schema to_dict conversion."""
    schema = Schema(
        name="test_schema",
        description="Test schema",
        fields=[
            Field("name", FieldType.STRING, required=True, description="Name field"),
        ],
    )

    schema_dict = schema.to_dict()
    assert schema_dict["name"] == "test_schema"
    assert schema_dict["description"] == "Test schema"
    assert len(schema_dict["fields"]) == 1
    assert schema_dict["fields"][0]["name"] == "name"

