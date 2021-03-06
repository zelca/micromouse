from policy import *


class Robot(object):
    Exploring, Validating, Testing = range(3)

    def __init__(self, maze_dim, init, goal_bounds):
        """
        Sets up attributes that a robot will use to learn and navigate the
        maze. Some initial attributes are provided based on common information,
        including the size of the maze the robot is placed in.
        """

        self.init = init
        self.goals = [[x, y] for x in goal_bounds for y in goal_bounds]

        self.maze = Maze(maze_dim)

        self.path = []
        self.optimal = []
        self.policy = None

        # start `exploring`
        self.mode = Robot.Exploring
        self.heading = 'up'
        self.location = [self.init[0], self.init[1]]

    def next_move(self, sensors):
        """
        Determines the next move the robot should make, based on the input
        from the sensors after its previous move. Sensor inputs are a list
        of three distances from the robot's left, front, and right-facing
        sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returning the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        """

        # update maze data, based on sensors
        if self.update_maze(sensors):
            # update policy and solution if maze was updated
            self.policy = compute_policy(self.maze, self.goals)
            self.optimal = compute_path(self.policy, self.init)

        # goal is reached in `exploring` phase, switch to `connecting` phase
        if self.mode == Robot.Exploring and self.location in self.goals:
            self.mode = Robot.Validating

        current_policy = self.policy
        if self.mode == Robot.Validating:
            # during `connecting` phase robot visits all unvisited cells
            # from the solution path and verifies that this path is optimal
            unvisited = last_unvisited(self.maze, self.optimal + self.goals)
            if unvisited:
                current_policy = compute_policy(self.maze, [unvisited])
            else:
                # if there are no unvisited cells switch to `testing` phase
                self.mode = Robot.Testing
                self.heading = 'up'
                self.location = [self.init[0], self.init[1]]
                return 'Reset', 'Reset'

        # find next rotation and movement, based on policy
        rotation, movement = self.next_action(current_policy)

        # update internal state (heading, location) of a robot
        self.update_state(sensors, rotation, movement)

        # update current path for visualization
        self.path = compute_path(current_policy, self.location)

        return rotations[rotation], movement

    def next_action(self, policy):
        """
        Chooses next rotation and movement, based on optimal policy, current
        heading and location of the robot.
        If new heading is reversed comparing to current robot doesn't rotate
        and does negative movement.
        """

        x, y = self.location
        heading, movement, _ = policy[x][y]

        if self.heading == heading_reverse[heading]:
            movement *= -1
            heading = self.heading

        rotation = heading_rotation[self.heading].index(heading)

        return rotation, movement

    def update_state(self, sensors, rotation, movement):
        """
        Updates robot heading and location, based on rotation, movement and
        current sensors values. Localization is skipped if no pending action.
        """

        # update heading
        self.heading = heading_rotation[self.heading][rotation]

        # check for a wall
        movement = min(sensors[rotation], movement)

        # update position
        move = heading_move[self.heading]
        self.location[0] += movement * move[0]
        self.location[1] += movement * move[1]

    def update_maze(self, sensors):
        """
        Updates information about spotted walls.
        Returns true if maze data is updated.
        """

        updated = False
        for s in range(len(sensors)):
            heading = heading_rotation[self.heading][s]
            x, y = self.location
            move = heading_move[heading]
            for i in range(sensors[s]):
                updated |= self.maze.set_wall([x, y], heading, False)
                x += move[0]
                y += move[1]
            updated |= self.maze.set_wall([x, y], heading, True)

        return updated


class Maze(object):
    """
    Internal robot's representation of the maze.
    Holds information about borders and spotted walls.
    """

    def __init__(self, dim):
        self.dim = dim
        self.walls = {}
        self.walls_dim = 2 * (dim - 1)

    def set_wall(self, cell, heading, is_wall):
        """
        Maps the cell coordinates to wall coordinates and stores
        information about a presence of a wall in specific heading.
        """

        updated = False
        move = heading_move[heading]
        x_ = 2 * cell[0] + move[0]
        y_ = 2 * cell[1] + move[1]
        if not (x_, y_) in self.walls:
            self.walls[x_, y_] = is_wall
            updated = True

        return updated

    def is_visited(self, cell):
        """
        Maps the cell coordinates to wall coordinates and checks
        if a presence of the walls for the specific cell is known.
        """

        for heading in heading_move:
            move = heading_move[heading]
            x_ = 2 * cell[0] + move[0]
            y_ = 2 * cell[1] + move[1]
            if self.in_bound(x_, y_) and not (x_, y_) in self.walls:
                return False

        return True

    def is_defined(self, cell, heading):
        """
        Maps the cell coordinates to wall coordinates and checks
        if a presence of the walls for the specific cell is known.
        """

        move = heading_move[heading]
        x_ = 2 * cell[0] + move[0]
        y_ = 2 * cell[1] + move[1]
        return not self.in_bound(x_, y_) or (x_, y_) in self.walls

    def is_permissible(self, cell, heading):
        """
        Maps the cell coordinates to a wall coordinates and checks
        if move in the specific heading is allowed.
        """

        move = heading_move[heading]
        x_ = 2 * cell[0] + move[0]
        y_ = 2 * cell[1] + move[1]
        return self.in_bound(x_, y_) and not self.walls.get((x_, y_), None)

    def in_bound(self, x, y):
        """
        Checks if the wall coordinates are in the maze bounds.
        """

        return 0 <= x <= self.walls_dim and 0 <= y <= self.walls_dim
