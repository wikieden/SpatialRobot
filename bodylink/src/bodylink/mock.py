"""MockBody — a deterministic reference `ExecutorAdapter` for tests and dev (D5).

`bodylink` is the adaptation framework: the 4th Chronotope member ships the
reference fill of the brain's executor seam. `MockBody` is a no-hardware,
no-network body — it accepts `SubTask`s, echoes their node ids (B9), and reports
success (or a scripted failure with a typed recovery hint). It lets the L3 brain
be built and tested end-to-end with no real robot. A real robot ships its own
package implementing the same `ExecutorAdapter`; only the Body Profile + verb set
differ ("swap the body, keep the mind", D3).
"""

from __future__ import annotations

import logging
from collections.abc import Iterator, Mapping

from mindloop import (
    BodyProfile,
    CapabilityManifest,
    ErrorCode,
    RecoveryHint,
    RecoveryKind,
    StatusUpdate,
    SubTask,
    TaskStatus,
    VerbSpec,
)

_log = logging.getLogger("bodylink.mock")


class UnsupportedVerbError(ValueError):
    """Raised when a `SubTask` names a verb the body does not declare.

    This is a programmer error: the planner must gate on the body's
    `CapabilityManifest` and never emit an unsupported verb (D3). Raised rather
    than returned because it signals a brain-side bug, not a task outcome.
    """


def g1d_manifest() -> CapabilityManifest:
    """The B10 reference manifest: G1-D wheeled humanoid (32 DOF, 2-D base)."""
    return CapabilityManifest(
        body_profile=BodyProfile(
            profile_id="g1d",
            display_name="Unitree G1-D",
            dof=32,
            base_type="wheeled",
        ),
        verbs=(
            VerbSpec("navigate", params=("target",)),
            VerbSpec("grasp", params=("target",)),
            VerbSpec("place", params=("target", "location")),
            VerbSpec("detect"),
            VerbSpec("open_door", params=("target",)),
            VerbSpec("charging"),
            VerbSpec(
                "operate_appliance",
                params=("target", "program"),
                appliance_types=("washer", "stove", "microwave", "dishwasher"),
            ),
        ),
    )


# Typed recovery hints a body offers with a failure (B3) — what the brain's
# replanner (P4) will consume.
_RECOVERY: dict[ErrorCode, tuple[RecoveryHint, ...]] = {
    ErrorCode.GRASP_FAILED: (RecoveryHint(RecoveryKind.POSITION_OFFSET, 0.02),),
    ErrorCode.OBJECT_LOST: (RecoveryHint(RecoveryKind.REPLAN),),
}


class MockBody:
    """A reference `ExecutorAdapter` that fakes execution deterministically.

    `manifest` defaults to the G1-D reference (`g1d_manifest`). `fail` scripts a
    verb → `ErrorCode` mapping so a dispatch of that verb terminates `FAILED`
    with the matching typed recovery hint — used to drive replan tests (P4). The
    `StatusUpdate.task_id` is left empty: a bare body does not own task identity
    (the brain / a real L2 populates it); correlation here is by `subtask_id`.
    """

    def __init__(
        self,
        manifest: CapabilityManifest | None = None,
        *,
        fail: Mapping[str, ErrorCode] | None = None,
    ) -> None:
        self._manifest = manifest or g1d_manifest()
        self._fail = dict(fail or {})

    def capabilities(self) -> CapabilityManifest:
        """Return this body's two-tier capability manifest (D3)."""
        return self._manifest

    def dispatch(self, subtask: SubTask) -> Iterator[StatusUpdate]:
        """Run one `SubTask`, streaming RUNNING → terminal `StatusUpdate`s.

        Echoes `subtask.target_node_ids` back as `touched_node_ids` (B9). Raises
        `UnsupportedVerbError` for a verb outside the manifest (a planner bug).
        """
        verb = subtask.verb
        if not self._manifest.supports(verb):
            raise UnsupportedVerbError(
                f"body {self._manifest.body_profile.profile_id!r} does not support verb {verb!r}"
            )
        ids = subtask.target_node_ids
        _log.debug("dispatch %s(%s) targets=%s", verb, subtask.id, ids)
        yield StatusUpdate("", subtask.id, TaskStatus.RUNNING, progress=0.0, touched_node_ids=ids)

        err = self._fail.get(verb)
        if err is not None:
            yield StatusUpdate(
                "",
                subtask.id,
                TaskStatus.FAILED,
                progress=1.0,
                error_code=err,
                recovery_actions=_RECOVERY.get(err, ()),
                touched_node_ids=ids,
                message=f"mock failure: {err.value}",
            )
            return
        yield StatusUpdate(
            "",
            subtask.id,
            TaskStatus.SUCCESS,
            progress=1.0,
            touched_node_ids=ids,
            message=f"mock {verb} ok",
        )
