"""
PRIMARY-SOURCE EVIDENCE — Shogi4 game logic, decompiled.

Source: official Oca Studios app `com.ocastudios.shogi4` v1.0.1 (2014), a Kivy/pygame
build. The APK ships its payload as a gzipped tar disguised as assets/private.mp3;
inside, the Python 2.7 bytecode logic.pyo was decompiled with uncompyle6.
Original dev path (from the bytecode header): .../Ocastudios/Android/Kivy/shogi4/logic.py
Oca releases all work into the PUBLIC DOMAIN, so this is reproduced freely.

This file is the authoritative ruleset: get_possible_squares() defines every piece
movement and the friendly-jump; fake_take_square() defines mandatory promotion;
capture() defines the win (king capture); can_take_square() defines drop legality.
"""

# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.14.5 (main, May 10 2026, 10:21:34) [Clang 21.0.0 (clang-2100.0.123.102)]
# Embedded file name: /home/isac/Documents/Ocastudios/Android/Kivy/shogi4/.buildozer/android/app/logic.py
# Compiled at: 2014-11-15 13:47:35
from kivy.animation import *
from kivy.clock import Clock
from math import sqrt
import random
from functools import partial
import g, ocanim as oa, os

def get_piece(square):
    if square == None:
        return
    else:
        return square.piece


def get_square_by_code(code):
    if code[0] < 1 or code[1] < 1:
        return None
    if code[0] > 4 or code[1] > 4:
        return None
    key = str(code[0]) + str(code[1])
    return g.square_dict[key]


def get_possible_squares(piece, exception_list=[]):
    if piece.square.__class__.__name__ == 'farmSquare':
        return g.square_list[:]
    else:
        possible_squares = []
        current_code = piece.square.code
        sq_L = get_square_by_code([current_code[0] - 1, current_code[1]])
        sq_R = get_square_by_code([current_code[0] + 1, current_code[1]])
        sq_T = get_square_by_code([current_code[0], current_code[1] + 1])
        sq_B = get_square_by_code([current_code[0], current_code[1] - 1])
        sq_TL = get_square_by_code([current_code[0] - 1, current_code[1] + 1])
        sq_TR = get_square_by_code([current_code[0] + 1, current_code[1] + 1])
        sq_BL = get_square_by_code([current_code[0] - 1, current_code[1] - 1])
        sq_BR = get_square_by_code([current_code[0] + 1, current_code[1] - 1])
        sq_FL = get_square_by_code([current_code[0] - 2, current_code[1]])
        sq_FR = get_square_by_code([current_code[0] + 2, current_code[1]])
        sq_FT = get_square_by_code([current_code[0], current_code[1] + 2])
        sq_FB = get_square_by_code([current_code[0], current_code[1] - 2])
        sq_FTL = get_square_by_code([current_code[0] - 2, current_code[1] + 2])
        sq_FTR = get_square_by_code([current_code[0] + 2, current_code[1] + 2])
        sq_FBL = get_square_by_code([current_code[0] - 2, current_code[1] - 2])
        sq_FBR = get_square_by_code([current_code[0] + 2, current_code[1] - 2])
        if piece.animal in ('king', 'fox'):
            possible_squares += [sq_L, sq_R, sq_T, sq_B]
            other = get_piece(sq_L)
            if other != None:
                if piece.is_allied(other):
                    if other not in exception_list:
                        possible_squares.append(sq_FL)
            other = get_piece(sq_R)
            if other != None:
                if piece.is_allied(other):
                    if other not in exception_list:
                        possible_squares.append(sq_FR)
            other = get_piece(sq_T)
            if other != None:
                if piece.is_allied(other):
                    if other not in exception_list:
                        possible_squares.append(sq_FT)
            other = get_piece(sq_B)
            if other != None:
                if piece.is_allied(other):
                    if other not in exception_list:
                        possible_squares.append(sq_FB)
        if piece.animal in ('king', 'raccoon'):
            possible_squares += [sq_TL, sq_TR, sq_BL, sq_BR]
            other = get_piece(sq_TL)
            if other != None:
                if piece.is_allied(other):
                    if other not in exception_list:
                        possible_squares.append(sq_FTL)
            other = get_piece(sq_TR)
            if other != None:
                if piece.is_allied(other):
                    if other not in exception_list:
                        possible_squares.append(sq_FTR)
            other = get_piece(sq_BL)
            if other != None:
                if piece.is_allied(other):
                    if other not in exception_list:
                        possible_squares.append(sq_FBL)
            other = get_piece(sq_BR)
            if other != None:
                if piece.is_allied(other):
                    if other not in exception_list:
                        possible_squares.append(sq_FBR)
        if piece.animal in ('carp', ):
            if piece.owner == 'player_1':
                possible_squares.append(sq_T)
                other = get_piece(sq_T)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FT)
            else:
                possible_squares.append(sq_B)
                other = get_piece(sq_B)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FB)
        if piece.animal in ('tapir', 'koi', 'tanuki', 'kitsune', 'baku'):
            if piece.owner == 'player_1':
                possible_squares.append(sq_T)
                other = get_piece(sq_T)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FT)
                possible_squares.append(sq_TL)
                other = get_piece(sq_TL)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FTL)
                possible_squares.append(sq_TR)
                other = get_piece(sq_TR)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FTR)
            else:
                possible_squares.append(sq_B)
                other = get_piece(sq_B)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FB)
                possible_squares.append(sq_BL)
                other = get_piece(sq_BL)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FBL)
                possible_squares.append(sq_BR)
                other = get_piece(sq_BR)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FBR)
        if piece.animal in ('koi', 'tanuki', 'baku'):
            if piece.owner == 'player_1':
                possible_squares.append(sq_BL)
                other = get_piece(sq_BL)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FBL)
                possible_squares.append(sq_BR)
                other = get_piece(sq_BR)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FBR)
            else:
                possible_squares.append(sq_TL)
                other = get_piece(sq_TL)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FTL)
                possible_squares.append(sq_TR)
                other = get_piece(sq_TR)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FTR)
        if piece.animal in ('kitsune', ):
            possible_squares.append(sq_L)
            other = get_piece(sq_L)
            if other != None:
                if piece.is_allied(other):
                    if other not in exception_list:
                        possible_squares.append(sq_FL)
            possible_squares.append(sq_R)
            other = get_piece(sq_R)
            if other != None:
                if piece.is_allied(other):
                    if other not in exception_list:
                        possible_squares.append(sq_FR)
            if piece.owner == 'player_1':
                possible_squares.append(sq_B)
                other = get_piece(sq_B)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FB)
            else:
                possible_squares.append(sq_T)
                other = get_piece(sq_T)
                if other != None:
                    if piece.is_allied(other):
                        if other not in exception_list:
                            possible_squares.append(sq_FT)
        possible_squares = filter(None, possible_squares)
        return possible_squares


def can_capture_square(piece, square, exception_list):
    if piece.square == square:
        return False
    else:
        if piece.square.__class__.__name__ == 'farmSquare':
            return False
        if square.piece != None and square.piece not in exception_list:
            if square.piece.owner == piece.owner:
                return False
        possible_squares = get_possible_squares(piece)
        if square not in possible_squares:
            return False
        return 'OK'


def can_take_square(piece, square):
    if piece.square == square:
        return g.xml_root[4][0].text
    else:
        possible_squares = get_possible_squares(piece)
        if square not in possible_squares:
            return g.xml_root[4][1].text
        if square.piece != None:
            if square.piece.owner == piece.owner:
                return g.xml_root[4][2].text
        if piece.square.__class__.__name__ == 'farmSquare':
            if piece.owner == 'player_1':
                code_list = [
                 [
                  1, 4], [2, 4], [3, 4], [4, 4]]
            else:
                code_list = [
                 [
                  1, 1], [2, 1], [3, 1], [4, 1]]
            if square.code in code_list:
                return g.xml_root[4][3].text
            if square.piece != None:
                if square.piece.owner != piece.owner:
                    return g.xml_root[4][4].text
        return 'OK'


def is_square_in_check_by_player(square, player, exception_list):
    is_in_check = False
    menace = []
    for piece in g.pieces:
        if piece != None:
            if piece.owner == player:
                if piece not in exception_list:
                    if can_capture_square(piece, square, exception_list) == 'OK':
                        is_in_check = True
                        menace.append(piece)

    return menace


def get_closest_square(position):
    square_selected = None
    closest_distance = 100 * g.scale
    i = 0
    for square in g.square_list:
        i += 1
        distance = sqrt((square.pos[0] - position[0]) ** 2 + (square.pos[1] - position[1]) ** 2)
        if distance < closest_distance:
            closest_distance = distance
            square_selected = square

    return square_selected


def capture(piece):
    if piece.animal == 'king':
        oa.fade_out(piece)
        g.game_over = True
    else:
        if piece.owner == 'player_1':
            piece.owner = 'player_2'
            piece.rotation = 180
        else:
            piece.owner = 'player_1'
            piece.rotation = 0
        farm = get_farm(piece.owner, get_original_animal(piece))
        piece.square.piece = None
        piece.square = farm
        farm.pieces.append(piece)
        end_position = (
         farm.pos[0] + g.screen_size[0] / 2 - g.piece_size * g.scale / 2, farm.pos[1] + g.screen_size[1] / 2 - g.piece_size * g.scale / 2)
        animation = Animation(pos=end_position, duration=0.08)
        if piece.promoted or piece.animal in ('koi', 'baku', 'tanuki', 'kitsune'):
            animation.bind(on_complete=piece.demote)
        animation.start(piece)
        piece.on_enter_komadai()
    return


def announce_capture(piece):
    main_screen = g.screens['main']
    if piece.owner == 'player_1':
        output = main_screen.output2
    else:
        output = main_screen.output1
    output.write(g.xml_root[4][11].text + get_name(piece))
    return


def announce_promotion(piece):
    main_screen = g.screens['main']
    if piece.owner == 'player_1':
        output = main_screen.output1
    else:
        output = main_screen.output2
    if piece.animal in ('carp', 'fox', 'raccoon', 'tapir'):
        output.write(g.xml_root[4][12].text + get_name(piece))
    return


def announce_nothing(piece):
    main_screen = g.screens['main']
    if piece.owner == 'player_1':
        main_screen.output1.blank()
    else:
        main_screen.output2.blank()
    return


def announce_move(piece, square):
    if square.piece != None:
        announce_capture(square.piece)
    else:
        if piece.owner == 'player_1':
            code_list = [
             [
              1, 4], [2, 4], [3, 4], [4, 4]]
        else:
            code_list = [
             [
              1, 1], [2, 1], [3, 1], [4, 1]]
        if square.code in code_list:
            if piece.animal == 'king':
                announce_nothing(piece)
            else:
                announce_promotion(piece)
        else:
            announce_nothing(piece)
    return


def get_name(piece):
    r = g.xml_root
    if piece.animal == 'king':
        if piece.owner == 'player_1':
            name = r[5][8]
        else:
            name = r[5][9]
    else:
        name_list = {'carp': (r[5][0]), 'tapir': (r[5][1]), 'raccoon': (r[5][2]), 'fox': (r[5][3]), 'koi': (r[5][4]), 'tanuki': (r[5][6]), 'baku': (r[5][5]), 'kitsune': (r[5][7])}
        name = name_list[piece.animal]
    return name.text


def get_original_animal(piece):
    if piece.animal in ('carp', 'tapir', 'raccoon', 'fox', 'king'):
        return piece.animal
    if piece.animal == 'koi':
        return 'carp'
    if piece.animal == 'baku':
        return 'tapir'
    if piece.animal == 'tanuki':
        return 'raccoon'
    if piece.animal == 'kitsune':
        return 'fox'
    return


def end_turn(arg1=None):
    time = 1.0
    if g.farm_db:
        time = 0.02
    main_screen = g.screens['main']
    if g.game_over:
        Clock.schedule_once(main_screen.end_game)
    else:
        if g.player == 'player_1':
            g.player = 'player_2'
            main_screen.output2.write(g.xml_root[4][5].text)
        else:
            g.player = 'player_1'
            if g.players == 2 or main_screen.output1.label.text == '':
                main_screen.output1.write(g.xml_root[4][5].text)
        if g.players == 1:
            if g.player == 'player_2':
                Clock.schedule_once(auto_play, time)
            elif g.player == 'player_1':
                if g.farm_db == True:
                    Clock.schedule_once(auto_play, time)
        elif g.players == 2:
            pass
    if g.show_piece_data:
        for piece in g.pieces:
            piece.reload_piece_data()

    return


def sort_pieces():
    g.p1 = []
    g.p2 = []
    for piece in g.pieces:
        if piece.owner == 'player_1':
            g.p1.append(piece)
        else:
            g.p2.append(piece)

    return


def auto_play(arg1=None):
    sort_pieces()
    if g.player == 'player_1':
        allied_pieces = g.p1[:]
    else:
        allied_pieces = g.p2[:]
    get_all_moves(allied_pieces)
    return


def get_all_moves(pieces, moves=[], arg1=None, arg2=None):
    list_of_pieces = pieces[:]
    list_of_moves = moves[:]
    piece = list_of_pieces.pop(0)
    squares = get_possible_squares(piece)
    for square in squares:
        if can_take_square(piece, square) == 'OK':
            list_of_moves.append([piece, square])

    if len(list_of_pieces) > 0:
        Clock.schedule_once(partial(get_all_moves, list_of_pieces, list_of_moves))
    else:
        Clock.schedule_once(partial(resume_auto_play, list_of_moves))
    return


def resume_auto_play(possible_moves, arg1=None):
    sort_pieces()
    if g.player == 'player_1':
        allied_pieces = g.p1[:]
        opponent = 'player_2'
    else:
        allied_pieces = g.p2[:]
        opponent = 'player_1'
    allied_king = None
    for piece in allied_pieces:
        if piece.animal == 'king':
            allied_king = piece

    chosen_move = None
    loop_moves = possible_moves[:]
    for move in loop_moves:
        if move[1].piece != None:
            if move[1].piece.animal == 'king':
                chosen_move = move
                print 'Auto_play (', len(g.moves_history['player_2']), '): capture', chosen_move
                break
        if move[0].animal == 'king':
            if is_square_in_check_by_player(move[1], opponent, [move[1].piece]) != []:
                if len(possible_moves) > 1:
                    possible_moves.remove(move)

    Clock.schedule_once(partial(resume_auto_play2, possible_moves, chosen_move))
    return


def resume_auto_play2(possible_moves, chosen_move, arg1=None):
    sort_pieces()
    if g.player == 'player_1':
        allied_pieces = g.p1[:]
        opponent = 'player_2'
    else:
        allied_pieces = g.p2[:]
        opponent = 'player_1'
    allied_king = None
    for piece in allied_pieces:
        if piece.animal == 'king':
            allied_king = piece

    king_in_check = False
    if is_square_in_check_by_player(allied_king.square, opponent, []) != []:
        king_in_check = True
    if king_in_check and chosen_move == None:
        for move in possible_moves[:]:
            if move[0].square.__class__.__name__ == 'farmSquare':
                if len(possible_moves) > 1:
                    possible_moves.remove(move)
            else:
                fake_list = fake_take_square(move[0], move[1])
                if is_square_in_check_by_player(allied_king.square, opponent, [move[1].piece]) != []:
                    if len(possible_moves) > 1:
                        possible_moves.remove(move)
                undo_fake(fake_list)

    if chosen_move == None:
        if g.difficulty == 'easy':
            temerity = g.temerity[0]
        elif g.difficulty == 'normal':
            temerity = g.temerity[1]
        elif g.difficulty == 'hard':
            temerity = g.temerity[2]
        random_roll = random.random()
        if random_roll < temerity:
            chosen_move = random.choice(possible_moves)
            print 'Auto_play (', len(g.moves_history['player_2']), '): temerity', chosen_move
        else:
            return_moves = choose_moves_db_txt(possible_moves[:], state=None, processed=[])
            if g.difficulty == 'easy':
                moves_to_chose = return_moves[:6]
            elif g.difficulty == 'normal':
                moves_to_chose = return_moves[:4]
            elif g.difficulty == 'hard':
                moves_to_chose = return_moves[:2]
            list_of_ranks = ''
            for move in return_moves:
                list_of_ranks += str(move[0])

            final_list = []
            for move in moves_to_chose:
                counter = move[0]
                while counter:
                    final_list.append(move)
                    counter -= 1

            chosen = random.choice(final_list)
            chosen_move = chosen[1]
            print 'Auto_play (', len(g.moves_history['player_2']), '): from database', chosen_move
    if chosen_move[1].piece != None:
        capture(chosen_move[1].piece)
    chosen_move[0].take_square(chosen_move[1])
    remember_state()
    Clock.schedule_once(end_turn)
    return


def get_opponent(player):
    if player == 'player_1':
        return 'player_2'
    return 'player_1'


def fake_take_square(piece, newsquare):
    player = piece.owner
    opponent = get_opponent(player)
    oldsquare = piece.square
    enemy = None
    if newsquare.piece:
        enemy = newsquare.piece
    piece.ft_square = piece.square
    piece.ft_animal = piece.animal
    piece.ft_owner = player
    if oldsquare.get_type() == 'Square':
        oldsquare.ft_piece = piece
    newsquare.ft_piece = enemy
    if enemy:
        enemy.ft_square = newsquare
        enemy.ft_owner = opponent
        enemy.ft_animal = enemy.animal
    piece.square = newsquare
    must_promote = False
    if piece.promoted == False:
        if piece.owner == 'player_1':
            goal_squares = [
             [
              1, 4], [2, 4], [3, 4], [4, 4]]
        else:
            goal_squares = [
             [
              1, 1], [2, 1], [3, 1], [4, 1]]
        if newsquare.code in goal_squares:
            must_promote = True
    if must_promote:
        piece.animal = [
         'koi', 'baku', 'tanuki', 'kitsune'][['carp', 'tapir', 'raccoon', 'fox'].index(piece.animal)]
    if oldsquare.get_type() == 'Square':
        oldsquare.piece = None
    elif oldsquare.get_type() == 'farmSquare':
        oldsquare.pieces.remove(piece)
    newsquare.piece = piece
    if enemy:
        farm = 'ops'
        for sq in g.farm[player]:
            if sq.animal == get_original_animal(enemy):
                farm = sq

        farm.pieces.append(enemy)
        enemy.owner = player
        enemy.square = farm
    fake_list = [
     piece, oldsquare, newsquare]
    if enemy != None:
        fake_list.append(enemy)
        fake_list.append(farm)
    return fake_list


def undo_fake(fake_list):
    for item in fake_list:
        if item.__class__.__name__ == 'Piece':
            item.square = item.ft_square
            item.animal = item.ft_animal
            item.owner = item.ft_owner
            del item.ft_square
            del item.ft_animal
            del item.ft_owner
        elif item.__class__.__name__ == 'Square':
            item.piece = item.ft_piece
            del item.ft_piece
        elif item.__class__.__name__ == 'farmSquare':
            if fake_list[1].__class__.__name__ == 'farmSquare':
                item.pieces.append(fake_list[0])
            else:
                item.pieces.remove(fake_list[-2])

    return


def get_farm(player, animal):
    for square in g.farm[player]:
        if square.animal == animal:
            return square

    return


def remember_state():
    game_state = get_game_state()
    g.moves_history[g.player].append(game_state)
    return


def get_game_state():
    list_of_squares = g.farm['player_1'] + g.square_list + g.farm['player_2'][::-1]
    player = g.player
    game_state = ''
    animal_dict = {'king': 'b', 'carp': 'c', 'koi': 'e', 'tapir': 'f', 'baku': 'h', 'raccoon': 'i', 'tanuki': 'k', 'fox': 'l', 'kitsune': 'n'}
    for square in list_of_squares:
        if square.get_type() == 'farmSquare':
            letter = 'a'
            if square.animal == 'carp':
                if len(square.pieces) == 1:
                    letter = 'c'
                elif len(square.pieces) == 2:
                    letter = 'd'
            elif square.animal == 'fox':
                if len(square.pieces) == 1:
                    letter = 'l'
                elif len(square.pieces) == 2:
                    letter = 'm'
            elif square.animal == 'raccoon':
                if len(square.pieces) == 1:
                    letter = 'i'
                elif len(square.pieces) == 2:
                    letter = 'j'
            elif square.animal == 'tapir':
                if len(square.pieces) == 1:
                    letter = 'f'
                elif len(square.pieces) == 2:
                    letter = 'g'
            if square.owner != player:
                if letter != 'a':
                    letter = letter.upper()
            game_state += letter
        else:
            if square.piece == None:
                letter = 'a'
            else:
                letter = animal_dict[square.piece.animal]
                if square.piece.owner != player:
                    letter = letter.upper()
            game_state += letter

    if player == 'player_2':
        game_state = game_state[::-1]
    return game_state


def update_database(arg1=None):
    if g.db_on:
        if g.player == 'player_1':
            win_moves = g.moves_history['player_1'][:]
            lose_moves = g.moves_history['player_2'][:]
        else:
            win_moves = g.moves_history['player_2'][:]
            lose_moves = g.moves_history['player_1'][:]
        g.moves_history['player_1'] = []
        g.moves_history['player_2'] = []
        if g.players == 2:
            Clock.schedule_once(partial(db_saveprocess_2p_txt, win_moves))
        else:
            Clock.schedule_once(partial(db_saveprocess_txt, win_moves, lose_moves))
    return


def db_saveprocess_txt(win_list0, lose_list0, arg1=None, arg2=None):
    win_list = win_list0[:]
    lose_list = lose_list0[:]
    if len(win_list) > 0:
        db_process_txt(win_list.pop(0), 'win')
        counter = 0
        while counter < 10:
            if len(win_list) > 0:
                db_process_txt(win_list.pop(0), 'win')
            counter += 1

        Clock.schedule_once(partial(db_saveprocess_txt, win_list, lose_list))
    elif len(lose_list) > 0:
        db_process_txt(lose_list.pop(0), 'lose')
        counter = 0
        while counter < 10:
            if len(lose_list) > 0:
                db_process_txt(lose_list.pop(0), 'lose')
            counter += 1

        Clock.schedule_once(partial(db_saveprocess_txt, win_list, lose_list))
    else:
        Clock.schedule_once(commitdb_txt)
    return


def db_saveprocess_2p_txt(win_list0, arg1=None, arg2=None):
    win_list = win_list0[:]
    if len(win_list) > 0:
        db_process_txt(win_list.pop(0), 'win')
        counter = 0
        while counter < 10:
            if len(win_list) > 0:
                win_item = win_list.pop(0)
                db_process_txt(win_item, 'win')
                db_process_txt(win_item, 'win')
            counter += 1

        Clock.schedule_once(partial(db_saveprocess_2p_txt, win_list))
    else:
        Clock.schedule_once(commitdb_txt)
    return


def reverse_gamestate(gamestate):
    return gamestate[::-1].swapcase().replace('A', 'a')


def undo(arg=None, arg2=None):
    if g.players == 1:
        if g.player == 'player_2':
            pass
        else:
            try:
                g.moves_history['player_2'].pop(-1)
                g.moves_history['player_1'].pop(-1)
                desired_state = g.moves_history['player_2'][-1]
                desired_state = desired_state[::-1].swapcase().replace('A', 'a')
                g.output['player_1'].write(g.xml_root[4][5].text)
            except Exception as e:
                desired_state = 'aaaablifcaaaaaaCFILBaaaa'
                if g.offer_first_move:
                    g.player = 'player_2'
                    auto_play()

            load_game_state(desired_state)
    elif g.player == 'player_1':
        try:
            g.moves_history['player_2'].pop(-1)
            desired_state = g.moves_history['player_1'][-1]
            g.player = 'player_2'
            g.output['player_2'].write(g.xml_root[4][5].text)
            g.output['player_1'].blank()
        except:
            desired_state = 'aaaablifcaaaaaaCFILBaaaa'

        load_game_state(desired_state)
    else:
        try:
            g.moves_history['player_1'].pop(-1)
            desired_state = g.moves_history['player_2'][-1]
            desired_state = desired_state[::-1].swapcase().replace('A', 'a')
            g.player = 'player_1'
            g.output['player_1'].write(g.xml_root[4][5].text)
            g.output['player_2'].blank()
        except:
            desired_state = 'aaaablifcaaaaaaCFILBaaaa'
            g.player = 'player_1'

        load_game_state(desired_state)
    return


def old_load_game_state(gamestate):
    list_of_all_pieces = g.pieces[:]
    sc = 1
    for square in g.square_list:
        square.piece = None

    for square in g.farm['player_1']:
        square.pieces = []

    for square in g.farm['player_2']:
        square.pieces = []

    mcount = 0
    for letter in gamestate:
        mcount += 1
        if letter == 'a':
            sc += 1
        else:
            data = get_data_by_letter(letter)
            square = get_square_by_number(sc)
            piece = None
            for i in list_of_all_pieces:
                if get_original_animal(i) == data['original']:
                    piece = i
                    list_of_all_pieces.remove(i)
                    break

            piece.square = square
            piece.move_to_square(square)
            piece.owner = data['player']
            undo_fix_promotion(piece, data['animal'])
            if square.get_type() == 'Square':
                square.piece = piece
            else:
                square.pieces.append(piece)
            other = None
            if data['double']:
                for i in list_of_all_pieces:
                    if get_original_animal(i) == data['original']:
                        if data['animal'] == 'king':
                            if i.owner == data['player']:
                                other = i
                                list_of_all_pieces.remove(i)
                                break
                        else:
                            other = i
                            list_of_all_pieces.remove(i)
                            break

                other.square = square
                other.move_to_square(square)
                other.owner = data['player']
                undo_fix_promotion(other, data['animal'])
                square.pieces.append(other)
            sc += 1

    return


def load_game_state(gamestate):
    list_of_all_pieces = g.pieces[:]
    released_pieces = []
    released_squares = []
    sc = 1
    for letter in gamestate:
        if letter == 'a':
            square = get_square_by_number(sc)
            if square.get_type() == 'Square':
                if square.piece != None:
                    released_pieces.append(square.piece)
                    square.piece = None
            elif square.get_type() == 'farmSquare':
                if len(square.pieces) > 0:
                    released_pieces.append(square.pieces.pop(0))
        else:
            data = get_data_by_letter(letter)
            square = get_square_by_number(sc)
            if square.get_type() == 'Square':
                if square.piece != None:
                    if square.piece.animal != data['animal']:
                        released_pieces.append(square.piece)
                        released_squares.append([square, data])
                elif square.piece == None:
                    released_squares.append([square, data])
            elif square.get_type() == 'farmSquare':
                if len(square.pieces) < 2 and data['double']:
                    released_squares.append([square, data])
                elif len(square.pieces) == 2 and data['double'] == False:
                    released_pieces.append(square.pieces.pop(0))
                elif len(square.pieces) == 0 and data['double'] == False:
                    released_squares.append([square, data])
        sc += 1

    for square_data in released_squares:
        square = square_data[0]
        data = square_data[1]
        piece = None
        for i in released_pieces:
            if get_original_animal(i) == data['original']:
                piece = i
                released_pieces.remove(i)
                break

        piece.square = square
        piece.move_to_square(square)
        piece.owner = data['player']
        undo_fix_promotion(piece, data['animal'])
        if square.get_type() == 'Square':
            square.piece = piece
        else:
            square.pieces.append(piece)
        other = None
        if data['double']:
            for i in released_pieces:
                if get_original_animal(i) == data['original']:
                    if data['animal'] == 'king':
                        if i.owner == data['player']:
                            other = i
                            released_pieces.remove(i)
                            break
                    else:
                        other = i
                        released_pieces.remove(i)
                        break

            other.square = square
            other.move_to_square(square)
            other.owner = data['player']
            undo_fix_promotion(other, data['animal'])
            square.pieces.append(other)

    all_farms = g.farm['player_1'][:] + g.farm['player_2'][:]
    for piece in g.pieces:
        if piece.square in all_farms:
            if len(piece.square.pieces) == 2:
                piece.square.pieces[0].double_image.opacity = 1.0
                piece.square.pieces[1].double_image.opacity = 1.0
            else:
                piece.double_image.opacity = 0.0
        else:
            piece.double_image.opacity = 0.0

    return


def undo_fix_promotion(piece, animal):
    small_list = [
     'carp', 'tapir', 'raccoon', 'fox']
    big_list = ['koi', 'baku', 'tanuki', 'kitsune']
    if piece.animal in small_list and animal in big_list:
        piece.animal = big_list[small_list.index(piece.animal)]
        piece.promoted = True
    elif piece.animal in big_list and animal in small_list:
        piece.animal = small_list[big_list.index(piece.animal)]
        piece.promoted = False
    if piece.owner == 'player_1':
        piece.rotation = 0.0
    else:
        piece.rotation = 180.0
    opacity = 0.0
    if piece.square.get_type() == 'farmSquare':
        if len(piece.square.pieces) == 2:
            for i in piece.square.pieces:
                opacity = 1.0

    piece.double_image.opacity = opacity
    piece.reload_image()
    return


def get_square_by_number(number):
    parameters = []
    if number in (1, 2, 3, 4, 21, 22, 23, 24):
        if number == 1:
            parameters = [
             'player_1', 'carp']
        elif number == 2:
            parameters = [
             'player_1', 'fox']
        elif number == 3:
            parameters = [
             'player_1', 'raccoon']
        elif number == 4:
            parameters = [
             'player_1', 'tapir']
        if number == 21:
            parameters = [
             'player_2', 'tapir']
        elif number == 22:
            parameters = [
             'player_2', 'raccoon']
        elif number == 23:
            parameters = [
             'player_2', 'fox']
        elif number == 24:
            parameters = [
             'player_2', 'carp']
        return get_farm(parameters[0], parameters[1])
    else:
        code_index = [
         None, None, None, None, [1, 1], [2, 1], [3, 1], [4, 1], [1, 2], [2, 2], [3, 2], [4, 2], [1, 3], [2, 3], [3, 3], [4, 3], [1, 4], [2, 4], [3, 4], [4, 4], None, None, None, None]
        return get_square_by_code(code_index[number - 1])
        return


def get_data_by_letter(letter):
    if letter == 'b':
        return {'animal': 'king', 'player': 'player_1', 'double': False, 'original': 'king'}
    if letter == 'B':
        return {'animal': 'king', 'player': 'player_2', 'double': False, 'original': 'king'}
    if letter == 'c':
        return {'animal': 'carp', 'player': 'player_1', 'double': False, 'original': 'carp'}
    if letter == 'C':
        return {'animal': 'carp', 'player': 'player_2', 'double': False, 'original': 'carp'}
    if letter == 'd':
        return {'animal': 'carp', 'player': 'player_1', 'double': True, 'original': 'carp'}
    if letter == 'D':
        return {'animal': 'carp', 'player': 'player_2', 'double': True, 'original': 'carp'}
    if letter == 'e':
        return {'animal': 'koi', 'player': 'player_1', 'double': False, 'original': 'carp'}
    if letter == 'E':
        return {'animal': 'koi', 'player': 'player_2', 'double': False, 'original': 'carp'}
    if letter == 'f':
        return {'animal': 'tapir', 'player': 'player_1', 'double': False, 'original': 'tapir'}
    if letter == 'F':
        return {'animal': 'tapir', 'player': 'player_2', 'double': False, 'original': 'tapir'}
    if letter == 'g':
        return {'animal': 'tapir', 'player': 'player_1', 'double': True, 'original': 'tapir'}
    if letter == 'G':
        return {'animal': 'tapir', 'player': 'player_2', 'double': True, 'original': 'tapir'}
    if letter == 'h':
        return {'animal': 'baku', 'player': 'player_1', 'double': False, 'original': 'tapir'}
    if letter == 'H':
        return {'animal': 'baku', 'player': 'player_2', 'double': False, 'original': 'tapir'}
    if letter == 'i':
        return {'animal': 'raccoon', 'player': 'player_1', 'double': False, 'original': 'raccoon'}
    if letter == 'I':
        return {'animal': 'raccoon', 'player': 'player_2', 'double': False, 'original': 'raccoon'}
    if letter == 'j':
        return {'animal': 'raccoon', 'player': 'player_1', 'double': True, 'original': 'raccoon'}
    if letter == 'J':
        return {'animal': 'raccoon', 'player': 'player_2', 'double': True, 'original': 'raccoon'}
    if letter == 'k':
        return {'animal': 'tanuki', 'player': 'player_1', 'double': False, 'original': 'raccoon'}
    if letter == 'K':
        return {'animal': 'tanuki', 'player': 'player_2', 'double': False, 'original': 'raccoon'}
    if letter == 'l':
        return {'animal': 'fox', 'player': 'player_1', 'double': False, 'original': 'fox'}
    if letter == 'L':
        return {'animal': 'fox', 'player': 'player_2', 'double': False, 'original': 'fox'}
    if letter == 'm':
        return {'animal': 'fox', 'player': 'player_1', 'double': True, 'original': 'fox'}
    if letter == 'M':
        return {'animal': 'fox', 'player': 'player_2', 'double': True, 'original': 'fox'}
    if letter == 'n':
        return {'animal': 'kitsune', 'player': 'player_1', 'double': False, 'original': 'fox'}
    if letter == 'N':
        return {'animal': 'kitsune', 'player': 'player_2', 'double': False, 'original': 'fox'}
    return


def start_database_txt():
    g.db = TxtBase('nelson.txt')
    return


def commitdb_txt(arg1=None):
    return


def closedb_txt(arg1=None):
    return


def db_process_txt(state, group):
    rank = g.db.get_ranking(state)
    if rank == None:
        rank = 5
    if group == 'win':
        if rank < 9:
            rank += 1
    elif group == 'lose':
        if rank > 1:
            rank -= 1
    g.db.set_ranking(state, rank)
    return


def db_bulk_process_txt(list_of_states, group):
    final_list = []
    for item in list_of_states:
        rank = g.db.get_ranking(item)
        if rank == None:
            rank = 5
        if group == 'win':
            if rank < 9:
                rank += 1
        elif group == 'lose':
            if rank > 1:
                rank -= 1
        final_list.append([item, rank])

    g.db.bulk_set_ranking(final_list)
    return


def choose_moves_db_txt(possibilities, state=None, processed=[]):
    list_of_moves = possibilities[:]
    game_state = state
    processed_moves = processed
    if game_state == None:
        game_state = get_game_state()
    while len(list_of_moves) > 0:
        move = list_of_moves[0]
        end_state = get_future_state(move)
        rank = g.db.get_ranking(end_state)
        if rank == None:
            rank = 5
        list_of_moves.remove(move)
        processed_moves.append([rank, move])

    processed_moves.sort(reverse=True)
    return processed_moves


def get_future_state(move):
    fake_list = fake_take_square(move[0], move[1])
    future_state = get_game_state()
    undo_fake(fake_list)
    return future_state


class TxtBase:

    def __init__(self, filename):
        if not os.path.isfile(filename):
            open(filename, 'w')
        self.filename = filename
        return

    def get_ranking(self, state):
        with open(self.filename, 'r') as f:
            for line in f:
                key = state[9]
                if line[9] == key and line[0:24] == state:
                    return int(line[24])

        return

    def set_ranking(self, state, ranking):
        linecount = 0
        with open(self.filename, 'rb+') as f:
            for line in f:
                if line[0:24] == state:
                    break
                else:
                    linecount += 1

            f.seek(linecount * 26)
            f.write(state + str(ranking) + '\n')
        return

    def print_base(self):
        with open(self.filename, 'r') as f:
            for line in f:
                print line

        return

    def bulk_set_ranking(self, ranking_list):
        for r in ranking_list:
            with open(self.filename, 'rb+') as f:
                linecount = 0
                for line in f:
                    if line[0:24] == r[0]:
                        break
                    else:
                        linecount += 1

                f.seek(linecount * 26)
                f.write(r[0] + str(r[1]) + '\n')

        return


return

# okay decompiling /tmp/logic_try.pyc
