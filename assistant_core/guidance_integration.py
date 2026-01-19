#!/usr/bin/env python3
"""
Guidance Integration - Advanced Prompt Templating and Control Flow

This module integrates Microsoft's Guidance library for better prompt
engineering with:
- Handlebars-style templating
- Interleaved generation, prompting, and logical control
- Constrained generation
- Better prompt structure management

License: Guidance is MIT licensed (safe for commercial use)
Reference: https://github.com/microsoft/guidance
"""

import os
from typing import Dict, Any, Optional, List, Union
import logging

logger = logging.getLogger(__name__)

# Try to import Guidance
GUIDANCE_IMPORT_ERROR: Optional[str] = None
try:
    import guidance
    # Guidance uses different import patterns depending on version
    # We'll use the programmatic API which is more stable
    GUIDANCE_AVAILABLE = True
except Exception as e:
    GUIDANCE_AVAILABLE = False
    GUIDANCE_IMPORT_ERROR = str(e)
    logger.debug("Guidance integration unavailable: %s", e)


class GuidancePromptEngine:
    """
    Prompt engine using Guidance for structured prompt generation
    and control flow.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        openai_api_key: Optional[str] = None,
    ):
        """
        Initialize Guidance prompt engine.

        Args:
            model: Model to use (default: gpt-4o-mini)
            openai_api_key: OpenAI API key (default: from env)
        """
        if not GUIDANCE_AVAILABLE:
            raise ImportError(
                "Guidance is not installed. Install with: pip install guidance"
            )

        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var.")

        # Initialize Guidance LLM
        # Note: Guidance API may vary by version
        try:
            self.llm = guidance.llms.OpenAI(
                model=model,
                api_key=api_key,
                temperature=0.7,
            )
        except AttributeError:
            # Fallback for different Guidance versions
            self.llm = guidance.llm(
                model=model,
                api_key=api_key,
                temperature=0.7,
            )
        self.model = model

    def generate_with_template(
        self,
        template: str,
        variables: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate text using a Guidance template with variables.

        Args:
            template: Guidance template string (Handlebars syntax)
            variables: Variables to inject into template
            **kwargs: Additional arguments for generation

        Returns:
            Dict with 'output' and 'metadata'
        """
        try:
            # Create Guidance program
            program = guidance(template, llm=self.llm)

            # Execute with variables
            result = program(**variables, **kwargs)

            return {
                "output": str(result),
                "variables": variables,
                "metadata": {
                    "model": self.model,
                    "template": template,
                },
            }
        except Exception as e:
            logger.error(f"Guidance generation failed: {e}")
            raise

    def create_conversation_template(
        self,
        system_prompt: str,
        conversation_history: List[Dict[str, str]],
        current_message: str,
    ) -> str:
        """
        Create a structured conversation template.

        Args:
            system_prompt: System instructions
            conversation_history: List of {'role': 'user/assistant', 'content': '...'}
            current_message: Current user message

        Returns:
            Generated response
        """
        # Build conversation template
        template_parts = [f"{{{{#system}}}}{system_prompt}{{{{/system}}}}"]

        # Add history
        for msg in conversation_history[-10:]:  # Last 10 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                template_parts.append(f"{{{{#user}}}}{content}{{{{/user}}}}")
            elif role == "assistant":
                template_parts.append(f"{{{{#assistant}}}}{content}{{{{/assistant}}}}")

        # Add current message
        template_parts.append(f"{{{{#user}}}}{current_message}{{{{/user}}}}")

        # Add assistant response
        template_parts.append("{{#assistant}}{{gen 'response'}}{{/assistant}}")

        template = "\n".join(template_parts)

        # Execute
        program = guidance(template, llm=self.llm)
        result = program()

        return result["response"]

    def generate_with_constraints(
        self,
        prompt: str,
        constraints: Dict[str, Any],
        **kwargs,
    ) -> str:
        """
        Generate text with constraints (e.g., format, length, keywords).

        Args:
            prompt: Base prompt
            constraints: Dict with constraints like:
                - max_length: Maximum output length
                - format: Output format (json, list, etc.)
                - keywords: Required keywords
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        # Build template with constraints
        template = f"{{{{#system}}}}{prompt}{{{{/system}}}}\n"

        if constraints.get("format") == "json":
            template += "{{#assistant}}{{gen 'response' stop='}}'}}{{/assistant}}"
        elif constraints.get("max_length"):
            max_tokens = constraints.get("max_length", 100)
            template += f"{{{{#assistant}}}}{{{{gen 'response' max_tokens={max_tokens}}}}}{{{{/assistant}}}}"
        else:
            template += "{{#assistant}}{{gen 'response'}}{{/assistant}}"

        program = guidance(template, llm=self.llm)
        result = program(**kwargs)

        return result.get("response", "")

    def create_structured_prompt(
        self,
        task_description: str,
        examples: Optional[List[Dict[str, str]]] = None,
        output_format: Optional[str] = None,
    ) -> str:
        """
        Create a structured prompt with examples and format specification.

        Args:
            task_description: Description of the task
            examples: Optional list of example input/output pairs
            output_format: Optional format specification

        Returns:
            Generated response
        """
        template_parts = [
            f"{{{{#system}}}}Task: {task_description}{{{{/system}}}}",
        ]

        # Add examples if provided
        if examples:
            template_parts.append("\nExamples:")
            for i, example in enumerate(examples, 1):
                input_text = example.get("input", "")
                output_text = example.get("output", "")
                template_parts.append(
                    f"\nExample {i}:\nInput: {input_text}\nOutput: {output_text}"
                )

        # Add format specification
        if output_format:
            template_parts.append(f"\nOutput format: {output_format}")

        # Add generation
        template_parts.append("\n{{#user}}Please complete the task.{{/user}}")
        template_parts.append("{{#assistant}}{{gen 'response'}}{{/assistant}}")

        template = "\n".join(template_parts)

        program = guidance(template, llm=self.llm)
        result = program()

        return result.get("response", "")


def create_guidance_engine(
    model: str = "gpt-4o-mini",
    openai_api_key: Optional[str] = None,
) -> Optional[GuidancePromptEngine]:
    """
    Factory function to create a Guidance prompt engine.

    Returns None if Guidance is not available (graceful degradation).
    """
    if not GUIDANCE_AVAILABLE:
        logger.debug("Guidance not available. Returning None.")
        return None

    try:
        return GuidancePromptEngine(model=model, openai_api_key=openai_api_key)
    except Exception as e:
        logger.error(f"Failed to create Guidance engine: {e}")
        return None
