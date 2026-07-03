import pygame
import sys
import random
import time
import cv2
import os

pygame.init()

# --- Fenêtre ---
LARGEUR, HAUTEUR = 1920, 1080
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Pixel Space Game")

clock = pygame.time.Clock()
FPS = 60

# --- Audio ---
intro_sound = pygame.mixer.Sound("dragon-studio-scary-sound-effect-359877.mp3")
intro_sound.set_volume(0.8)

game_over_sound = pygame.mixer.Sound("musique game over.mp3")
game_over_sound.set_volume(0.7)

pygame.mixer.music.load("musique fond.mp3")
pygame.mixer.music.set_volume(0.5)

# --- Police pixelisée ---
pixel_font = pygame.font.Font(None, 60)
pixel_big = pygame.font.Font(None, 120)

# --- FOND ANIMÉ PIXELISÉ ---
stars = []
for _ in range(200):
    x = random.randint(0, LARGEUR)
    y = random.randint(0, HAUTEUR)
    speed = random.randint(1, 3)
    stars.append([x, y, speed])

def draw_starfield():
    for star in stars:
        star[1] += star[2]
        if star[1] > HAUTEUR:
            star[0] = random.randint(0, LARGEUR)
            star[1] = 0
        pygame.draw.rect(ecran, (255, 255, 255), (star[0], star[1], 2, 2))

# --- HIGH SCORES ---
def load_score(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return int(f.read())
    return 0

def save_score(filename, score):
    with open(filename, "w") as f:
        f.write(str(score))

global_highscore = load_score("global_highscore.txt")
personal_highscore = load_score("personal_highscore.txt")

# --- Fonction vidéo intro ---
def play_intro_video():
    intro_sound.play()
    cap = cv2.VideoCapture("intro slowgames.mp4")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (LARGEUR, HAUTEUR))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

        ecran.blit(surf, (0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()

    cap.release()
    intro_sound.stop()

# --- Jouer la vidéo ---
play_intro_video()
pygame.mixer.music.play(-1)

# --- Images ---
try:
    joueur_img = pygame.image.load("vaisseau.png").convert_alpha()
    joueur_img = pygame.transform.scale(joueur_img, (60, 60))

    ennemi_img = pygame.image.load("vaisseau-ennemi.png").convert_alpha()
    ennemi_img = pygame.transform.rotate(ennemi_img, 180)
    ennemi_img = pygame.transform.scale(ennemi_img, (60, 60))

except:
    print("❌ ERROR: Cannot load images.")
    pygame.quit()
    sys.exit()

joueur_mask = pygame.mask.from_surface(joueur_img)
ennemi_mask = pygame.mask.from_surface(ennemi_img)

# --- Joueur ---
player_rect = joueur_img.get_rect()
player_rect.center = (LARGEUR // 2, HAUTEUR - 150)
player_speed = 8

# --- Ennemis ---
def creer_enemy():
    rect_img = ennemi_img.get_rect()
    rect_img.x = random.randint(0, LARGEUR - rect_img.width)
    rect_img.y = random.randint(-HAUTEUR, -50)
    speed = random.randint(4, 7)
    return {"rect": rect_img, "speed": speed}

# --- États ---
STATE_MENU = 0
STATE_GAME = 1
STATE_PAUSE = 2
STATE_GAMEOVER = 3
state = STATE_MENU

# --- Boutons ---
play_button = pygame.Rect(0, 0, 350, 120)
play_button.center = (LARGEUR // 2, HAUTEUR // 2)

quit_button = pygame.Rect(0, 0, 350, 120)
quit_button.center = (LARGEUR // 2, HAUTEUR // 2 + 200)

resume_button = pygame.Rect(0, 0, 350, 120)
resume_button.center = (LARGEUR // 2, HAUTEUR // 2 - 100)

pause_quit_button = pygame.Rect(0, 0, 350, 120)
pause_quit_button.center = (LARGEUR // 2, HAUTEUR // 2 + 100)

# --- Score & difficulté ---
score = 0
enemy_count = 10
next_threshold = 20
spawn_offset = 0

# --- Nouvelle partie ---
def start_game():
    global score, player_rect, enemies, state, enemy_count, next_threshold, spawn_offset
    score = 0
    enemy_count = 10
    next_threshold = 20
    spawn_offset = 0
    player_rect.center = (LARGEUR // 2, HAUTEUR - 150)
    enemies = [creer_enemy() for _ in range(enemy_count)]
    pygame.mixer.music.play(-1)
    state = STATE_GAME

# --- Boucle principale ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state == STATE_MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    start_game()
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        if state == STATE_GAME:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = STATE_PAUSE

        if state == STATE_PAUSE:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.collidepoint(event.pos):
                    state = STATE_GAME
                if pause_quit_button.collidepoint(event.pos):
                    state = STATE_MENU

    # --- MENU ---
    if state == STATE_MENU:
        ecran.fill((0, 0, 0))
        draw_starfield()

        title = pixel_big.render("PIXEL SPACE GAME", True, (0, 200, 255))
        ecran.blit(title, title.get_rect(center=(LARGEUR // 2, 200)))

        help_txt = pixel_font.render("Use the arrow keys to move your ship", True, (255, 255, 255))
        ecran.blit(help_txt, help_txt.get_rect(center=(LARGEUR // 2, 350)))

        # --- High scores positionnés correctement ---
        global_txt = pixel_font.render("World High Score", True, (255, 255, 0))
        global_num = pixel_font.render(str(global_highscore), True, (255, 255, 0))

        personal_txt = pixel_font.render("Your Best", True, (0, 255, 0))
        personal_num = pixel_font.render(str(personal_highscore), True, (0, 255, 0))

        # Gauche du bouton PLAY
        ecran.blit(global_txt, (play_button.centerx - 600, play_button.centery - 80))
        ecran.blit(global_num, (play_button.centerx - 600, play_button.centery))

        # Droite du bouton PLAY
        ecran.blit(personal_txt, (play_button.centerx + 250, play_button.centery - 80))
        ecran.blit(personal_num, (play_button.centerx + 250, play_button.centery))

        # Bouton PLAY
        pygame.draw.rect(ecran, (0, 120, 255), play_button)
        pygame.draw.rect(ecran, (255, 255, 255), play_button, 4)
        play_txt = pixel_big.render("PLAY", True, (255, 255, 255))
        ecran.blit(play_txt, play_txt.get_rect(center=play_button.center))

        # Bouton QUIT
        pygame.draw.rect(ecran, (200, 0, 0), quit_button)
        pygame.draw.rect(ecran, (255, 255, 255), quit_button, 4)
        quit_txt = pixel_big.render("QUIT", True, (255, 255, 255))
        ecran.blit(quit_txt, quit_txt.get_rect(center=quit_button.center))

        pygame.display.flip()
        clock.tick(FPS)
        continue

    # --- PAUSE ---
    if state == STATE_PAUSE:
        ecran.fill((0, 0, 0))
        draw_starfield()

        pause_txt = pixel_big.render("PAUSED", True, (255, 255, 255))
        ecran.blit(pause_txt, pause_txt.get_rect(center=(LARGEUR // 2, 250)))

        pygame.draw.rect(ecran, (0, 120, 255), resume_button)
        pygame.draw.rect(ecran, (255, 255, 255), resume_button, 4)
        resume_txt = pixel_big.render("RESUME", True, (255, 255, 255))
        ecran.blit(resume_txt, resume_txt.get_rect(center=resume_button.center))

        pygame.draw.rect(ecran, (200, 0, 0), pause_quit_button)
        pygame.draw.rect(ecran, (255, 255, 255), pause_quit_button, 4)
        pq_txt = pixel_big.render("QUIT GAME", True, (255, 255, 255))
        ecran.blit(pq_txt, pq_txt.get_rect(center=pause_quit_button.center))

        pygame.display.flip()
        clock.tick(FPS)
        continue

    # --- GAME OVER ---
    if state == STATE_GAMEOVER:
        pygame.mixer.music.stop()
        game_over_sound.play()

        # Mise à jour des high scores
        if score > global_highscore:
            global_highscore = score
            save_score("global_highscore.txt", global_highscore)

        if score > personal_highscore:
            personal_highscore = score
            save_score("personal_highscore.txt", personal_highscore)

        ecran.fill((0, 0, 0))
        draw_starfield()

        go_txt = pixel_big.render("GAME OVER", True, (255, 50, 50))
        ecran.blit(go_txt, go_txt.get_rect(center=(LARGEUR // 2, HAUTEUR // 2)))

        pygame.display.flip()
        time.sleep(3)

        pygame.mixer.music.load("musique fond.mp3")
        pygame.mixer.music.play(-1)

        state = STATE_MENU
        continue

    # --- JEU ---
    touches = pygame.key.get_pressed()

    if touches[pygame.K_LEFT]:
        player_rect.x -= player_speed
    if touches[pygame.K_RIGHT]:
        player_rect.x += player_speed
    if touches[pygame.K_UP]:
        player_rect.y -= player_speed
    if touches[pygame.K_DOWN]:
        player_rect.y += player_speed

    player_rect.clamp_ip(ecran.get_rect())

    # --- Augmentation du nombre d'ennemis ---
    if score >= next_threshold:
        enemies.extend([creer_enemy() for _ in range(4)])
        enemy_count += 4

        # Tous les 100 points → on décale le prochain spawn de +20
        if score % 100 == 0:
            next_threshold += 20
        else:
            next_threshold += 20

    # --- Mise à jour des ennemis ---
    for enemy in enemies:
        enemy["rect"].y += enemy["speed"]

        if enemy["rect"].top > HAUTEUR:
            enemy["rect"] = creer_enemy()["rect"]
            score += 1

        offset_x = enemy["rect"].x - player_rect.x
        offset_y = enemy["rect"].y - player_rect.y

        if joueur_mask.overlap(ennemi_mask, (offset_x, offset_y)):
            state = STATE_GAMEOVER

    ecran.fill((0, 0, 0))
    draw_starfield()

    ecran.blit(joueur_img, player_rect)

    for enemy in enemies:
        ecran.blit(ennemi_img, enemy["rect"])

    score_txt = pixel_font.render(f"Score : {score}", True, (255, 255, 255))
    ecran.blit(score_txt, (20, 20))

    pygame.display.flip()
    clock.tick(FPS)
