import pygame
import random
import time

colors = [
    (0, 0, 0),
    (0, 240, 240),
    (0, 0, 240),
    (240, 160, 0),
    (240, 240, 0),
    (0, 240, 0),
    (160, 0, 240),
    (240, 0, 0)
]


class Figure:
    x = 0
    y = 0
    Figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 2, 5, 6]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[4, 5, 9, 10], [2, 6, 5, 9]]
    ]

    def __init__(self, x_coord, y_coord):
        self.x = x_coord
        self.y = y_coord
        self.type = random.randint(0, len(self.Figures) - 1)
        self.color = colors[self.type + 1]
        self.rotation = 0

    def image(self):
        return self.Figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.Figures[self.type])


class Tetris:
    height = 0
    width = 0
    field = []
    score = 0
    state = "start"
    Figure = None
    Shadow = None

    def __init__(self, _height, _width):
        self.new_best_lines = False
        self.new_best_score = False
        self.width = _width
        self.height = _height
        self.field = []
        self.score = 0
        self.broken_lines = 0
        self.state = "start"
        self.hold_Figure = None
        self.primary_Figure = None
        self.next_Figure = None
        for i in range(_height):
            new_line = []
            for j in range(_width):
                new_line.append(0)
            self.field.append(new_line)
        self.new_figure()

    def new_figure(self):
        if self.next_Figure is None:
            self.Figure = Figure(5, 0)
            self.Shadow = Figure(5, 0)
            self.next_Figure = Figure(5, 0)
        else:
            self.Figure = self.next_Figure
            self.Shadow = Figure(5, 0)
            self.next_Figure = Figure(5, 0)
        self.position_shadow()

    def position_shadow(self):
        grounded = False
        self.Shadow.x = self.Figure.x
        self.Shadow.y = self.Figure.y
        while not grounded:
            self.Shadow.y += 1
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.Figure.image():
                        if i + self.Shadow.y > self.height - 1 or \
                                i + self.Shadow.y < 0 or \
                                self.field[i + self.Shadow.y][j + self.Shadow.x] > 0:
                            grounded = True
                            self.Shadow.y -= 1

    def go_down(self):
        self.Figure.y += 1
        if self.intersects():
            self.Figure.y -= 1
            self.freeze()

    def side(self, dx):
        old_x = self.Figure.x
        edge = False
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in self.Figure.image():
                    if j + self.Figure.x + dx > self.width - 1 or \
                            j + self.Figure.x + dx < 0:
                        edge = True
        if not edge:
            self.Figure.x += dx
        if self.intersects():
            self.Figure.x = old_x
        self.position_shadow()

    def left(self):
        self.side(-1)

    def right(self):
        self.side(1)

    def down(self):
        while not self.intersects():
            self.Figure.y += 1
        self.Figure.y -= 1
        self.freeze()

    def rotate(self):
        old_rotation = self.Figure.rotation
        self.Figure.rotate()
        if self.intersects():
            self.Figure.rotation = old_rotation
        else:
            self.position_shadow()

    def hold(self):
        self.Figure.x = 5
        self.Figure.y = 0
        if self.hold_Figure is None:
            self.hold_Figure = self.Figure
            self.Figure = None
            self.new_figure()
        else:
            self.primary_Figure = self.Figure
            self.Figure = self.hold_Figure
            self.hold_Figure = self.primary_Figure
        self.position_shadow()

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in self.Figure.image():
                    try:
                        if i + self.Figure.y > self.height - 1 or \
                                i + self.Figure.y < 0 or \
                                self.field[i + self.Figure.y][j + self.Figure.x] > 0 or \
                                self.Figure.x + j < 0:
                            intersection = True
                    except IndexError:
                        intersection = True
        return intersection

    def freeze(self):
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in self.Figure.image():
                    self.field[i + self.Figure.y][j + self.Figure.x] = self.Figure.type + 1
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 5
                self.broken_lines += 1
                for i2 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i2][j] = self.field[i2 - 1][j]
        self.score += lines ** 2


pygame.init()
screen = pygame.display.set_mode((650, 670))
pygame.display.set_caption('Tetris')

BACKGROUND = (0, 0, 0)
FOREGROUND = (255, 255, 255)
GRAY = (128, 128, 128)

if 7 < time.localtime().tm_hour < 17:
    BACKGROUND = (255, 255, 255)
    FOREGROUND = (0, 0, 0)

done = False
fps = 45
frame = 0
clock = pygame.time.Clock()
counter = 0
zoom = 30

game = Tetris(20, 15)

while not done:
    frame += 1
    if game.state == "start" and frame == 30:
        frame = 0
        game.go_down()
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game.rotate()
            if event.key == pygame.K_DOWN:
                game.go_down()
            if event.key == pygame.K_t:
                if BACKGROUND == (0, 0, 0):
                    BACKGROUND = (255, 255, 255)
                    FOREGROUND = (0, 0, 0)
                else:
                    BACKGROUND = (0, 0, 0)
                    FOREGROUND = (255, 255, 255)
            if event.key == pygame.K_LEFT:
                game.left()
            if event.key == pygame.K_RIGHT:
                game.right()
            if event.key == pygame.K_c:
                game.hold()
            if event.key == pygame.K_SPACE and game.state == "gameover":
                game.Figure = None
                game.Shadow = None
                game.field = []
                game.__init__(20, 15)
                game.broken_lines = 0
                game.score = 0
                frame = 0
                screen.fill(color=BACKGROUND)
                game.new_figure()
                game.state = "start"
            elif event.key == pygame.K_SPACE:
                game.down()
        if event.type == pygame.QUIT:
            done = True

    screen.fill(color=BACKGROUND)
    for i in range(game.height):
        for j in range(game.width):
            if game.field[i][j] == 0:
                color = GRAY
                just_border = 1
            else:
                color = colors[game.field[i][j]]
                just_border = 0
            pygame.draw.rect(screen, color, [38 + j * zoom, 50 + i * zoom, zoom, zoom], just_border)
    if game.Figure is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.Figure.image():
                    pygame.draw.rect(screen, GRAY, [38 + (j + game.Shadow.x) * zoom, 50 + (i + game.Shadow.y) * zoom,
                                                    zoom, zoom])
                    pygame.draw.rect(screen, game.Figure.color,
                                     [38 + (j + game.Figure.x) * zoom, 50 + (i + game.Figure.y) * zoom, zoom, zoom])
                if game.hold_Figure is not None:
                    if p in game.hold_Figure.image():
                        pygame.draw.rect(screen, game.hold_Figure.color, [410 + (j + game.hold_Figure.x) * zoom,
                                                                          550 + (i + game.hold_Figure.y) * zoom, zoom,
                                                                          zoom])
                if game.next_Figure is not None:
                    if p in game.next_Figure.image():
                        pygame.draw.rect(screen, game.next_Figure.color, [350 + (j + game.next_Figure.x) * zoom,
                                                                          200 + (i + game.next_Figure.y) * zoom, zoom,
                                                                          zoom])

    gameover_font = pygame.font.SysFont('Calibri', 55, True, False)
    text_gameover = gameover_font.render("Game Over!", True, (255, 0, 0))
    text_message = gameover_font.render("Press Space to Restart", True, (255, 0, 0))
    standard_font = pygame.font.SysFont('Arial', 55)
    little_font = pygame.font.SysFont('Arial', 35)
    next_Figure_text = little_font.render('Next Shape:', True, FOREGROUND)
    holding_text = little_font.render('Holding', True, FOREGROUND)
    Figure_text = little_font.render('Shape:', True, FOREGROUND)
    text_best_score = standard_font.render('New Highscore for best score!', True, (0, 255, 0))
    text_best_lines = standard_font.render('New Highscore for most lines!', True, (0, 255, 0))
    screen.blit(next_Figure_text, [490, 100])
    if game.hold_Figure is not None:
        screen.blit(holding_text, [510, 450])
        screen.blit(Figure_text, [510, 500])
    if game.state == "gameover":
        best_scores_file = open("Data File.txt", 'r')
        scores_with_new_lines = best_scores_file.readlines()
        best_score = scores_with_new_lines[0].split('\n')
        best_lines = scores_with_new_lines[1].split('\n')
        if game.score > int(best_score[0]):
            best_scores_file.close()
            game.new_best_score = True
            write_file = open("Data File.txt", 'w')
            write_file.writelines(str(game.score) + "\n" + str(best_lines[0]))
            write_file.close()
        if game.broken_lines > int(best_lines[0]):
            best_scores_file.close()
            game.new_best_lines = True
            write_file = open("Data File.txt", 'w')
            write_file.writelines(str(best_score[0]) + "\n" + str(game.broken_lines))
            write_file.close()
        if not best_scores_file.closed:
            best_scores_file.close()
        if game.new_best_score:
            screen.blit(text_best_score, [25, 400])
        if game.new_best_lines:
            screen.blit(text_best_lines, [25, 500])
        screen.blit(text_gameover, [25, 250])
        screen.blit(text_message, [25, 350])
    score_font = pygame.font.SysFont('Calibri', 50, True, False)
    text_score = score_font.render("Score: " + str(game.score), True, FOREGROUND)
    text_lines = score_font.render("Lines: " + str(game.broken_lines), True, FOREGROUND)
    screen.blit(text_score, [20, 0])
    screen.blit(text_lines, [screen.get_width() - 200, 0])
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()
