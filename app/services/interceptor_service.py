# interceptor_service.py — Core interception engine: evaluates tool calls and creates audit logs
from sqlalchemy.orm import Session
from app.schemas.intercept import InterceptDecision, InterceptRequest, InterceptResponse
from app.schemas.audit_log import AuditLogCreate
from app.services.audit_log_service import create_log


class InterceptorService:
    def __init__(self, policy_engine=None):
        self.policy_engine = policy_engine  # None in Week 2, injected in Week 3

    def evaluate(self, request: InterceptRequest) -> tuple[InterceptDecision, str | None]:
        """
        Evaluates a tool call and returns (decision, reason).
        In Week 2: always returns ALLOWED.
        In Week 3: delegates to self.policy_engine if available.
        """
        if self.policy_engine is not None:
            return self.policy_engine.evaluate(request)
        return InterceptDecision.ALLOWED, None

    def intercept(self, request: InterceptRequest, db: Session) -> InterceptResponse:
        """
        Full interception flow:
        1. Evaluate the request (allow/deny decision)
        2. Create audit log automatically
        3. Return structured response
        """
        decision, reason = self.evaluate(request)

        log_data = AuditLogCreate(
            agent=request.agent,
            tool=request.tool,
            arguments=request.arguments,
            status=decision.value,
            reason=reason,
        )
        log = create_log(db, log_data)

        return InterceptResponse(
            decision=decision,
            reason=reason,
            log_id=log.id,
            agent=log.agent,
            tool=log.tool,
            timestamp=log.timestamp,
        )


interceptor_service = InterceptorService()
