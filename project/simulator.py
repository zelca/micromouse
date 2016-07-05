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

    info_color = colors['orange']

    robot_color = colors['blue']

    sensor_color = colors['orange']

    start_color = colors['red']

    finish_color = colors['green']

    hidden_wall_color = colors['gray']

    visited_wall_color = colors['black']

    robot_shape = {
        'up': [(-.2, -.4), (0, .4), (.2, -.4)],
        'left': [(-.4, 0), (.4, .2), (.4, -.2)],
        'down': [(-.2, .4), (0, -.4), (.2, .4)],
        'right': [(.4, 0), (-.4, .2), (-.4, -.2)],
    }

    directions = ['up', 'left', 'down', 'right']

    def __init__(self, maze, robot, delay=None):
        self.maze = maze
        self.robot = robot

        start_center = self.center(robot.location[0], robot.location[1])
        self.start = [start_center[0], start_center[1], int(.3 * self.block_size)]

        finish_center = self.center(robot.goal[0], robot.goal[1])
        finish_point = finish_center[0] - .3 * self.block_size, finish_center[1] - .3 * self.block_size
        self.finish = [finish_point[0], finish_point[1], .6 * self.block_size, .6 * self.block_size]

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

    def render(self, robot_pos):
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

            # draw maze
            # iterate through squares one by one to decide where to draw walls
            for x in range(self.maze.dim):
                for y in range(self.maze.dim):
                    for d in self.directions:
                        if not self.maze.is_permissible([x, y], d):
                            self.render_wall(x, y, d, self.hidden_wall_color)

            # draw start and finish
            self.game.draw.circle(self.screen, self.start_color,
                                  (self.start[0], self.start[1]), self.start[2], self.line_width)
            self.game.draw.rect(self.screen, self.finish_color, self.finish, self.line_width)

            # draw robot additional info
            self.render_robot_info(self.robot, robot_pos)

            # draw robot pos
            self.render_robot_pos(robot_pos)

            # replace buffer
            self.game.display.flip()

            # apply frame delay
            self.game.time.wait(self.frame_delay)

    def render_robot_pos(self, robot_pos):
        """
        Calculates robots points and draws robot's triangle.
        """

        x = robot_pos['location'][0]
        y = robot_pos['location'][1]
        center = self.center(x, y)
        points = []
        for p in self.robot_shape[robot_pos['heading']]:
            points.append((center[0] + p[0] * self.block_size, center[1] + p[1] * self.block_size))

        self.game.draw.lines(self.screen, self.robot_color, True, points, self.line_width)

    def render_robot_info(self, robot, robot_pos):
        """
        Renders robot's additional info like sensors etc.
        """

        for x in range(self.maze.dim):
            for y in range(self.maze.dim):
                # info
                if robot.info[x][y]:
                    center = self.center(x, y)
                    info = self.font.render(robot.info[x][y], 1, self.info_color)
                    self.screen.blit(info, [center[0] - info.get_width() / 2, center[1] - info.get_height() / 2])

                # visited wall
                if robot.visited[x][y]:
                    for d in self.directions:
                        if not self.maze.is_permissible([x, y], d):
                            self.render_wall(x, y, d, self.visited_wall_color)

        if robot.sensors and len(robot.sensors) == 3:
            x = robot_pos['location'][0]
            y = robot_pos['location'][1]
            if robot_pos['heading'] == 'up':
                self.render_wall(x - robot.sensors[0], y, 'left', self.sensor_color)
                self.render_wall(x, y + robot.sensors[1], 'up', self.sensor_color)
                self.render_wall(x + robot.sensors[2], y, 'right', self.sensor_color)
            elif robot_pos['heading'] == 'left':
                self.render_wall(x, y + robot.sensors[2], 'up', self.sensor_color)
                self.render_wall(x - robot.sensors[1], y, 'left', self.sensor_color)
                self.render_wall(x, y - robot.sensors[0], 'down', self.sensor_color)
            elif robot_pos['heading'] == 'down':
                self.render_wall(x - robot.sensors[2], y, 'left', self.sensor_color)
                self.render_wall(x, y - robot.sensors[1], 'down', self.sensor_color)
                self.render_wall(x + robot.sensors[0], y, 'right', self.sensor_color)
            elif robot_pos['heading'] == 'right':
                self.render_wall(x, y + robot.sensors[0], 'up', self.sensor_color)
                self.render_wall(x + robot.sensors[1], y, 'right', self.sensor_color)
                self.render_wall(x, y - robot.sensors[2], 'down', self.sensor_color)

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
