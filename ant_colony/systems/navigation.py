from __future__ import annotations

import heapq
import math
from typing import TYPE_CHECKING, Any

from ant_colony.components import AntState
from ant_colony.config import settings
from ant_colony.entities.ant import Ant
from ant_colony.entities.pheromone import Pheromone, PheromoneType
from ant_colony.systems.collision import CollisionMap

if TYPE_CHECKING:
    from ant_colony.world import World


class AntNavigator:
    def __init__(
        self,
        world: World,
        collision_map: CollisionMap,
    ) -> None:
        self._world = world
        self._collision_map = collision_map
        self._blocked_headings: dict[int, list[tuple[float, int]]] = {}
        self._wall_follow_sides: dict[int, int] = {}
        self._wall_follow_progress: dict[int, tuple[float, int]] = {}
        self._maze_recovery_targets: dict[int, tuple[tuple[float, float], int]] = {}

    def __getattr__(self, name: str) -> Any:
        return getattr(self._world, name)

    def update_ant_movement(self, ant: Ant) -> None:
        self._update_ant_movement(ant)

    def move_ant_around_obstacle(
        self,
        ant: Ant,
        blocked_count: int = 1,
    ) -> None:
        self._move_ant_around_obstacle(ant, blocked_count)

    def record_blocked_heading(
        self,
        ant: Ant,
        heading: float,
    ) -> int:
        return self._record_blocked_heading(ant, heading)

    def target_distance_for(
        self,
        ant: Ant,
        candidate: tuple[float, float],
    ) -> float:
        return self._target_distance_for(ant, candidate)

    def _update_ant_movement(self, ant: Ant) -> None:
        """Move an ant for one tick, gating wandering departure on nest proximity.

        A wandering ant that is physically at the nest must pay the one-time
        excursion cost before it can leave.  If it cannot afford to depart,
        movement is suppressed this tick.
        """
        nest = self.nest
        at_nest = ant.intersects_entity(
            nest,
            padding=settings.ANT_INTERACTION_RADIUS,
        )

        if at_nest and not ant.on_excursion and ant.state == AntState.WANDERING:
            if not ant.depart():
                return

        self._decay_blocked_headings_for(ant)
        previous_position = (ant.x, ant.y)
        previous_heading = ant.heading

        if self._position_is_blocked(
            ant.x,
            ant.y,
            radius=ant.hitbox_radius,
        ):
            if self._move_ant_out_of_obstacle_contact(ant):
                self._start_wall_following(ant)
            return

        if self._is_wall_following(ant):
            if (
                self._direct_route_to_target_is_clear(ant)
                and self._try_direct_navigation_step(ant)
            ):
                self._stop_wall_following(ant)
                return

            self._move_ant_along_wall(ant)
            return

        ant.update()
        attempted_heading = ant.heading
        if self._movement_intersects_obstacle(
            previous_position,
            (ant.x, ant.y),
            radius=ant.hitbox_radius,
        ):
            ant.x, ant.y = previous_position
            ant.heading = previous_heading
            blocked_count = self._record_blocked_heading(
                ant,
                attempted_heading,
            )
            if blocked_count >= settings.ANT_AVOID_PHEROMONE_REPEAT_COUNT:
                self._deposit_avoid_pheromone_for(ant)
            self._start_wall_following(ant)
            self._move_ant_around_obstacle(ant, blocked_count)

    def _move_ant_around_obstacle(
        self,
        ant: Ant,
        blocked_count: int = 1,
    ) -> None:
        base_heading = self._preferred_heading_for(ant)
        clear_candidates: list[
            tuple[tuple[float, ...], float, tuple[float, float]]
        ] = []

        for heading in self._avoidance_headings(base_heading, blocked_count):
            candidate = self._candidate_position_for(ant, heading)
            if self._movement_intersects_obstacle(
                (ant.x, ant.y),
                candidate,
                radius=ant.hitbox_radius,
            ):
                continue

            clear_candidates.append(
                (
                    self._avoidance_score(
                        ant,
                        candidate,
                        heading,
                        base_heading,
                        blocked_count,
                    ),
                    heading,
                    candidate,
                )
            )

        if clear_candidates:
            _, heading, candidate = min(clear_candidates)
            ant.x, ant.y = candidate
            ant.heading = heading % 360
            return

        if self._move_ant_out_of_obstacle_contact(ant):
            self._start_wall_following(ant)
        else:
            ant.heading = (base_heading + 180) % 360

    def _is_wall_following(
        self,
        ant: Ant,
    ) -> bool:
        return ant.id in self._wall_follow_sides and self._has_navigation_target(ant)

    def _start_wall_following(
        self,
        ant: Ant,
    ) -> None:
        if not self._has_navigation_target(ant):
            return

        base_heading = self._preferred_heading_for(ant)
        left_score = self._wall_follow_side_score(ant, base_heading, -1)
        right_score = self._wall_follow_side_score(ant, base_heading, 1)
        self._wall_follow_sides[ant.id] = -1 if left_score <= right_score else 1
        self._wall_follow_progress[ant.id] = (
            self._target_distance_for(ant, (ant.x, ant.y)),
            0,
        )

    def _stop_wall_following(
        self,
        ant: Ant,
    ) -> None:
        self._wall_follow_sides.pop(ant.id, None)
        self._wall_follow_progress.pop(ant.id, None)
        self._maze_recovery_targets.pop(ant.id, None)

    @staticmethod
    def _has_navigation_target(
        ant: Ant,
    ) -> bool:
        return (
            ant.state == AntState.SEEKING_FOOD
            and ant.food_target is not None
        ) or (
            ant.state == AntState.CARRYING_FOOD
            and ant.nest_target is not None
        )

    def _wall_follow_side_score(
        self,
        ant: Ant,
        base_heading: float,
        side: int,
    ) -> tuple[int, float, int]:
        candidate = self._candidate_position_for(
            ant,
            base_heading + (90 * side),
        )
        blocked = self._movement_intersects_obstacle(
            (ant.x, ant.y),
            candidate,
            radius=ant.hitbox_radius,
        )
        return (
            int(blocked),
            self._target_distance_for(ant, candidate),
            0 if side == -1 else 1,
        )

    def _try_direct_navigation_step(
        self,
        ant: Ant,
    ) -> bool:
        base_heading = self._preferred_heading_for(ant)
        candidate = self._candidate_position_for(ant, base_heading)
        if self._movement_intersects_obstacle(
            (ant.x, ant.y),
            candidate,
            radius=ant.hitbox_radius,
        ):
            return False

        ant.x, ant.y = candidate
        ant.heading = base_heading % 360
        return True

    def _direct_route_to_target_is_clear(
        self,
        ant: Ant,
    ) -> bool:
        target = self._target_position_for(ant)
        if target is None:
            return False

        return not self._movement_intersects_obstacle(
            (ant.x, ant.y),
            target,
            radius=ant.hitbox_radius,
        )

    def _move_ant_along_wall(
        self,
        ant: Ant,
    ) -> None:
        base_heading = self._preferred_heading_for(ant)
        side = self._wall_follow_sides.get(ant.id, -1)
        if (
            self.scenario_name == settings.MAZE_PHEROMONE_ARENA_NAME
            and self._try_maze_stall_recovery_step(ant, base_heading)
        ):
            return

        stalled = self._wall_follow_is_stalled(ant)
        if stalled:
            if self._try_boundary_recovery_step(ant, base_heading):
                self._start_wall_following(ant)
                return
            if self.scenario_name == settings.MAZE_PHEROMONE_ARENA_NAME:
                if self._try_maze_stall_recovery_step(ant, base_heading):
                    self._start_wall_following(ant)
                    return
                side = -side
                self._wall_follow_sides[ant.id] = side

        headings = tuple(
            (base_heading + offset * side) % 360
            for offset in (90, 60, 120, 45, 135)
        ) + tuple(
            (base_heading - offset * side) % 360
            for offset in (90, 135)
        ) + ((base_heading + 180) % 360,)

        clear_candidates: list[
            tuple[tuple[float, ...], float, tuple[float, float]]
        ] = []
        for heading in headings:
            candidate = self._candidate_position_for(ant, heading)
            if self._movement_intersects_obstacle(
                (ant.x, ant.y),
                candidate,
                radius=ant.hitbox_radius,
            ):
                continue

            clear_candidates.append(
                (
                    self._wall_follow_candidate_score(
                        ant,
                        candidate,
                        heading,
                        base_heading,
                        side,
                        target_first=(
                            stalled
                            and self.scenario_name
                            == settings.MAZE_PHEROMONE_ARENA_NAME
                        ),
                    ),
                    heading,
                    candidate,
                )
            )

        if clear_candidates:
            _, heading, candidate = min(clear_candidates)
            ant.x, ant.y = candidate
            ant.heading = heading % 360
            return

        self._wall_follow_sides[ant.id] = -side
        if self._move_ant_out_of_obstacle_contact(ant):
            self._start_wall_following(ant)
        else:
            ant.heading = (base_heading + 180) % 360

    def _wall_follow_candidate_score(
        self,
        ant: Ant,
        candidate: tuple[float, float],
        heading: float,
        base_heading: float,
        side: int,
        *,
        target_first: bool,
    ) -> tuple[float, ...]:
        common_score = (
            self._boundary_contact_penalty(ant, candidate),
            self._avoid_pheromone_penalty(ant, candidate),
            self._blocked_heading_penalty(ant, heading),
        )
        target_distance = self._target_distance_for(ant, candidate)
        follow_heading_delta = self._heading_delta(
            heading,
            (base_heading + 90 * side) % 360,
        )

        if target_first:
            return common_score + (target_distance, follow_heading_delta)

        return common_score + (follow_heading_delta, target_distance)

    def _wall_follow_is_stalled(
        self,
        ant: Ant,
    ) -> bool:
        current_distance = self._target_distance_for(ant, (ant.x, ant.y))
        best_distance, stale_ticks = self._wall_follow_progress.get(
            ant.id,
            (current_distance, 0),
        )

        if current_distance < best_distance - 0.5:
            self._wall_follow_progress[ant.id] = (current_distance, 0)
            return False

        stale_ticks += 1
        self._wall_follow_progress[ant.id] = (best_distance, stale_ticks)
        return stale_ticks >= settings.ANT_WALL_FOLLOW_STALL_TICKS

    def _try_boundary_recovery_step(
        self,
        ant: Ant,
        base_heading: float,
    ) -> bool:
        if self._world_boundary_clearance(ant.x, ant.y) > ant.speed:
            return False

        candidates: list[tuple[tuple[float, ...], float, tuple[float, float]]] = []
        for heading in self._escape_headings(base_heading):
            candidate = self._candidate_position_for(ant, heading)
            if self._movement_intersects_obstacle(
                (ant.x, ant.y),
                candidate,
                radius=ant.hitbox_radius,
            ):
                continue

            candidates.append(
                (
                    (
                        -self._world_boundary_clearance(
                            candidate[0],
                            candidate[1],
                        ),
                        self._target_distance_for(ant, candidate),
                        self._heading_delta(heading, base_heading),
                    ),
                    heading,
                    candidate,
                )
            )

        if not candidates:
            return False

        _, heading, candidate = min(candidates)
        ant.x, ant.y = candidate
        ant.heading = heading % 360
        return True

    def _try_maze_stall_recovery_step(
        self,
        ant: Ant,
        base_heading: float,
    ) -> bool:
        waypoint = self._active_maze_recovery_waypoint_for(ant)
        if waypoint is not None:
            heading = math.degrees(
                math.atan2(
                    waypoint[1] - ant.y,
                    waypoint[0] - ant.x,
                )
            )
            candidate = self._candidate_position_for(ant, heading)
            if not self._movement_intersects_obstacle(
                (ant.x, ant.y),
                candidate,
                radius=ant.hitbox_radius,
            ):
                ant.x, ant.y = candidate
                ant.heading = heading % 360
                return True

        candidates: list[tuple[tuple[float, ...], float, tuple[float, float]]] = []

        for heading in self._escape_headings(base_heading):
            candidate = self._candidate_position_for(ant, heading)
            if self._movement_intersects_obstacle(
                (ant.x, ant.y),
                candidate,
                radius=ant.hitbox_radius,
            ):
                continue

            candidates.append(
                (
                    (
                        self._target_distance_for(ant, candidate),
                        self._blocked_heading_penalty(ant, heading),
                        self._heading_delta(heading, base_heading),
                    ),
                    heading,
                    candidate,
                )
            )

        if not candidates:
            return False

        _, heading, candidate = min(candidates)
        ant.x, ant.y = candidate
        ant.heading = heading % 360
        return True

    def _active_maze_recovery_waypoint_for(
        self,
        ant: Ant,
    ) -> tuple[float, float] | None:
        active_target = self._maze_recovery_targets.get(ant.id)
        if active_target is not None:
            waypoint, remaining_ticks = active_target
            if (
                remaining_ticks > 0
                and math.hypot(waypoint[0] - ant.x, waypoint[1] - ant.y)
                > ant.speed
            ):
                self._maze_recovery_targets[ant.id] = (
                    waypoint,
                    remaining_ticks - 1,
                )
                return waypoint

        waypoint = self._maze_recovery_waypoint_for(ant)
        if waypoint is None:
            self._maze_recovery_targets.pop(ant.id, None)
            return None

        self._maze_recovery_targets[ant.id] = (waypoint, 12)
        return waypoint

    def _maze_recovery_waypoint_for(
        self,
        ant: Ant,
    ) -> tuple[float, float] | None:
        target = self._target_position_for(ant)
        if target is None:
            return None

        grid_size = settings.ANT_RADIUS * 2
        start = self._nearest_open_grid_point(
            (ant.x, ant.y),
            grid_size=grid_size,
            radius=ant.hitbox_radius,
        )
        goal = self._nearest_open_grid_point(
            target,
            grid_size=grid_size,
            radius=ant.hitbox_radius,
        )
        if start is None or goal is None:
            return None

        path = self._find_grid_path(
            start,
            goal,
            grid_size=grid_size,
            radius=ant.hitbox_radius,
        )
        if len(path) < 2:
            return None

        return path[min(2, len(path) - 1)]

    def _nearest_open_grid_point(
        self,
        point: tuple[float, float],
        *,
        grid_size: float,
        radius: float,
    ) -> tuple[int, int] | None:
        start = self._grid_key_for(point, grid_size)
        candidates: list[tuple[float, tuple[int, int]]] = []
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                key = (start[0] + dx, start[1] + dy)
                position = self._grid_position_for(key, grid_size)
                if self._grid_position_is_open(position, radius=radius):
                    candidates.append(
                        (
                            math.hypot(
                                point[0] - position[0],
                                point[1] - position[1],
                            ),
                            key,
                        )
                    )

        if not candidates:
            return None

        return min(candidates)[1]

    def _find_grid_path(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
        *,
        grid_size: float,
        radius: float,
    ) -> tuple[tuple[float, float], ...]:
        frontier: list[tuple[float, int, tuple[int, int]]] = [(0.0, 0, start)]
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        cost_so_far: dict[tuple[int, int], float] = {start: 0.0}
        sequence = 0

        while frontier:
            _, _, current = heapq.heappop(frontier)
            if current == goal:
                break

            for neighbor in self._grid_neighbors(current):
                position = self._grid_position_for(neighbor, grid_size)
                if not self._grid_position_is_open(position, radius=radius):
                    continue
                if self._movement_intersects_obstacle(
                    self._grid_position_for(current, grid_size),
                    position,
                    radius=radius,
                ):
                    continue

                step_cost = math.hypot(
                    neighbor[0] - current[0],
                    neighbor[1] - current[1],
                )
                new_cost = cost_so_far[current] + step_cost
                if (
                    neighbor in cost_so_far
                    and new_cost >= cost_so_far[neighbor]
                ):
                    continue

                cost_so_far[neighbor] = new_cost
                priority = new_cost + math.hypot(
                    goal[0] - neighbor[0],
                    goal[1] - neighbor[1],
                )
                sequence += 1
                heapq.heappush(frontier, (priority, sequence, neighbor))
                came_from[neighbor] = current

        if goal not in came_from:
            return ()

        path_keys: list[tuple[int, int]] = []
        current_key: tuple[int, int] | None = goal
        while current_key is not None:
            path_keys.append(current_key)
            current_key = came_from[current_key]

        return tuple(
            self._grid_position_for(key, grid_size)
            for key in reversed(path_keys)
        )

    @staticmethod
    def _grid_key_for(
        point: tuple[float, float],
        grid_size: float,
    ) -> tuple[int, int]:
        return (
            round(point[0] / grid_size),
            round(point[1] / grid_size),
        )

    @staticmethod
    def _grid_position_for(
        key: tuple[int, int],
        grid_size: float,
    ) -> tuple[float, float]:
        return (key[0] * grid_size, key[1] * grid_size)

    @staticmethod
    def _grid_neighbors(
        key: tuple[int, int],
    ) -> tuple[tuple[int, int], ...]:
        x, y = key
        return (
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
            (x + 1, y + 1),
            (x + 1, y - 1),
            (x - 1, y + 1),
            (x - 1, y - 1),
        )

    def _grid_position_is_open(
        self,
        position: tuple[float, float],
        *,
        radius: float,
    ) -> bool:
        padding = settings.ANT_BOUNDARY_PADDING
        if not (
            padding <= position[0] <= settings.WORLD_WIDTH - padding
            and padding <= position[1] <= settings.WORLD_HEIGHT - padding
        ):
            return False

        return not self._position_is_blocked(
            position[0],
            position[1],
            radius=radius,
        )

    def _move_ant_out_of_obstacle_contact(
        self,
        ant: Ant,
    ) -> bool:
        base_heading = self._preferred_heading_for(ant)
        candidates: list[tuple[tuple[float, ...], float, tuple[float, float]]] = []

        for heading in self._escape_headings(base_heading):
            for step_count in range(
                1,
                settings.ANT_OBSTACLE_ESCAPE_MAX_STEPS + 1,
            ):
                candidate = self._candidate_position_for(
                    ant,
                    heading,
                    distance=ant.speed * step_count,
                )
                if self._position_is_blocked(
                    candidate[0],
                    candidate[1],
                    radius=ant.hitbox_radius,
                ):
                    continue

                candidates.append(
                    (
                        (
                            step_count,
                            self._target_distance_for(ant, candidate),
                            self._heading_delta(heading, base_heading),
                        ),
                        heading,
                        candidate,
                    )
                )
                break

        if not candidates:
            self._wall_follow_sides[ant.id] = (
                -self._wall_follow_sides.get(ant.id, -1)
            )
            return False

        _, heading, candidate = min(candidates)
        ant.x, ant.y = candidate
        ant.heading = heading % 360
        return True

    def _avoidance_score(
        self,
        ant: Ant,
        candidate: tuple[float, float],
        heading: float,
        base_heading: float,
        blocked_count: int = 1,
    ) -> tuple[float, ...]:
        blocked_penalty = self._blocked_heading_penalty(ant, heading)
        avoid_penalty = self._avoid_pheromone_penalty(ant, candidate)
        boundary_penalty = self._boundary_contact_penalty(ant, candidate)
        recovery_penalty = 0
        if blocked_count >= settings.ANT_AVOID_PHEROMONE_REPEAT_COUNT:
            recovery_heading = (base_heading + 180) % 360
            recovery_penalty = self._heading_delta(heading, recovery_heading)

        pheromone_distance = self._route_pheromone_distance(
            ant,
            candidate,
        )
        if pheromone_distance is not None:
            return (
                boundary_penalty,
                blocked_penalty,
                avoid_penalty,
                recovery_penalty,
                0,
                pheromone_distance,
                self._heading_delta(heading, base_heading),
            )

        target_distance = self._target_distance_for(
            ant,
            candidate,
        )
        return (
            boundary_penalty,
            blocked_penalty,
            avoid_penalty,
            recovery_penalty,
            1,
            target_distance,
            self._heading_delta(heading, base_heading),
        )

    @staticmethod
    def _world_boundary_clearance(
        x: float,
        y: float,
    ) -> float:
        padding = settings.ANT_BOUNDARY_PADDING
        return min(
            x - padding,
            settings.WORLD_WIDTH - padding - x,
            y - padding,
            settings.WORLD_HEIGHT - padding - y,
        )

    def _boundary_contact_penalty(
        self,
        ant: Ant,
        candidate: tuple[float, float],
    ) -> int:
        current_clearance = self._world_boundary_clearance(ant.x, ant.y)
        if current_clearance > ant.speed:
            return 0

        candidate_clearance = self._world_boundary_clearance(
            candidate[0],
            candidate[1],
        )
        minimum_escape_clearance = current_clearance + 1
        return int(candidate_clearance < minimum_escape_clearance)

    def _route_pheromone_distance(
        self,
        ant: Ant,
        candidate: tuple[float, float],
    ) -> float | None:
        source_ids = self._route_pheromone_source_ids(ant)
        if not source_ids:
            return None

        matching_pheromones = tuple(
            pheromone
            for pheromone in self.pheromones
            if pheromone.pheromone_type == PheromoneType.FOOD
            and pheromone.source_food_id in source_ids
            and ant.senses.can_detect(ant, pheromone)
            and self._pheromone_supports_current_route(ant, pheromone)
        )

        if not matching_pheromones:
            return None

        return min(
            math.hypot(
                candidate[0] - pheromone.x,
                candidate[1] - pheromone.y,
            )
            for pheromone in matching_pheromones
        )

    @staticmethod
    def _route_pheromone_source_ids(
        ant: Ant,
    ) -> tuple[int | str, ...]:
        if ant.state == AntState.SEEKING_FOOD and ant.food_target is not None:
            return (ant.food_target.id,)

        if ant.state == AntState.CARRYING_FOOD:
            return tuple(
                portion.source_id
                for portion in ant.inventory
            )

        return ()

    def _pheromone_supports_current_route(
        self,
        ant: Ant,
        pheromone: Pheromone,
    ) -> bool:
        if ant.state != AntState.CARRYING_FOOD:
            return True

        if ant.nest_target is None:
            return False

        current_nest_distance = math.hypot(
            ant.nest_target.x - ant.x,
            ant.nest_target.y - ant.y,
        )
        pheromone_nest_distance = math.hypot(
            ant.nest_target.x - pheromone.x,
            ant.nest_target.y - pheromone.y,
        )
        return pheromone_nest_distance < current_nest_distance

    def _target_distance_for(
        self,
        ant: Ant,
        candidate: tuple[float, float],
    ) -> float:
        target = self._target_position_for(ant)

        if target is None:
            return 0

        return math.hypot(
            target[0] - candidate[0],
            target[1] - candidate[1],
        )

    @staticmethod
    def _target_position_for(
        ant: Ant,
    ) -> tuple[float, float] | None:
        if ant.state == AntState.SEEKING_FOOD and ant.food_target is not None:
            return (ant.food_target.x, ant.food_target.y)
        if ant.state == AntState.CARRYING_FOOD and ant.nest_target is not None:
            return (ant.nest_target.x, ant.nest_target.y)
        return None

    @staticmethod
    def _heading_delta(
        heading: float,
        base_heading: float,
    ) -> float:
        return abs((heading - base_heading + 180) % 360 - 180)

    def _preferred_heading_for(
        self,
        ant: Ant,
    ) -> float:
        target: tuple[float, float] | None = None
        target = self._target_position_for(ant)

        if target is None:
            return ant.heading

        return math.degrees(
            math.atan2(
                target[1] - ant.y,
                target[0] - ant.x,
            )
        )

    @staticmethod
    def _avoidance_headings(
        base_heading: float,
        blocked_count: int = 1,
    ) -> tuple[float, ...]:
        if blocked_count >= settings.ANT_AVOID_PHEROMONE_REPEAT_COUNT:
            return tuple(
                (base_heading + offset) % 360
                for offset in (
                    180,
                    135,
                    -135,
                    90,
                    -90,
                    45,
                    -45,
                )
            )

        return tuple(
            (base_heading + offset) % 360
            for offset in (
                45,
                -45,
                90,
                -90,
                135,
                -135,
                180,
            )
        )

    @staticmethod
    def _escape_headings(
        base_heading: float,
    ) -> tuple[float, ...]:
        return tuple(
            (base_heading + offset) % 360
            for offset in (
                0,
                45,
                -45,
                90,
                -90,
                135,
                -135,
                180,
            )
        )

    def _record_blocked_heading(
        self,
        ant: Ant,
        heading: float,
    ) -> int:
        recent_headings = self._blocked_headings.setdefault(ant.id, [])
        recent_headings.append(
            (
                heading % 360,
                settings.ANT_BLOCKED_HEADING_MEMORY_TICKS,
            )
        )
        return sum(
            1
            for blocked_heading, _ in recent_headings
            if self._heading_delta(blocked_heading, heading)
            <= settings.ANT_BLOCKED_HEADING_MATCH_DEGREES
        )

    def _decay_blocked_headings_for(
        self,
        ant: Ant,
    ) -> None:
        recent_headings = self._blocked_headings.get(ant.id)
        if not recent_headings:
            return

        remaining = tuple(
            (heading, ticks - 1)
            for heading, ticks in recent_headings
            if ticks > 1
        )

        if remaining:
            self._blocked_headings[ant.id] = list(remaining)
        else:
            del self._blocked_headings[ant.id]

    def _blocked_heading_penalty(
        self,
        ant: Ant,
        heading: float,
    ) -> int:
        return sum(
            1
            for blocked_heading, _ in self._blocked_headings.get(ant.id, ())
            if self._heading_delta(blocked_heading, heading)
            <= settings.ANT_BLOCKED_HEADING_MATCH_DEGREES
        )

    def _avoid_pheromone_penalty(
        self,
        ant: Ant,
        candidate: tuple[float, float],
    ) -> float:
        penalties = tuple(
            pheromone.strength
            for pheromone in self.pheromones
            if pheromone.pheromone_type == PheromoneType.AVOID
            and ant.senses.can_detect(ant, pheromone)
            and math.hypot(
                candidate[0] - pheromone.x,
                candidate[1] - pheromone.y,
            )
            <= settings.PHEROMONE_DISCOVERABLE_RADIUS
        )
        return sum(penalties)

    def _deposit_avoid_pheromone_for(
        self,
        ant: Ant,
    ) -> None:
        self._world.add_entity(
            Pheromone(
                pheromone_id=self._world._next_pheromone_id,
                pheromone_type=PheromoneType.AVOID,
                strength=settings.AVOID_PHEROMONE_INITIAL_STRENGTH,
                x=ant.x,
                y=ant.y,
            )
        )
        self._world._next_pheromone_id += 1

    @staticmethod
    def _candidate_position_for(
        ant: Ant,
        heading: float,
        distance: float | None = None,
    ) -> tuple[float, float]:
        heading_radians = math.radians(heading)
        step_distance = ant.speed if distance is None else distance
        x = ant.x + math.cos(heading_radians) * step_distance
        y = ant.y + math.sin(heading_radians) * step_distance
        padding = settings.ANT_BOUNDARY_PADDING
        return (
            min(max(x, padding), settings.WORLD_WIDTH - padding),
            min(max(y, padding), settings.WORLD_HEIGHT - padding),
        )

    def _movement_intersects_obstacle(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        *,
        radius: float = 0.0,
    ) -> bool:
        return self._collision_map.movement_intersects_obstacle(
            start,
            end,
            radius=radius,
        )

    def _position_is_blocked(
        self,
        x: float,
        y: float,
        *,
        radius: float = 0.0,
    ) -> bool:
        return self._collision_map.position_is_blocked(
            x,
            y,
            radius=radius,
        )
