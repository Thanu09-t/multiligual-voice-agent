import ast
import operator
import re
from typing import Any, Dict
from app.tools.base import BaseTool

# Supported mathematical operators
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        return float(node.value)
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        return SAFE_OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = safe_eval(node.operand)
        return SAFE_OPERATORS[op_type](operand)
    else:
        raise ValueError(f"Unsupported expression node: {type(node).__name__}")


class CalculatorTool(BaseTool):
    """Mathematical computation tool for exact calculations."""

    name = "calculator"
    description = "Execute exact mathematical calculations. Use for any arithmetic, percentages, or equations."
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate, e.g. '25% of 840', '15 * 24 + 10'",
            }
        },
        "required": ["expression"],
    }
    requires_confirmation = False

    async def execute(self, expression: str, **kwargs) -> Any:
        cleaned = expression.strip()

        # Handle percentage phrasing like "25% of 840" or "25 percent of 840"
        pct_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s*(?:of)?\s*(\d+(?:\.\d+)?)", cleaned, re.IGNORECASE)
        if pct_match:
            pct = float(pct_match.group(1)) / 100.0
            val = float(pct_match.group(2))
            res = pct * val
            formatted = int(res) if res.is_integer() else round(res, 6)
            return {"expression": expression, "result": formatted}

        # Replace natural language math words
        cleaned = re.sub(r"\btimes\b|\bmultiplied\s+by\b", "*", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\bdivided\s+by\b", "/", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\bplus\b", "+", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\bminus\b", "-", cleaned, flags=re.IGNORECASE)

        # Replace 'x' or 'X' with '*'
        cleaned = re.sub(r"(\d+)\s*[xX]\s*(\d+)", r"\1 * \2", cleaned)
        cleaned = cleaned.replace("^", "**")

        # Parse AST and evaluate safely
        parsed = ast.parse(cleaned, mode="eval")
        result = safe_eval(parsed.body)
        formatted_result = int(result) if isinstance(result, float) and result.is_integer() else round(result, 6)

        return {
            "expression": expression,
            "result": formatted_result,
        }
