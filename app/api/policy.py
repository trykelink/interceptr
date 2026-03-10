# policy.py — API routes for inspecting and reloading the active policy
from fastapi import APIRouter, HTTPException
from app.services.interceptor_service import interceptor_service

router = APIRouter(prefix="/api/v1/policy", tags=["policy"])


@router.get("/")
def get_policy_info():
    if interceptor_service.policy_engine is None:
        return {"status": "no_policy_loaded"}
    return interceptor_service.policy_engine.info


@router.post("/reload")
def reload_policy():
    import os
    from app.core.policy_engine import PolicyEngine

    POLICY_PATH = "policy.yaml"

    if interceptor_service.policy_engine is None:
        if not os.path.isfile(POLICY_PATH):
            raise HTTPException(
                status_code=404,
                detail={"error": "policy.yaml not found. Place policy.yaml in the app directory and try again."}
            )
        interceptor_service.policy_engine = PolicyEngine(POLICY_PATH)
    else:
        interceptor_service.policy_engine.reload()

    return {"status": "reloaded", "policy": interceptor_service.policy_engine.info}
