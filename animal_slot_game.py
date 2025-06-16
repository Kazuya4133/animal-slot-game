import pygame
import sys
import random
import os
import math

# Pygameの初期化
pygame.init()

# 画面サイズの設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animal Slot Game")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BROWN = (139, 69, 19)
DARK_BLUE = (25, 25, 112)
GREEN = (34, 139, 34)

# フォントの設定
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

# 画像の読み込み
def load_image(filename, size=(80, 80)):
    try:
        image_path = os.path.join("images", filename)
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, size)
    except pygame.error as e:
        print(f"Failed to load image: {filename}, {e}")
        # 代替として色付きの四角形を返す
        surf = pygame.Surface(size)
        surf.fill(PINK)
        return surf

# 動物の画像とデータ
animals = [
    {"name": "Cat", "image": load_image("cat.png", (100, 100))},
    {"name": "Dog", "image": load_image("dog.png", (100, 100))},
    {"name": "Koala", "image": load_image("chick.png", (100, 100))},
    {"name": "Panda", "image": load_image("panda.png", (100, 100))},
    {"name": "Sloth", "image": load_image("sloth.png", (100, 100))}
]

# スロットの状態
slots = [0, 0, 0]  # 各列の現在の動物インデックス
spinning = False
spin_speeds = [5, 8, 10]  # 各列の回転速度
spin_counters = [0, 0, 0]  # 各列の回転カウンター
spin_times = [0, 0, 0]  # 各列の回転時間
win = False
animation_counter = 0
lever_pulled = False
lever_angle = 0

# ボタンの設定
button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 80)

# スロットマシンの装飾用画像
def draw_slot_machine_decoration():
    # 背景のグラデーション
    for i in range(HEIGHT):
        c = min(255, int(150 + i * 0.2))
        pygame.draw.line(screen, (c, c, 255), (0, i), (WIDTH, i))
    
    # スロットマシン本体
    pygame.draw.rect(screen, BROWN, (WIDTH // 2 - 350, 80, 700, 400), 0, 20)
    pygame.draw.rect(screen, GOLD, (WIDTH // 2 - 350, 80, 700, 400), 5, 20)
    
    # スロットマシンの上部装飾
    pygame.draw.rect(screen, RED, (WIDTH // 2 - 300, 30, 600, 50), 0, 10)
    pygame.draw.rect(screen, GOLD, (WIDTH // 2 - 300, 30, 600, 50), 3, 10)
    
    # スロットマシンのタイトル
    title_text = font_medium.render("ANIMAL SLOT", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, 55))
    screen.blit(title_text, title_rect)
    
    # レバー
    lever_x = WIDTH // 2 + 300
    lever_y = 180
    lever_length = 150
    
    # レバーの支点
    pygame.draw.circle(screen, SILVER, (lever_x + 15, lever_y), 15)
    pygame.draw.circle(screen, BLACK, (lever_x + 15, lever_y), 15, 2)
    
    # レバーの棒部分（角度に応じて回転）
    if lever_pulled:
        # 上から下に引く動き（0度から90度）
        end_x = lever_x + 15
        end_y = lever_y + int(math.sin(math.radians(lever_angle)) * lever_length)
        pygame.draw.line(screen, SILVER, (lever_x + 15, lever_y), (end_x, end_y), 10)
        
        # レバーのつまみ部分
        pygame.draw.circle(screen, RED, (end_x, end_y), 20)
        pygame.draw.circle(screen, BLACK, (end_x, end_y), 20, 2)
    else:
        # 通常状態（垂直）
        pygame.draw.rect(screen, SILVER, (lever_x, lever_y, 30, lever_length), 0, 5)
        pygame.draw.circle(screen, RED, (lever_x + 15, lever_y), 20)
        pygame.draw.circle(screen, BLACK, (lever_x + 15, lever_y), 20, 2)
    
    # コイン投入口
    pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 300, 380, 80, 20), 0, 5)
    pygame.draw.rect(screen, GOLD, (WIDTH // 2 - 300, 380, 80, 20), 2, 5)
    coin_text = font_small.render("COIN", True, GOLD)
    screen.blit(coin_text, (WIDTH // 2 - 290, 360))
    
    # コイン払い出し口
    pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 100, 430, 200, 30), 0, 10)
    pygame.draw.rect(screen, SILVER, (WIDTH // 2 - 100, 430, 200, 30), 2, 10)
    
    # 装飾ランプ
    for i in range(7):
        x = WIDTH // 2 - 300 + i * 100
        color = RED if i % 2 == 0 else YELLOW
        if win and animation_counter % 10 < 5:
            color = GREEN if i % 2 == 0 else GOLD
        pygame.draw.circle(screen, color, (x, 100), 10)
        pygame.draw.circle(screen, WHITE, (x, 100), 3)

# スロットリールの描画
def draw_slot_reel(x_pos, y_pos, animal_idx):
    # リールの背景
    pygame.draw.rect(screen, WHITE, (x_pos - 60, y_pos - 60, 120, 120), 0, 15)
    
    # リールの枠
    pygame.draw.rect(screen, SILVER, (x_pos - 60, y_pos - 60, 120, 120), 4, 15)
    
    # リールの内側の枠
    pygame.draw.rect(screen, GOLD, (x_pos - 55, y_pos - 55, 110, 110), 2, 12)
    
    # リールの回転線（装飾）
    for i in range(6):
        angle = i * 30
        rad = math.radians(angle)
        start_x = x_pos + 50 * math.cos(rad)
        start_y = y_pos + 50 * math.sin(rad)
        end_x = x_pos + 55 * math.cos(rad)
        end_y = y_pos + 55 * math.sin(rad)
        pygame.draw.line(screen, SILVER, (start_x, start_y), (end_x, end_y), 1)
    
    # 動物の画像
    animal = animals[animal_idx]
    image_rect = animal["image"].get_rect(center=(x_pos, y_pos))
    screen.blit(animal["image"], image_rect)
    
    # 動物の名前
    name_text = font_small.render(animal["name"], True, BLACK)
    name_rect = name_text.get_rect(center=(x_pos, y_pos + 80))
    screen.blit(name_text, name_rect)

def draw_slot_machine():
    global animation_counter
    
    # 背景
    draw_slot_machine_decoration()
    
    # 3つの列を描画
    for i in range(3):
        x_pos = WIDTH // 2 - 150 + i * 150
        y_pos = 230
        
        # 現在の絵柄
        current_idx = slots[i]
        draw_slot_reel(x_pos, y_pos, current_idx)
    
    # スタートボタン
    button_color = YELLOW if not spinning else LIGHT_BLUE
    pygame.draw.rect(screen, button_color, button_rect, 0, 15)
    pygame.draw.rect(screen, BLACK, button_rect, 3, 15)
    
    button_text = font_medium.render("START", True, BLACK)
    button_text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, button_text_rect)
    
    # 勝利メッセージ
    if win:
        animation_counter = (animation_counter + 1) % 60
        
        # 勝利メッセージの背景
        message_bg_rect = pygame.Rect(WIDTH // 2 - 300, HEIGHT - 200, 600, 80)
        pygame.draw.rect(screen, DARK_BLUE, message_bg_rect, 0, 15)
        pygame.draw.rect(screen, GOLD, message_bg_rect, 4, 15)
        
        if animation_counter < 30:
            win_text = font_large.render("CONGRATULATIONS!", True, RED)
        else:
            win_text = font_large.render("CONGRATULATIONS!", True, YELLOW)
        win_text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT - 160))
        
        # 勝利時の装飾
        for i in range(20):
            offset = (animation_counter + i * 10) % 200
            x = offset * 4
            y = 50 + math.sin(offset * 0.1) * 20
            if x < WIDTH:
                pygame.draw.circle(screen, GOLD, (x, y), 3)
        
        screen.blit(win_text, win_text_rect)

def spin_slots():
    global spinning, slots, win, spin_times, spin_counters, lever_pulled, lever_angle
    
    # レバーのアニメーション
    if lever_pulled:
        if lever_angle < 90:
            lever_angle += 9
        else:
            # レバーが最大角度に達したら、少し待ってから戻す
            if animation_counter % 60 == 0:
                lever_pulled = False
                lever_angle = 0
    
    if spinning:
        all_stopped = True
        
        # 各列の回転処理
        for i in range(3):
            if spin_times[i] > 0:
                all_stopped = False
                spin_counters[i] += 1
                
                if spin_counters[i] >= spin_speeds[i]:
                    spin_counters[i] = 0
                    slots[i] = (slots[i] + 1) % len(animals)
                    
                spin_times[i] -= 1
        
        # すべての列の回転が終わったかチェック
        if all_stopped:
            spinning = False
            check_win()

def check_win():
    global win
    # 3つの絵柄が揃っているかチェック
    if slots[0] == slots[1] == slots[2]:
        win = True

def main():
    global spinning, slots, win, spin_times, spin_counters, animation_counter, lever_pulled, lever_angle
    
    clock = pygame.time.Clock()
    animation_counter = 0
    
    # ゲームループ
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos) and not spinning:
                    # スタートボタンが押された
                    spinning = True
                    lever_pulled = True
                    win = False
                    # 各列の回転時間をランダムに設定
                    spin_times = [random.randint(30, 50), random.randint(50, 70), random.randint(70, 90)]
                    spin_counters = [0, 0, 0]
        
        # スロットの回転処理
        spin_slots()
        
        # アニメーションカウンターの更新
        animation_counter += 1
        
        # 描画
        draw_slot_machine()
        
        # 画面の更新
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
