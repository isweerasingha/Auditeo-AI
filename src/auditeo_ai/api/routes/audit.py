from typing import Any

from fastapi import APIRouter, HTTPException

from auditeo_ai.flows.audit_flow import AuditFlow
from auditeo_ai.models import APIResponse, AuditRunRequest, AuditRunResponse
from auditeo_ai.utils import flow_loop_executor, get_logger

router = APIRouter(tags=["audit"])
logger = get_logger("auditeo-ai:api")


def _execute_audit_flow(
    inputs: dict[str, Any],
) -> APIResponse:
    """
    Execute the audit flow synchronously.

    Args:
        inputs: The inputs for the audit flow

    Returns:
        APIResponse
    """

    try:
        flow = AuditFlow()
        flow.kickoff(inputs=inputs)
        data = AuditRunResponse(
            website_url=inputs["website_url"],
            factual_metrics=flow.state.factual_metrics,
            kpis=flow.state.insights_crew_output.kpis,
            insights_report=flow.state.insights_crew_output.structured_report,
            recommendations=(
                flow.state.recommendations_crew_output.recommendations
                if flow.state.recommendations_crew_output
                else None
            ),
        )
        trace_id = logger.info("Audit flow executed successfully")
        return APIResponse(
            success=True,
            trace_id=trace_id,
            message="Audit flow executed successfully",
            data=data,
        )

    except Exception as e:
        trace_id = logger.error(f"Audit flow failed: \n{e}", exc_info=True)
        return APIResponse(
            success=False,
            trace_id=trace_id,
            message="Audit flow execution failed",
            data=None,
        )


@router.post("/audit", response_model=AuditRunResponse)
async def run_audit(payload: AuditRunRequest) -> AuditRunResponse:

    inputs = {"website_url": payload.website_url}

    response = await flow_loop_executor(_execute_audit_flow, inputs)

    if not response.success:
        raise HTTPException(status_code=500, detail=response.message)

    return response
