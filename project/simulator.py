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

    policy_color = colors['cyan']

    robot_color = colors['blue']

    sensor_color = colors['orange']

    start_color = colors['red']

    finish_color = colors['green']

    hidden_wall_color = colors['gray']

    known_wall_color = colors['black']

    dir_label = {'up': 'v',
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

        if delay:
            try:
                self.game = importlib.import_module('pygame')
                self.game.init()
                size = maze.dim * self.block_size + (maze.dim + 1) * self.line_width
                self.screen = self.game.display.set_mode((size, size))
                self.font = self.game.font.Font(None, 20)
                self.frame_delay = max(1, int(delay * 1000))  # delay between frames in ms (min: 1)
            except Exception as e:
                self.game = None
                print 'Error initializing simulator; disabled.\n{}: {}'.format(e.__class__.__name__, e)

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

            # draw start and finish
            self.render_start_goal()

            # draw robot additional info
            self.render_robot_info()

            # draw robot pos
            self.render_robot_shape()

            # replace buffer
            self.game.display.flip()

            # apply frame delay
            self.game.time.wait(self.frame_delay)

    def render_maze(self):
        """
        Iterates through squares one by one to decide where to draw walls.
        """

        for x in range(self.maze.dim):
            for y in range(self.maze.dim):
                for dir in self.dir_label:
                    if not self.maze.is_permissible([x, y], dir):
                        self.render_wall(x, y, dir, self.hidden_wall_color)

    def render_start_goal(self):
        """
        Draw start and goal point taken from the robot.
        """

        start_center = self.center(self.robot.start[0], self.robot.start[1])
        start_point, start_radius = [start_center[0], start_center[1]], int(.3 * self.block_size)
        self.game.draw.circle(self.screen, self.start_color, start_point, start_radius, self.line_width)

        finish_center = self.center(self.robot.goal[0], self.robot.goal[1])
        finish_point = finish_center[0] - .3 * self.block_size, finish_center[1] - .3 * self.block_size
        finish_point = [finish_point[0], finish_point[1], .6 * self.block_size, .6 * self.block_size]
        self.game.draw.rect(self.screen, self.finish_color, finish_point, self.line_width)

    def render_robot_info(self):
        """
        Draws robot's policy and spotted walls.
        """

        for x in range(self.maze.dim):
            for y in range(self.maze.dim):
                # policy
                if self.robot.policy[x][y]:
                    center = self.center(x, y)
                    policy = self.robot.policy[x][y]
                    label = self.font.render(self.dir_label[policy], 1, self.policy_color)
                    self.screen.blit(label, [center[0] - label.get_width() / 2, center[1] - label.get_height() / 2])

                # walls
                for dir in self.dir_label:
                    if self.robot.maze.has_wall(x, y, dir):
                        self.render_wall(x, y, dir, self.known_wall_color)

    def render_robot_shape(self):
        """
        Calculates robots points and draws robot's triangle.
        """

        x, y = self.robot.location
        center = self.center(x, y)
        heading = self.robot.heading
        points = []
        for p in self.robot_shape[heading]:
            points.append((center[0] + p[0] * self.block_size, center[1] + p[1] * self.block_size))

        self.game.draw.lines(self.screen, self.robot_color, True, points, self.line_width)

    def render_wall(self, x, y, direction, color):
        """
        Renders wall for given cell in the maze and direction of the wall.
        """

        if direction == 'up':
            self.game.draw.line(self.screen, color,
                                self.transform(x, y + 1), self.transform(x + 1, y + 1),
                                self.line_width)
        elif direction == 'right':
            self.game.draw.line(self.screen, color,
                                self.transform(x + 1, y), self.transform(x + 1, y + 1),
                                self.line_width)
        elif direction == 'down':
            self.game.draw.line(self.screen, color,
                                self.transform(x, y), self.transform(x + 1, y),
                                self.line_width)
        elif direction == 'left':
            self.game.draw.line(self.screen, color,
                                self.transform(x, y), self.transform(x, y + 1),
                                self.line_width)

    def center(self, x, y):
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
