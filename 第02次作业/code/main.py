import pygame
import sys

pygame.init()

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 60
ROWS = 6
COLS = 8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")

clock = pygame.time.Clock()

BOARD_X = 160
BOARD_Y = 120

MOVE_DELAY = 100

font = pygame.font.Font(None, 40)
big_font = pygame.font.Font(None, 64)
small_font = pygame.font.Font(None, 26)

LEVELS = [
    [
        {"row": 2, "col": 1, "direction": "right"},
        {"row": 2, "col": 5, "direction": "up"},
        {"row": 4, "col": 3, "direction": "up"},
    ],

    [
        {"row": 1, "col": 1, "direction": "right"},
        {"row": 1, "col": 6, "direction": "up"},
        {"row": 4, "col": 1, "direction": "up"},
        {"row": 4, "col": 6, "direction": "left"},
    ],

    [
        {"row": 0, "col": 3, "direction": "down"},
        {"row": 3, "col": 3, "direction": "right"},
        {"row": 3, "col": 6, "direction": "down"},
        {"row": 5, "col": 1, "direction": "right"},
        {"row": 5, "col": 5, "direction": "up"},
    ],
]


# =========================
# 关卡可解性检测
# =========================

def next_pos(row, col, direction):
    if direction == "right":
        return row, col + 1

    if direction == "left":
        return row, col - 1

    if direction == "up":
        return row - 1, col

    if direction == "down":
        return row + 1, col

    return row, col


def arrow_can_leave(index, state):
    arrow = state[index]

    row = arrow["row"]
    col = arrow["col"]
    direction = arrow["direction"]

    occupied = {
        (a["row"], a["col"])
        for i, a in enumerate(state)
        if i != index
    }

    while True:
        row, col = next_pos(
            row,
            col,
            direction,
        )

        if not (
            0 <= row < ROWS
            and 0 <= col < COLS
        ):
            return True

        if (row, col) in occupied:
            return False


def level_is_solvable(level):
    memo = {}

    def dfs(state):
        key = tuple(
            sorted(
                (
                    a["row"],
                    a["col"],
                    a["direction"],
                )
                for a in state
            )
        )

        if key in memo:
            return memo[key]

        if not state:
            return True

        for i in range(len(state)):

            if arrow_can_leave(i, state):

                new_state = [
                    a.copy()
                    for j, a in enumerate(state)
                    if j != i
                ]

                if dfs(new_state):
                    memo[key] = True
                    return True

        memo[key] = False
        return False

    return dfs(
        [a.copy() for a in level]
    )


for i, level in enumerate(LEVELS, start=1):

    result = level_is_solvable(level)

    print(
        f"Level {i}: "
        f"{'SOLVABLE' if result else 'UNSOLVABLE'}"
    )


# =========================
# 游戏变量
# =========================

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_GAME_COMPLETE = "game_complete"
STATE_GAME_OVER = "game_over"
game_state = STATE_MENU

current_level = 0

arrows = []
flying_arrow = None

last_move_time = 0

message = ""
MAX_MISTAKES = 3
mistakes_left = MAX_MISTAKES

# =========================
# 按钮
# =========================

start_button = pygame.Rect(
    300,
    330,
    200,
    60,
)

next_button = pygame.Rect(
    300,
    350,
    200,
    60,
)

restart_button = pygame.Rect(
    300,
    430,
    200,
    50,
)


# =========================
# 游戏逻辑
# =========================

def load_level(level_index):
    global arrows
    global flying_arrow
    global message
    global mistakes_left

    arrows = [
        arrow.copy()
        for arrow in LEVELS[level_index]
    ]

    flying_arrow = None
    message = ""
    mistakes_left = MAX_MISTAKES

def get_next_position(
    row,
    col,
    direction,
):
    return next_pos(
        row,
        col,
        direction,
    )


def is_inside(row, col):
    return (
        0 <= row < ROWS
        and
        0 <= col < COLS
    )


def is_occupied(row, col):
    for arrow in arrows:

        if (
            arrow["row"] == row
            and
            arrow["col"] == col
        ):
            return True

    return False


def path_is_clear(arrow):
    row = arrow["row"]
    col = arrow["col"]

    direction = arrow["direction"]

    while True:

        row, col = get_next_position(
            row,
            col,
            direction,
        )

        if not is_inside(row, col):
            return True

        if is_occupied(row, col):
            return False


def get_arrow_rect(arrow):
    x = (
        BOARD_X
        + arrow["col"] * CELL_SIZE
    )

    y = (
        BOARD_Y
        + arrow["row"] * CELL_SIZE
    )

    return pygame.Rect(
        x,
        y,
        CELL_SIZE,
        CELL_SIZE,
    )


# =========================
# 绘图函数
# =========================

def draw_arrow(
    row,
    col,
    direction,
    highlighted=False,
):

    center_x = (
        BOARD_X
        + col * CELL_SIZE
        + CELL_SIZE // 2
    )

    center_y = (
        BOARD_Y
        + row * CELL_SIZE
        + CELL_SIZE // 2
    )

    if direction == "right":

        points = [
            (center_x + 20, center_y),
            (center_x - 10, center_y - 15),
            (center_x - 10, center_y + 15),
        ]

    elif direction == "left":

        points = [
            (center_x - 20, center_y),
            (center_x + 10, center_y - 15),
            (center_x + 10, center_y + 15),
        ]

    elif direction == "up":

        points = [
            (center_x, center_y - 20),
            (center_x - 15, center_y + 10),
            (center_x + 15, center_y + 10),
        ]

    else:

        points = [
            (center_x, center_y + 20),
            (center_x - 15, center_y - 10),
            (center_x + 15, center_y - 10),
        ]

    color = (
        (230, 140, 40)
        if highlighted
        else (50, 100, 220)
    )

    pygame.draw.polygon(
        screen,
        color,
        points,
    )

def draw_button(rect, text):
    mouse_pos = pygame.mouse.get_pos()

    if rect.collidepoint(mouse_pos):
        color = (50, 100, 200)
    else:
        color = (70, 120, 220)

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=10,
    )

    text_surface = small_font.render(
        text,
        True,
        (255, 255, 255),
    )

    screen.blit(
        text_surface,
        (
            rect.centerx - text_surface.get_width() // 2,
            rect.centery - text_surface.get_height() // 2,
        ),
    )


def draw_menu():

    screen.fill(
        (245, 245, 245)
    )

    title = big_font.render(
        "Arrow Game",
        True,
        (40, 40, 40),
    )

    screen.blit(
        title,
        (
            WIDTH // 2
            - title.get_width() // 2,
            170,
        ),
    )

    subtitle = small_font.render(
        "Click arrows and clear the board",
        True,
        (90, 90, 90),
    )

    screen.blit(
        subtitle,
        (
            WIDTH // 2
            - subtitle.get_width() // 2,
            250,
        ),
    )

    draw_button(
        start_button,
        "START",
    )


def draw_game():

    screen.fill(
        (245, 245, 245)
    )

    title = font.render(
        "Arrow Game",
        True,
        (40, 40, 40),
    )

    screen.blit(
        title,
        (
            WIDTH // 2
            - title.get_width() // 2,
            30,
        ),
    )

    level_text = small_font.render(
        f"Level {current_level + 1} / {len(LEVELS)}",
        True,
        (60, 60, 60),
    )
    
    chance_text = small_font.render(
        f"Chances: {mistakes_left}",
        True,
        (60, 60, 60),
    )
    remaining_text = small_font.render(
        f"Arrows: {len(arrows)}",
        True,
        (60, 60, 60),
    )

    screen.blit(
        remaining_text,
        (20, 50),
    )

    screen.blit(
        chance_text,
        (20, 20),
    )

    screen.blit(
        level_text,
        (
            WIDTH // 2
            - level_text.get_width() // 2,
            80,
        ),
    )

    for row in range(ROWS):

        for col in range(COLS):

            rect = pygame.Rect(
                BOARD_X
                + col * CELL_SIZE,

                BOARD_Y
                + row * CELL_SIZE,

                CELL_SIZE,
                CELL_SIZE,
            )

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                rect,
            )

            pygame.draw.rect(
                screen,
                (180, 180, 180),
                rect,
                1,
            )

    mouse_pos = pygame.mouse.get_pos()

    for arrow in arrows:
        rect = get_arrow_rect(arrow)

        highlighted = (
            rect.collidepoint(mouse_pos)
            and flying_arrow is None
        )

        draw_arrow(
            arrow["row"],
            arrow["col"],
            arrow["direction"],
            highlighted,
        )

    if flying_arrow is not None:

        draw_arrow(
            flying_arrow["row"],
            flying_arrow["col"],
            flying_arrow["direction"],
        )

    instruction = small_font.render(
        "Click arrow to shoot    Hover to select    R: Restart",
        True,
        (80, 80, 80),
    )

    screen.blit(
        instruction,
        (
            WIDTH // 2
            - instruction.get_width() // 2,
            520,
        ),
    )

    if message:

        message_text = small_font.render(
            message,
            True,
            (200, 60, 60),
        )

        screen.blit(
            message_text,
            (
                WIDTH // 2
                - message_text.get_width() // 2,
                480,
            ),
        )


def draw_level_complete():

    screen.fill(
        (245, 245, 245)
    )

    title = big_font.render(
        "LEVEL COMPLETE!",
        True,
        (50, 160, 80),
    )

    screen.blit(
        title,
        (
            WIDTH // 2
            - title.get_width() // 2,
            190,
        ),
    )

    level_text = font.render(
        f"Level {current_level + 1} cleared",
        True,
        (70, 70, 70),
    )

    screen.blit(
        level_text,
        (
            WIDTH // 2
            - level_text.get_width() // 2,
            280,
        ),
    )

    draw_button(
        next_button,
        "NEXT LEVEL",
    )


def draw_game_complete():

    screen.fill(
        (245, 245, 245)
    )

    title = big_font.render(
        "YOU WIN!",
        True,
        (50, 160, 80),
    )

    screen.blit(
        title,
        (
            WIDTH // 2
            - title.get_width() // 2,
            180,
        ),
    )

    subtitle = font.render(
        "All levels completed",
        True,
        (70, 70, 70),
    )

    screen.blit(
        subtitle,
        (
            WIDTH // 2
            - subtitle.get_width() // 2,
            270,
        ),
    )

    draw_button(
        restart_button,
        "PLAY AGAIN",
    )

def draw_game_over():

    screen.fill(
        (245, 245, 245)
    )

    title = big_font.render(
        "GAME OVER",
        True,
        (200, 60, 60),
    )

    screen.blit(
        title,
        (
            WIDTH // 2
            - title.get_width() // 2,
            180,
        ),
    )

    subtitle = font.render(
        f"Level {current_level + 1} failed",
        True,
        (70, 70, 70),
    )

    screen.blit(
        subtitle,
        (
            WIDTH // 2
            - subtitle.get_width() // 2,
            270,
        ),
    )

    draw_button(
        restart_button,
        "RETRY",
    )
# =========================
# 主循环
# =========================

running = True

while running:

    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # -------------------------
        # 开始菜单
        # -------------------------

        if game_state == STATE_MENU:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if start_button.collidepoint(
                    event.pos
                ):

                    current_level = 0

                    load_level(
                        current_level
                    )

                    game_state = STATE_PLAYING

        # -------------------------
        # 正在游戏
        # -------------------------

        elif game_state == STATE_PLAYING:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and flying_arrow is None
            ):

                clicked_index = None

                for i, arrow in enumerate(arrows):

                    rect = get_arrow_rect(
                        arrow
                    )

                    if rect.collidepoint(
                        event.pos
                    ):
                        clicked_index = i
                        break

                if clicked_index is not None:

                    selected_arrow = arrows[
                        clicked_index
                    ]

                    if path_is_clear(
                        selected_arrow
                    ):

                        flying_arrow = (
                            selected_arrow.copy()
                        )

                        arrows.pop(
                            clicked_index
                        )

                        last_move_time = (
                            current_time
                        )

                        message = ""

                    else:
                        mistakes_left -= 1

                        message = f"Blocked! Chances left: {mistakes_left}"

                        if mistakes_left <= 0:
                            game_state = STATE_GAME_OVER

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:

                    load_level(
                        current_level
                    )

        # -------------------------
        # 关卡完成
        # -------------------------

        elif game_state == STATE_LEVEL_COMPLETE:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if next_button.collidepoint(
                    event.pos
                ):

                    current_level += 1

                    load_level(
                        current_level
                    )

                    game_state = STATE_PLAYING

        # -------------------------
        # 全部通关
        # -------------------------

        elif game_state == STATE_GAME_COMPLETE:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if restart_button.collidepoint(
                    event.pos
                ):

                    current_level = 0

                    load_level(
                        current_level
                    )

                    game_state = STATE_PLAYING
        elif game_state == STATE_GAME_OVER:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if restart_button.collidepoint(
                    event.pos
                ):

                    load_level(
                        current_level
                    )

                    game_state = STATE_PLAYING
    # =========================
    # 飞行动画
    # =========================

    if (
        game_state == STATE_PLAYING
        and flying_arrow is not None
        and
        current_time - last_move_time
        >= MOVE_DELAY
    ):

        new_row, new_col = (
            get_next_position(
                flying_arrow["row"],
                flying_arrow["col"],
                flying_arrow["direction"],
            )
        )

        if not is_inside(
            new_row,
            new_col,
        ):

            flying_arrow = None

        else:

            flying_arrow["row"] = (
                new_row
            )

            flying_arrow["col"] = (
                new_col
            )

        last_move_time = current_time

    # =========================
    # 胜利判断
    # =========================

    if (
        game_state == STATE_PLAYING
        and len(arrows) == 0
        and flying_arrow is None
    ):

        if current_level < len(LEVELS) - 1:

            game_state = (
                STATE_LEVEL_COMPLETE
            )

        else:

            game_state = (
                STATE_GAME_COMPLETE
            )

    # =========================
    # 绘制
    # =========================

    if game_state == STATE_MENU:

        draw_menu()

    elif game_state == STATE_PLAYING:

        draw_game()

    elif game_state == STATE_LEVEL_COMPLETE:

        draw_level_complete()

    elif game_state == STATE_GAME_COMPLETE:

        draw_game_complete()
    elif game_state == STATE_GAME_OVER:
        draw_game_over()
    pygame.display.flip()

    clock.tick(60)


pygame.quit()
sys.exit()