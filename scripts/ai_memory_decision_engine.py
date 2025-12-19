#!/usr/bin/env python3
"""
AI-Enhanced Memory Decision Engine

Uses AI to make intelligent decisions about resource allocation and process management.
Can be integrated with the Memory Resource Manager for advanced decision making.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not available. AI features will be disabled.")


@dataclass
class ProcessContext:
    """Context about a process for AI decision making"""
    pid: int
    name: str
    memory_mb: float
    memory_percent: float
    cpu_percent: float
    complexity: str
    memory_history: List[float]
    last_user_interaction: Optional[str]
    current_state: str
    throttle_level: float


@dataclass
class SystemContext:
    """System-wide context for AI decision making"""
    total_memory_mb: float
    available_memory_mb: float
    memory_percent: float
    swap_percent: float
    user_inactive_seconds: float
    top_processes: List[Dict[str, Any]]
    timestamp: str


class AIMemoryDecisionEngine:
    """AI-powered decision engine for memory management"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('ai_decision_making', {})
        self.enabled = self.config.get('enabled', False) and OPENAI_AVAILABLE
        self.logger = logging.getLogger(__name__)
        
        if self.enabled:
            try:
                openai.api_key = os.getenv('OPENAI_API_KEY')
                if not openai.api_key:
                    self.logger.warning("OPENAI_API_KEY not set. AI features disabled.")
                    self.enabled = False
            except Exception as e:
                self.logger.warning(f"Could not initialize OpenAI: {e}")
                self.enabled = False
    
    def analyze_with_ai(self, process_context: ProcessContext, 
                       system_context: SystemContext) -> Dict[str, Any]:
        """
        Use AI to analyze and make decisions about process resource allocation.
        
        Returns:
            Dictionary with recommendations including:
            - action: 'throttle', 'suspend', 'resume', 'terminate', 'none'
            - throttle_level: 0.0 to 1.0
            - reasoning: Explanation of the decision
            - confidence: 0.0 to 1.0
        """
        if not self.enabled:
            return self._fallback_decision(process_context, system_context)
        
        try:
            prompt = self._build_decision_prompt(process_context, system_context)
            
            response = openai.ChatCompletion.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert system administrator managing memory resources.
                        Analyze the process and system context to make intelligent decisions about resource allocation.
                        Consider:
                        1. Process memory complexity (O(n), O(n^2), O(2^n))
                        2. Current system memory pressure
                        3. User activity status
                        4. Process importance and usage patterns
                        5. Impact of throttling/suspension on user experience
                        
                        Respond with a JSON object containing:
                        - action: one of 'throttle', 'suspend', 'resume', 'terminate', 'none'
                        - throttle_level: float between 0.0 and 1.0 (only if action is 'throttle')
                        - reasoning: brief explanation
                        - confidence: float between 0.0 and 1.0
                        """
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 500)
            )
            
            result_text = response.choices[0].message.content
            # Try to extract JSON from response
            try:
                # Look for JSON in the response
                if '{' in result_text:
                    json_start = result_text.find('{')
                    json_end = result_text.rfind('}') + 1
                    result_json = json.loads(result_text[json_start:json_end])
                else:
                    raise ValueError("No JSON found in response")
            except json.JSONDecodeError:
                self.logger.warning("Could not parse AI response as JSON, using fallback")
                return self._fallback_decision(process_context, system_context)
            
            return result_json
            
        except Exception as e:
            self.logger.error(f"AI decision making failed: {e}")
            return self._fallback_decision(process_context, system_context)
    
    def _build_decision_prompt(self, process_context: ProcessContext,
                              system_context: SystemContext) -> str:
        """Build the prompt for AI decision making"""
        prompt = f"""Analyze the following system state and make a decision about process {process_context.name} (PID {process_context.pid}):

PROCESS CONTEXT:
- Name: {process_context.name}
- Memory Usage: {process_context.memory_mb:.1f} MB ({process_context.memory_percent:.1f}% of system)
- CPU Usage: {process_context.cpu_percent:.1f}%
- Complexity: {process_context.complexity}
- Current State: {process_context.current_state}
- Current Throttle Level: {process_context.throttle_level:.2f}
- Last User Interaction: {process_context.last_user_interaction or 'Unknown'}
- Memory History (last 5 values): {process_context.memory_history[-5:]}

SYSTEM CONTEXT:
- Total Memory: {system_context.total_memory_mb:.1f} MB
- Available Memory: {system_context.available_memory_mb:.1f} MB
- Memory Usage: {system_context.memory_percent:.1f}%
- Swap Usage: {system_context.swap_percent:.1f}%
- User Inactive For: {system_context.user_inactive_seconds:.0f} seconds
- Top Memory Consumers: {json.dumps(system_context.top_processes[:5], indent=2)}

Make a decision about what action to take for this process. Consider:
1. Is the process consuming excessive resources?
2. Is the system under memory pressure?
3. Is the user currently active?
4. What is the complexity pattern (exponential/quadratic processes are more problematic)?
5. Would throttling/suspension significantly impact user experience?

Respond with a JSON object only."""
        
        return prompt
    
    def _fallback_decision(self, process_context: ProcessContext,
                          system_context: SystemContext) -> Dict[str, Any]:
        """Fallback decision logic when AI is not available"""
        # Simple heuristic-based decision
        action = 'none'
        throttle_level = 1.0
        reasoning = "No action needed"
        confidence = 0.5
        
        # High memory pressure + high complexity = throttle
        if (system_context.memory_percent > 85 and 
            process_context.complexity in ['O(2^n)', 'O(n^2)']):
            action = 'throttle'
            if process_context.complexity == 'O(2^n)':
                throttle_level = 0.1
            else:
                throttle_level = 0.3
            reasoning = f"High memory pressure ({system_context.memory_percent:.1f}%) and {process_context.complexity} complexity"
            confidence = 0.8
        
        # User inactive + high memory = more aggressive throttling
        if system_context.user_inactive_seconds > 300:
            if process_context.memory_percent > 5:
                action = 'throttle'
                throttle_level = min(throttle_level, 0.5)
                reasoning += ". User inactive, reducing resources."
                confidence = 0.9
        
        return {
            'action': action,
            'throttle_level': throttle_level,
            'reasoning': reasoning,
            'confidence': confidence
        }
    
    def batch_analyze(self, processes: List[ProcessContext],
                     system_context: SystemContext) -> List[Dict[str, Any]]:
        """Analyze multiple processes at once for efficiency"""
        results = []
        for process in processes:
            decision = self.analyze_with_ai(process, system_context)
            results.append({
                'pid': process.pid,
                'name': process.name,
                'decision': decision
            })
        return results


if __name__ == '__main__':
    # Example usage
    import os
    
    config = {
        'ai_decision_making': {
            'enabled': True,
            'model': 'gpt-4',
            'temperature': 0.3,
            'max_tokens': 500
        }
    }
    
    engine = AIMemoryDecisionEngine(config)
    
    # Example process context
    process = ProcessContext(
        pid=12345,
        name="example_process",
        memory_mb=2048.0,
        memory_percent=15.0,
        cpu_percent=25.0,
        complexity="O(2^n)",
        memory_history=[1000, 1200, 1500, 1800, 2048],
        last_user_interaction=None,
        current_state="active",
        throttle_level=1.0
    )
    
    # Example system context
    system = SystemContext(
        total_memory_mb=16384.0,
        available_memory_mb=2048.0,
        memory_percent=87.5,
        swap_percent=10.0,
        user_inactive_seconds=600,
        top_processes=[],
        timestamp=datetime.now().isoformat()
    )
    
    if engine.enabled:
        decision = engine.analyze_with_ai(process, system)
        print(json.dumps(decision, indent=2))
    else:
        print("AI features not available")


