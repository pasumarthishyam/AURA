from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time


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

        # ---- Retrieve long-term memory once ----
        memory_context = self.memory.retrieve(user_goal)

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

            action = self.brain.next_action(
                goal=user_goal,
                memory_context=memory_context,
                last_observation=last_observation,
                last_error=last_error,
                step_state=self.state,
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

            except Exception as e:
                error = str(e)
                self.state.failure_count += 1

            # -------------------------------------------------
            # OBSERVE (PERCEPTION)
            # -------------------------------------------------

            observation = self.perception.observe(
                action=action,
                result=result,
                error=error,
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
