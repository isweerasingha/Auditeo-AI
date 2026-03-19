import asyncio
from collections.abc import Callable
from functools import partial

from auditeo_ai.utils.logger import correlation_id_ctx, ip_address_ctx


def _run_with_context[R](
    function: Callable[..., R],
    correlation_id: str,
    ip_address: str,
    *args,
    **kwargs,
) -> R:
    """Run function with context variables set in the executor thread."""
    correlation_id_ctx.set(correlation_id)
    ip_address_ctx.set(ip_address)
    return function(*args, **kwargs)


async def flow_loop_executor[R](function: Callable[..., R], *args, **kwargs) -> R:
    """Flow loop executor to execute blocking operations in a thread pool."""
    # Capture context variables before running in executor
    correlation_id = correlation_id_ctx.get()
    ip_address = ip_address_ctx.get()

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        partial(
            _run_with_context,
            function,
            correlation_id,
            ip_address,
            *args,
            **kwargs,
        ),
    )
