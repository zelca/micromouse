import importlib


class Simulator(object):
    """
    Simulates robot in a maze environment.
    Uses PyGame to display GUI, if available.
    """

    colors = {
        'black': (0, 0, 0),
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

    wall_color = colors['black']

    robot_color = colors['blue']

    start_color = colors['red']

    finish_color = colors['green']

    robot_shape = {
        'up': [(-.2, -.4), (0, .4), (.2, -.4)],
        'left': [(-.4, 0), (.4, .2), (.4, -.2)],
        'down': [(-.2, .4), (0, -.4), (.2, .4)],
        'right': [(.4, 0), (-.4, .2), (-.4, -.2)],
    }

    def __init__(self, maze, delay=None):
        self.maze = maze

        start_init = self.transform(1, 1)
        start_center = start_init[0] - int(.5 * self.block_size), start_init[1] - int(.5 * self.block_size)
        self.start = [start_center[0], start_center[1], int(.3 * self.block_size)]

        finish_init = self.transform(maze.dim / 2, maze.dim / 2 + 1)
        finish_point = finish_init[0] - int(.8 * self.block_size), finish_init[1] - int(.8 * self.block_size)
        finish_size = int(.6 * self.block_size)
        self.finish = [finish_point[0], finish_point[1], finish_size, finish_size]

        if delay:
            try:
                self.game = importlib.import_module('pygame')
                self.game.init()
                size = maze.dim * self.block_size + (maze.dim + 1) * self.line_width
                self.screen = self.game.display.set_mode((size, size))
                self.frame_delay = max(1, int(delay * 1000))  # delay between frames in ms (min: 1)
            except Exception as e:
                self.game = None
                print 'Error initializing simulator; disabled.\n{}: {}'.format(e.__class__.__name__, e)

    def render(self, robot_pos):
        if self.game:
            # clear screen
            self.screen.fill(self.maze_color)

            # draw maze
            # iterate through squares one by one to decide where to draw walls
            for x in range(self.maze.dim):
                for y in range(self.maze.dim):
                    if not self.maze.is_permissible([x, y], 'up'):
                        self.game.draw.line(self.screen, self.wall_color,
                                            self.transform(x, y + 1), self.transform(x + 1, y + 1),
                                            self.line_width)

                    if not self.maze.is_permissible([x, y], 'right'):
                        self.game.draw.line(self.screen, self.wall_color,
                                            self.transform(x + 1, y), self.transform(x + 1, y + 1),
                                            self.line_width)

                    # only check bottom wall if on lowest row
                    if not self.maze.is_permissible([x, y], 'down'):
                        self.game.draw.line(self.screen, self.wall_color,
                                            self.transform(x, y), self.transform(x + 1, y),
                                            self.line_width)

                    # only check left wall if on leftmost column
                    if not self.maze.is_permissible([x, y], 'left'):
                        self.game.draw.line(self.screen, self.wall_color,
                                            self.transform(x, y), self.transform(x, y + 1),
                                            self.line_width)

            # draw start and finish
            self.game.draw.circle(self.screen, self.start_color,
                                  (self.start[0], self.start[1]), self.start[2], self.line_width)
            self.game.draw.rect(self.screen, self.finish_color, self.finish, self.line_width)

            # draw robot
            self.render_robot(robot_pos)

            # replace buffer
            self.game.display.flip()

            # apply frame delay
            self.game.time.wait(self.frame_delay)

    def render_robot(self, robot_pos):
        init = self.transform(robot_pos['location'][0] + 1, robot_pos['location'][1] + 1)
        center = init[0] - int(.5 * self.block_size), init[1] - int(.5 * self.block_size)
        points = []
        for p in self.robot_shape[robot_pos['heading']]:
            points.append((center[0] + p[0] * self.block_size, center[1] + p[1] * self.block_size))

        self.game.draw.lines(self.screen, self.robot_color, True, points, self.line_width)

    def transform(self, x, y):
        return x * (self.block_size + self.line_width), y * (self.block_size + self.line_width)
