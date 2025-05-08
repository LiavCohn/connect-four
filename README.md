# 🟡🔴 Connect Four - Python Multiplayer Desktop Game

A simple 2-player **online Connect Four** game built using **Python**, **Pygame**, and **Socket programming**. The game is played through a graphical interface where two players take turns dropping colored tokens into a grid until one wins or the board is full.

---

## 🎮 Gameplay

- Two players take turns dropping red or yellow tokens into a vertical grid.
- The goal is to get four of your tokens in a row — vertically, horizontally, or diagonally.
- The game can be played between two machines on the same network.

---

## 📦 Features

- 🧠 Centralized server handles game state and turn logic.
- 🎨 Desktop GUI made with `pygame`.
- 🔄 Real-time updates using multithreading on the client side.
- 🔐 Turn-based locking ensures fairness.

---

## 🔧 How It Works

This project uses **Python sockets** for network communication and **threading** to keep the UI responsive while listening for server messages.

### 🧩 Sockets

- The **server** uses `socket` to listen on a port and accept connections from two clients.
- Once connected, the server sends the initial game state to each client using **pickle serialization**.
- During the game:
  - Clients send their move (column index) to the server.
  - The server processes the move, updates the board, and broadcasts the new game state along with the current turn and game status (WIN, LOSE, DRAW, CONTINUE).

### 🧵 Threading

- On the **client side**, a background thread (`listen_for_updates`) runs in parallel to the main `pygame` loop.
- This thread continuously listens (`recv`) for updates from the server and updates:
  - The shared game board
  - The current game status/message
- Without threading, the client would block waiting for server responses and freeze the UI.

This structure ensures:

- Smooth and responsive gameplay.
- Players can see real-time updates even while not interacting.
- Only the player whose turn it is can interact with the game board.
