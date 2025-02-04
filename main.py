import random, collections, time, sys, copy
import pygame as pg
from numba.core.cgutils import printf
from qtconsole.mainwindow import background
from sympy.codegen.ast import break_

from BFS import bfs
import json
import os
from PIL import Image, ImageDraw, ImageFont

pg.init()
pg.font.init()
pg.mixer.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60
Time = pg.time.Clock()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

difficulty = None  # Khởi tạo biến độ khó ban đầu

LIST_BACKGROUND = [
    pg.transform.scale(pg.image.load("assets/images/background/" + str(i) + ".jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT)) for
    i in range(10)]


BOARD_ROW = 9  # 7
BOARD_COLUMN = 14  # 12
NUM_TILE_ON_BOARD = 21
NUM_SAME_TILE = 4
button_font = pg.font.Font(None, 40)
easy_button = pg.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60, 200, 50)
medium_button = pg.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
hard_button = pg.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 50)
TILE_WIDTH = 50
TILE_HEIGHT = 55
MARGIN_X = (SCREEN_WIDTH - TILE_WIDTH * BOARD_COLUMN) // 2
MARGIN_Y = (SCREEN_HEIGHT - TILE_HEIGHT * BOARD_ROW) // 2 + 15
NUM_TILE = 33
LIST_TILE = [0] * (NUM_TILE + 1)
for i in range(1, NUM_TILE + 1): LIST_TILE[i] = pg.transform.scale(
    pg.image.load("assets/images/tiles/section" + str(i) + ".png"), (TILE_WIDTH, TILE_HEIGHT))

GAME_TIME = 180
HINT_TIME = 20

# time bar
TIME_BAR_WIDTH = 500
TIME_BAR_HEIGHT = 30
TIME_BAR_POS = ((SCREEN_WIDTH - TIME_BAR_WIDTH) // 2, (MARGIN_Y - TIME_BAR_HEIGHT) // 2)
TIME_ICON = pg.transform.scale(pg.image.load("assets/images/tiles/section1.png"), (TILE_WIDTH, TILE_HEIGHT))

MAX_LEVEL = 5

LIVES_IMAGE = pg.transform.scale(pg.image.load("assets/images/heart.png"), (50, 50))

FONT_COMICSANSMS = pg.font.SysFont('dejavusans', 40)
FONT_TUROK = pg.font.SysFont('timesnewroman', 60)
FONT_PIKACHU = pg.font.Font("assets/font/pikachu.otf", 50)
FONT_ARIAL = pg.font.Font('assets/font/Folty-Bold.ttf', 50)

# start screen
START_SCREEN_BACKGOUND = pg.transform.scale(pg.image.load("assets/images/background/b1g.jpg"),
                                            (SCREEN_WIDTH, SCREEN_HEIGHT))
LOGIN_BACKGROUND = pg.transform.scale(pg.image.load("assets/images/background/login_background.png"),
                                      (SCREEN_WIDTH, SCREEN_HEIGHT))
LIST_LEVEL = [pg.transform.scale(pg.image.load("assets/images/level/" + str(i) + ".png"), (50, 50)) for i in
              range(1, 10)]

# assets button
LOGO_IMAGE = pg.transform.scale(pg.image.load("assets/images/logo/logo_home.png"), (600, 200))
# PLAY_IMAGE = pg.transform.scale(pg.image.load("assets/images/button/play.png"), (144, 48))
PLAY_IMAGE = pg.image.load("assets/images/button/play.png")

SOUND_IMAGE = pg.transform.scale(pg.image.load("assets/images/button/sound.png"), (50, 50))
INFO_IMAGE = pg.transform.scale(pg.image.load("assets/images/button/info.png"), (50, 50))
EXIT_IMAGE = pg.transform.scale(pg.image.load("assets/images/button/close.png"), (60, 60))
PAUSE_PANEL_IMAGE = pg.transform.scale(pg.image.load("assets/images/button/panel_pause.png"), (300, 200))
REPLAY_BUTTON = pg.image.load("assets/images/button/replay.png")
HOME_BUTTON = pg.image.load("assets/images/button/exit.png").convert_alpha()
PAUSE_BUTTON = pg.transform.scale(pg.image.load("assets/images/button/pause.png").convert_alpha(), (50, 50))
##
HINT_BUTTON = pg.transform.scale(pg.image.load("assets/images/button/hint.png").convert_alpha(), (60, 60))
##
CONTINUE_BUTTON = pg.image.load("assets/images/button/continue.png").convert_alpha()
GAMEOVER_BACKGROUND = pg.image.load("assets/images/button/gameover.png").convert_alpha()
WIN_BACKGROUND = pg.image.load("assets/images/button/win1.png").convert_alpha()
INSTRUCTION_PANEL = pg.transform.scale(pg.image.load("assets/images/button/instruction.png"),
                                       (700, 469)).convert_alpha()
TIME_END = 6
show_instruction = False
show_leaderboard = False
running_draw_leaderboard = False
# Đường dẫn đến tệp JSON
USER_DATA_FILE = "users.json"

# load background music
pg.mixer.music.load("assets/music/background1.mp3")
pg.mixer.music.set_volume(0.1)
pg.mixer.music.play(-1, 0.0, 5000)
sound_on = True

# load sound
click_sound = pg.mixer.Sound("assets/sound/click_sound.mp3")
click_sound.set_volume(0.2)
success_sound = pg.mixer.Sound("assets/sound/success.mp3")
success_sound.set_volume(0.2)
fail_sound = pg.mixer.Sound("assets/sound/fail.mp3")
fail_sound.set_volume(0.2)
win_sound = pg.mixer.Sound("assets/sound/win.mp3")
win_sound.set_volume(0.2)
game_over_sound = pg.mixer.Sound("assets/sound/gameover.wav")
game_over_sound.set_volume(0.2)


def main():
    username = login_screen()
    # init pygame and module
    global level, lives, running_draw_leaderboard
    while True:
        level = 1
        lives = 3
        start_screen()
        if not running_draw_leaderboard  and show_leaderboard:
            start_screen()
        while level <= MAX_LEVEL:
            random.shuffle(LIST_BACKGROUND)
            playing(username)
            level += 1
            pg.time.wait(300)
            pg.mixer.music.play()
    # end


def login_screen():
    username = ""
    password = ""
    input_active = None  # None, 'username', or 'password'

    # Calculate positions for centering
    screen_width = SCREEN_WIDTH
    screen_height = SCREEN_HEIGHT

    username_rect = pg.Rect((screen_width - 400) // 2, (screen_height - 250) // 2, 400, 50)
    password_rect = pg.Rect((screen_width - 400) // 2, (screen_height - 100) // 2, 400, 50)
    login_button_rect = pg.Rect((screen_width - 200) // 2, (screen_height - 100) // 2 + 90, 200, 50)
    register_button_rect = pg.Rect((screen_width - 200) // 2, (screen_height - 100) // 2 + 160, 200, 50)

    font = pg.font.Font(None, 36)
    active_color = pg.Color('dodgerblue2')
    inactive_color = pg.Color('gray15')

    while True:
        Time.tick(FPS)
        screen.fill((30, 30, 30))  # Background color
        screen.blit(LOGIN_BACKGROUND, (0, 0))  # Draw the background image

        # Fill input boxes with white
        pg.draw.rect(screen, pg.Color('white'), username_rect)  # White fill for username box
        pg.draw.rect(screen, pg.Color('white'), password_rect)  # White fill for password box

        # Draw login and register buttons
        pg.draw.rect(screen, pg.Color('green'), login_button_rect)
        login_text = font.render("Login", True, pg.Color('white'))
        screen.blit(login_text, login_button_rect.move(50, 10))

        pg.draw.rect(screen, pg.Color('blue'), register_button_rect)
        register_text = font.render("Register", True, pg.Color('white'))
        screen.blit(register_text, register_button_rect.move(35, 10))

        # Render username and password text in black
        username_text = font.render(username, True, pg.Color('black'))
        password_text = font.render('*' * len(password), True, pg.Color('black'))  # Mask password
        screen.blit(username_text, (username_rect.x + 10, username_rect.y + 10))
        screen.blit(password_text, (password_rect.x + 10, password_rect.y + 10))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if username_rect.collidepoint(event.pos):
                    input_active = 'username'
                elif password_rect.collidepoint(event.pos):
                    input_active = 'password'
                elif login_button_rect.collidepoint(event.pos):
                    if validate_user(username, password):  # Kiểm tra thông tin đăng nhập
                        print(f"Login successful for user: {username}")
                        return username  # Trả về username khi đăng nhập thành công
                    else:
                        print("Invalid username or password")
                elif register_button_rect.collidepoint(event.pos):
                    if username and password:
                        save_user(username, password)  # Lưu thông tin người dùng
                        print(f"User {username} registered successfully")
                    else:
                        print("Please enter a username and password to register.")
            if event.type == pg.KEYDOWN:
                if input_active == 'username':
                    if event.key == pg.K_BACKSPACE:
                        username = username[:-1]
                    else:
                        username += event.unicode
                elif input_active == 'password':
                    if event.key == pg.K_BACKSPACE:
                        password = password[:-1]
                    else:
                        password += event.unicode

        pg.display.flip()


def start_screen():
    global sound_on, music_on, show_instruction, show_leaderboard, running_draw_leaderboard

    rank_button = pg.image.load("assets/images/button/rank button.png")
    rank_button = pg.transform.scale(rank_button, (100, 100))  # Thay đổi kích thước nếu cần
    rank_rect = rank_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200))  # Đặt vị trí nút

    while True:
        Time.tick(FPS)
        screen.blit(START_SCREEN_BACKGOUND, (0, 0))

        # Render logo
        image_width, image_height = LOGO_IMAGE.get_size()
        screen.blit(LOGO_IMAGE, ((SCREEN_WIDTH - image_width) // 2 - 20, (SCREEN_HEIGHT - image_height) // 2 - 150))
        mouse_x, mouse_y = pg.mouse.get_pos()

        # Blit play button
        image_width, image_height = PLAY_IMAGE.get_size()
        play_rect = pg.Rect((SCREEN_WIDTH - image_width) // 2, (SCREEN_HEIGHT - image_height) // 2 + 100, image_width,
                            image_height)
        screen.blit(PLAY_IMAGE, play_rect)

        # Blit rank button
        screen.blit(rank_button, rank_rect)

        # Other buttons (sound, info, exit)
        image_width, image_height = SOUND_IMAGE.get_size()
        sound_rect = pg.Rect(15, SCREEN_HEIGHT - 15 - image_height, image_width, image_height)
        if sound_on:
            screen.blit(SOUND_IMAGE, sound_rect)
        else:
            draw_dark_image(SOUND_IMAGE, sound_rect, (120, 120, 120))

        image_width, image_height = INFO_IMAGE.get_size()
        info_rect = pg.Rect(SCREEN_WIDTH - 15 - image_width, SCREEN_HEIGHT - 15 - image_height, image_width,
                            image_height)
        screen.blit(INFO_IMAGE, info_rect)

        image_width, image_height = EXIT_IMAGE.get_size()
        exit_rect = pg.Rect(SCREEN_WIDTH - 220, 105, image_width, image_height)

        if show_instruction:
            show_dim_screen()
            draw_instruction()
            screen.blit(EXIT_IMAGE, exit_rect)

        # Highlight buttons on hover
        if play_rect.collidepoint(mouse_x, mouse_y) and not show_instruction:
            draw_dark_image(PLAY_IMAGE, play_rect, (60, 60, 60))

        if rank_rect.collidepoint(mouse_x, mouse_y):
            draw_dark_image(rank_button, rank_rect, (60, 60, 60))  # Làm tối nút rank khi hover


        for event in pg.event.get():

            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                show_leaderboard = False
                if play_rect.collidepoint((mouse_x, mouse_y)) and not show_instruction and not show_leaderboard:
                    show_leaderboard = False
                    click_sound.play()
                    draw_dark_image(PLAY_IMAGE, play_rect, (120, 120, 120))
                    pg.display.flip()
                    pg.time.wait(200)
                    return

                elif rank_rect.collidepoint(mouse_x, mouse_y):
                    click_sound.play()
                    show_leaderboard = True
                    while show_leaderboard:
                        Time.tick(FPS)
                        screen.blit(START_SCREEN_BACKGOUND, (0, 0))

                        draw_leaderboard()

                        back_button = pg.image.load("assets/images/button/exit.png")
                        back_button = pg.transform.scale(back_button, (100, 50))
                        back_rect = back_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 300))
                        screen.blit(back_button, back_rect)
                        if running_draw_leaderboard == False:
                            return

                        pg.display.flip()
                if sound_rect.collidepoint(mouse_x, mouse_y):
                    sound_on = not sound_on
                    volume = 0.2 if sound_on else 0
                    pg.mixer.music.set_volume(volume)
                    success_sound.set_volume(volume)
                    fail_sound.set_volume(volume)
                    click_sound.set_volume(volume)

                if info_rect.collidepoint(mouse_x, mouse_y):
                    show_instruction = True
                    click_sound.play()
                if exit_rect.collidepoint(mouse_x, mouse_y):
                    show_instruction = False
                    click_sound.play()

        pg.display.flip()


def playing(username):
    global difficulty

    # Chỉ chọn độ khó nếu chưa có (tức là khi mới khởi động trò chơi lần đầu)
    if difficulty is None:
        difficulty = choose_difficulty()  # Chọn độ khó lần đầu tiên

    set_board_size(difficulty)  # Thiết lập kích thước bảng theo độ khó đã chọn
    global level, lives, paused, time_start_paused, last_time_get_point, time_paused, hinted, hint_shown
    hinted = False
    hint_shown = False
    paused = False
    time_start_paused = 0
    time_paused = 0

    background = LIST_BACKGROUND[0]  # get random background
    board = get_random_board()  # get random board of game

    mouse_x, mouse_y = 0, 0
    clicked_tiles = []  # store index cards clicked
    hint = get_hint(board)

    last_time_get_point = time.time()
    start_time = time.time()
    bouns_time = 0

    while True:
        Time.tick(FPS)

        screen.blit(background, (0, 0))  # set background
        dim_screen = pg.Surface(screen.get_size(), pg.SRCALPHA)
        pg.draw.rect(dim_screen, (0, 0, 0, 150), dim_screen.get_rect())
        screen.blit(dim_screen, (0, 0))
        draw_board(board)  # Đảm bảo hàm draw_board sử dụng BOARD_ROW và BOARD_COLUMN
        draw_lives(lives, level)
        draw_time_bar(start_time, bouns_time)
        draw_clicked_tiles(board, clicked_tiles)

        mouse_clicked = False

        if lives == 0:
            update_user_level(username, level)
            show_dim_screen()
            level = MAX_LEVEL + 1
            game_over_sound.play()
            pg.mixer.music.pause()
            start_end = time.time()
            while time.time() - start_end <= TIME_END:
                screen.blit(GAMEOVER_BACKGROUND, (0, 0))
                pg.display.flip()
            difficulty = None
            return

        # check event
        for event in pg.event.get():
            if event.type == pg.QUIT: pg.quit(), sys.exit()
            if event.type == pg.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                mouse_clicked = True
            if event.type == pg.KEYUP:
                if event.key == pg.K_k:  # use key k to hack game
                    tile1_i, tile1_j = hint[0][0], hint[0][1]
                    tile2_i, tile2_j = hint[1][0], hint[1][1]
                    board[tile1_i][tile1_j] = 0
                    board[tile2_i][tile2_j] = 0
                    bouns_time += 1
                    update_difficulty(board, level, tile1_i, tile1_j, tile2_i, tile2_j)
                    update_user_level(username, level)
                    if is_level_complete(board): return

                    if not (board[tile1_i][tile1_j] != 0 and bfs(board, tile1_i, tile1_j, tile2_i, tile2_j)):
                        hint = get_hint(board)
                        while not hint:
                            pg.time.wait(100)
                            reset_board(board)
                            hint = get_hint(board)

        draw_pause_button(mouse_x, mouse_y, mouse_clicked)
        draw_hint_button(mouse_x, mouse_y, mouse_clicked)

        is_time_up = check_time(start_time, bouns_time)  # 0 if game over, 1 if lives -= 1, 2 if nothing
        if paused:
            show_dim_screen()
            if is_time_up == 0:  # game over
                lives -= 1
            elif is_time_up == 1:
                lives -= 1
                level -= 1
                difficulty = None
                return

            select = panel_pause(mouse_x, mouse_y,
                                 mouse_clicked)  # 0 if click replay, 1 if click home, 2 if continue, 3 if nothing
            if select == 0:
                lives -= 1
                if lives > 0:
                    level -= 1
                    return
            elif select == 1:
                level = MAX_LEVEL + 1
                difficulty = None
                return
            elif select == 2:
                mouse_clicked = False  # continue

        # check time get hint
        if time.time() - last_time_get_point - time_paused > HINT_TIME and not paused: draw_hint(hint)
        # click button to get hint
        if hinted and not paused and hint_shown == True:
            draw_hint(hint)
        # update
        try:
            tile_i, tile_j = get_index_at_mouse(mouse_x, mouse_y)
            if board[tile_i][tile_j] != 0 and not paused:
                draw_border_tile(board, tile_i, tile_j)
                if mouse_clicked:
                    mouse_clicked = False
                    clicked_tiles.append((tile_i, tile_j))
                    draw_clicked_tiles(board, clicked_tiles)
                    if len(clicked_tiles) > 1:  # 2 cards was clicked
                        path = bfs(board, clicked_tiles[0][0], clicked_tiles[0][1], tile_i, tile_j)
                        if path:
                            # delete the same card
                            board[clicked_tiles[0][0]][clicked_tiles[0][1]] = 0
                            board[tile_i][tile_j] = 0
                            success_sound.play(maxtime=1500)
                            draw_path(path)
                            hint_shown = False

                            bouns_time += 1
                            last_time_get_point = time.time()  # count time hint
                            # if level > 1, upgrade difficulty by moving cards
                            update_difficulty(board, level, clicked_tiles[0][0], clicked_tiles[0][1], tile_i, tile_j)
                            if is_level_complete(board):
                                print(level)
                                update_user_level(username, level)
                                if level == 5:
                                    pg.mixer.music.pause()
                                    fade_speed = 2
                                    alpha = 0
                                    time_win = 10
                                    tmp = time.time()
                                    win_sound.play(maxtime=10000)
                                    show_dim_screen()
                                    while time.time() - tmp < 10:
                                        alpha += fade_speed
                                        if alpha > 255: alpha = 255
                                        tmp_image = WIN_BACKGROUND.copy()
                                        tmp_image.set_alpha(alpha)
                                        screen.blit(tmp_image, (180, 70))
                                        pg.display.flip()
                                return
                            # if hint got by player
                            if not (board[hint[0][0]][hint[0][1]] != 0 and bfs(board, hint[0][0], hint[0][1],
                                                                               hint[1][0], hint[1][1])):
                                hint = get_hint(board)
                                while not hint:
                                    pg.time.wait(100)
                                    reset_board(board)
                                    hint = get_hint(board)
                        else:
                            if not (clicked_tiles[0][0] == clicked_tiles[1][0] and clicked_tiles[0][1] ==
                                    clicked_tiles[1][1]):
                                fail_sound.play(maxtime=500)

                        # reset
                        clicked_tiles = []
        except:
            pass
        pg.display.flip()


# Hàm lưu thông tin vào tệp JSON
def save_user(username, password, level=0):
    users = load_users()  # Tải dữ liệu hiện có
    if username not in users:
        users[username] = {"password": password, "level": level}  # Thêm người dùng mới
    else:
        # Nếu người dùng đã tồn tại, chỉ cập nhật mật khẩu hoặc giữ nguyên
        users[username]["password"] = password
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)  # Ghi dữ liệu vào tệp JSON # Ghi dữ liệu vào tệp JSON


# Hàm tải thông tin từ tệp JSON
def load_users():
    if not os.path.exists(USER_DATA_FILE):  # Nếu tệp chưa tồn tại
        return {}
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)  # Tải dữ liệu từ tệp JSON


# Hàm kiểm tra thông tin đăng nhập
def validate_user(username, password):
    users = load_users()
    return username in users and users[username]["password"] == password


def update_user_level(username, level):
    users = load_users()
    if username in users:
        # Cập nhật level nếu level mới cao hơn level hiện tại
        users[username]["level"] = max(users[username]["level"], level)
        with open(USER_DATA_FILE, "w") as f:
            json.dump(users, f, indent=4)


def get_leaderboard():
    users = load_users()
    # Lấy danh sách người chơi với username và level
    leaderboard = [{"username": username, "level": data["level"]} for username, data in users.items()]
    # Sắp xếp theo level giảm dần
    return sorted(leaderboard, key=lambda x: x["level"], reverse=True)


def draw_difficult_buttons():
    # Vẽ nút "Easy"
    pg.draw.rect(screen, (127, 255, 0), easy_button)
    text = button_font.render("Easy", True, (0, 0, 0))
    screen.blit(text, (easy_button.x + 60, easy_button.y + 10))

    # Vẽ nút "Medium"
    pg.draw.rect(screen, (255, 255, 0), medium_button)
    text = button_font.render("Medium", True, (0, 0, 0))
    screen.blit(text, (medium_button.x + 40, medium_button.y + 10))

    # Vẽ nút "Hard"
    pg.draw.rect(screen, (255, 0, 0), hard_button)
    text = button_font.render("Hard", True, (0, 0, 0))
    screen.blit(text, (hard_button.x + 60, hard_button.y + 10))


def set_board_size(difficulty):
    global BOARD_ROW, BOARD_COLUMN, NUM_TILE_ON_BOARD, NUM_SAME_TILE, MARGIN_Y, MARGIN_X
    # Thiết lập kích thước bảng theo độ khó
    if difficulty == "easy":
        BOARD_ROW, BOARD_COLUMN = 7, 12
        NUM_TILE_ON_BOARD = 25  # Hoặc điều chỉnh sao cho phù hợp
        NUM_SAME_TILE = 2
    elif difficulty == "medium":
        BOARD_ROW, BOARD_COLUMN = 9, 14
        NUM_TILE_ON_BOARD = 21
        NUM_SAME_TILE = 4
    elif difficulty == "hard":
        BOARD_ROW, BOARD_COLUMN = 11, 16
        NUM_TILE_ON_BOARD = 21
        NUM_SAME_TILE = 6

    MARGIN_X = (SCREEN_WIDTH - TILE_WIDTH * BOARD_COLUMN) // 2
    MARGIN_Y = (SCREEN_HEIGHT - TILE_HEIGHT * BOARD_ROW) // 2 + 15

    # In ra thông tin kích thước bảng
    print(f"Set board size for {difficulty}:")
    print(f"BOARD_ROW: {BOARD_ROW}, BOARD_COLUMN: {BOARD_COLUMN}, NUM_TILE_ON_BOARD: {NUM_TILE_ON_BOARD}")

def choose_difficulty():
    global difficulty  # Đảm bảo biến difficulty được sử dụng đúng

    # Hiển thị giao diện chọn độ khó
    background = pg.image.load("assets/images/background/choose_size_background.png")
    background = pg.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Thay đổi kích thước nếu cần

    running = True
    while running:
        screen.blit(background, (0, 0))  # Vẽ nền
        draw_difficult_buttons()  # Vẽ các nút chọn độ khó

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if easy_button.collidepoint(mouse_x, mouse_y):
                    print("Chọn mức độ Easy")
                    running = False
                    difficulty = "easy"  # Lưu lựa chọn độ khó
                elif medium_button.collidepoint(mouse_x, mouse_y):
                    print("Chọn mức độ Medium")
                    running = False
                    difficulty = "medium"
                elif hard_button.collidepoint(mouse_x, mouse_y):
                    print("Chọn mức độ Hard")
                    running = False
                    difficulty = "hard"

        pg.display.flip()

    return difficulty


def draw_board_size():
    # Vẽ thông tin kích thước bảng lên màn hình
    font = pg.font.Font(None, 36)
      # Thay đổi kích thước nếu cần
    text = font.render(f"Rows: {BOARD_ROW}, Columns: {BOARD_COLUMN}, Tiles: {NUM_TILE_ON_BOARD}", True, (255, 255, 255))
    screen.blit(text, (20, 20))  # Vẽ lên góc trái màn hình

def set_and_draw_board_size(difficulty):
    set_board_size(difficulty)  # Thiết lập kích thước bảng
    draw_board_size()           # Vẽ thông tin kích thước bảng lên màn hình

def get_random_board():
    list_index_tiles = list(range(1, NUM_TILE_ON_BOARD + 1))  # Điều chỉnh số lượng ô theo `NUM_TILE_ON_BOARD`
    random.shuffle(list_index_tiles)
    list_index_tiles = list_index_tiles * NUM_SAME_TILE  # Điều chỉnh số lần xuất hiện của mỗi ô
    random.shuffle(list_index_tiles)
    board = [[0 for _ in range(BOARD_COLUMN)] for _ in range(BOARD_ROW)]  # Sử dụng BOARD_ROW và BOARD_COLUMN
    k = 0
    for i in range(1, BOARD_ROW - 1):
        for j in range(1, BOARD_COLUMN - 1):
            board[i][j] = list_index_tiles[k]
            k += 1
    return board

def get_left_top_coords(i, j):  # get left top coords of card from index i, j
    x = j * TILE_WIDTH + MARGIN_X
    y = i * TILE_HEIGHT + MARGIN_Y
    return x, y


def get_center_coords(i, j):  # get center coords of card from index i, j
    x, y = get_left_top_coords(i, j)
    return x + TILE_WIDTH // 2, y + TILE_HEIGHT // 2


def get_index_at_mouse(x, y):  # get index of card at mouse clicked from coords x, y
    if x < MARGIN_X or y < MARGIN_Y: return None, None
    return (y - MARGIN_Y) // TILE_HEIGHT, (x - MARGIN_X) // TILE_WIDTH


def draw_board(board):
    for i in range(1, BOARD_ROW - 1):
        for j in range(1, BOARD_COLUMN - 1):
            if board[i][j] != 0:
                screen.blit(LIST_TILE[board[i][j]], get_left_top_coords(i, j))


def draw_dark_image(image, image_rect, color):
    dark_image = image.copy()
    dark_image.fill(color, special_flags=pg.BLEND_RGB_SUB)
    screen.blit(dark_image, image_rect)


def draw_clicked_tiles(board, clicked_tiles):
    for i, j in clicked_tiles:
        x, y = get_left_top_coords(i, j)
        try:
            darkImage = LIST_TILE[board[i][j]].copy()
            darkImage.fill((60, 60, 60), special_flags=pg.BLEND_RGB_SUB)
            screen.blit(darkImage, (x, y))
        except:
            pass


def draw_border_tile(board, i, j):
    x, y = get_left_top_coords(i, j)
    pg.draw.rect(screen, (0, 0, 255), (x - 1, y - 3, TILE_WIDTH + 4, TILE_HEIGHT + 4), 2)


def draw_path(path):
    for i in range(len(path) - 1):
        start_pos = (get_center_coords(path[i][0], path[i][1]))
        end_pos = (get_center_coords(path[i + 1][0], path[i + 1][1]))
        pg.draw.line(screen, 'red', start_pos, end_pos, 4)
        pg.display.update()
    pg.time.wait(400)


def get_hint(board):
    hint = []  # stories two tuple
    tiles_location = collections.defaultdict(list)
    for i in range(BOARD_ROW):
        for j in range(BOARD_COLUMN):
            if board[i][j]:
                tiles_location[board[i][j]].append((i, j))
    for i in range(BOARD_ROW):
        for j in range(BOARD_COLUMN):
            if board[i][j]:
                for o in tiles_location[board[i][j]]:
                    if o != (i, j) and bfs(board, i, j, o[0], o[1]):
                        hint.append((i, j))
                        hint.append(o)
                        return hint
    return []


def draw_hint(hint):
    for i, j in hint:
        x, y = get_left_top_coords(i, j)
        pg.draw.rect(screen, (0, 255, 0), (x - +1, y - 2, TILE_WIDTH + 4, TILE_HEIGHT + 4), 2)


def draw_hint_button(mouse_x, mouse_y, mouse_clicked):
    global hinted, hint_shown
    # Define button's position and size
    hint_button_rect = pg.Rect(0, 0, *HINT_BUTTON.get_size())
    hint_button_rect.center = (SCREEN_WIDTH - 780, 35)
    screen.blit(HINT_BUTTON, hint_button_rect)
    if hint_button_rect.collidepoint(mouse_x, mouse_y):
        if not hinted: draw_dark_image(HINT_BUTTON, hint_button_rect, (60, 60, 60))
        if mouse_clicked:
            mouse_clicked = False
            hinted = True
            hint_shown = True
            click_sound.play()


def draw_time_bar(start_time, bouns_time):
    global time_start_paused, time_paused
    pg.draw.rect(screen, (255, 255, 255, 5), (TIME_BAR_POS[0], TIME_BAR_POS[1], TIME_BAR_WIDTH, TIME_BAR_HEIGHT), 2,
                 border_radius=20)
    timeOut = 1 - (
                time.time() - start_time - bouns_time - time_paused) / GAME_TIME  # ratio between remaining time and total time
    if paused:
        if not time_start_paused: time_start_paused = time.time()
        timeOut = 1 - (time_start_paused - start_time - bouns_time - time_paused) / GAME_TIME
    else:
        if time_start_paused:
            time_paused += time.time() - time_start_paused
            timeOut = 1 - (time.time() - start_time - bouns_time - time_paused) / GAME_TIME
        time_start_paused = 0

    innerPos = (TIME_BAR_POS[0] + 2, TIME_BAR_POS[1] + 2)
    innerSize = (TIME_BAR_WIDTH * timeOut - 4, TIME_BAR_HEIGHT - 4)
    pg.draw.rect(screen, 'green', (innerPos, innerSize), border_radius=20)


def is_level_complete(board):
    global level, username
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] != 0:
                return False
    return True


def update_difficulty(board, level, tile1_i, tile1_j, tile2_i, tile2_j):
    if level == 2:  # all card move up
        for j in (tile1_j, tile2_j):
            new_column = [0]
            for i in range(BOARD_ROW):
                if board[i][j] != 0:
                    new_column.append(board[i][j])
            while (len(new_column) < BOARD_ROW): new_column.append(0)
            for k in range(BOARD_ROW):
                board[k][j] = new_column[k]
    if level == 3:  # all card move down
        for j in (tile1_j, tile2_j):
            new_column = []
            for i in range(BOARD_ROW):
                if board[i][j] != 0:
                    new_column.append(board[i][j])
            while (len(new_column) < BOARD_ROW - 1): new_column = [0] + new_column
            new_column.append(0)
            for k in range(BOARD_ROW):
                board[k][j] = new_column[k]
    if level == 4:  # all card move left
        for i in (tile1_i, tile2_i):
            new_row = [0]
            for j in range(BOARD_COLUMN):
                if board[i][j] != 0:
                    new_row.append(board[i][j])
            while (len(new_row) < BOARD_COLUMN): new_row.append(0)
            for k in range(BOARD_COLUMN):
                board[i][k] = new_row[k]
    if level == 5:  # all card move right
        for i in (tile1_i, tile2_i):
            new_row = []
            for j in range(BOARD_COLUMN):
                if board[i][j] != 0:
                    new_row.append(board[i][j])
            while len(new_row) < BOARD_COLUMN - 1: new_row = [0] + new_row
            new_row.append(0)
            for k in range(BOARD_COLUMN):
                board[i][k] = new_row[k]


def draw_lives(lives, level):
    screen.blit(LIVES_IMAGE, (10, 12))
    lives_count = FONT_PIKACHU.render(str(lives), True, 'white')
    screen.blit(lives_count, (60, 13))

    screen.blit(LIST_LEVEL[level - 1], (SCREEN_WIDTH - 70, 12))


def reset_board(board):
    current_tiles = []
    for i in range(BOARD_ROW):
        for j in range(BOARD_COLUMN):
            if board[i][j]: current_tiles.append(board[i][j])
    tmp = current_tiles[:]
    while tmp == current_tiles:
        random.shuffle(current_tiles)
    k = 0
    for i in range(BOARD_ROW):
        for j in range(BOARD_COLUMN):
            if board[i][j]:
                board[i][j] = current_tiles[k]
                k += 1
    return board


def check_time(start_time, bouns_time):
    global lives, level, paused, time_start_paused, time_paused
    if paused: return 2
    # check game lost
    if time.time() - start_time - time_paused > GAME_TIME + bouns_time:  # time up
        paused = True
        if lives <= 1: return 0
        return 1
    return 2


def show_dim_screen():
    dim_screen = pg.Surface(screen.get_size(), pg.SRCALPHA)
    pg.draw.rect(dim_screen, (0, 0, 0, 220), dim_screen.get_rect())
    screen.blit(dim_screen, (0, 0))


def panel_pause(mouse_x, mouse_y, mouse_clicked):
    global lives, paused
    panel_rect = pg.Rect(0, 0, *PAUSE_PANEL_IMAGE.get_size())
    panel_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    screen.blit(PAUSE_PANEL_IMAGE, panel_rect)

    continue_rect = pg.Rect(0, 0, *CONTINUE_BUTTON.get_size())
    continue_rect.center = (panel_rect.centerx, panel_rect.centery)
    screen.blit(CONTINUE_BUTTON, continue_rect)
    if continue_rect.collidepoint(mouse_x, mouse_y):
        draw_dark_image(CONTINUE_BUTTON, continue_rect, (60, 60, 60))
        if mouse_clicked:
            draw_dark_image(CONTINUE_BUTTON, continue_rect, (120, 120, 120))
            paused = False
            click_sound.play()
            return 2

    replay_rect = pg.Rect(0, 0, *REPLAY_BUTTON.get_size())
    replay_rect.center = (panel_rect.centerx - 80, panel_rect.centery)
    screen.blit(REPLAY_BUTTON, replay_rect)
    if replay_rect.collidepoint(mouse_x, mouse_y):
        draw_dark_image(REPLAY_BUTTON, replay_rect, (60, 60, 60))
        if mouse_clicked:
            draw_dark_image(REPLAY_BUTTON, replay_rect, (120, 120, 120))
            click_sound.play()
            return 0

    home_rect = pg.Rect(0, 0, *HOME_BUTTON.get_size())
    home_rect.center = (panel_rect.centerx + 80, panel_rect.centery)
    screen.blit(HOME_BUTTON, home_rect)
    if home_rect.collidepoint(mouse_x, mouse_y):
        draw_dark_image(HOME_BUTTON, home_rect, (60, 60, 60))
        if mouse_clicked:
            draw_dark_image(HOME_BUTTON, home_rect, (120, 120, 120))
            click_sound.play()
            return 1

    return 3


def draw_pause_button(mouse_x, mouse_y, mouse_clicked):
    global paused
    pause_rect = pg.Rect(0, 0, *PAUSE_BUTTON.get_size())
    pause_rect.center = (SCREEN_WIDTH - 220, 35)
    screen.blit(PAUSE_BUTTON, pause_rect)
    if pause_rect.collidepoint(mouse_x, mouse_y):
        if not paused: draw_dark_image(PAUSE_BUTTON, pause_rect, (60, 60, 60))
        if mouse_clicked:
            mouse_clicked = False
            paused = True
            click_sound.play()


def draw_instruction():
    panel_rect = pg.Rect(0, 0, *INSTRUCTION_PANEL.get_size())
    panel_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    screen.blit(INSTRUCTION_PANEL, panel_rect)


# Ghi dữ liệu vào file user.json
def load_leaderboard(filename="user.json"):
    with open(filename, "r") as file:
        return json.load(file)


def save_leaderboard(data, filename="user.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


# Hàm lấy leaderboard đã được tích hợp vào update_user_level
def get_leaderboard():
    try:
        with open(USER_DATA_FILE, "r") as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}

    leaderboard = [{"username": username, "level": data["level"]} for username, data in users.items()]
    leaderboard.sort(key=lambda x: x["level"], reverse=True)

    return leaderboard


# Hàm hiển thị bảng xếp hạng
def draw_leaderboard():
	# Khởi tạo Pygame
	global running_draw_leaderboard
	pg.init()
	SCREEN_WIDTH = 1000  # Kích thước màn hình
	SCREEN_HEIGHT = 600
	screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pg.display.set_caption("Bảng xếp hạng")
	font = pg.font.Font(None, 36)

	# Tải background
	background = pg.image.load("assets/images/background/login_background.png")
	background = pg.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

	# Tải ảnh exit.png
	exit_button = pg.image.load("assets/images/button/exit.png")
	exit_button = pg.transform.scale(exit_button, (50, 50))  # Đảm bảo kích thước phù hợp

	# Lấy dữ liệu bảng xếp hạng
	leaderboard = get_leaderboard()

	running_draw_leaderboard = True
	while running_draw_leaderboard:
		screen.blit(background, (0, 0))  # Vẽ background

		# Vẽ tiêu đề
		title_text = font.render("RANK", True, (255, 0, 0))
		screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

		# Hiển thị danh sách người chơi
		y = 125  # Vị trí Y bắt đầu
		for i, entry in enumerate(leaderboard[:10]):  # Hiển thị top 10
			rank_text = f"{i + 1}.    {entry['username']}  -  Level:  {entry['level']}"
			text_surface = font.render(rank_text, True, (0, 0, 0))
			screen.blit(text_surface, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 - 70, y))
			y += 35  # Khoảng cách giữa các dòng

		# Vẽ nút Exit
		exit_rect = exit_button.get_rect(topleft=(SCREEN_WIDTH - 60, 20))  # Đặt nút exit ở góc trên bên phải
		screen.blit(exit_button, exit_rect)

		# Kiểm tra sự kiện
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running_draw_leaderboard = False
				break
			elif event.type == pg.MOUSEBUTTONDOWN:
				# Kiểm tra nếu người dùng click vào nút exit
				if exit_rect.collidepoint(event.pos):
					running_draw_leaderboard = False
					break

		pg.display.flip()

def draw_rank_button(rank):
    # Kích thước nút
    button_size = 100
    center = button_size // 2
    radius = button_size // 2 - 10

    # Tạo ảnh trong suốt bằng Pillow
    button = Image.new("RGBA", (button_size, button_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(button)

    # Vẽ hình tròn
    draw.ellipse(
        (10, 10, button_size - 10, button_size - 10),
        fill=(255, 223, 0),  # Màu vàng
        outline=(255, 200, 0),
        width=5
    )

    # Vẽ biểu tượng chiếc cúp
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    trophy_icon = "🏆"
    icon_width, icon_height = draw.textsize(trophy_icon, font=font)
    draw.text((center - icon_width // 2, center - 40), trophy_icon, font=font, fill="black")

    # Vẽ thứ hạng
    rank_text = f"#{rank}"
    rank_width, rank_height = draw.textsize(rank_text, font=font)
    draw.text((center - rank_width // 2, center + 10), rank_text, font=font, fill="black")

    # Chuyển đổi nút sang Surface của Pygame
    return pg.image.fromstring(button.tobytes(), button.size, button.mode)


if __name__ == '__main__':
    main()