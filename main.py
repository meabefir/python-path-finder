import pygame, sys, time

pygame.init()
#screen_size = (int(pygame.display.Info().current_w*.83),int(pygame.display.Info().current_h*.83))
screen_size = (1000, 600)
print(screen_size)
screen = pygame.display.set_mode(screen_size)#,pygame.FULLSCREEN)

font = pygame.font.SysFont('calibri', 32)

colors = {'black': (0, 0, 0), 'blue': (0, 0, 255), 'red': (255, 0, 0), 'yellow': (255, 255, 0), -1: (0, 0, 0),
          's': (255, 0, 0),
          'e': (0, 255, 0), 0: (255, 255, 255), 't': (255, 255, 0), 'v': (0, 0, 255)}

values = {'wall': -1, 'start': 's', 'end': 'e'}

button_width = 150
button_height = 60
size = 40


class Text():
    def set_text_size(self, text):
        text_rect = text.get_rect()
        return ((text_rect[2] - text_rect[0], text_rect[3] - text_rect[1]))

    def draw_text(self, text_render, x_off=0, y_off=0, color=colors['black'], centered=1):
        if not isinstance(text_render, pygame.Surface):
            if type(text_render) is type([]):
                text_render = " ".join([str(el.name) for el in text_render])
                text_render = font.render(text_render, True, color)
            else:
                text_render = font.render(str(text_render), True, color)
        text_size = self.set_text_size(text_render)
        screen.blit(text_render,
                    (self.rect.x - (text_size[0] // 2) * centered + x_off,
                     self.rect.y - (text_size[1] // 2) * centered + y_off))


class PathFinder():
    def __init__(self, grid_size):
        self.generating = False
        self.generator = None
        self.last_iteration = time.time()
        self.iteration_delay = .0000001
        self.x = 0
        self.y = 0
        self.wall_mode = False
        self.size = screen_size[1]
        self.rows = grid_size
        self.cell_size = self.size // self.rows
        self.cols = (screen_size[0]-button_width)//self.cell_size
        self.start = None
        self.end = None
        self.matrix = [[Cell(self, x, y) for x in range(self.rows)] for y in range(self.cols)]

    def update(self):
        for row in self.matrix:
            for cell in row:
                cell.update()
        if self.generating:
            self.iterate_generation()

    def draw(self):
        for row in self.matrix:
            for cell in row:
                cell.draw()

    def clear_cells(self):
        self.generator = None
        self.generating = False
        for row in self.matrix:
            for cell in row:
                cell.reset()

    def clear_path(self):
        self.generator = None
        self.generating = False
        for row in self.matrix:
            for cell in row:
                cell.set_default()

    def iterate_generation(self):
        if (time.time() - self.last_iteration) > self.iteration_delay:
            self.last_iteration = time.time()
            try:
                next(self.generator)
            except Exception as e:
                print(e)
                self.generating = False

    def find_path(self, method):
        self.clear_path()
        self.generator = method()
        self.generating = True

    def brute_visit(self, pos):
        xx, yy = pos
        # if visited
        if self.matrix[xx][yy].value == -1 or self.matrix[xx][yy].visited:
            self.search_que.pop(0)
            return

        yield
        # if end
        if self.matrix[xx][yy].value == 'e':
            self.search_que = []
            return

        self.matrix[xx][yy].visited = True
        if self.matrix[xx][yy].value != 's':
            self.matrix[xx][yy].value = 'v'

        dx = [-1, 0, 1, 0]
        dy = [0, 1, 0, -1]
        for i in range(4):
            visit_x = xx + dx[i]
            visit_y = yy + dy[i]
            if self.cols > visit_x >= 0 and self.rows > visit_y >= 0:
                if not self.matrix[visit_x][visit_y].visited:
                    self.matrix[visit_x][visit_y].trail = self.matrix[xx][yy].trail + 1
                    self.search_que.append((visit_x, visit_y))
        self.search_que.pop(0)

    def brute_force(self):
        self.search_que = []
        current_pos = (self.start.col, self.start.row)
        self.search_que.append(current_pos)
        while len(self.search_que):
            yield from self.brute_visit(self.search_que[0])

        # TRAIL
        curr = self.end
        while curr.trail != 0:
            yield
            if curr != self.end:
                curr.value = 't'
            curr.set_color(colors['yellow'])
            dx = [1, 0, -1, 0]
            dy = [0, 1, 0, -1]
            for i in range(4):
                if self.rows > curr.col + dx[i] >= 0 and self.rows > curr.row + dy[i] >= 0:
                    if self.matrix[curr.col + dx[i]][curr.row + dy[i]].trail == curr.trail - 1:
                        curr = self.matrix[curr.col + dx[i]][curr.row + dy[i]]
                        break

    def get_distance(self,nodeA,nodeB):
        dstX = abs(nodeA.row-nodeB.row)
        dstY = abs(nodeA.col-nodeB.col)

        if dstX>dstY:
            return 14*dstY+10*(dstX-dstY)
        return 14*dstX+10*(dstY-dstX)

    def a_star(self):
        open = []
        closed = []
        open.append(self.start)

        while len(open):
            current = open[0]
            for i in range(1,len(open)):
                if open[i].f_cost < current.f_cost or (open[i].f_cost == current.f_cost and open[i].h_cost < current.h_cost):
                    current = open[i]

            open.remove(current)
            closed.append(current)

            if current == self.end:
                current = self.end
                # trail
                trail = []
                current = current.parent
                while current.parent is not None and current.parent not in trail:
                    yield
                    trail.append(current)
                    print(current)
                    current.value = 't'
                    current = current.parent
                return

            dx = [1,0,-1,0]
            dy = [0,1,0,-1]
            for i in range(4):
            # for j in range(-1,2):
            #     for i in range(-1,2):
            #         if i == 0 and j == 0:
            #             continue
            #         new_row = current.row+i
            #         new_col = current.col+j
                new_row = current.row + dx[i]
                new_col = current.col + dy[i]
                if self.size > new_col >= 0 and self.size > new_row >= 0:
                    try:
                        neighbour = self.matrix[new_col][new_row]

                        if neighbour.value == -1 or neighbour in closed:
                            continue
                        if neighbour != self.end:
                            neighbour.value = 'v'
                        yield
                        new_movement_cost = current.g_cost + self.get_distance(current,neighbour)
                        if new_movement_cost < neighbour.g_cost or neighbour not in open:
                            neighbour.g_cost = new_movement_cost
                            neighbour.h_cost = self.get_distance(neighbour,self.end)
                            neighbour.parent = current

                            if neighbour not in open:
                                open.append(neighbour)
                    except:
                        print("BULLSHIT")


class Cell(Text):
    default_color = (255, 255, 255)

    def __init__(self, path_finder, row, col):
        self.g_cost = 0
        self.h_cost = 0
        self.f_cost = 0
        self.parent = None
        self.trail = 0
        self.visited = False
        self.last_change = time.time()
        self.value = 0
        self.path_finder = path_finder
        self.row = row
        self.col = col
        self.color = Cell.default_color
        self.rect = pygame.Rect(path_finder.x + self.col * path_finder.cell_size,
                                path_finder.y + self.row * path_finder.cell_size,
                                self.path_finder.cell_size,
                                self.path_finder.cell_size)
        self.name = f'{self.row};{self.col}'

    def __str__(self):
        return self.name

    def set_costs(self):
        minn = min(abs(self.path_finder.start.row - self.row),
                   abs(self.path_finder.start.col - self.col))
        self.g_cost = minn * 14 + (
                max(abs(self.path_finder.start.row - self.row),
                    abs(self.path_finder.start.col - self.col)) - minn) * 10
        minn = min(abs(self.path_finder.end.row - self.row),
                   abs(self.path_finder.end.col - self.col))
        self.h_cost = minn * 14 + (
                max(abs(self.path_finder.end.row - self.row),
                    abs(self.path_finder.end.col - self.col)) - minn) * 10
        self.f_cost = self.g_cost+self.h_cost

    def set_color(self, color):
        self.color = color

    def update(self):
        if gui.active_gui is not None:
            if self.rect.collidepoint(mouse.x, mouse.y):
                if gui.active_gui.name == 'wall':
                    if mouse.clicked:
                        self.path_finder.wall_mode = False if self.value == -1 else True
                    if mouse.held:
                        if self.path_finder.wall_mode:
                            self.value = -1
                        else:
                            self.value = 0
                elif gui.active_gui.name == 'start':
                    if mouse.clicked:
                        if self.path_finder.start is not None:
                            self.path_finder.start.value = 0
                        self.path_finder.start = self
                        self.value = 's'
                elif gui.active_gui.name == 'end':
                    if mouse.clicked:
                        if self.path_finder.end is not None:
                            self.path_finder.end.value = 0
                        self.path_finder.end = self
                        self.value = 'e'
        self.color = colors[self.value]

    def reset(self):
        self.visited = False
        self.trail = 0
        if self.value not in ['s','e']:
            self.value = 0

    def set_default(self):
        self.visited = False
        self.trail = 0
        if self.value not in [0,-1,'s','e']:
            self.value = 0

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, colors['black'], self.rect, 2)
        #self.draw_text(self.name, centered=0)
        # if self.trail != 0: self.draw_text(self.trail, self.path_finder.cell_size / 2, self.path_finder.cell_size / 2, centered=1)


class GUI():
    def __init__(self):
        self.x = screen_size[0]-button_width
        self.y = 0
        self.rect = pygame.Rect(self.x, self.y, button_width, screen_size[1])
        self.active_gui = None
        self.gui_elements_names = ['wall', 'start', 'end', 'clear', 'brute-force', 'A-star']
        self.gui_elements = [
            GUIElement(self, self.gui_elements_names[i], self.rect.x,
                       self.rect.y + button_height * (i) * 1.2) for i in range(4)]
        self.gui_elements += [GUIElement(self, self.gui_elements_names[i], self.rect.x,
                                         self.rect.y + screen_size[1] - button_height * (i - 3) * 1.2)
                              for i in range(4, len(self.gui_elements_names))]

    def update(self):
        for gui_element in self.gui_elements:
            gui_element.update()

    def draw(self):
        pygame.draw.rect(screen, (0, 0, 0), self.rect)
        pygame.draw.rect(screen, (255, 255, 0), self.rect, 2)
        for gui_element in self.gui_elements:
            gui_element.draw()


class GUIElement(Text):
    highlight_color = colors['blue']
    default_color = colors['red']

    def __init__(self, gui, name, x, y):
        self.gui = gui
        self.name = name
        self.rect = pygame.Rect(x, y, button_width, button_height)
        self.color = self.default_color

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (255, 255, 0), self.rect, 2)
        self.draw_text(self.name, self.rect.w / 2, self.rect.h / 2)

    def update(self):
        if mouse.clicked and self.rect.collidepoint(mouse.x, mouse.y):
            if self.name in ['start', 'end', 'wall']:
                self.gui.active_gui = self
                self.color = self.highlight_color
            elif self.name == 'clear':
                path_finder.clear_cells()
            elif self.name == 'brute-force':
                if path_finder.end is not None and path_finder.start is not None:
                    path_finder.find_path(path_finder.brute_force)
            elif self.name == 'A-star':
                if path_finder.end is not None and path_finder.start is not None:
                    path_finder.find_path(path_finder.a_star)

        if self.gui.active_gui != self:
            self.color = self.default_color


class Mouse():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.held = False
        self.clicked = False

    def update(self):
        self.x, self.y = pygame.mouse.get_pos()
        inp = pygame.mouse.get_pressed()
        self.clicked = False
        if self.held == False and inp[0] == 1:
            self.clicked = True
        self.held = True if inp[0] == 1 else False


path_finder = PathFinder(size)
gui = GUI()
mouse = Mouse()
while True:
    screen.fill((0, 0, 0))

    # pygame.draw.rect(screen,(255,0,0),(0,0,screen_size[0],screen_size[1]),3)
    mouse.update()
    gui.update()
    path_finder.update()

    path_finder.draw()
    gui.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_i:
                print(path_finder.start)

    pygame.display.update()
