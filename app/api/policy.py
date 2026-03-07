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
    if interceptor_service.policy_engine is None:
        raise HTTPException(status_code=404, detail={"error": "no policy configured"})
    interceptor_service.policy_engine.reload()
    return {"status": "reloaded", "policy": interceptor_service.policy_engine.info}
