import unittest
from unittest.mock import patch

import ludo

class TestLudoLogic(unittest.TestCase):
    def test_piece_enter_sets_active(self):
        piece = ludo.Piece(1)
        self.assertTrue(piece.is_base())
        piece.enter()
        self.assertTrue(piece.is_active())
        self.assertEqual(piece.distance, 1)

    def test_piece_move_finishes_when_reaching_total(self):
        piece = ludo.Piece(1)
        piece.status = "active"
        piece.distance = ludo.TOTAL_STEPS - 2
        piece.move(4)
        self.assertTrue(piece.is_finished())
        self.assertEqual(piece.distance, ludo.TOTAL_STEPS)

    def test_player_valid_moves_allows_enter_on_six(self):
        player = ludo.Player("Rouge", ludo.ENTRY_INDEX[0])
        board = {}
        moves = player.valid_moves(6, board)
        self.assertEqual(len(moves), 1)
        piece, target = moves[0]
        self.assertEqual(piece.index, 1)
        self.assertEqual(target, "enter")

    def test_player_valid_moves_prevents_enter_when_entry_occupied(self):
        player = ludo.Player("Rouge", ludo.ENTRY_INDEX[0])
        other_piece = ludo.Piece(2)
        other_piece.status = "active"
        other_piece.distance = 1
        board = {ludo.ENTRY_INDEX[0]: [(player, other_piece)]}

        moves = player.valid_moves(6, board)
        self.assertEqual(len(moves), 0)

    def test_capture_opponent_resets_piece(self):
        game = ludo.Game()
        red = game.players[0]
        blue = game.players[1]

        red_piece = red.pieces[0]
        blue_piece = blue.pieces[0]
        red_piece.enter()
        blue_piece.enter()

        # Placer le pion bleu sur la même case que le pion rouge
        # Calculer une distance pour bleu qui lui donnera la position 0 sur le plateau
        blue_piece.distance = 40
        captured = game.capture_opponent(red.get_board_position_for_distance(red_piece.distance), red)

        self.assertTrue(captured)
        self.assertTrue(blue_piece.is_base())
        self.assertEqual(blue_piece.distance, 0)

    @patch('time.time', side_effect=[1000.0, 1005.0])
    def test_game_stats_returns_expected_keys(self, mock_time):
        game = ludo.Game()
        game.total_turns = 3
        stats = game.get_game_stats()

        self.assertIn('duration', stats)
        self.assertIn('total_turns', stats)
        self.assertIn('player_scores', stats)
        self.assertIn('finished_pieces', stats)
        self.assertEqual(stats['duration'], 5.0)
        self.assertEqual(stats['total_turns'], 3)
        self.assertIsInstance(stats['player_scores'], dict)
        self.assertIsInstance(stats['finished_pieces'], dict)

    @patch('random.randint', return_value=6)
    def test_roll_die_returns_six(self, mock_randint):
        game = ludo.Game()
        self.assertEqual(game.roll_die(), 6)

if __name__ == '__main__':
    unittest.main()
