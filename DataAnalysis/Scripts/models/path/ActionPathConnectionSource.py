from models.actions.JumpActionNode import JumpActionNode
from models.path.ActionPath import ActionPath
from models.path.ActionPathSegment import ActionPathSegment


from typing import Callable, Generator


class ActionPathConnectionSource(Callable[[ActionPath], Generator[ActionPath, None, None]]):

    def __call__(self, path: ActionPath) -> Generator[ActionPath, None, None]:
        raise NotImplementedError()
