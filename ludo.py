import random
import tkinter as tk
from tkinter import messagebox, ttk
import time

TOTAL_MAIN_SQUARES = 52
HOME_PATH_LENGTH = 6
TOTAL_STEPS = TOTAL_MAIN_SQUARES + HOME_PATH_LENGTH
PIECES_PER_PLAYER = 4

COLOR_NAMES = ["Rouge", "Bleu", "Jaune", "Vert"]
ENTRY_INDEX = [0, 13, 26, 39]
COLORS = ["#FF4444", "#4444FF", "#FFFF44", "#44FF44"]  # Rouge, Bleu, Jaune, Vert

class Piece:
    def __init__(self, index: int):
        self.index = index
        self.status = "base"
        self.distance = 0

    def is_base(self) -> bool:
        return self.status == "base"

    def is_active(self) -> bool:
        return self.status == "active"

    def is_finished(self) -> bool:
        return self.status == "finished"

    def enter(self) -> None:
        self.status = "active"
        self.distance = 1

    def move(self, steps: int) -> None:
        self.distance += steps
        if self.distance >= TOTAL_STEPS:
            self.status = "finished"
            self.distance = TOTAL_STEPS

    def position_label(self, player_entry: int) -> str:
        if self.is_base():
            return "Base"
        if self.is_finished():
            return "Arrivée"
        if self.distance <= TOTAL_MAIN_SQUARES:
            board_index = (player_entry + self.distance - 1) % TOTAL_MAIN_SQUARES
            return f"Piste({board_index})"
        home_step = self.distance - TOTAL_MAIN_SQUARES
        return f"Maison({home_step}/{HOME_PATH_LENGTH})"

class Player:
    def __init__(self, name: str, entry_index: int):
        self.name = name
        self.entry_index = entry_index
        self.pieces = [Piece(i + 1) for i in range(PIECES_PER_PLAYER)]
        self.score = 0
        self.turns_played = 0

    def finished_count(self) -> int:
        return sum(piece.is_finished() for piece in self.pieces)

    def active_pieces(self):
        return [piece for piece in self.pieces if piece.is_active()]

    def base_pieces(self):
        return [piece for piece in self.pieces if piece.is_base()]

    def has_any_move(self, roll: int, board: dict) -> bool:
        return len(self.valid_moves(roll, board)) > 0

    def valid_moves(self, roll: int, board: dict) -> list:
        moves = []
        for piece in self.pieces:
            if piece.is_finished():
                continue
            if piece.is_base():
                if roll == 6:
                    if not self._is_occupied_by_self(self.entry_index, board):
                        moves.append((piece, "enter"))
                continue
            target_distance = piece.distance + roll
            if target_distance > TOTAL_STEPS:
                continue
            target_position = self.get_board_position_for_distance(target_distance)
            if target_position is None or not self._is_occupied_by_self(target_position, board):
                moves.append((piece, target_distance))
        return moves

    def get_board_position_for_distance(self, distance: int):
        if distance <= TOTAL_MAIN_SQUARES:
            return (self.entry_index + distance - 1) % TOTAL_MAIN_SQUARES
        return None

    def _is_occupied_by_self(self, position, board) -> bool:
        if position is None:
            return False
        return any(piece_info[0] == self for piece_info in board.get(position, []))

class Game:
    def __init__(self):
        self.players = [Player(COLOR_NAMES[i], ENTRY_INDEX[i]) for i in range(len(COLOR_NAMES))]
        self.current = 0
        self.game_start_time = time.time()
        self.total_turns = 0

    def build_board(self):
        board = {}
        for player in self.players:
            for piece in player.active_pieces():
                if piece.distance <= TOTAL_MAIN_SQUARES:
                    position = player.get_board_position_for_distance(piece.distance)
                    board.setdefault(position, []).append((player, piece))
        return board

    def roll_die(self) -> int:
        return random.randint(1, 6)

    def capture_opponent(self, position: int, moving_player: Player):
        board = self.build_board()
        pieces_at_position = board.get(position, [])
        if not pieces_at_position:
            return False
        captured = False
        for opponent, piece in pieces_at_position:
            if opponent is not moving_player:
                piece.status = "base"
                piece.distance = 0
                captured = True
        return captured

    def get_game_stats(self):
        """Retourne les statistiques de la partie"""
        elapsed_time = time.time() - self.game_start_time
        return {
            'duration': elapsed_time,
            'total_turns': self.total_turns,
            'player_scores': {p.name: p.score for p in self.players},
            'finished_pieces': {p.name: p.finished_count() for p in self.players}
        }

class LudoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ludo - Jeu de société")
        self.game = None
        self.selected_piece = None
        self.roll_value = None
        self.moves = []
        self.animation_speed = 50  # millisecondes entre frames

        # Menu principal
        self.show_main_menu()

    def show_main_menu(self):
        """Affiche le menu principal du jeu"""
        # Effacer tout contenu existant
        for widget in self.root.winfo_children():
            widget.destroy()

        # Titre
        title_label = tk.Label(self.root, text="🎲 JEU DE LUDO 🎲",
                              font=("Arial", 24, "bold"), fg="#FF4444")
        title_label.pack(pady=20)

        # Boutons du menu
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        play_button = tk.Button(button_frame, text="🎮 Nouvelle Partie",
                               command=self.start_new_game, font=("Arial", 14),
                               bg="#4CAF50", fg="white", padx=20, pady=10)
        play_button.pack(pady=10)

        rules_button = tk.Button(button_frame, text="📖 Règles du Jeu",
                                command=self.show_rules, font=("Arial", 14),
                                bg="#2196F3", fg="white", padx=20, pady=10)
        rules_button.pack(pady=10)

        stats_button = tk.Button(button_frame, text="📊 Statistiques",
                                command=self.show_stats, font=("Arial", 14),
                                bg="#FF9800", fg="white", padx=20, pady=10)
        stats_button.pack(pady=10)

        quit_button = tk.Button(button_frame, text="❌ Quitter",
                               command=self.root.quit, font=("Arial", 14),
                               bg="#F44336", fg="white", padx=20, pady=10)
        quit_button.pack(pady=10)

        # Crédits
        credits_label = tk.Label(self.root, text="Créé avec ❤️ en Python",
                                font=("Arial", 10), fg="#666666")
        credits_label.pack(side=tk.BOTTOM, pady=20)

    def start_new_game(self):
        """Démarre une nouvelle partie"""
        self.game = Game()

        # Effacer le menu
        for widget in self.root.winfo_children():
            widget.destroy()

        # Configuration du plateau de jeu
        self.canvas = tk.Canvas(self.root, width=700, height=700, bg="#F5F5DC")
        self.canvas.pack()

        # Frame pour les contrôles
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Bouton pour lancer le dé
        self.roll_button = tk.Button(control_frame, text="🎲 Lancer le dé",
                                   command=self.roll_die, font=("Arial", 14, "bold"),
                                   bg="#4CAF50", fg="white", relief="raised", padx=20, pady=10)
        self.roll_button.pack(side=tk.LEFT, padx=10)

        # Label pour afficher le résultat du dé
        self.roll_label = tk.Label(control_frame, text="Résultat du dé: -",
                                  font=("Arial", 12, "bold"))
        self.roll_label.pack(side=tk.LEFT, padx=20)

        # Label pour afficher le joueur actuel
        self.player_label = tk.Label(control_frame, text="",
                                    font=("Arial", 12, "bold"))
        self.player_label.pack(side=tk.LEFT, padx=20)

        # Bouton menu
        menu_button = tk.Button(control_frame, text="🏠 Menu",
                               command=self.return_to_menu, font=("Arial", 10),
                               bg="#666666", fg="white")
        menu_button.pack(side=tk.RIGHT, padx=10)

        # Dessiner le plateau initial
        self.draw_board()
        self.update_display()

    def return_to_menu(self):
        """Retour au menu principal"""
        if messagebox.askyesno("Retour au menu", "Voulez-vous vraiment retourner au menu principal ?\nLa partie en cours sera perdue."):
            self.show_main_menu()

    def show_rules(self):
        """Affiche les règles du jeu"""
        rules_window = tk.Toplevel(self.root)
        rules_window.title("Règles du Ludo")
        rules_window.geometry("600x500")

        # Titre
        title = tk.Label(rules_window, text="📖 RÈGLES DU JEU DE LUDO",
                        font=("Arial", 16, "bold"), fg="#FF4444")
        title.pack(pady=10)

        # Zone de texte avec scrollbar
        frame = tk.Frame(rules_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_area = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                           font=("Arial", 11), padx=10, pady=10)
        text_area.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_area.yview)

        # Contenu des règles
        rules_text = """
🎯 OBJECTIF
Être le premier joueur à amener ses 4 pions à l'arrivée au centre du plateau.

👥 JOUEURS
4 joueurs : Rouge, Bleu, Jaune, Vert

🎲 DÉROULEMENT D'UN TOUR
1. Cliquez sur "🎲 Lancer le dé"
2. Si vous obtenez un 6, vous pouvez sortir un pion de votre base
3. Les pions surlignés en cercle coloré peuvent être déplacés
4. Cliquez sur un pion pour le déplacer
5. Les positions possibles sont marquées en jaune

⚔️ RÈGLES SPÉCIALES
• Sortie de base : Uniquement avec un 6
• Capture : Un pion adverse sur votre case retourne à sa base
• Chemin d'arrivée : Chaque couleur a son propre chemin coloré
• Tour supplémentaire : Si vous faites un 6, vous rejouez

🏆 VICTOIRE
Le premier joueur qui amène ses 4 pions au centre gagne !

🎨 INTERFACE
• Plateau : Représentation fidèle d'un vrai plateau de Ludo
• Pions : Cercles colorés pour chaque joueur
• Surlignage : Les pions jouables sont entourés d'un cercle coloré
• Messages : Informations sur les actions en cours
• Animations : Effets visuels pour les mouvements

🎮 CONTRÔLES
• 🎲 Lancer le dé : Bouton pour obtenir un nombre aléatoire
• Clic sur pion : Sélectionner et déplacer un pion
• Messages : Boîtes de dialogue pour les informations importantes

Bonne chance et amusez-vous bien ! 🎉
        """

        text_area.insert(tk.END, rules_text)
        text_area.config(state=tk.DISABLED)

        # Bouton fermer
        close_button = tk.Button(rules_window, text="Fermer",
                                command=rules_window.destroy,
                                font=("Arial", 12), bg="#666666", fg="white")
        close_button.pack(pady=10)

    def show_stats(self):
        """Affiche les statistiques du jeu"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistiques du Jeu")
        stats_window.geometry("400x300")

        title = tk.Label(stats_window, text="📊 STATISTIQUES",
                        font=("Arial", 16, "bold"), fg="#FF9800")
        title.pack(pady=10)

        if self.game is None:
            no_game_label = tk.Label(stats_window,
                                   text="Aucune partie en cours.\nCommencez une nouvelle partie pour voir les statistiques.",
                                   font=("Arial", 12))
            no_game_label.pack(pady=20)
        else:
            stats = self.game.get_game_stats()

            # Durée de jeu
            duration_min = int(stats['duration'] // 60)
            duration_sec = int(stats['duration'] % 60)
            duration_label = tk.Label(stats_window,
                                    text=f"⏱️ Durée: {duration_min}min {duration_sec}s",
                                    font=("Arial", 12))
            duration_label.pack(pady=5)

            # Nombre de tours
            turns_label = tk.Label(stats_window,
                                 text=f"🔄 Tours joués: {stats['total_turns']}",
                                 font=("Arial", 12))
            turns_label.pack(pady=5)

            # Pions terminés par joueur
            finished_frame = tk.Frame(stats_window)
            finished_frame.pack(pady=10)

            tk.Label(finished_frame, text="🏁 Pions terminés:",
                    font=("Arial", 12, "bold")).pack()

            for player_name, count in stats['finished_pieces'].items():
                color = COLORS[COLOR_NAMES.index(player_name)]
                tk.Label(finished_frame, text=f"{player_name}: {count}/4",
                        font=("Arial", 11), fg=color).pack()

        close_button = tk.Button(stats_window, text="Fermer",
                                command=stats_window.destroy,
                                font=("Arial", 12), bg="#666666", fg="white")
        close_button.pack(pady=20)

    def draw_board(self):
        """Dessine le plateau de jeu"""
        # Cases principales (carré extérieur)
        for i in range(15):
            # Ligne supérieure (Rouge)
            color = "#FFCCCC" if i < 6 else "#FFE0E0" if i < 9 else "#FFFFFF"
            self.canvas.create_rectangle(150 + i*30, 150, 180 + i*30, 180, fill=color, outline="black", width=2)

            # Ligne inférieure (Bleu)
            color = "#CCCCFF" if i < 6 else "#E0E0FF" if i < 9 else "#FFFFFF"
            self.canvas.create_rectangle(150 + i*30, 520, 180 + i*30, 550, fill=color, outline="black", width=2)

            # Colonne gauche (Vert)
            color = "#CCFFCC" if i < 6 else "#E0FFE0" if i < 9 else "#FFFFFF"
            self.canvas.create_rectangle(150, 150 + i*30, 180, 180 + i*30, fill=color, outline="black", width=2)

            # Colonne droite (Jaune)
            color = "#FFFFCC" if i < 6 else "#FFFFE0" if i < 9 else "#FFFFFF"
            self.canvas.create_rectangle(520, 150 + i*30, 550, 180 + i*30, fill=color, outline="black", width=2)

        # Cases d'entrée spéciales
        self.canvas.create_rectangle(150, 150, 180, 180, fill="#FF4444", outline="black", width=3)  # Entrée rouge
        self.canvas.create_rectangle(520, 150, 550, 180, fill="#FFFF44", outline="black", width=3)  # Entrée jaune
        self.canvas.create_rectangle(150, 520, 180, 550, fill="#44FF44", outline="black", width=3)  # Entrée verte
        self.canvas.create_rectangle(520, 520, 550, 550, fill="#4444FF", outline="black", width=3)  # Entrée bleue

        # Zones de base (coins)
        # Base rouge (haut-gauche)
        self.canvas.create_rectangle(30, 30, 120, 120, fill="#FFCCCC", outline="#FF4444", width=3)
        self.canvas.create_text(75, 75, text="ROUGE", font=("Arial", 12, "bold"), fill="#FF4444")

        # Base bleue (bas-droite)
        self.canvas.create_rectangle(580, 580, 670, 670, fill="#CCCCFF", outline="#4444FF", width=3)
        self.canvas.create_text(625, 625, text="BLEU", font=("Arial", 12, "bold"), fill="#4444FF")

        # Base jaune (haut-droite)
        self.canvas.create_rectangle(580, 30, 670, 120, fill="#FFFFCC", outline="#FFFF44", width=3)
        self.canvas.create_text(625, 75, text="JAUNE", font=("Arial", 12, "bold"), fill="#FFFF44")

        # Base verte (bas-gauche)
        self.canvas.create_rectangle(30, 580, 120, 670, fill="#CCFFCC", outline="#44FF44", width=3)
        self.canvas.create_text(75, 625, text="VERT", font=("Arial", 12, "bold"), fill="#44FF44")

        # Zone d'arrivée centrale
        self.canvas.create_rectangle(300, 300, 400, 400, fill="#F0F0F0", outline="black", width=3)
        self.canvas.create_text(350, 350, text="ARRIVÉE", font=("Arial", 10, "bold"), fill="black")

        # Chemins d'arrivée colorés
        # Rouge (vers le bas)
        for i in range(5):
            self.canvas.create_rectangle(330, 180 + i*30, 360, 210 + i*30, fill="#FFCCCC", outline="black", width=2)

        # Bleu (vers le haut)
        for i in range(5):
            self.canvas.create_rectangle(330, 490 - i*30, 360, 520 - i*30, fill="#CCCCFF", outline="black", width=2)

        # Jaune (vers la gauche)
        for i in range(5):
            self.canvas.create_rectangle(490 - i*30, 330, 520 - i*30, 360, fill="#FFFFCC", outline="black", width=2)

        # Vert (vers la droite)
        for i in range(5):
            self.canvas.create_rectangle(180 + i*30, 330, 210 + i*30, 360, fill="#CCFFCC", outline="black", width=2)

    def update_display(self):
        """Met à jour l'affichage du jeu"""
        if self.game is None:
            return

        # Effacer les pions existants
        self.canvas.delete("piece")

        # Dessiner les pions
        for player_idx, player in enumerate(self.game.players):
            color = COLORS[player_idx]
            for piece in player.pieces:
                x, y = self.get_piece_position(player, piece)
                self.canvas.create_oval(x-12, y-12, x+12, y+12, fill=color, outline="black", width=2,
                                      tags=("piece", f"piece_{player_idx}_{piece.index}"))

        # Mettre à jour le label du joueur
        current_player = self.game.players[self.game.current]
        self.player_label.config(text=f"Tour de {current_player.name}", fg=COLORS[self.game.current])

        # Activer/désactiver le bouton de lancer
        if self.roll_value is None:
            self.roll_button.config(state="normal")
        else:
            self.roll_button.config(state="disabled")

    def get_piece_position(self, player, piece):
        """Calcule la position d'un pion sur le canvas"""
        player_idx = COLOR_NAMES.index(player.name)

        if piece.is_base():
            if player.name == "Rouge":
                base_positions = [(50, 50), (90, 50), (50, 90), (90, 90)]
                return base_positions[piece.index - 1]
            elif player.name == "Bleu":
                base_positions = [(600, 600), (640, 600), (600, 640), (640, 640)]
                return base_positions[piece.index - 1]
            elif player.name == "Jaune":
                base_positions = [(600, 50), (640, 50), (600, 90), (640, 90)]
                return base_positions[piece.index - 1]
            else:  # Vert
                base_positions = [(50, 600), (90, 600), (50, 640), (90, 640)]
                return base_positions[piece.index - 1]
        elif piece.is_finished():
            # Positions dans la zone d'arrivée centrale
            center_positions = [
                (320, 320), (350, 320), (380, 320), (320, 350),
                (350, 350), (380, 350), (320, 380), (380, 380),
                (330, 330), (370, 330), (330, 370), (370, 370),
                (340, 340), (360, 340), (340, 360), (360, 360)
            ]
            base_idx = player_idx * 4
            return center_positions[base_idx + piece.index - 1]
        else:
            # Position sur la piste
            if piece.distance <= TOTAL_MAIN_SQUARES:
                position = player.get_board_position_for_distance(piece.distance)
                return self.get_board_coordinates(position)
            else:
                # Dans le chemin d'arrivée
                home_step = piece.distance - TOTAL_MAIN_SQUARES
                if player.name == "Rouge":
                    return (345, 195 + (home_step - 1) * 30)
                elif player.name == "Bleu":
                    return (345, 505 - (home_step - 1) * 30)
                elif player.name == "Jaune":
                    return (505 - (home_step - 1) * 30, 345)
                else:  # Vert
                    return (195 + (home_step - 1) * 30, 345)

    def get_board_coordinates(self, position):
        """Convertit une position de plateau en coordonnées canvas"""
        # Cases du plateau circulaire
        if position < 6:  # Ligne supérieure (Rouge)
            return (165 + position * 30, 165)
        elif position < 12:  # Colonne droite supérieure (Jaune)
            return (535, 165 + (position - 5) * 30)
        elif position < 18:  # Ligne droite (Bleu)
            return (535 - (position - 11) * 30, 535)
        elif position < 24:  # Colonne gauche inférieure (Vert)
            return (165, 535 - (position - 17) * 30)
        elif position < 30:  # Ligne inférieure (Bleu)
            return (165 + (position - 23) * 30, 535)
        elif position < 36:  # Colonne gauche supérieure (Rouge)
            return (165, 165 + (position - 29) * 30)
        elif position < 42:  # Ligne supérieure droite (Jaune)
            return (535 - (position - 35) * 30, 165)
        elif position < 48:  # Colonne droite inférieure (Bleu)
            return (535, 535 - (position - 41) * 30)
        else:  # Ligne inférieure gauche (Vert)
            return (165 + (position - 47) * 30, 535)

    def roll_die(self):
        """Lance le dé et gère le tour du joueur"""
        if self.roll_value is not None or self.game is None:
            return

        self.roll_value = self.game.roll_die()
        self.roll_label.config(text=f"🎲 Résultat du dé: {self.roll_value} 🎲", fg=COLORS[self.game.current])

        player = self.game.players[self.game.current]
        board = self.game.build_board()
        self.moves = player.valid_moves(self.roll_value, board)

        if not self.moves:
            messagebox.showinfo("Aucun mouvement possible",
                              f"{player.name}, aucun mouvement valide possible avec {self.roll_value}.\nTour suivant.")
            self.next_turn()
            return

        # Afficher les mouvements possibles
        self.show_possible_moves()

        # Lier les clics sur les pions du joueur actuel
        for player_idx, player in enumerate(self.game.players):
            for piece in player.pieces:
                if player_idx == self.game.current:  # Seulement les pions du joueur actuel
                    self.canvas.tag_bind(f"piece_{player_idx}_{piece.index}", "<Button-1>", lambda e, p=piece: self.select_piece(p))
                    # Mettre en évidence les pions jouables
                    if piece in [p for p, _ in self.moves]:
                        x, y = self.get_piece_position(player, piece)
                        self.canvas.create_oval(x-15, y-15, x+15, y+15, fill="", outline=COLORS[player_idx], width=3, tags="highlight")

        messagebox.showinfo(f"Tour de {player.name}",
                          f"{player.name}, vous avez obtenu {self.roll_value} !\n"
                          f"Cliquez sur un de vos pions surlignés pour le déplacer.")

    def show_possible_moves(self):
        """Affiche visuellement les mouvements possibles"""
        self.canvas.delete("possible_move")
        player = self.game.players[self.game.current]

        for piece, target in self.moves:
            if target == "enter":
                # Montrer la case d'entrée
                x, y = self.get_board_coordinates(player.entry_index)
                self.canvas.create_oval(x-8, y-8, x+8, y+8, fill="yellow", outline="black", width=2, tags="possible_move")
            else:
                # Montrer la position cible
                if target <= TOTAL_MAIN_SQUARES:
                    position = player.get_board_position_for_distance(target)
                    x, y = self.get_board_coordinates(position)
                    self.canvas.create_oval(x-8, y-8, x+8, y+8, fill="yellow", outline="black", width=2, tags="possible_move")
                else:
                    # Position dans le chemin d'arrivée
                    home_step = target - TOTAL_MAIN_SQUARES
                    if player.name == "Rouge":
                        x, y = (345, 195 + (home_step - 1) * 30)
                    elif player.name == "Bleu":
                        x, y = (345, 505 - (home_step - 1) * 30)
                    elif player.name == "Jaune":
                        x, y = (505 - (home_step - 1) * 30, 345)
                    else:  # Vert
                        x, y = (195 + (home_step - 1) * 30, 345)
                    self.canvas.create_oval(x-8, y-8, x+8, y+8, fill="yellow", outline="black", width=2, tags="possible_move")

    def select_piece(self, piece):
        """Gère la sélection d'un pion par le joueur"""
        if self.roll_value is None or not self.moves or self.game is None:
            return

        player = self.game.players[self.game.current]
        if piece not in [p for p, _ in self.moves]:
            messagebox.showerror("Pion invalide", f"Ce pion de {player.name} ne peut pas être déplacé avec {self.roll_value}.")
            return

        # Trouver le mouvement correspondant
        for p, target in self.moves:
            if p == piece:
                self.execute_move(piece, target)
                break

    def execute_move(self, piece, target):
        """Exécute le mouvement d'un pion"""
        player = self.game.players[self.game.current]

        # Effacer les surlignages
        self.canvas.delete("highlight")
        self.canvas.delete("possible_move")

        # Calculer les positions avant et après
        start_pos = self.get_piece_position(player, piece)

        if target == "enter":
            piece.enter()
            target_position = player.get_board_position_for_distance(piece.distance)
            captured = self.game.capture_opponent(target_position, player)
            message = f"🎉 {player.name} sort un pion en jeu !"
        else:
            piece.move(self.roll_value)
            if piece.is_finished():
                message = f"🏁 {player.name} a amené un pion à l'arrivée !"
                player.score += 10  # Points pour arrivée
            elif piece.distance <= TOTAL_MAIN_SQUARES:
                target_position = player.get_board_position_for_distance(piece.distance)
                captured = self.game.capture_opponent(target_position, player)
                if captured:
                    message = f"⚔️ {player.name} capture un pion adverse !"
                    player.score += 5  # Points pour capture
                else:
                    message = f"➡️ {player.name} déplace un pion."
            else:
                home_step = piece.distance - TOTAL_MAIN_SQUARES
                message = f"🏠 {player.name} avance dans le chemin d'arrivée ({home_step}/6)."

        # Animation du mouvement
        end_pos = self.get_piece_position(player, piece)
        self.animate_move(piece, start_pos, end_pos)

        # Mettre à jour l'affichage
        self.update_display()

        # Afficher le message de mouvement
        self.show_message(message)

        # Incrémenter les compteurs
        player.turns_played += 1
        self.game.total_turns += 1

        # Vérifier la victoire
        if player.finished_count() == PIECES_PER_PLAYER:
            messagebox.showinfo("🎉 VICTOIRE !",
                              f"🎊 Félicitations {player.name} ! Vous avez gagné la partie ! 🎊\n"
                              f"Score final: {player.score} points")
            self.show_final_stats()
            return

        self.next_turn()

    def animate_move(self, piece, start_pos, end_pos):
        """Anime le mouvement d'un pion"""
        if start_pos == end_pos:
            return  # Pas de mouvement à animer

        # Nombre d'étapes d'animation
        steps = 10
        dx = (end_pos[0] - start_pos[0]) / steps
        dy = (end_pos[1] - start_pos[1]) / steps

        player_idx = COLOR_NAMES.index(self.game.players[self.game.current].name)
        piece_tag = f"piece_{player_idx}_{piece.index}"

        def animate_step(step_num):
            if step_num >= steps:
                return

            # Calculer la nouvelle position
            current_x = start_pos[0] + dx * step_num
            current_y = start_pos[1] + dy * step_num

            # Effacer l'ancien pion et en dessiner un nouveau
            self.canvas.delete(piece_tag)
            color = COLORS[player_idx]
            self.canvas.create_oval(current_x-12, current_y-12, current_x+12, current_y+12,
                                  fill=color, outline="black", width=2, tags=piece_tag)

            # Programmer l'étape suivante
            self.root.after(self.animation_speed, lambda: animate_step(step_num + 1))

        # Démarrer l'animation
        animate_step(0)

        # Attendre que l'animation se termine
        self.root.after(self.animation_speed * steps + 50)

    def show_message(self, message):
        """Affiche un message temporaire sur le canvas"""
        # Créer un label temporaire
        msg_label = tk.Label(self.root, text=message, font=("Arial", 12, "bold"),
                           fg=COLORS[self.game.current], bg="#FFFFE0", relief="solid")
        msg_label.pack(pady=5)

        # Supprimer le message après 3 secondes
        self.root.after(3000, msg_label.destroy)

    def next_turn(self):
        """Passe au tour suivant"""
        if self.roll_value != 6:
            self.game.current = (self.game.current + 1) % len(self.game.players)

        self.roll_value = None
        self.moves = []
        self.selected_piece = None
        self.roll_label.config(text="🎲 Résultat du dé: - 🎲", fg="black")
        self.update_display()

        # Réactiver le bouton de lancer
        self.roll_button.config(state="normal")

    def show_final_stats(self):
        """Affiche les statistiques finales de la partie"""
        stats = self.game.get_game_stats()

        stats_window = tk.Toplevel(self.root)
        stats_window.title("Résultats de la Partie")
        stats_window.geometry("500x400")

        title = tk.Label(stats_window, text="🎊 RÉSULTATS FINAUX",
                        font=("Arial", 18, "bold"), fg="#4CAF50")
        title.pack(pady=15)

        # Durée et tours
        duration_min = int(stats['duration'] // 60)
        duration_sec = int(stats['duration'] % 60)

        info_frame = tk.Frame(stats_window)
        info_frame.pack(pady=10)

        tk.Label(info_frame, text=f"⏱️ Durée de la partie: {duration_min}min {duration_sec}s",
                font=("Arial", 12)).pack()
        tk.Label(info_frame, text=f"🔄 Nombre total de tours: {stats['total_turns']}",
                font=("Arial", 12)).pack()

        # Scores par joueur
        scores_frame = tk.Frame(stats_window)
        scores_frame.pack(pady=15)

        tk.Label(scores_frame, text="🏆 SCORES FINAUX",
                font=("Arial", 14, "bold")).pack(pady=5)

        # Trier les joueurs par score décroissant
        sorted_players = sorted(stats['player_scores'].items(), key=lambda x: x[1], reverse=True)

        for i, (player_name, score) in enumerate(sorted_players, 1):
            color = COLORS[COLOR_NAMES.index(player_name)]
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
            tk.Label(scores_frame, text=f"{medal} {player_name}: {score} points",
                    font=("Arial", 12, "bold"), fg=color).pack()

        # Boutons
        button_frame = tk.Frame(stats_window)
        button_frame.pack(pady=20)

        new_game_button = tk.Button(button_frame, text="🎮 Nouvelle Partie",
                                   command=lambda: [stats_window.destroy(), self.start_new_game()],
                                   font=("Arial", 12), bg="#4CAF50", fg="white", padx=15, pady=8)
        new_game_button.pack(side=tk.LEFT, padx=10)

        menu_button = tk.Button(button_frame, text="🏠 Menu Principal",
                               command=lambda: [stats_window.destroy(), self.show_main_menu()],
                               font=("Arial", 12), bg="#666666", fg="white", padx=15, pady=8)
        menu_button.pack(side=tk.LEFT, padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = LudoGUI(root)
    root.mainloop()