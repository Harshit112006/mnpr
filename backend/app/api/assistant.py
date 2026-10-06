from typing import (
    Literal,
)

from fastapi import (
    APIRouter,
    HTTPException,
)

from fastapi.concurrency import (
    run_in_threadpool,
)

from pydantic import (
    BaseModel,
    Field,
)

from app.services.assistant.assistant_service import (
    get_assistant_service,
)


router = APIRouter(
    prefix="/api/assistant",
    tags=[
        "AI Assistant",
    ],
)


class HistoryMessage(
    BaseModel
):

    role: Literal[
        "user",
        "assistant",
    ]

    content: str = Field(
        min_length=1,
        max_length=12000,
    )


class AssistantChatRequest(
    BaseModel
):

    message: str = Field(
        min_length=1,
        max_length=12000,
    )

    history: list[
        HistoryMessage
    ] = Field(
        default_factory=list
    )

    use_project_context: bool = (
        True
    )


@router.get(
    "/health"
)
def assistant_health():

    return (
        get_assistant_service()
        .health()
    )


@router.post(
    "/chat"
)
async def assistant_chat(
    payload:
        AssistantChatRequest,
):

    service = (
        get_assistant_service()
    )


    try:

        return await run_in_threadpool(

            service.chat,

            payload.message,

            [
                item.model_dump()

                for item
                in payload.history
            ],

            payload.use_project_context,
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(
                error
            ),
        ) from error


    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(
                error
            ),
        ) from error


    except Exception as error:

        print(
            "Unexpected assistant error:",
            repr(
                error
            ),
        )


        raise HTTPException(
            status_code=502,
            detail=(
                "BreedVision AI Assistant "
                "could not complete the request."
            ),
        ) from error