# policy.py — API routes for inspecting and reloading the active policy
import os
from fastapi import APIRouter, HTTPException, Request, Response
from app.core.policy_engine import PolicyEngine
from app.core.rate_limiter import limiter
from app.services.interceptor_service import interceptor_service

router = APIRouter(prefix="/api/v1/policy", tags=["policy"])


@router.get("/")
def get_policy_info():
    if interceptor_service.policy_engine is None:
        return {"status": "no_policy_loaded"}
    return interceptor_service.policy_engine.info


@router.post("/reload")
@limiter.limit("5/minute")
def reload_policy(request: Request, response: Response):
    policy_path = "policy.yaml"
    if interceptor_service.policy_engine is None:
        if not os.path.isfile(policy_path):
            raise HTTPException(
                status_code=422,
                detail=(
                    "No policy.yaml found in the container. "
                    "Run 'interceptr policy edit' to create one, then try again."
                ),
            )
        interceptor_service.policy_engine = PolicyEngine(policy_path)
    else:
        interceptor_service.policy_engine.reload()

    return {"status": "reloaded", "policy": interceptor_service.policy_engine.info}
