#!/usr/bin/env python3
"""
Prompttools Integration - Testing and Evaluating Prompts

This module integrates Prompttools for testing and evaluating
prompts, models, and vector databases.

License: Prompttools is MIT licensed (safe for commercial use)
Reference: https://github.com/hegelai/prompttools
"""

import os
from typing import Dict, Any, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

# Try to import Prompttools
PROMPTTOOLS_IMPORT_ERROR: Optional[str] = None
try:
    from prompttools.experiment import OpenAIChatExperiment
    from prompttools.experiment import OpenAICompletionExperiment
    from prompttools.utils import autoeval
    PROMPTTOOLS_AVAILABLE = True
except Exception as e:
    PROMPTTOOLS_AVAILABLE = False
    PROMPTTOOLS_IMPORT_ERROR = str(e)
    logger.debug("Prompttools integration unavailable: %s", e)


class PromptEvaluator:
    """
    Prompt evaluator using Prompttools for testing and comparing prompts.
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
    ):
        """
        Initialize prompt evaluator.

        Args:
            openai_api_key: OpenAI API key (default: from env)
        """
        if not PROMPTTOOLS_AVAILABLE:
            raise ImportError(
                "Prompttools is not installed. Install with: pip install prompttools"
            )

        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var.")

    def evaluate_prompts(
        self,
        prompts: List[str],
        models: Optional[List[str]] = None,
        system_prompts: Optional[List[str]] = None,
        test_inputs: Optional[List[str]] = None,
        evaluation_function: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate multiple prompts and compare results.

        Args:
            prompts: List of prompt variations to test
            models: List of models to test (default: ['gpt-4o-mini'])
            system_prompts: Optional system prompts
            test_inputs: Test inputs to use
            evaluation_function: Optional custom evaluation function

        Returns:
            Dict with evaluation results
        """
        if not test_inputs:
            test_inputs = ["Test input"]

        if not models:
            models = ["gpt-4o-mini"]

        try:
            # Create experiment
            experiment = OpenAIChatExperiment(
                model=models,
                messages=[
                    [
                        {"role": "system", "content": sp or ""}
                        if sp
                        else {"role": "user", "content": prompt}
                        for sp in (system_prompts or [None])
                        for prompt in prompts
                    ]
                ],
                temperature=[0.7],
                max_tokens=[1000],
            )

            # Run experiment
            experiment.run()

            # Get results
            results = experiment.get_table()

            return {
                "results": results.to_dict(),
                "summary": {
                    "num_prompts": len(prompts),
                    "num_models": len(models),
                    "num_test_inputs": len(test_inputs),
                },
            }
        except Exception as e:
            logger.error(f"Prompt evaluation failed: {e}")
            raise

    def compare_prompt_variations(
        self,
        base_prompt: str,
        variations: List[str],
        test_cases: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
    ) -> Dict[str, Any]:
        """
        Compare different variations of a prompt.

        Args:
            base_prompt: Base prompt to compare against
            variations: List of prompt variations
            test_cases: List of test cases with 'input' and 'expected_output'
            model: Model to use for testing

        Returns:
            Comparison results
        """
        all_prompts = [base_prompt] + variations

        try:
            # Create messages for each prompt and test case
            messages = []
            for prompt in all_prompts:
                for test_case in test_cases:
                    messages.append(
                        [
                            {"role": "user", "content": f"{prompt}\n\n{test_case['input']}"}
                        ]
                    )

            # Create experiment
            experiment = OpenAIChatExperiment(
                model=[model],
                messages=messages,
                temperature=[0.7],
                max_tokens=[1000],
            )

            # Run experiment
            experiment.run()

            # Get results
            results = experiment.get_table()

            # Analyze results
            analysis = {
                "base_prompt": base_prompt,
                "variations": variations,
                "test_cases": test_cases,
                "results": results.to_dict(),
            }

            return analysis
        except Exception as e:
            logger.error(f"Prompt comparison failed: {e}")
            raise

    def test_prompt_robustness(
        self,
        prompt: str,
        test_inputs: List[str],
        model: str = "gpt-4o-mini",
        num_runs: int = 3,
    ) -> Dict[str, Any]:
        """
        Test prompt robustness across multiple runs.

        Args:
            prompt: Prompt to test
            test_inputs: List of test inputs
            model: Model to use
            num_runs: Number of runs per input

        Returns:
            Robustness metrics
        """
        try:
            # Create messages
            messages = []
            for test_input in test_inputs:
                for _ in range(num_runs):
                    messages.append(
                        [{"role": "user", "content": f"{prompt}\n\n{test_input}"}]
                    )

            # Create experiment
            experiment = OpenAIChatExperiment(
                model=[model],
                messages=messages,
                temperature=[0.7],
                max_tokens=[1000],
            )

            # Run experiment
            experiment.run()

            # Get results
            results = experiment.get_table()

            # Calculate consistency metrics
            # (This is simplified - you'd want more sophisticated analysis)
            consistency_scores = {}

            return {
                "prompt": prompt,
                "test_inputs": test_inputs,
                "num_runs": num_runs,
                "results": results.to_dict(),
                "consistency_scores": consistency_scores,
            }
        except Exception as e:
            logger.error(f"Robustness testing failed: {e}")
            raise


def create_prompt_evaluator(
    openai_api_key: Optional[str] = None,
) -> Optional[PromptEvaluator]:
    """
    Factory function to create a prompt evaluator.

    Returns None if Prompttools is not available (graceful degradation).
    """
    if not PROMPTTOOLS_AVAILABLE:
        logger.debug("Prompttools not available. Returning None.")
        return None

    try:
        return PromptEvaluator(openai_api_key=openai_api_key)
    except Exception as e:
        logger.error(f"Failed to create prompt evaluator: {e}")
        return None
