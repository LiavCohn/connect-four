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
import time

HOST = "localhost"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)
print("Server started, waiting for players...")

players = [None, None]  # Index 0 for Player 1, Index 1 for Player 2
board = create_board()
turn = PLAYER1
lock = threading.Lock()  # Prevent race conditions


def client_thread(conn, player_id):
    global board, turn

    try:
        # Send initial board and player_id
        conn.send(pickle.dumps((board, player_id, turn)))

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                col = pickle.loads(data)

                with lock:
                    if player_id == turn and is_valid_move(board, col):
                        drop_token(board, col, player_id)

                        # Check for win, draw, or continue
                        if check_winner(board, player_id):
                            conn.send(pickle.dumps((board, turn, "WIN")))
                            other = players[0] if player_id == 1 else players[1]
                            if other:
                                other.send(pickle.dumps((board, turn, "LOSE")))
                            break

                        elif is_full(board):
                            for p in players:
                                if p:
                                    p.send(pickle.dumps((board, turn, "DRAW")))
                            break

                        # Switch turn and notify both players
                        turn = PLAYER1 if turn == PLAYER2 else PLAYER2
                        for p in players:
                            if p:
                                p.send(pickle.dumps((board, turn, "CONTINUE")))
            except:
                break
    finally:
        with lock:
            players[player_id - 1] = None  # Mark slot as empty
        try:
            for p in players:
                if p and p != conn:
                    p.send(pickle.dumps((board, None, "DISCONNECTED")))
                    time.sleep(2)
                    board = create_board()
                    turn = PLAYER1
                    while len(players) < 2:
                        time.sleep()
                    p.send(pickle.dumps((board, turn, "CONTINUE")))
        except:
            pass
        conn.close()


# Accept exactly 2 players
while True:
    conn, addr = server.accept()
    print(f"Connection from {addr}")

    with lock:
        if players[0] is None:
            player_id = 1
        elif players[1] is None:
            player_id = 2
        else:
            # Reject extra connections
            conn.send(pickle.dumps(("Game full", -1, -1)))
            conn.close()
            continue

        players[player_id - 1] = conn
        threading.Thread(
            target=client_thread, args=(conn, player_id), daemon=True
        ).start()
        print(f"Player {player_id} joined.")
