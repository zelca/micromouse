import importlib


class Simulator(object):
    """
    Simulates robot in a maze environment.
    Uses PyGame to display GUI, if available.
    """

    colors = {
        'black': (0, 0, 0),
        'gray': (200, 200, 200),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'cyan': (0, 200, 200),
        'magenta': (200, 0, 200),
        'yellow': (255, 255, 0),
        'orange': (255, 128, 0)
    }

    line_width = 2

    block_size = 30

    maze_color = colors['white']

    path_color = colors['red']

    policy_color = colors['cyan']

    robot_color = colors['blue']

    sensor_color = colors['orange']

    start_color = colors['red']

    finish_color = colors['green']

    hidden_wall_color = colors['gray']

    known_wall_color = colors['black']

    heading_label = {'up': 'v',
                     'right': '>',
                     'down': '^',
                     'left': '<'}

    robot_shape = {
        'up': [(-.2, -.4), (0, .4), (.2, -.4)],
        'left': [(-.4, 0), (.4, .2), (.4, -.2)],
        'down': [(-.2, .4), (0, -.4), (.2, .4)],
        'right': [(.4, 0), (-.4, .2), (-.4, -.2)],
    }

    def __init__(self, maze, robot, delay=None, show_maze=None):
        self.maze = maze
        self.robot = robot
        self.show_maze = show_maze

        self.game = None
        if delay:
            try:
                self.game = importlib.import_module('pygame')
                self.game.init()
                size = maze.dim * self.block_size + (maze.dim + 1) * self.line_width
                self.screen = self.game.display.set_mode((size, size))
                self.font = self.game.font.Font(None, 20)
                self.frame_delay = max(1, delay)  # delay between frames in ms (min: 1)
            except Exception as e:

                print 'Error initializing simulator; disabled.\n{}: {}'.format(e.__class__.__name__, e)

        # render initial state
        self.render()

    def render(self):
        """
        Renders maze and robot if game is initialized.
        Rendering can be interrupted by close button.
        """

        # check for quit event
        if self.game:
            for event in self.game.event.get():
                if self.game and event.type == self.game.QUIT:
                    self.game.quit()
                    self.game = None

        # draw environment
        if self.game:
            # clear screen
            self.screen.fill(self.maze_color)

            # draw maze if show_maze is set to True
            if self.show_maze:
                self.render_maze()

            # draw robot data
            self.render_robot_data()

            # draw robot pos
            self.render_robot_shape()

            # replace buffer
            self.game.display.flip()

            # apply frame delay
            self.game.time.wait(self.frame_delay)

    def render_maze(self):
        """
        Iterates through cells one by one to decide where to draw walls.
        """

        for x in range(self.maze.dim):
            for y in range(self.maze.dim):
                for heading in self.heading_label:
                    if not self.maze.is_permissible([x, y], heading):
                        self.render_wall(x, y, heading, self.hidden_wall_color)

    def render_robot_data(self):
        """
        Draws robot's policy, spotted walls and the goal.
        """

        for x in range(self.maze.dim):
            for y in range(self.maze.dim):
                # policy
                if self.robot.policy[x][y]:
                    center = self.center((x, y))
                    heading, movement, _ = self.robot.policy[x][y]
                    color = self.path_color if (x, y) in self.robot.path else self.policy_color
                    label = self.font.render(self.heading_label[heading] + "{}".format(movement), 1, color)
                    self.screen.blit(label, [center[0] - label.get_width() / 2, center[1] - label.get_height() / 2])

                # walls
                for heading in self.heading_label:
                    if not self.robot.maze.is_permissible((x, y), heading):
                        self.render_wall(x, y, heading, self.known_wall_color)

        # goal
        goal_center = self.center(self.robot.goal)
        goal_point = goal_center[0] - .3 * self.block_size, goal_center[1] - .3 * self.block_size
        goal_point = [goal_point[0], goal_point[1], .6 * self.block_size, .6 * self.block_size]
        self.game.draw.rect(self.screen, self.finish_color, goal_point, self.line_width)

        # path
        prev_cell = None
        for cell in self.robot.path:
            if prev_cell:
                p1 = self.center(prev_cell)
                p2 = self.center(cell)
                self.game.draw.line(self.screen, self.path_color, p1, p2, self.line_width)
            prev_cell = cell
        if prev_cell:
            p1 = self.center(prev_cell)
            p2 = self.center(self.robot.goal)
            self.game.draw.line(self.screen, self.path_color, p1, p2, self.line_width)

    def render_robot_shape(self):
        """
        Calculates robots points and draws robot's triangle.
        """

        center = self.center(self.robot.location)
        heading = self.robot.heading
        points = []
        for p in self.robot_shape[heading]:
            points.append((center[0] + p[0] * self.block_size, center[1] + p[1] * self.block_size))

        self.game.draw.lines(self.screen, self.robot_color, True, points, self.line_width)

    def render_wall(self, x, y, side, color):
        """
        Renders wall for given cell in the maze and side of the wall.
        """

        if side == 'up':
            self.game.draw.line(self.screen, color,
                                self.transform(x, y + 1), self.transform(x + 1, y + 1),
                                self.line_width)
        elif side == 'right':
            self.game.draw.line(self.screen, color,
                                self.transform(x + 1, y), self.transform(x + 1, y + 1),
                                self.line_width)
        elif side == 'down':
            self.game.draw.line(self.screen, color,
                                self.transform(x, y), self.transform(x + 1, y),
                                self.line_width)
        elif side == 'left':
            self.game.draw.line(self.screen, color,
                                self.transform(x, y), self.transform(x, y + 1),
                                self.line_width)

    def center(self, (x, y)):
        """
        Transforms maze coordinates to canvas coordinates of the cell's center.
        """

        pos = self.transform(x + 1, y + 1)
        return pos[0] - int(.5 * self.block_size), pos[1] - int(.5 * self.block_size)

    def transform(self, x, y):
        """
        Transforms maze coordinates to canvas coordinates.
        """

        return x * (self.block_size + self.line_width), y * (self.block_size + self.line_width)
