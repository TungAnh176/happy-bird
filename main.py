import pygame, sys, random

pygame.init()
pygame.display.set_caption("Happy Bird")
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)


# Hàm vẽ sàn
def draw_floor():
    screen.blit(floor, (floor_x_pos, 650))
    screen.blit(floor, (floor_x_pos + 432, 650))


# Hàm tạo ống
def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop=(500, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midtop=(500, random_pipe_pos - 650))
    return bottom_pipe, top_pipe


# Hàm di chuyển các ống
def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return pipes


# Hàm vẽ các ống
def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 600:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)


# Hàm kiểm tra va chạm
def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            hit_sound.play()
            return False
    if bird_rect.top <= 0 or bird_rect.bottom >= 650:
        return False
    return True


# Hàm xoay chim
def rotate_bird(bird1):
    new_bird = pygame.transform.rotozoom(bird1, -bird_movement * 3, 1)
    return new_bird


# Hàm hoạt ảnh của chim
def bird_animations():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery))
    return new_bird, new_bird_rect


def update_score(score, high_score):
    if score > high_score:
        high_score = score
    return high_score


# Hàm hiển thị điểm
def score_display(game_state):
    if game_state == "main_game":
        score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(216, 100))
        screen.blit(score_surface, score_rect)
    if game_state == "game_over":
        score_surface = game_font.render(f"Score: {int(score)}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(216, 100))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(
            f"High score: {int(high_score)}", True, (255, 255, 255)
        )
        high_score_rect = high_score_surface.get_rect(center=(216, 630))
        screen.blit(high_score_surface, high_score_rect)


screen = pygame.display.set_mode((432, 768))
clock = pygame.time.Clock()
game_font = pygame.font.Font("file/04B_19.ttf", 40)

# Biến trò chơi
gravity = 0.25 # Trọng lực
bird_movement = 0
pipe_height = [200, 300, 400]
game_active = True
score = 0
high_score = 0
passed_pipe = False

# Hình nền
bg = pygame.transform.scale2x(
    pygame.image.load("file/assets/background-night.png").convert()
)
game_over_surface = pygame.transform.scale2x(
    pygame.image.load("file/assets/message.png").convert_alpha()
)
game_over_rect = game_over_surface.get_rect(center=(216, 384))

# Sàn
floor = pygame.transform.scale2x(pygame.image.load("file/assets/floor.png").convert())
floor_x_pos = 0

# Chim
bird_downflap = pygame.transform.scale2x(
    pygame.image.load("file/assets/yellowbird-downflap.png").convert_alpha()
)
bird_midflap = pygame.transform.scale2x(
    pygame.image.load("file/assets/yellowbird-midflap.png").convert_alpha()
)
bird_upflap = pygame.transform.scale2x(
    pygame.image.load("file/assets/yellowbird-upflap.png").convert_alpha()
)
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 0
bird = bird_frames[bird_index]
bird_rect = bird.get_rect(center=(100, 384))

bird_flap = pygame.USEREVENT + 1
pygame.time.set_timer(bird_flap, 200)

# Ống
pipe_surface = pygame.transform.scale2x(
    pygame.image.load("file/assets/pipe-green.png").convert()
)

# Sự kiện tạo ống
spawn_pipe = pygame.USEREVENT
pygame.time.set_timer(spawn_pipe, 1200) # thời gian tạo ống
pipe_list = []

# chèn âm thanh
flap_sound = pygame.mixer.Sound("file/sound/sfx_wing.wav")
hit_sound = pygame.mixer.Sound("file/sound/sfx_hit.wav")
score_sound = pygame.mixer.Sound("file/sound/sfx_point.wav")
score_sound_countdown = 100


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = 0
                bird_movement -= 11
                flap_sound.play()
            if event.key == pygame.K_RETURN and not game_active:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (100, 384)
                bird_movement = 0
                score = 0
        if event.type == spawn_pipe:
            pipe_list.extend(create_pipe())
        if event.type == bird_flap:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0
        bird, bird_rect = bird_animations()

    screen.blit(bg, (0, 0))

    if game_active:
        # Chim
        bird_movement += gravity
        rotated_bird = rotate_bird(bird)
        bird_rect.centery += bird_movement

        # Kiểm tra va chạm
        if bird_rect.top <= 0:
            bird_rect.top = 0
        if bird_rect.bottom >= 650:
            bird_rect.bottom = 650
        screen.blit(rotated_bird, bird_rect)

        # Di chuyển ống
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Kiểm tra khi chim vượt qua ống
        for pipe in pipe_list:
            if pipe.centerx == bird_rect.centerx and not passed_pipe:
                passed_pipe = True
                score += 1
                score_sound.play()
        if pipe_list and pipe_list[0].right < 0:
            passed_pipe = False

        score_display("main_game")
        game_active = check_collision(pipe_list)
    else:
        screen.blit(game_over_surface, game_over_rect)
        high_score = update_score(score, high_score)
        score_display("game_over")

    # Vẽ sàn
    draw_floor()
    floor_x_pos -= 1
    if floor_x_pos <= -432:
        floor_x_pos = 0

    pygame.display.update()
    clock.tick(100) # tốc độ game
