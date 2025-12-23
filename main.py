import os, pygame, random
pygame.init()

# --- KONSTANTA ---
WIDTH, HEIGHT = 400, 600
FPS = 60
WHITE = (255,255,255)
BLACK = (0,0,0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sky Jump - Bird Edition")
clock = pygame.time.Clock()

def load_image_checked(filename, size=None):
    candidates = [
        filename,
        os.path.join("assets", filename),
        os.path.join("images", filename),
        os.path.join(os.path.dirname(__file__), filename),
        os.path.abspath(filename)
    ]

    for p in candidates:
        if p and os.path.exists(p):
            try:
                img = pygame.image.load(p)
                try: img = img.convert_alpha()
                except: img = img.convert()
                if size:
                    img = pygame.transform.scale(img, size)
                return img
            except:
                pass
    return None

bg_image = load_image_checked("bg.png", (WIDTH, HEIGHT))
if bg_image is None:
    bg_image = pygame.Surface((WIDTH, HEIGHT))
    bg_image.fill((135,206,235))

def load_platform_image(filename, size):
    img = load_image_checked(filename)
    if img is None:
        surf = pygame.Surface(size)
        surf.fill((139,69,19))
        return surf
    return pygame.transform.scale(img, size)

def load_player_image():
    img = load_image_checked("bird.png")
    if img is None:
        surf = pygame.Surface((35,35))
        surf.fill((0,100,255))
        return surf

    scale_h = 40
    w, h = img.get_size()
    scale_w = int((w/h)*scale_h)
    return pygame.transform.scale(img, (scale_w, scale_h))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_player_image()
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT - 150))
        self.vel_y = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  self.rect.x -= 4
        if keys[pygame.K_RIGHT]: self.rect.x += 4

        if self.rect.right < 0: self.rect.left = WIDTH
        if self.rect.left > WIDTH: self.rect.right = 0

        self.vel_y += 0.4
        self.rect.y += self.vel_y

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w=80, h=20):
        super().__init__()
        self.image = load_platform_image("wood.png", (w, h))
        self.rect = self.image.get_rect(topleft=(x, y))

def generate_ordered_platforms(count):
    platforms = []

    min_gap = 60
    max_gap = 90

    y = HEIGHT - 80

    for i in range(count):
        width = random.randint(60, 100)
        x = random.randint(10, WIDTH - width - 10)

        y -= random.randint(min_gap, max_gap)
        if y < -50:
            break

        platforms.append(Platform(x, y, width, 20))

    return platforms

font = pygame.font.SysFont("arial", 28)
font_big = pygame.font.SysFont("arial", 48)

def draw_text(text, size, color, x, y):
    f = pygame.font.SysFont("arial", size)
    surf = f.render(text, True, color)
    rect = surf.get_rect(center=(x,y))
    screen.blit(surf, rect)


def show_menu():
    menu_running = True

    while menu_running:
        screen.blit(bg_image, (0,0))
        draw_text("SKY JUMP", 50, WHITE, WIDTH//2, HEIGHT//3)
        draw_text("Press SPACE to Play", 30, WHITE, WIDTH//2, HEIGHT//2)
        draw_text("Press ESC to Quit", 25, WHITE, WIDTH//2, HEIGHT//2 + 40)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); quit()

def run_game():
    # SETUP
    player = Player()
    platforms = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)

    # PLATFORM DASAR
    ground = Platform(0, HEIGHT - 10, 400, 20)
    platforms.add(ground)
    all_sprites.add(ground)

    # PLATFORM RAPI
    ordered = generate_ordered_platforms(5)
    for p in ordered:
        platforms.add(p)
        all_sprites.add(p)

    score = 0
    running = True
    last_high = player.rect.bottom 

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()

        all_sprites.update()

        # SCORE
        if player.rect.top < last_high:
            score += (last_high - player.rect.top)
            last_high = player.rect.top

        # TABRAK PLATFORM
        if player.vel_y > 0:
            hits = pygame.sprite.spritecollide(player, platforms, False)
            if hits:
                player.vel_y = -10

        # SCROLL
        if player.rect.top <= HEIGHT // 3:
            player.rect.y += 4
            for p in platforms:
                p.rect.y += 4
                if p.rect.top > HEIGHT:
                    p.kill()
                    new_p = Platform(random.randint(0, WIDTH - 80), random.randint(-40, -10))
                    platforms.add(new_p)
                    all_sprites.add(new_p)

        # GAME OVER
        if player.rect.top > HEIGHT:
            return score

        # DRAW
        screen.blit(bg_image, (0,0))
        all_sprites.draw(screen)
        draw_text(f"Score: {score}", 25, WHITE, WIDTH - 80, 30)

        pygame.display.flip()

def show_game_over(score):
    over = True

    while over:
        screen.blit(bg_image, (0,0))
        draw_text("GAME OVER", 50, WHITE, WIDTH//2, HEIGHT//3)
        draw_text(f"Score: {score}", 35, WHITE, WIDTH//2, HEIGHT//2)
        draw_text("Press SPACE to Restart", 25, WHITE, WIDTH//2, HEIGHT//2 + 50)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    over = False

show_menu()

while True:
    final_score = run_game()
    show_game_over(final_score)
