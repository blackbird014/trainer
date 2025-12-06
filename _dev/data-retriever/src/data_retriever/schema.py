"""
Schema definitions for data validation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class FieldType(Enum):
    """Field type enumeration."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DICT = "dict"
    LIST = "list"
    ANY = "any"


@dataclass
class Field:
    """Schema field definition."""

    name: str
    field_type: FieldType
    required: bool = True
    description: Optional[str] = None
    default: Any = None
    validator: Optional[callable] = None

    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a value against this field.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            if self.required:
                return False, f"Field '{self.name}' is required"
            return True, None

        # Type checking
        if self.field_type == FieldType.STRING and not isinstance(value, str):
            return False, f"Field '{self.name}' must be a string"
        elif self.field_type == FieldType.INTEGER and not isinstance(value, int):
            return False, f"Field '{self.name}' must be an integer"
        elif self.field_type == FieldType.FLOAT and not isinstance(value, (int, float)):
            return False, f"Field '{self.name}' must be a float"
        elif self.field_type == FieldType.BOOLEAN and not isinstance(value, bool):
            return False, f"Field '{self.name}' must be a boolean"
        elif self.field_type == FieldType.DICT and not isinstance(value, dict):
            return False, f"Field '{self.name}' must be a dict"
        elif self.field_type == FieldType.LIST and not isinstance(value, list):
            return False, f"Field '{self.name}' must be a list"

        # Custom validator
        if self.validator is not None:
            try:
                if not self.validator(value):
                    return False, f"Field '{self.name}' failed custom validation"
            except Exception as e:
                return False, f"Field '{self.name}' validation error: {str(e)}"

        return True, None


@dataclass
class Schema:
    """Schema definition for data validation."""

    name: str
    fields: List[Field]
    description: Optional[str] = None

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate data against this schema.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        for field in self.fields:
            if field.name not in data:
                if field.required:
                    errors.append(f"Missing required field: {field.name}")
                elif field.default is not None:
                    data[field.name] = field.default
            else:
                is_valid, error = field.validate(data[field.name])
                if not is_valid:
                    errors.append(error)

        # Check for extra fields (warn but don't fail)
        extra_fields = set(data.keys()) - {f.name for f in self.fields}
        if extra_fields:
            # Allow extra fields, but could log warning
            pass

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "fields": [
                {
                    "name": f.name,
                    "type": f.field_type.value,
                    "required": f.required,
                    "description": f.description,
                    "default": f.default,
                }
                for f in self.fields
            ],
        }


# Common schemas
YAHOO_FINANCE_SCHEMA = Schema(
    name="yahoo_finance_stock_data",
    description="Yahoo Finance stock data schema",
    fields=[
        Field("ticker", FieldType.STRING, required=True, description="Stock ticker symbol"),
        Field("extractedAt", FieldType.STRING, required=True, description="ISO timestamp"),
        Field(
            "valuation",
            FieldType.DICT,
            required=True,
            description="Valuation metrics",
        ),
        Field(
            "financials",
            FieldType.DICT,
            required=True,
            description="Financial metrics",
        ),
        Field(
            "profitability",
            FieldType.DICT,
            required=True,
            description="Profitability metrics",
        ),
    ],
)

FILE_RETRIEVER_SCHEMA = Schema(
    name="file_data",
    description="File-based data schema",
    fields=[
        Field("path", FieldType.STRING, required=True, description="File path"),
        Field("content", FieldType.ANY, required=True, description="File content"),
        Field("format", FieldType.STRING, required=False, description="File format"),
    ],
)

API_RETRIEVER_SCHEMA = Schema(
    name="api_data",
    description="Generic API data schema",
    fields=[
        Field("url", FieldType.STRING, required=True, description="API URL"),
        Field("data", FieldType.ANY, required=True, description="Response data"),
        Field("status_code", FieldType.INTEGER, required=False, description="HTTP status code"),
    ],
)

