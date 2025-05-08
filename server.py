import socket
import threading
import pickle
from logic import (
    create_board,
    drop_token,
    is_valid_move,
    check_winner,
    is_full,
    PLAYER1,
    PLAYER2,
)

HOST = "localhost"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)
print("Server started, waiting for players...")

players = []
board = create_board()
turn = PLAYER1


def client_thread(conn, player_id):
    global turn, board
    conn.send(pickle.dumps((board, player_id)))
    while True:
        try:
            col = pickle.loads(conn.recv(1024))
            if player_id == turn and is_valid_move(board, col):
                drop_token(board, col, player_id)
                if check_winner(board, player_id):
                    conn.send(pickle.dumps((board, turn, "WIN")))
                    other = players[0] if player_id == 1 else players[1]
                    other.send(pickle.dumps((board, turn, "LOSE")))
                    break
                elif is_full(board):
                    for p in players:
                        p.send(pickle.dumps((board, turn, "DRAW")))
                    break
                turn = PLAYER1 if turn == PLAYER2 else PLAYER2
                for p in players:
                    p.send(pickle.dumps((board, turn, "CONTINUE")))
        except:
            break
    conn.close()


while len(players) < 2:
    conn, addr = server.accept()
    print(f"Player connected from {addr}")
    players.append(conn)
    threading.Thread(target=client_thread, args=(conn, len(players))).start()
