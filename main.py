# project_folder/main.py

import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QMessageBox
)
from treys import Evaluator, Deck

from cards import Player, Flop
from helpers import card_to_image_path
from probability import calculate_win_probability


class PokerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Poker Win Probability Calculator")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: #35654d")

        self.deck = Deck()
        self.evaluator = Evaluator()
        self.num_opponents = 7  # Total 8 players

        self.players = [Player() for _ in range(8)]
        self.flop = Flop()
        self.turn = []
        self.river = []

        self.init_ui()
        self.deal_initial()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Hero Hand
        hero_layout = QHBoxLayout()
        hero_label = QLabel("Hero Hand:")
        hero_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        hero_layout.addWidget(hero_label)
        self.hero_card_labels = [QLabel(), QLabel()]
        for label in self.hero_card_labels:
            label.setFixedSize(100, 145)
            label.setScaledContents(True)
            hero_layout.addWidget(label)
        main_layout.addLayout(hero_layout)

        # Community Cards
        community_layout = QHBoxLayout()
        community_label = QLabel("Community Cards:")
        community_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        community_layout.addWidget(community_label)
        self.community_card_labels = []
        for _ in range(5):
            label = QLabel()
            label.setFixedSize(100, 145)
            label.setScaledContents(True)
            label.setStyleSheet("border: 1px solid black;")
            placeholder_pixmap = QPixmap(
                "graphics/cards/back.png")  # Update with the correct path to your placeholder image
            if placeholder_pixmap.isNull():
                label.setStyleSheet("border: 1px solid black; background-color: gray;")  # Fallback style
            else:
                label.setPixmap(placeholder_pixmap)
            self.community_card_labels.append(label)
            community_layout.addWidget(label)
        main_layout.addLayout(community_layout)

        # Probabilities
        prob_layout = QVBoxLayout()
        self.preflop_label = QLabel("Pre-Flop Win Probability: N/A")
        self.preflop_label.setStyleSheet("font-size: 14px; font-weight: bold")
        self.postflop_label = QLabel("Post-Flop Win Probability: N/A")
        self.postflop_label.setStyleSheet("font-size: 14px; font-weight: bold")
        self.after_turn_label = QLabel("After Turn Win Probability: N/A")
        self.after_turn_label.setStyleSheet("font-size: 14px; font-weight: bold")
        self.after_river_label = QLabel("After River Win Probability: N/A")
        self.after_river_label.setStyleSheet("font-size: 14px; font-weight: bold")
        prob_layout.addWidget(self.preflop_label)
        prob_layout.addWidget(self.postflop_label)
        prob_layout.addWidget(self.after_turn_label)
        prob_layout.addWidget(self.after_river_label)
        main_layout.addLayout(prob_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.deal_flop_btn = QPushButton("Deal Flop")
        self.deal_flop_btn.setStyleSheet("background-color: #005f64")
        self.deal_flop_btn.clicked.connect(self.deal_flop)
        self.deal_turn_btn = QPushButton("Deal Turn")
        self.deal_turn_btn.setStyleSheet("background-color: #005f64")
        self.deal_turn_btn.clicked.connect(self.deal_turn)
        self.deal_river_btn = QPushButton("Deal River")
        self.deal_river_btn.setStyleSheet("background-color: #005f64")
        self.deal_river_btn.clicked.connect(self.deal_river)
        self.reset_btn = QPushButton("Reset Game")
        self.reset_btn.setStyleSheet("background-color: #5a0a21")
        self.reset_btn.clicked.connect(self.reset_game)
        button_layout.addWidget(self.deal_flop_btn)
        button_layout.addWidget(self.deal_turn_btn)
        button_layout.addWidget(self.deal_river_btn)
        button_layout.addWidget(self.reset_btn)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def deal_initial(self):
        # Deal two hole cards to hero
        hero = self.players[0]
        hero.cards = self.deck.draw(2)
        self.update_card_labels(self.hero_card_labels, hero.cards)

        # Calculate Pre-Flop Probability
        self.calculate_and_display_probabilities()

    def deal_flop(self):
        if self.flop.cards:
            QMessageBox.warning(self, "Warning", "Flop already dealt!")
            return
        self.flop.generate_flop(self.deck)
        self.update_card_labels(self.community_card_labels, self.flop.cards, start=0)
        self.calculate_and_display_probabilities()

    def deal_turn(self):
        if not self.flop.cards:
            QMessageBox.warning(self, "Warning", "Deal the flop first!")
            return
        if self.turn:
            QMessageBox.warning(self, "Warning", "Turn already dealt!")
            return
        self.turn = self.deck.draw(1)
        self.update_card_labels(self.community_card_labels, self.turn, start=3)
        self.calculate_and_display_probabilities()

    def deal_river(self):
        if not self.turn:
            QMessageBox.warning(self, "Warning", "Deal the turn first!")
            return
        if self.river:
            QMessageBox.warning(self, "Warning", "River already dealt!")
            return
        self.river = self.deck.draw(1)
        self.update_card_labels(self.community_card_labels, self.river, start=4)
        self.calculate_and_display_probabilities()

    def reset_game(self):
        self.deck = Deck()
        self.evaluator = Evaluator()
        self.players = [Player() for _ in range(8)]
        self.flop = Flop()
        self.turn = []
        self.river = []
        self.clear_card_labels()
        self.deal_initial()

    def update_card_labels(self, labels, cards, start=0):
        for i, card in enumerate(cards):
            if start + i < len(labels):
                pixmap = QPixmap(card_to_image_path(card))
                if pixmap.isNull():
                    pixmap = QPixmap("graphics/cards/back.png")  # Placeholder for missing images
                labels[start + i].setPixmap(pixmap)

    def clear_card_labels(self):
        for label in self.hero_card_labels:
            label.clear()
        for label in self.community_card_labels:
            placeholder_pixmap = QPixmap(
                "graphics/cards/back.png")  # Update with the correct path to your placeholder image
            label.setPixmap(placeholder_pixmap)
            
    def calculate_and_display_probabilities(self):
        hero = self.players[0]
        hero_cards = hero.cards
        community_cards = self.flop.cards + self.turn + self.river

        # Pre-Flop Probability
        if not self.flop.cards and not self.turn and not self.river:
            preflop_prob = calculate_win_probability(
                hero_cards, [], self.num_opponents, self.evaluator, num_simulations=10000
            )
            self.preflop_label.setText(f"Pre-Flop Win Probability: {preflop_prob:.4f}")
            self.postflop_label.setText("Post-Flop Win Probability: N/A")
            self.after_turn_label.setText("After Turn Win Probability: N/A")
            self.after_river_label.setText("After River Win Probability: N/A")
            return

        # Post-Flop Probability
        if len(self.flop.cards) == 3 and not self.turn and not self.river:
            postflop_prob = calculate_win_probability(
                hero_cards, self.flop.cards, self.num_opponents, self.evaluator, num_simulations=10000
            )
            self.postflop_label.setText(f"Post-Flop Win Probability: {postflop_prob:.4f}")
            self.after_turn_label.setText("After Turn Win Probability: N/A")
            self.after_river_label.setText("After River Win Probability: N/A")
            return

        # After Turn Probability
        if len(self.flop.cards) == 3 and len(self.turn) == 1 and not self.river:
            community_after_turn = self.flop.cards + self.turn
            after_turn_prob = calculate_win_probability(
                hero_cards, community_after_turn, self.num_opponents, self.evaluator, num_simulations=10000
            )
            self.after_turn_label.setText(f"After Turn Win Probability: {after_turn_prob:.4f}")
            self.after_river_label.setText("After River Win Probability: N/A")
            return

        # After River Probability
        if len(self.flop.cards) == 3 and len(self.turn) == 1 and len(self.river) == 1:
            community_full = self.flop.cards + self.turn + self.river
            after_river_prob = calculate_win_probability(
                hero_cards, community_full, self.num_opponents, self.evaluator, num_simulations=10000
            )
            self.after_river_label.setText(f"After River Win Probability: {after_river_prob:.4f}")
            return

class PokerApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = PokerUI()
        self.window.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    PokerApp()
