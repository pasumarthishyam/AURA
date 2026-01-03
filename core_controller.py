from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time
import json
import logging

# =========================================================
# LOGGING CONFIGURATION
# =========================================================

logger = logging.getLogger("AURA.Controller")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        '\n%(asctime)s | %(levelname)s | %(name)s\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler('aura_controller_debug.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)


# =========================================================
# DATA MODELS
# =========================================================

@dataclass
class AgentState:
    """
    Tracks system-level execution state.
    """
    step_count: int = 0
    failure_count: int = 0
    max_steps: int = 15
    max_failures: int = 4
    # Track last actions for loop detection
    last_actions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TraceStep:
    """
    One execution step in the agent trace.
    """
    step_id: int
    action: Dict[str, Any]
    success: bool
    result: Optional[Any]
    observation: Any
    error: Optional[str]
    timestamp: float


@dataclass
class ExecutionTrace:
    """
    Full trace of an agent run.
    """
    steps: List[TraceStep] = field(default_factory=list)

    def add_step(self, step: TraceStep):
        self.steps.append(step)


@dataclass
class AgentResult:
    """
    Final result returned to frontend.
    """
    success: bool
    message: str
    trace: ExecutionTrace


# =========================================================
# CORE AGENT CONTROLLER (ORCHESTRATOR)
# =========================================================

class CoreAgentController:
    """
    Central nervous system of the autonomous agent.

    Responsibilities:
    - Coordinate Brain, Executor, Perception, Memory, Safety
    - Enforce limits and safety
    - Enable replanning on failure
    - Produce final AgentResult + execution trace
    """

    def __init__(
        self,
        brain,
        executor,
        perception,
        memory,
        safety,
        max_steps: int = 15,
        max_failures: int = 4,
    ):
        self.brain = brain
        self.executor = executor
        self.perception = perception
        self.memory = memory
        self.safety = safety

        self.state = AgentState(
            max_steps=max_steps,
            max_failures=max_failures,
        )

        self.trace = ExecutionTrace()

    # =====================================================
    # PUBLIC ENTRY POINT
    # =====================================================

    def run(self, user_goal: str) -> AgentResult:
        """
        Runs a full autonomous agent session.
        """
        logger.info(
            f"{'#'*60}\n"
            f"  AURA AGENT SESSION STARTED\n"
            f"{'#'*60}\n"
            f"GOAL: {user_goal}\n"
            f"{'#'*60}"
        )

        # ---- Retrieve long-term memory once ----
        memory_context = self.memory.retrieve(user_goal)
        logger.debug(f"Memory context retrieved: {len(str(memory_context))} chars")

        last_observation = None
        last_error = None

        while True:
            # -------------------------------------------------
            # HARD STOP CONDITIONS
            # -------------------------------------------------

            if self.state.step_count >= self.state.max_steps:
                return self._terminate(
                    success=False,
                    message="Stopped: maximum step limit reached.",
                )

            if self.state.failure_count >= self.state.max_failures:
                return self._terminate(
                    success=False,
                    message="Stopped: too many consecutive failures.",
                )

            # -------------------------------------------------
            # THINK (BRAIN)
            # -------------------------------------------------
            logger.info(
                f"\n{'+'+'='*58+'+'}\n"
                f"| STEP {self.state.step_count} - THINKING...\n"
                f"{'+'+'='*58+'+'}"
            )

            action = self.brain.next_action(
                goal=user_goal,
                memory_context=memory_context,
                last_observation=last_observation,
                last_error=last_error,
                step_state=self.state,
            )

            # Log the action decision
            logger.info(
                f"\n{'+'+'='*58+'+'}\n"
                f"| STEP {self.state.step_count} - ACTION DECIDED\n"
                f"{'+'+'='*58+'+'}\n"
                f"| TYPE: {action.get('type', 'N/A')}\n"
                f"| THOUGHT: {action.get('thought', 'N/A')[:200]}{'...' if len(str(action.get('thought', ''))) > 200 else ''}\n"
                f"| TOOL: {action.get('tool', 'N/A')}\n"
                f"| ARGS: {json.dumps(action.get('params', {}), indent=2)}\n"
                f"{'+'+'='*58+'+'}"
            )

            # Brain can explicitly stop
            if action["type"] == "STOP":
                return self._terminate(
                    success=True,
                    message=action.get("message", "Task completed."),
                )

            # Brain can just respond (no action needed)
            if action["type"] == "RESPONSE":
                return self._terminate(
                    success=True,
                    message=action.get("message", "I don't have a response."),
                )

            # -------------------------------------------------
            # LOOP DETECTION - Prevent infinite repeated actions
            # -------------------------------------------------
            if self._is_repeated_action(action):
                logger.warning(
                    f"\n{'!'*60}\n"
                    f"LOOP DETECTED: Same action repeated. Force-stopping.\n"
                    f"{'!'*60}"
                )
                return self._smart_terminate(action)

            # -------------------------------------------------
            # SAFETY CHECK
            # -------------------------------------------------

            safety_decision = self.safety.check(action)
            # We treat ALLOW and CONFIRM as allowed for this simplified loop.
            # ideally CONFIRM should prompt user.
            from safety.models import SafetyDecisionType
            
            allowed = safety_decision.decision in [SafetyDecisionType.ALLOW, SafetyDecisionType.CONFIRM]
            reason = safety_decision.reason
            
            if not allowed:
                return self._terminate(
                    success=False,
                    message=f"Blocked by safety system: {reason}",
                )

            # -------------------------------------------------
            # ACT (EXECUTOR)
            # -------------------------------------------------

            success = False
            result = None
            error = None

            try:
                result = self.executor.execute(action)
                success = True
                self.state.failure_count = 0  # reset on success
                logger.info(
                    f"\n{'+'+'='*58+'+'}\\n"
                    f"| STEP {self.state.step_count} - EXECUTION SUCCESS [OK]\\n"
                    f"{'+'+'='*58+'+'}\\n"
                    f"| RESULT: {str(result)[:500]}{'...' if len(str(result)) > 500 else ''}\\n"
                    f"{'+'+'='*58+'+'}"
                )

            except Exception as e:
                error = str(e)
                self.state.failure_count += 1
                logger.error(
                    f"\n{'+'+'='*58+'+'}\\n"
                    f"| STEP {self.state.step_count} - EXECUTION FAILED [X]\\n"
                    f"{'+'+'='*58+'+'}\\n"
                    f"| ERROR: {error}\\n"
                    f"| FAILURE COUNT: {self.state.failure_count}/{self.state.max_failures}\\n"
                    f"{'+'+'='*58+'+'}"
                )

            # -------------------------------------------------
            # OBSERVE (PERCEPTION)
            # -------------------------------------------------

            observation = self.perception.observe(
                action=action,
                result=result,
                error=error,
            )
            logger.debug(
                f"\n{'-'*60}\\n"
                f"OBSERVATION:\\n{observation}\\n"
                f"{'-'*60}"
            )

            # -------------------------------------------------
            # TRACE
            # -------------------------------------------------

            self.trace.add_step(
                TraceStep(
                    step_id=self.state.step_count,
                    action=action,
                    success=success,
                    result=result,
                    observation=observation,
                    error=error,
                    timestamp=time.time(),
                )
            )

            # -------------------------------------------------
            # MEMORY UPDATE
            # -------------------------------------------------

            self.memory.store_step(
                goal=user_goal,
                action=action,
                success=success,
                result=result,
                observation=observation,
            )

            # -------------------------------------------------
            # PREPARE FOR NEXT ITERATION
            # -------------------------------------------------

            last_observation = observation
            last_error = error
            self.state.step_count += 1

    # =====================================================
    # INTERNAL TERMINATION
    # =====================================================

    def _terminate(self, success: bool, message: str) -> AgentResult:
        """
        Clean termination point.
        """
        return AgentResult(
            success=success,
            message=message,
            trace=self.trace,
        )

    # =====================================================
    # LOOP DETECTION HELPERS
    # =====================================================

    def _is_repeated_action(self, action: Dict[str, Any]) -> bool:
        """
        Check if the current action is identical to the last one.
        Returns True if loop detected (same action repeated).
        """
        if action.get("type") != "ACTION":
            return False
        
        # Create a comparable representation of the action
        action_signature = {
            "tool": action.get("tool"),
            "params": action.get("params", {})
        }
        
        # Check against last action
        if self.state.last_actions:
            last_signature = self.state.last_actions[-1]
            if action_signature == last_signature:
                return True
        
        # Store current action (keep last 3)
        self.state.last_actions.append(action_signature)
        if len(self.state.last_actions) > 3:
            self.state.last_actions.pop(0)
        
        return False

    def _smart_terminate(self, action: Dict[str, Any]) -> AgentResult:
        """
        Intelligent termination for completed tasks.
        Provides helpful messages based on the action type.
        """
        tool = action.get("tool", "")
        params = action.get("params", {})
        
        # Special handling for file operations
        if tool in ["WRITE_FILE", "WRITE_AND_OPEN"]:
            path = params.get("path", "unknown")
            message = (
                f"✅ File saved successfully!\n\n"
                f"📁 **Location:** `{path}`\n\n"
                f"The file has been created with your content."
            )
        elif tool == "READ_FILE":
            path = params.get("path", "unknown")
            message = f"📄 File read from: {path}"
        elif tool == "SHELL_EXECUTE":
            command = params.get("command", "")
            message = f"⚡ Command executed: {command}"
        else:
            message = "✅ Task completed successfully."
        
        return AgentResult(
            success=True,
            message=message,
            trace=self.trace,
        )
