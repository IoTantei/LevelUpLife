from typing import Sequence
from uuid import UUID
from fastapi import APIRouter, Depends
from leveluplife.auth.utils import get_current_active_user
from leveluplife.controllers.task import TaskController
from leveluplife.dependencies import get_task_controller
from leveluplife.models.task import TaskCreate, TaskUpdate
from leveluplife.models.view import TaskView

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=TaskView, status_code=201)
async def create_task(
    task: TaskCreate, task_controller: TaskController = Depends(get_task_controller)
) -> TaskView:
    return TaskView.model_validate(await task_controller.create_task(task))


@router.get("/", response_model=Sequence[TaskView])
async def get_tasks(
    *, offset: int = 0, task_controller: TaskController = Depends(get_task_controller)
) -> Sequence[TaskView]:
    return [
        TaskView.model_validate(task)
        for task in await task_controller.get_tasks(offset * 20, 20)
    ]


@router.get("/{task_id}", response_model=TaskView)
async def get_task_by_id(
    *, task_id: UUID, task_controller: TaskController = Depends(get_task_controller)
) -> TaskView:
    return TaskView.model_validate(await task_controller.get_task_by_id(task_id))


@router.get("/type/title", response_model=TaskView)
async def get_task_by_title(
    *, task_title: str, task_controller: TaskController = Depends(get_task_controller)
) -> TaskView:
    return TaskView.model_validate(await task_controller.get_task_by_title(task_title))


@router.patch("/{task_id}", response_model=TaskView)
async def update_task(
    *,
    task_id: UUID,
    task_update: TaskUpdate,
    task_controller: TaskController = Depends(get_task_controller),
) -> TaskView:
    return TaskView.model_validate(
        await task_controller.update_task(task_id, task_update)
    )


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    *, task_id: UUID, task_controller: TaskController = Depends(get_task_controller)
) -> None:
    await task_controller.delete_task(task_id)
