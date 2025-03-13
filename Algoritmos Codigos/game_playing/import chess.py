import chess  # Biblioteca para manejar la lógica del ajedrez
import chess.svg  # Permite representar tableros en formato SVG
import random  # Para la selección aleatoria de movimientos en la simulación
import math  # Para cálculos matemáticos en el algoritmo MCTS
from tkinter import Tk, Canvas, Frame, Button, Label, StringVar, Text, Scrollbar  # Interfaz gráfica
from PIL import Image, ImageTk  # Para manipular imágenes y mostrarlas en Tkinter
from io import BytesIO  # Manejo de datos en memoria
from svglib.svglib import svg2rlg  # Convertir SVG a un objeto de reporte gráfico
from reportlab.graphics import renderPDF  # Renderizar el objeto gráfico en PDF
import fitz  # PyMuPDF, para convertir PDF a imagen

# Valor de las piezas para la heurística
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0  # El rey no tiene valor en la evaluación
}

class Node:
    def __init__(self, move=None, parent=None):
        self.move = move  # Movimiento asociado al nodo
        self.parent = parent  # Nodo padre en el árbol de búsqueda
        self.children = []  # Lista de nodos hijos
        self.wins = 0  # Número de victorias en simulaciones
        self.visits = 0  # Número de veces que se ha visitado el nodo

    def ucb1(self, exploration_weight=1.4):
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + exploration_weight * math.sqrt(math.log(self.parent.visits) / self.visits)

    def best_child(self):
        return max(self.children, key=lambda child: child.ucb1())

def evaluate_board(board):
    """
    Evalúa la posición del tablero basada en el valor de las piezas y el control del centro.
    """
    score = 0

    # Valor de las piezas
    for piece_type in PIECE_VALUES:
        score += len(board.pieces(piece_type, chess.WHITE)) * PIECE_VALUES[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * PIECE_VALUES[piece_type]

    # Control del centro (cuadros centrales: d4, d5, e4, e5)
    center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
    for square in center_squares:
        if board.piece_at(square) and board.piece_at(square).color == chess.WHITE:
            score += 0.1
        elif board.piece_at(square) and board.piece_at(square).color == chess.BLACK:
            score -= 0.1

    return score

def mcts(board, iterations=1000, simulation_depth=20):
    root = Node()

    for _ in range(iterations):
        node = root
        temp_board = board.copy()

        # Selección
        while node.children:
            node = node.best_child()
            temp_board.push(node.move)

        # Expansión
        if not temp_board.is_game_over():
            for move in temp_board.legal_moves:
                node.children.append(Node(move, node))
            node = random.choice(node.children)
            temp_board.push(node.move)

        # Simulación con límite de profundidad
        depth = 0
        while not temp_board.is_game_over() and depth < simulation_depth:
            move = random.choice(list(temp_board.legal_moves))
            temp_board.push(move)
            depth += 1

        # Evaluación heurística si no se alcanza un resultado final
        if temp_board.is_game_over():
            result = temp_board.result()
            if result == "1-0":
                score = 1
            elif result == "0-1":
                score = -1
            else:
                score = 0
        else:
            score = evaluate_board(temp_board)

        # Retropropagación
        while node is not None:
            node.visits += 1
            node.wins += score if temp_board.turn == chess.WHITE else -score
            node = node.parent

    return root

def get_top_moves(node, top_n=3):
    """
    Obtiene los mejores movimientos basados en las visitas y victorias.
    """
    sorted_children = sorted(node.children, key=lambda child: child.visits, reverse=True)
    return sorted_children[:top_n]

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ajedrez con MCTS")
        self.board = chess.Board()
        self.canvas = Canvas(root, width=400, height=400)
        self.canvas.pack()
        self.move_var = StringVar()
        self.move_label = Label(root, textvariable=self.move_var, font=("Arial", 12))
        self.move_label.pack()

        # Cuadro de texto para mostrar detalles de los movimientos
        self.text_frame = Frame(root)
        self.text_frame.pack()
        self.text_area = Text(self.text_frame, width=50, height=10, wrap="word")
        self.text_area.pack(side="left", fill="y")
        scrollbar = Scrollbar(self.text_frame, command=self.text_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=scrollbar.set)

        # Frame para los botones de sugerencias
        self.suggestion_frame = Frame(root)
        self.suggestion_frame.pack()

        # Botón para detener el juego
        self.stop_button = Button(root, text="Detener Juego", command=self.stop_game)
        self.stop_button.pack()

        # Manejar el cierre de la ventana
        self.root.protocol("WM_DELETE_WINDOW", self.stop_game)

        self.update_board()

    def update_board(self):
        """
        Actualiza el tablero en la interfaz gráfica.
        """
        svg = chess.svg.board(board=self.board)
        drawing = svg2rlg(BytesIO(svg.encode()))
        pdf_data = BytesIO()
        renderPDF.drawToFile(drawing, pdf_data)
        pdf_data.seek(0)

        # Convertir PDF a imagen usando PyMuPDF (fitz)
        pdf_document = fitz.open(stream=pdf_data.read(), filetype="pdf")
        page = pdf_document.load_page(0)  # Cargar la primera página
        pix = page.get_pixmap()  # Convertir la página a una imagen
        img_data = pix.tobytes("png")  # Obtener los datos de la imagen en formato PNG

        # Mostrar la imagen con PIL y tkinter
        image = Image.open(BytesIO(img_data))
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

        # Mostrar sugerencias de movimientos
        if self.board.turn == chess.WHITE:
            self.show_suggestions()
        else:
            self.make_opponent_move()

    def show_suggestions(self):
        """
        Muestra las sugerencias de movimientos en la interfaz gráfica.
        """
        # Limpiar el cuadro de texto y los botones anteriores
        self.text_area.delete(1.0, "end")
        for widget in self.suggestion_frame.winfo_children():
            widget.destroy()

        root = mcts(self.board)
        top_moves = get_top_moves(root, top_n=3)

        # Mostrar detalles de los movimientos en el cuadro de texto
        self.text_area.insert("end", "Sugerencias de movimientos:\n\n")
        for i, node in enumerate(top_moves):
            move = node.move
            score = node.wins / node.visits
            self.text_area.insert("end", f"Move {i + 1}: {move}\n")
            self.text_area.insert("end", f"  - Score: {score:.2f}\n")
            self.text_area.insert("end", f"  - Visits: {node.visits}\n")
            self.text_area.insert("end", f"  - Win Rate: {node.wins / node.visits:.2f}\n")
            self.text_area.insert("end", "\n")

        # Crear botones para cada movimiento
        for i, node in enumerate(top_moves):
            button = Button(
                self.suggestion_frame,
                text=f"Move {i + 1}",
                command=lambda m=node.move: self.make_move(m),
                width=10,
            )
            button.pack(side="left", padx=5)

    def make_move(self, move):
        """
        Realiza un movimiento en el tablero.
        """
        self.board.push(move)
        self.move_var.set(f"Last move: {move}")
        self.update_board()

    def make_opponent_move(self):
        """
        Realiza un movimiento aleatorio para el oponente.
        """
        move = random.choice(list(self.board.legal_moves))
        self.board.push(move)
        self.move_var.set(f"Opponent's move: {move}")
        self.update_board()

    def stop_game(self):
        """
        Detiene el juego y cierra la ventana.
        """
        self.root.quit()  # Cerrar la ventana y detener el bucle principal
        self.root.destroy()  # Destruir la ventana

# Crear la ventana principal
root = Tk()
gui = ChessGUI(root)
root.mainloop()