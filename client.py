import pygame
import socket
import pickle
import threading
from logic import ROWS, COLS, PLAYER1, PLAYER2

WIDTH, HEIGHT = 700, 650
CELL_SIZE = WIDTH // COLS
RADIUS = CELL_SIZE // 2 - 5

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect Four")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 5555))

board, player_id = pickle.loads(client.recv(4096))

my_color = RED if player_id == PLAYER1 else YELLOW
op_color = YELLOW if my_color == RED else RED
font = pygame.font.SysFont(None, 40)

message = "Your Turn" if player_id == PLAYER1 else "Waiting..."
status = None
lock = threading.Lock()


def draw_board():
    screen.fill(BLUE)
    for r in range(ROWS):
        for c in range(COLS):
            color = WHITE
            if board[r][c] == PLAYER1:
                color = RED
            elif board[r][c] == PLAYER2:
                color = YELLOW
            pygame.draw.circle(
                screen,
                color,
                (c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2),
                RADIUS,
            )
    pygame.draw.rect(screen, WHITE, (0, HEIGHT - 40, WIDTH, 40))  # Clear message area
    label = font.render(message, True, BLACK)
    screen.blit(label, (10, HEIGHT - 35))
    pygame.display.flip()


def listen_for_updates():
    global board, message, status, turn
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break
            with lock:
                board, turn, status = pickle.loads(data)
                if status == "WIN":
                    message = "You Win!"
                elif status == "LOSE":
                    message = "You Lose!"
                elif status == "DRAW":
                    message = "Draw!"
                else:
                    message = "Your Turn" if turn == player_id else "Waiting..."
        except:
            break


threading.Thread(target=listen_for_updates, daemon=True).start()

run = True
while run:
    draw_board()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and player_id == turn:
            with lock:
                if message == "Your Turn":
                    x = event.pos[0] // CELL_SIZE
                    client.send(pickle.dumps(x))

pygame.quit()
