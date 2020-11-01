#!/usr/bin/env python3
#TODO команды с клавиатуры
#TODO окно с финишем
#TODO подумать над тем, усилить ли контраст

#сделать лог

#(если чёрная фишка на последнем поле, то линия заблокирована) \

import sys
import random
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel, QSizePolicy, QDesktopWidget
#QDialog

from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import pyqtSlot, QTimer

debug_flag = False
no_28_flag = False

HORIZONTAL_END = 12
HORIZONTAL_START = 2
VERTICAL_SIZE = 13

PLAYER_COLOR = {True:'blue', False:'red'} # цвета игроков, используются в окраске (но не везде TODO)
LIGHTER_CONSTANT = 160
BUTTONS_PLAYERS_COLOR = {True: QColor('blue').lighter(LIGHTER_CONSTANT).name(),
                         False: QColor('red').lighter(LIGHTER_CONSTANT).name()}
# цвета для кнопок, зависящие от текущего игрока

AVAIABLE_POSITIONS = ('center', 'bottom right')
# POSITION = 'center'
POSITION = 'bottom right' # задаёт стартовую позицию окна
assert POSITION in AVAIABLE_POSITIONS\

global field_size
field_size = {2:3, 3:5, 4:7, 5:9, 6:11, 7:13, 8:11, 9:9, 10:7, 11:5, 12:3}

global win_flag #флаг победы, True когда победа
win_flag = False

class ColoredPushButton(QPushButton):
    '''окрашенная в нужный цвет цветная кнопка'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_color(current_player)

    def set_color(self, current_player):
        '''устанавливает цвет кнопки'''
        # self.setStyleSheet(f"background-color : {PLAYER_COLOR[current_player]}")
        self.setStyleSheet(f"background-color : \
                           {BUTTONS_PLAYERS_COLOR[current_player]}")

class MyException(Exception):
    pass

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        grid = QGridLayout()
        grid.setFixedHeight = 1000
        grid.setFixedWidth = 400

        self.set_position()

        global labels
        labels = {}
        for i in range(HORIZONTAL_START, HORIZONTAL_END + 1):
            labels[i] = {}
            for j in range(VERTICAL_SIZE):
                l = QLabel(str(j)+':'+str(i))
                l.setFixedHeight(25)
                l.setFixedWidth(35)

                labels[i][j] = l

                #снизу вверх на экране
                grid.addWidget(l,VERTICAL_SIZE - j - 1,i)


        global able
        able = {i:QLabel('Нельзя') for i in range(3)}
        for l in able.values():
            l.hide()

        global buttons
        buttons = {0:{}, 1:{}, 2:{}, 3:{}}
        global sets
        sets = {}
        sets = {0:QLabel('0'), 1:QLabel('1'), 2:QLabel('2')}
        #серым цветом, чтобы не отвлекало
        for i in range(3):
            sets[i].setStyleSheet("QLabel { color : gray; }")

        for i in range(3):
            grid.addWidget(sets[i], 2 * i, HORIZONTAL_END + 1, 1, 2)
            # buttons[i][0] = QPushButton(str(i) + '-0')
            buttons[i][0] = ColoredPushButton(str(i) + '-0')
            # buttons[i][1] = QPushButton(str(i) + '-1')
            buttons[i][1] = ColoredPushButton(str(i) + '-1')

            #установка полужирного шрифта на кнопки
            font = buttons[i][0].font()
            font.setBold(True)
            buttons[i][0].setFont(font)
            buttons[i][1].setFont(font)

            grid.addWidget(buttons[i][0], 1 + 2 * i, HORIZONTAL_END + 1)
            grid.addWidget(able[i], 1 + 2 * i, HORIZONTAL_END + 1)
            grid.addWidget(buttons[i][1], 1 + 2 * i, HORIZONTAL_END + 2)

        #продолжить ход или остановиться
        # buttons[3][0] = QPushButton('Continue')
        buttons[3][0] = ColoredPushButton('Continue')
        #HACK почему-то надо принудительно ставить True, хотя по умолчанию в функции и так стоит
        buttons[3][0].clicked.connect(lambda: drop_dices(True))

        # buttons[3][1] = QPushButton('Stop')
        buttons[3][1] = ColoredPushButton('Stop')
        buttons[3][1].clicked.connect(stop_turn)

        grid.addWidget(buttons[3][0], VERTICAL_SIZE - 1, HORIZONTAL_END + 1)
        grid.addWidget(buttons[3][1], VERTICAL_SIZE - 1, HORIZONTAL_END + 2)
        #buttons[3][0].hide()
        #buttons[3][1].hide()

        for i in range(HORIZONTAL_END + 1):
            grid.setColumnStretch(i, 0)
        for i in range(VERTICAL_SIZE + 2):
            grid.setRowStretch(i, 0)
        grid.setColumnStretch(HORIZONTAL_END + 3, 1)
        grid.setRowStretch(VERTICAL_SIZE + 2, 1)

        for i in range(HORIZONTAL_START, HORIZONTAL_END + 1):
            w = QLabel(str(i))
            grid.addWidget(w, VERTICAL_SIZE, i)

        global status_bar
        status_bar = QLabel('Игра началась. Ход красного игрока.')
        grid.addWidget(status_bar, VERTICAL_SIZE + 1, HORIZONTAL_START + 1, 1, HORIZONTAL_END - HORIZONTAL_START)

        #цветные квадратики статуса, стартовый цвет красный
        global status_square
        status_square = {}

        status_square[0] = QLabel('')
        grid.addWidget(status_square[0], VERTICAL_SIZE + 1, HORIZONTAL_START)
        status_square[1] = QLabel('')
        grid.addWidget(status_square[1], VERTICAL_SIZE + 1, HORIZONTAL_END)

        status_square[0].setStyleSheet("QLabel {{ background-color : {}; color : {}; }}".format('red','red'))
        status_square[1].setStyleSheet("QLabel {{ background-color : {}; color : {}; }}".format('red','red'))



        self.setLayout(grid)

        # метка для подсчёта очков по правилу 28
        global score
        score = QLabel('1')
        grid.addWidget(score, VERTICAL_SIZE - 2, HORIZONTAL_END + 1)
        #подсчёт очков
        #self.refresh_score()


        self.setWindowTitle("Can't stop!")

        self.show()

    def change_color_bar(self, completed):
        '''меняет цвет, выводит результат последнего хода (фишки зафиксированы True или сброшены False)'''
        color = PLAYER_COLOR[current_player]

        status_square[0].setStyleSheet("QLabel {{ background-color : {}; color : {}; }}".format(color, color))
        status_square[1].setStyleSheet("QLabel {{ background-color : {}; color : {}; }}".format(color, color))

        status_bar.setText('Фишки {}. Ход {} игрока.'.format('зафиксированы' if completed else 'сброшены','синего' if current_player else 'красного'))

    def renew_color_bar(self):
        '''убирает надпись "фишки сброшены/поставлены"'''
        status_bar.setText('Ход {} игрока.'.format('синего' if current_player else 'красного'))


    def hide_buttons(self):
        '''скрывает 6 кнопок, метки с наборами, должна и горячие клавиши'''
        global buttons
        for i in range(3):
            for j in range(2):
                buttons[i][j].hide()

        global able
        for i in range(3):
            able[i].hide()

        global sets
        for i in range(3):
            sets[i].hide()

    def hide_turn_buttons(self):
        '''скрывает нижние 2 кнопки, и горячие клавиши должна'''
        global buttons
        for i in range(2):
            buttons[3][i].hide()

    def show_turn_buttons(self):
        '''показывает нижние 2 кнопки, и горячие клавиши должна'''
        global buttons
        for i in range(2):
            buttons[3][i].set_color(current_player)
            buttons[3][i].show()

    def set_position(self):
        '''ставит окно в центр (или соответствующий край экрана, если нужно)'''

        qr = self.frameGeometry()
        # print(qr)
        if POSITION == 'center':
            cp = QDesktopWidget().availableGeometry().center()
            qr.moveCenter(cp)
        elif POSITION == 'bottom right':
            cp = QDesktopWidget().availableGeometry().bottomRight()
            qr.moveBottomLeft(cp)
        else:
            raise AssertionError('window position incorrect')

        self.move(qr.topLeft())

    def refresh_score(self):
        '''обновляет очки, подсчитываемые по правилу 28
        Glenn J, Aloi C (2009). "A Generalized Heuristic for Can't Stop". Proceedings of the Twenty-Second International FLAIRS Conference: 421–426.
        https://www.aaai.org/ocs/index.php/FLAIRS/2009/paper/download/123/338
        '''
        global black
        def count_scores_28():
            '''возвращает очки, подсчитанные по правилу 28 scores'''
            score = 0
            for k, v in black.items():
                progress = v - state[current_player].get(k, -1)
                score += (progress + 1) * (abs(7 - k) + 1)

            if len(black) >= 3:
                ost = [k % 2 == 0 for k in black]
                #все чётные
                if all(ost):
                    score -= 2
                #все нечётные
                elif all([not t for t in ost]):
                    score += 2

                #все с одной стороны
                if all([t >= 7 for t in black]) or all([t <= 7 for t in black]):
                    score += 4

            return score

        score.setText('Score: ' + str(count_scores_28()) if not no_28_flag else 'No score.')

def go(a, b = None):
    '''генерирует функцию для продвижения'''
    assert isinstance(a, int)
    assert isinstance(b, int) or b is None
    assert 1 <= a <= 12
    assert b == None or 1 <= b <= 12


    global black
    #проверка на 3 фишки
    assert len(set(black.keys()) | set([t for t in (a, b) if t is not None])) <= 3

    def return_go():
        '''продвижение чёрных фишек вперёд'''
        assert isinstance(a, int)
        assert isinstance(b, int) or b is None
        assert 1 <= a <= 12
        assert b == None or 1 <= b <= 12
        assert len(set(black.keys()) | set([t for t in (a, b) if t is not None])) <= 3


        lines = (a, b) if b is not None else (a,)
        for l in lines:
            black[l] = black.get(l, state[int(current_player)].get(l,-1)) + 1


        refresh_field()

        win.hide_buttons()
        win.show_turn_buttons()
        #drop_dices()

    return return_go

def refresh_field():
    '''обновляет изображение поля'''
    def make_green(num, color):
        '''делает всю вертикаль одним цветом'''
        for i in range(field_size[num]):
            labels[num][i].setStyleSheet("QLabel {{ background-color : {}; color : {}; }}".format(color, color))
        for i in range(field_size[num], VERTICAL_SIZE):
            labels[num][i].setText('X')

    for i in range(HORIZONTAL_START, HORIZONTAL_END + 1):
        #проверка на занятость вертикали
        if (state[0].get(i, -1) + 1) == field_size[i]:
            make_green(i, 'red')
            continue
        elif (state[1].get(i, -1) + 1) == field_size[i]:
            make_green(i, 'blue')
            continue

        for j in range(VERTICAL_SIZE):
            j = 13 - j - 1
            if j in range(field_size[i]):
                res = []
                color = True
                for m in range(2):
                    if state[m].get(i, None) == j:
                        res.append(str(m))

                if black.get(i, None) == j:
                    res.append('B')

                color = 'black'
                bcolor = 'transparent'
                if '0' in res:
                    if '1' in res:
                        bcolor = 'purple'
                        color = 'purple'
                        #нет отображения если две фишки
                    else:
                        bcolor = 'red'
                        color = 'white'
                elif '1' in res:
                    bcolor = 'blue'
                    color = 'white'
                #чёрное самое приоритетное
                if 'B' in res:
                    bcolor = 'black'
                    if '0' in res and '1' in res:
                        color = 'purple'
                    elif '0' in res:
                        color = 'red'
                    elif '1' in res:
                        color = 'blue'
                    else:
                        color = 'white'

                    #bcolor = 'black'


                res = '/'.join(res) if len(res)>=2 else '' if res else '.'
            else:
                res = 'X'
                color = 'black'
                bcolor = 'transparent'
            labels[i][j].setStyleSheet("QLabel {{ background-color : {}; color : {}; }}".format(bcolor, color))
            labels[i][j].setText(res)

    #обновляет количество очков
    win.refresh_score()
def drop_dices(renew = True):
    '''при нажатии на кнопку "продолжить ход"
    renew - обновить ли надпись'''
    if renew: win.renew_color_bar()

    win.hide_turn_buttons()

    global current_player

    def button_enable(i, j, numbers = None):
        if not numbers:
            buttons[i][j].hide()
            return False
        else:
            try:
                buttons[i][j].clicked.disconnect()
            except TypeError:
                pass

            buttons[i][j].clicked.connect(go(*numbers))

            numbers = [str(t) for t in numbers]

            buttons[i][j].setText(' и '.join(numbers))
            buttons[i][j].set_color(current_player)
            buttons[i][j].show()
            #print('True')
            return True


    dices = tuple((random.randint(1, 6) for i in range(4)))

    sums = [(dices[0] + dices[1], dices[2] + dices[3]),
            (dices[0] + dices[2], dices[1] + dices[3]),
    #        (7, 7),
            (dices[0] + dices[3], dices[1] + dices[2])]
    dices_combinations = [(dices[0], dices[1], dices[2], dices[3]),
            (dices[0], dices[2], dices[1], dices[3]),
    #        (3, 4, 3, 4),
            (dices[0], dices[3], dices[1], dices[2])]

    #предварительная сортировка суммы
    #чтобы кнопки шли по порядку
    for i in range(3):
        if sums[i][0] > sums[i][1]:
            sums[i] = (sums[i][1], sums[i][0])
            dk = dices_combinations[i]
            dices_combinations[i] = (dk[2], dk[3], dk[0], dk[1])

    turn_avaiable = False

    for i in range(3):
        sets[i].setText('{}+{} {}+{}'.format(*dices_combinations[i]))
        sets[i].show()

        choices = [False, False]
        what_to_print = []

        #проверяем оба шага по отдельности:
        for j in range(2):
            summ = sums[i][j]

            #проверяется 1)допустимость множества чёрных фишек
            #свободность линии
            #TODO кажется, третье условие избыточно
            if (len(set(black.keys()) | set([summ])) <= 3 and summ not in filled_lines and
            # проверка на незаполненность до конца линии \
            #(если чёрная фишка на последнем поле, то линия заблокирована) \
            max(state[int(current_player)].get(summ, -1), black.get(summ, -1)) < (field_size[summ] - 1)):
                choices[j] = True
                what_to_print.append([sums[i][j]])

        double_break = False
        #если оба варианта возможны, то проверяем, можно ли одновременно
        if all(choices):
            #незаполненность линий уже проверена
            if len(set(black.keys()) | set(sums[i])) <= 3:
                #проверяем совпадают ли суммы
                if (sums[i][0] != sums[i][1]):
                    what_to_print = [sums[i]]
                #если совпадают - то не выйдет ли за пределы поля
                elif max(state[int(current_player)].get(sums[i][0], -1), black.get(sums[i][0], -1)) + 2 < field_size[sums[i][0]]:
                    what_to_print = [sums[i]]
                else:
                    double_break = True

        #проверка на двойной переход
        if not double_break:
            what_to_print = what_to_print + [[]]*(2 - len(what_to_print))
        else:
            what_to_print =[[],[]]


        temp = button_enable(i, 0, what_to_print[0])
        temp |= button_enable(i, 1, what_to_print[1])
        if temp:
            able[i].hide()
        else:
            able[i].show()

        turn_avaiable |= temp

    if not turn_avaiable:
        #смена игрока при сбросе фишек
        print('фишки сброшены игроком ', PLAYER_COLOR[current_player])
        current_player = not current_player
        win.change_color_bar(False)

        black.clear()
        refresh_field()

        drop_dices(renew = False)
    else:
        pass



def stop_turn():
    '''при нажатии на кнопку "остановить ход"'''

    #фиксация чёрных фишек
    global state
    global black
    global current_player

    state[int(current_player)].update(black)
    black.clear()


    #проверка победы, занятие линий
    wins = 0
    global win_flag
    win_flag = False
    for i in field_size:
        if state[int(current_player)].get(i, -1) == (field_size[i] - 1):
            wins += 1
            filled_lines.add(i)
        elif state[int(current_player)].get(i, -1) > (field_size[i] - 1):
            raise MyException('слишком далеко зашла чёрная фишка')

    win_flag = wins >= 3
    win_player = current_player

    refresh_field()
    if not win_flag:
        #передача хода и бросок кубиков
        current_player = not current_player
        win.change_color_bar(True) #окончил ход самое

        drop_dices(False) #не обновлять строку
    else:
        #TODO +вывести результат и -закончить программу
        win.hide_turn_buttons()
        status_bar.setText('{} игрок победил!'.format('Синий' if current_player else 'Красный'))



if __name__ == '__main__':
    #игрок, 0 (красный) или 1 (синий)
    global current_player
    current_player = False

    app = QApplication(sys.argv)
    win = MainWindow()


    #состояние всех цветных фишек, внутри словарей ключи от 2 до 12
    global state
    state = {0:{}, 1:{}}


    #state = {0:{2:1, 3:3, 4:0, 8:1}, 1:{4:0, 5:7, 8:1}}
    if debug_flag: state = {0:{},1:{6:10, 8:10, 7:11}}

    #чёрные фишки
    global black
    black = {}
    if debug_flag: black = {2:1, 8:1}


    #занятые полностью линии
    global filled_lines
    filled_lines = set()
    if debug_flag: filled_lines = set([6,8])

    #if not debug_flag: win.hide_turn_buttons()

    refresh_field()
    drop_dices(renew = True)


    sys.exit(app.exec_())
