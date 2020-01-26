import random, re
import tkinter as tk

#Chess

class Error(Exception): pass #General class for the following custom errors

class oobError(Error): pass #Coordinates are out of bounds

class existError(Error): pass #Origin square is empty

class turnError(Error): pass #Other player's turn (Wrong colour piece for this turn)

class stillError(Error): pass #Stationary piece (Origin square is the same as the destination square)

class allyError(Error): pass #Destination square has an ally piece on it

class illegalError(Error): pass #For remaining errors involving piece mechanics

class endError(Error): pass #User input after the game is over

class checkError(Error): pass #King in check or will be in check

class drawError(Error): pass #Any kind of draw (see drawCheck function for more details)

class mateError(Error): pass #Checkmate

class TerminalBoard():
    #The logical chess class (Contains the computer's board view)
    def __init__(self):
        #Initialises the board variable as a 2d array with all empty squares
        self.board = [["  " for y in range(8)] for x in range(8)]

    def initTerminalBoard(self):
        #Places all the pieces on the board; Pieces consists of two characters
        for n in range(len(self.board)):
            self.board[1][n] = "BP"
            self.board[6][n] = "WP"

        #The first character is the colour of the piece
        self.board[0][0] = self.board[0][7] = "BR"
        self.board[0][1] = self.board[0][6] = "BN"
        self.board[0][2] = self.board[0][5] = "BB"
        self.board[0][3] = "BQ"
        self.board[0][4] = "BK"

        #The second character is which type of piece
        self.board[7][0] = self.board[7][7] = "WR"
        self.board[7][1] = self.board[7][6] = "WN"
        self.board[7][2] = self.board[7][5] = "WB"
        self.board[7][3] = "WQ"
        self.board[7][4] = "WK"

class PopUp():
    #The pop-up class (Creates a pop-up with tkinter's TopLevel widget)
    #Adapted from: https://stackoverflow.com/questions/48033347/pause-function-execution-while-awaiting-input-in-entry-tkinter/48035417#48035417
    def __init__(self, text, default = ""):
        #Initialises the pop-up class with the TopLevel widget
        self.popup = tk.Toplevel()
        #Featuring a message and an entry widget for user input
        self.popup.title(text)
        self.entryVar = tk.StringVar(value = default)
        #Makes a transient window (i.e. on top of the original)
        self.popup.transient()

        #Creates the label, entry, and button widgets, the padding and fill makes the pop-up wider
        labelPopUp = tk.Label(self.popup, text = text)
        labelPopUp.pack(side = "top", fill = "both", padx = 42, pady = 24)

        entryPopUp = tk.Entry(self.popup, textvariable = self.entryVar)
        entryPopUp.pack(side = "top", fill = "both", padx = 42, pady = 24)

        buttonFrame = tk.Frame(self.popup)
        buttonFrame.pack(side = "bottom", fill = "both", expand = "true")
        #If this button is clicked then the pop-up is destroyed
        buttonEnterP = tk.Button(buttonFrame, text= "Enter", command = self.popup.destroy)
        buttonEnterP.pack(side = "top")
        #You have to do these self-referential calls in tkinter for widgets to stay packed
        self.entryPopUp = entryPopUp

    def show(self):
        #Makes the pop-up appear
        frame = tk.Frame()
        self.entryPopUp.focus_force()
        frame.wait_window(self.popup)
        #Returns the user entry when it is closed
        return self.entryVar.get()

def Menu():
    #Here is the in-game menu, featuring several options
    while True:
        #The program enters a while loop that will be broken if a valid option (or 0) is entered
        try:
            #The options are brinted
            brint('''1) See moves
2) See taken pieces
3) See legal moves
4) See highscores
5) Toggle learner mode
6) Save
7) Load''')
            #Then the user enputs their choice
            choice = int(enput("\nPlease enter a number (enter 0 to quit the Menu): "))
            if choice != 0:
                #Calls the relevant function according to the user's choice
                options[choice - 1]()

            #If the user enters 0, then this menu loop is broken, thus quitting the Menu
            break

        except ValueError:
            #If the enput cannot be converted to an integer then the user can try again
            brint("\nNot a valid number")

        except IndexError:
            #This error is raised if the integer is too large for the options list
            brint("\nTry again")

def Undo():
    global move_count, board
    #This function undoes moves
    #Originally, this function was going to work revert to a previous board state in a list of board states ...
    #... , but I felt that creating this many 2d arrays in memory would not be a good idea
    try:
        #If there have been no moves the move_count will be zero
        ZDE = 1 / move_count

    except ZeroDivisionError:
        #This error is triggered so it is impossible to undo
        brint("\nNo moves to undo")
        return None

    #The colour is arbitrarily assigned
    enemy_colour = "B"
    if extras[move_count][0] == "W":
        #If the piece colour is white then this is corrected, otherwise it remains unchanged
        enemy_colour = "W"

    if extras[move_count][1] == "P":
        #The extras list keeps track of special moves, here en passent is accounted for
        board.board[int(extras[move_count][3])][int(extras[move_count][2])] = enemy_colour + "P"

    if extras[move_count][1] == "R":
        #The special rook move is castling
        x0 = int(extras[move_count][2])
        y0 = int(extras[move_count][3])
        x1 = int(extras[move_count][4])
        y1 = int(extras[move_count][5])
        #The rook is moved back to the original position
        moved_rook = str(board.board[y1][x1])
        #The destination position is replaced with an empty square
        board.board[y1][x1] = "  "
        board.board[y0][x0] = moved_rook

    if moved_pieces[-1][1] == "K":
        #If the last move involved a king then the Kings position dictionary is re-updated
        Kings[moved_pieces[-1][1]] = str(int(moves[-1][1])) + str(int(moves[-1][0]))

    #After dealing with special moves the moved and taken pieces are moved back
    board.board[int(moves[-1][3])][int(moves[-1][2])] = taken_pieces[-1]
    board.board[int(moves[-1][1])][int(moves[-1][0])] = moved_pieces[-1]
    #The lists that contain move data are also adjusted
    #The most recent entries are popped off the lists
    moves.pop(-1)
    moved_pieces.pop(-1)
    taken_pieces.pop(-1)
    extras[move_count] = "  "
    extras.pop(-1)
    #move_count is also reduced at the end
    move_count -= 1

def seeMoves():
    #This function brints all the moves that were played during the game
    Rmoves = easyReadMoves(moves)
    brint("\n{}".format(Rmoves))

def seeTakenPieces():
    #This function brints the taken pieces
    brint("\n{}".format(taken_pieces))

def seeLegalMoves():
    #This brints legal moves with use of the generateLegalMoves function
    Lmoves = generateLegalMoves()
    Rmoves = easyReadMoves(Lmoves)
    brint("\n{}".format(Rmoves))

def seeHighscores():
    #This function brints a leaderboard of highscores
    with open("highscores.txt") as f:
        #The data from the file is read
        h_data = f.read()

    #Then the data is split by line
    h_split = h_data.split("\n")
    scores = []
    for n in range(len(h_split) - 1):
        #For each of these lines, the score is extracted by splitting by comma
        s_split = []
        s_split = h_split[n].split(",")
        #The score is the first comma-separated entry on each line
        scores.append(int(s_split[0]))

    #Next the scores are sorted descendingly with merge sort
    scores = mergeSort(scores)
    brint("Here are the top 5 highscores: ")
    for s in range(5):
        #Finally, the top five scores are indexed and outputted
        score_string = str(s + 1) + ": " + str(scores[s])
        brint(score_string)

def mergeSort(disarray):
    #Here is the recursive merge sort algorithm
    if len(disarray) < 2:
        #When the array is divided into length less than two the smaller arrays are recombined to produce the sorted array
        return disarray

    #The midpoint is the length of the array modulo two (how many times two fits into the length exactly)
    mid = len(disarray) // 2
    #The array is divided into two smaller arrays
    left = disarray[:mid]
    right = disarray[mid:]
    #Then the algorithm recursively calls itself for these smaller arrays
    left = mergeSort(left)
    right = mergeSort(right)
    #The sorted array is returned so that the algorithm can continue
    return merge(left, right)

def merge(left, right):
    #Here is the second part of the merge sort algorithm
    array = []
    #While the left and right arrays are not empty recombine the arrays
    while left != [] and right != []:
        #If the first value in the left array is greater than in the right ...
        if left[0] > right[0]:
            #Then add it to the array and remove this item from the left array
            array.append(left[0])
            left.pop(0)

        else:
            #Otherwise, add the item and remove in the right array
            array.append(right[0])
            right.pop(0)

    #If there are still numbers left in the smaller arrays then add them to the array
    while left != []:
        array.append(left[0])
        left.pop(0)

    #By recursiving calling itself, the algorithm has sorted the array
    while right != []:
        array.append(right[0])
        right.pop(0)

    #Finally, return the sorted array
    return array

def toggleLearnerMode():
    global learner_flag
    #This function toggles the learner mode
    if learner_flag == False:
        #If learner mode is off then switch it on (make the flag True)
        learner_flag = True

    else:
        #Otherwise the mode must be on already, so switch it off
        learner_flag = False

    #Finally, the function provides user feedback about the state of learner mode
    brint("\nLearner mode is: {}".format(learner_flag))

def printLearnerMoves(y, x):
    #Here, moves that originate from a user inputted position are outputted
    Lmoves = generateLegalMoves()
    Mmoves = []
    for move in Lmoves:
        #For each legal move, the moves that start on a user-inputted square are selected
        if int(move[0]) == y and int(move[1]) == x:
            #Then the moves are appended to the learner moves list
            Mmoves.append(move)

    #Finally, these moves are brinted
    Mmmoves = easyReadMoves(Mmoves)
    brint("\n{}\n".format(Mmmoves))

def easyReadMoves(Lmoves):
    #This function converts the computer syntax for moves to the human syntax
    Lemoves = []
    #The moves are converted from four list indexes to the normal move syntax
    for move in Lmoves:
        #For example, 6646 becomes g2g4
        y0 = 8 - int(move[0])
        #This 97 comes by looking at ASCII tables and working out the distance from 0 to a
        x0 = chr(int(move[1]) + 97)
        #Note that not only are the number themselves manipulated, but also their relative position
        y1 = 8 - int(move[2])
        #Since y0x0y1x1 is shuffled to x0y0x1y1
        x1 = chr(int(move[3]) + 97)
        #Then the moves are appended to legible moves list
        Lemoves.append(str(x0) + str(y0) + str(x1) + str(y1))

    return Lemoves

def Save():
    global Kings, move_count, learner_flag, promo_flag, ai_flag, ai_colour_flag, ai_duel_flag, end_flag, difficulty_level, moves, moved_pieces, taken_pieces, extras, board
    #This function saves games by exporting the board state
    while True:
        #The user inputs a filename or leaves the entry blank to close without saving
        f_choice = enput("\nEnter file name without .txt (leave blank to close menu): ")
        if f_choice == "":
            return None

        invalid_chars = re.findall("\.|\,|\<|\>|\:|\"|\/|\\|\||\?|\*|\0", f_choice)
        #Regex is used to find any invalid characters in teh filename
        if invalid_chars == []:
            #If no invalid characters are found then the function continues
            break

    #The filename is combined with the .txt extension
    filename = f_choice + ".txt"
    #Then the board state is combined into a line-separated string
    c_data = str(Kings["WK"]) + "\n" + str(Kings["BK"]) + "\n"+ str(move_count) + "\n" + str(learner_flag) + "\n" + str(promo_flag) + "\n" + str(ai_flag) + "\n" + str(ai_colour_flag) + "\n" + str(ai_duel_flag) + "\n" + str(end_flag) + "\n" + str(difficulty_level)
    #Next the move_data lists are dealt with, all start as empty lists, but extras always has an extra empty element for insertion
    for n in range(move_count):
        #By using only one for loop rather than four separate ones, some time is saved
        c_data += "\n" + str(moves[n]) + "\n" + str(moved_pieces[n]) + "\n" + str(taken_pieces[n]) + "\n" + str(extras[n + 1])

    #The only remaining variable is the two dimensional board array
    board_size = len(board.board)
    #For each square on the board
    for y in range(board_size):
        for x in range(board_size):
            #Append the piece on the board in that square to the data
            c_data += "\n" + board.board[y][x]

    #Finally, write the data to the file
    f = open(filename, "w")
    f.write(c_data)
    f.close()

def Load():
    global Kings, move_count, learner_flag, promo_flag, ai_flag, ai_colour_flag, ai_duel_flag, end_flag, difficulty_level, moves, moved_pieces, taken_pieces, extras, board
    #Here is the inverse function of the last: load
    f_choice = enput("\nEnter file name: ")
    #The user inputs the name of the file that they want to load
    filename = f_choice + ".txt"
    try:
        #The file is read if it exists
        with open(filename) as f:
            c_data = f.read()

    #If the file does not exist, there is no point in creating it, since it would have no data to load in it
    except FileNotFoundError:
        #The error is handled if the file does not exist
        brint("\nPlease enter a valid file name\n")
        #If there is no file to be loaded then exit the function
        return None

    #The data is split by line
    c_split = c_data.split("\n")
    #Then if any flags were False they need to be dealt with manually, since bool("False") = True, not False
    for a in range(3, 9):
        if c_split[a] == "False":
            c_split[a] = False

    #Check the ai flag and ai colour flag and duel flag to make sure they match, otherwise don't allow the load
    temp_continuity_ai_flag_1 = bool(c_split[5])
    temp_continuity_ai_flag_2 = bool(c_split[6])
    temp_continuity_ai_flag_3 = bool(c_split[7])
    if temp_continuity_ai_flag_1 != ai_flag or temp_continuity_ai_flag_2 != ai_colour_flag or temp_continuity_ai_flag_3 != ai_duel_flag:
        #If any of the flags do not match then the function ends early again
        brint("\nThis game cannot be loaded.\n")
        brint("\nPlease make sure you are in the correct player mode and that ...\n")
        brint("\n... the AI is playing as the same colour as in the saved game.\n")
        return None

    #Now the data is loaded, so that the current board state becomes the old board state, whilst making sure that data types match
    Kings["WK"] = str(c_split[0])
    Kings["BK"] = str(c_split[1])
    move_count = int(c_split[2])
    learner_flag = bool(c_split[3])
    promo_flag = bool(c_split[4])
    ai_flag = bool(c_split[5])
    ai_colour_flag = bool(c_split[6])
    ai_duel_flag = bool(c_split[7])
    end_flag = bool(c_split[8])
    difficulty_level = int(c_split[9])
    #The lists are reset, notice how extras starts with an empty element
    moves = []
    moved_pieces = []
    taken_pieces = []
    extras = ["  "]
    #Then the data is read back from the file
    for n in range(move_count):
        #The for loop goes four steps at a time since we are reading back four lists in each iteration
        m = 4 * n
        #The read data by 10 since that is where the list data starts
        moves.append(c_split[10 + m + 0])
        moved_pieces.append(c_split[10 + m + 1])
        taken_pieces.append(c_split[10 + m + 2])
        extras.append(c_split[10 + m + 3])

    #Finally, the board is loaded
    board_size = len(board.board)
    #The board is wiped clean and reset back to being fully empty
    board.board = [["  " for y in range(8)] for x in range(8)]
    #The board data starts when the data above ends, so there is a pointer to slice the rest of the used data away
    snip = 10 + 4 * move_count
    #The data is sliced, only leaving the board data
    c_snipt = c_split[snip:]
    c_snip = 0
    #Then the board data is loaded
    for y in range(board_size):
        for x in range(board_size):
            #For each square there is an associated data element, so the data pointer is incremented for each square
            board.board[y][x] = c_snipt[c_snip]
            c_snip += 1

def offerTakeback():
    #This function asks the user if they want to takeback the last move and then Undoes it if the response is affirmative
    t_choice = enput("\nDo you want to takeback the last move? (Y/N): ")
    if t_choice == "Y":
        Undo()

def offerDraw():
    global end_flag
    #This function asks the user if they want to accept a drawn game and then draws the game if the response is affirmative
    if end_flag == True:
        #If the user has called this function previously during this game then don't run the algorithm
        brint("\nThe game has ended\n")
        return

    d_choice = enput("\nDo you want to accept the draw? (Y/N): ")
    if d_choice == "Y":
        brint("\nDraw\n")
        End()

def Resign():
    global move_count, end_flag
    #This function asks the user if they want to forfeit the game and then forfeits the game if the response is affirmative
    if end_flag == True:
        #If the user has called this function previously during this game then don't run the algorithm
        brint("\nThe game has ended\n")
        return None

    f_choice = enput("\nDo you want to forfeit the game? (Y/N): ")
    if f_choice == "Y":
        brint("\nYou lose\n")
        End(move_count)

def brint(text):
    global incr
    #This function is responsible for outputting messages to the user with click-to-destroy buttons
    newIncr = int(incr)
    #There is a counter for the buttons so that no buttons share the same variable name (which wouldn't allow another buttons to be created)
    buttons.append(tk.Button(text = text, command = lambda : buttons[newIncr].destroy()))
    #The button is packed, when the button is clicked it will be destroyed through the use of the lambda function
    buttons[newIncr].pack(side = "top")
    #Finally, the counter is incremented
    incr += 1

def enput(text):
    global encr
    #This function is responsible for outputting messages and receiving inputs from the user with pop-ups
    newEncr = int(encr)
    #The function works similarly to the previous one, except that it uses the PopUp class rather than buttons
    popups.append(PopUp(text = text))
    response = popups[newEncr].show()
    encr += 1
    #The function also return the input from the user once the pop-up is closed
    return response

def turnCheck(colour, turn):
    #This function makes sure that the correct colour piece is moved on a given turn
    if colour == "B" and turn % 2 == 0 or colour == "W" and turn % 2 != 0:
        #An even or odd turn (move_count) corresponds to a colour, if there is a contradiction then an error is raised
        return False

def coordCheck(y0, x0, y1, x1):
    #This functions chekcs that all of the coordinates are within bounds of the chessboard
    coords = [y0, x0, y1, x1]
    #The coordinates are put into a list and then iterated through
    for n in range(len(coords)):
        if coords[n] < 0 or coords[n] >= 8:
            #If a coordinate is less than zero or greater or equal to eight then an error is raised
            return False

def allyCheck(colour, y1, x1):
    #This function checks that the destination square does no contain an ally piece with the use of colour
    if board.board[y1][x1][0] == colour:
        #If the colour of the pieces match then an error is raised
        return False

def rookMove(colour, y0, x0, y1, x1):
    #This function checks that rook moves are valid
    x = x0
    y = y0
    #Copies of the original coordinates are created for later incremental iteration use
    if x0 == x1 or y0 == y1:
        #If the rook moves straight then one of the coords must remain constant
        if x0 == x1:
            #If the x-coordinate remain constant then the rook moves vertically
            if y0 < y1:
                #If the original y-coordinate is less than the destination y-coordinate then the rook moves down
                while y != y1:
                    #This while loop checks all the coordinates in a straight line from the origin to destination squares
                    y += 1
                    if board.board[y][x] != "  ":
                        #If the square being checked contains a piece (is not empty)
                        if board.board[y][x][0] == colour:
                            #If the square contains an ally piece then the rook cannot move there
                            return False

                        elif y1 == y:
                            #If the square is the destination square with no previous errors then it is valid
                            return True

                        elif board.board[y1 - 1][x] != "  ":
                            #If the square above the destination is not empty then the rook cannot move there
                            return False

                        else:
                            #Similarly to the last check, if a square on the path contains a piece then the move is invalid
                            return False

            if y0 > y1:
                #Rook moves up (with top left being 0, 0)
                while y != y1:
                    #Now the rest of the directions are checked in the same manner as above
                    y -= 1
                    #The only change is that the checks move in the respective directions
                    if board.board[y][x] != "  ":
                        if board.board[y][x][0] == colour:
                            return False

                        elif y1 == y:
                            return True

                        elif board.board[y1 + 1][x] != "  ":
                            #For instance, this square is now below rather than above
                            return False

                        else:
                            return False

        if y0 == y1:
            if x0 < x1:
                #Rook moves right
                while x != x1:
                    #X-coordinates are iterated over, rather than y-coordinates since this movement is in the x-axis
                    x += 1
                    if board.board[y][x] != "  ":
                        if board.board[y][x][0] == colour:
                            return False

                        elif x1 == x:
                            return True

                        elif board.board[y][x - 1] != "  ":
                            return False

                        else:
                            return False

            if x0 > x1:
                #Rook moves left
                while x != x1:
                    x -= 1
                    if board.board[y][x] != "  ":
                        if board.board[y][x][0] == colour:
                            return False

                        elif x1 == x:
                            return True

                        elif board.board[y][x + 1] != "  ":
                            return False

                        else:
                            return False

        #If the move passes all the checks then it is legal
        return True

    #If the rook does not move vertically or horizontally then the move is illegal
    return False

def bishopMove(colour, y0, x0, y1, x1):
    #The bishop move function works similarly to the rook move function
    x = x0
    y = y0
    #The key different being that the bishop can only move diagonally rather than orthogonally (up and down)
    if y0 + x0 == y1 + x1 or y0 - x0 == y1 - x1:
        #We can consider the bishop move to be a straight line in the cartesian plane with gradient of +- one
        #As such the sum or difference of the bishops coordinates will always satisfy the above conditions
        #If the bishop moves from top left to bottom right (and vice versa) then this is the first condition
        #For example, (7, 0) to (0, 7)
        #If the bishop moved from bottom left to top right (and backwards) then it is the second condition
        #For example, (0, 0) to (8, 8)
        if x0 < x1:
            #Now we also need two selections to decide the diagonal path the bishop takes and other checks
            if y0 < y1:
                #Bishop moves diagonally down-right
                while x != x1 or y != y1:
                    x += 1
                    y += 1
                    if board.board[y][x] != "  ":
                        #The rest is the same, in principle, as the rook move
                        if board.board[y][x][0] == colour:
                            return False

                        elif x1 == x and y1 == y:
                            #Here we need both conditions to be satisfied
                            return True

                        elif board.board[y - 1][x - 1] != "  ":
                            #And similarly here the square before is a change in both axis directions
                            return False

                        else:
                            return False

            if y0 > y1:
                #Bishop moves diagonally up-right
                while x != x1 or y != y1:
                    x += 1
                    y -= 1
                    if board.board[y][x] != "  ":
                        if board.board[y][x][0] == colour:
                            return False

                        elif x1 == x and y1 == y:
                            return True

                        elif board.board[y + 1][x - 1] != "  ":
                            return False

                        else:
                            return False

        if x0 > x1:
            if y0 < y1:
                #Bishop moves diagonally down-left
                while x != x1 or y != y1:
                    x -= 1
                    y += 1
                    if board.board[y][x] != "  ":
                        if board.board[y][x][0] == colour:
                            return False

                        elif x1 == x and y1 == y:
                            return True

                        elif board.board[y - 1][x + 1] != "  ":
                            return False

                        else:
                            return False

            if y0 > y1:
                #Bishop moves diagonally up-left
                while x != x1 or y != y1:
                    x -= 1
                    y -= 1
                    if board.board[y][x] != "  ":
                        if board.board[y][x][0] == colour:
                            return False

                        elif x1 == x and y1 == y:
                            return True

                        elif board.board[y + 1][x + 1] != "  ":
                            return False

                        else:
                            return False

        #If the bishop passes all the checks it is valid
        return True

    #If the bishop does not move diagonally then the move is invalid
    return False

def queenMove(colour, y0, x0, y1, x1):
    #A queen move is either a rook move or a bishop move
    if x0 == x1 or y0 == y1:
        #If the move is orthogonal then do the rook move check
        if rookMove(colour, y0, x0, y1, x1) == True:
            return True

    if y0 + x0 == y1 + x1 or y0 - x0 == y1 - x1:
        #If the move is diagonal then do the bishop move check
        if bishopMove(colour, y0, x0, y1, x1) == True:
            return True

    #If the move is neither then it is invalid
    return False

def knightMove(y0, x0, y1, x1):
    #This is the knight move function, a knight only has a maximum of eight moves so this function simply checks all cases
    #I originally wanted to do the knight move in the same way as the bishop move check
    #The critical point is that a knight's move can be thought of as a line in the cartisian plane with gradient +- two
    #However, the other difference (that the knight can only have a maximum of eight moves) means that it is simpler just to try all eight
    #It would be more efficient to nest the selection here, but I prefer this layout since it is more obvious that the function works
    if y0 == y1 + 2:
        #For example, if the move is down 2 and right 1 then it is valid
        if x0 == x1 + 1:
            return True

    if y0 == y1 - 2:
        #Similarly, up 2 and right 1
        if x0 == x1 + 1:
            return True

    if y0 == y1 + 2:
        if x0 == x1 - 1:
            return True

    if y0 == y1 - 2:
        if x0 == x1 - 1:
            return True

    if x0 == x1 + 2:
        if y0 == y1 + 1:
            return True

    if x0 == x1 - 2:
        if y0 == y1 + 1:
            return True

    if x0 == x1 + 2:
        if y0 == y1 - 1:
            return True

    if x0 == x1 - 2:
        if y0 == y1 - 1:
            return True

    #All other potential moves are rejected since they are not one of the valid eight
    return False

def kingMove(piece, y0, x0, y1, x1, move_count):
    #Here is the king move check, it works just like the the knight move function
    #Except with all the squares next to the piece, rather than 2 steps in a direction and 1 step in the other
    #One the surface, the king is similar to the knight because it only has eight moves
    #However, this is not true due to the castling move which complicates things
    if y0 == y1:
        #Again, I could nest this selection, but it is easier to read like this
        if x0 == x1 + 1:
            return True

    if y0 == y1:
        if x0 == x1 - 1:
            return True

    if x0 == x1:
        if y0 == y1 + 1:
            return True

    if x0 == x1:
        if y0 == y1 - 1:
            return True

    if x0 == x1 - 1:
        if y0 == y1 - 1:
            return True

    if x0 == x1 + 1:
        if y0 == y1 + 1:
            return True

    if x0 == x1 - 1:
        if y0 == y1 + 1:
            return True

    if x0 == x1 + 1:
        if y0 == y1 - 1:
            return True

    #Now the interesting part: castling
    if x1 == x0 + 2:
        #If the king moves right or left by two then it is trying to castle
        if y0 == y1:
            #The height y-coordinate must remain constant
            if castleCheck("Kingside", piece, y0, x0, y1, x1) == True:
                #Now another function is called to check more conditions
                if board.board[y0][x0 + 1] == "  ":
                    #The square immediately to the right of the king must be empty
                    if checkCheck(piece, y0, x0 + 1, move_count) == True:
                        if checkCheck(piece, y0, x0, move_count) == True:
                            if checkCheck(piece, y1, x1, move_count) == True:
                                #The king cannot castle into or through a checked square
                                if x1 != 7:
                                    if board.board[y1][x1 + 1][1] == "R":
                                        #A rook must also be in the corner square to castle
                                        board.board[y0][x0 + 1] = board.board[y1][x1 + 1]
                                        #The rook is moved and replaced with an empty square
                                        board.board[y1][x1 + 1] = "  "
                                        #Finally, a note of the castle is made in the extras list so this can be undone
                                        extras.insert(move_count, piece[0] + "R" + str(x1 + 1) + str(y1) + str(x0 + 1) + str(y0))
                                        return True

    if x1 == x0 - 2:
        #Left is queenside and right is kingside
        if y0 == y1:
            #The queenside involves a rook that is four squares away from the king, rather than just three
            if castleCheck("Queenside", piece, y0, x0, y1, x1) == True:
                if board.board[y0][x0 - 1] == "  ":
                    if checkCheck(piece, y0, x0 - 1, move_count) == True:
                        if checkCheck(piece, y0, x0, move_count) == True:
                            if checkCheck(piece, y1, x1, move_count) == True:
                                if board.board[y1][x1 - 1] == "  ":
                                    if x1 > 1:
                                        if board.board[y1][x1 - 2][1] == "R":
                                            #Here is the different in rook position
                                            board.board[y0][x0 - 1] = board.board[y1][x1 - 2]
                                            board.board[y1][x1 - 2] = "  "
                                            #The rest is the same
                                            extras.insert(move_count, piece[0] + "R" + str(x1 - 2) + str(y1) + str(x0 - 1) + str(y0))
                                            return True

    return False

def castleCheck(side, king, y0, x0, y1, x1):
    #This function checks if the king or its rook have moved
    rook = king[0] + "R"
    #The king's colour is used to generate the rook name
    for n in range(len(moved_pieces)):
        #Then the list of moved pieces is checked for the king
        if moved_pieces[n] == king:
            #If the king is found then the move is invalid
            return False

    if side == "Kingside":
        #Remember how the rook is in the other corner for kingside vs queenside
        for n in range(len(moved_pieces)):
            if moved_pieces[n] == rook:
                #If the rook is found in the moved pieces list ...
                if int(moves[n][0]) == 7:
                    #... and it originated from the right-hand corner, then it has moved
                    return False

    if side == "Queenside":
        #Again for queenside the rook originated from the left-hand corner
        for n in range(len(moved_pieces)):
            if moved_pieces[n] == rook:
                if int(moves[n][0]) == 0:
                    return False

    #If neither piece has moved than the move is valid
    return True

def pawnMove(colour, y0, x0, y1, x1, move_count):
    #Here is the pawn move function
    #One might consider the pawn to be the simplest piece, but this is far from the truth
    #Generally, a pawn only moves forwards one square, or two when it is on the original rank
    #However, a pawn can also capture diagonally (including en passent) and if it reaches the final rank it gets a promotion
    #As such, this pawn move function is unexpectedly complex
    if colour == "W":
        #If the pawn is white and on the 7th rank (6 since lists start indexing at 0)
        if y0 == 6:
            if y0 - 2 == y1:
                #Then the pawn is able to move two steps forward, rather than just one 
                if x0 == x1:
                    #The pawn does not move horizonally in this case
                    if board.board[y0 - 1][x1] == "  ":
                        if board.board[y0 - 2][x1] == "  ":
                            #The squares in front of the pawn must also be empty
                            return True

        if y0 - 1 == y1:
            #If the pawn only move one step then there are some more checks
            if x0 == x1:
                if board.board[y0 - 1][x1] == "  ":
                    #For the basic case, as long as the square in front is empty, then the move is valid
                    return True

            if x0 + 1 == x1 or x0 - 1 == x1:
                #If the pawn moves diagonally  and ...
                if board.board[y1][x1][0] == "B":
                    #... if the destination square contains an enemy, then it can take, and the move is valid
                    return True

                elif board.board[y0][x1] == "BP":
                    #However, there is one last rule: en passent
                    if moved_pieces[-1] == "BP":
                        #If the last moved piece was an enemy pawn and it moved two steps forward (originating from the relevant rank)
                        if moves[-1][0] == str(x1) and moves[-1][2] == str(x1):
                            if moves[-1][1] == "1":
                                #Then en passant is possible and the enemy piece is taken
                                board.board[y0][x1] = "  "
                                #The extras list is also updated so the enemy piece can come back if the move is undone
                                extras.insert(move_count, "BP" + str(x1) + str(y0))
                                return True

    if colour == "B":
        #Next the case of a black pawn is considered, the difference is what rank it came from and what direction
        if y0 == 1:
            if y0 + 2 == y1:
                #The black pawns move down rather than up
                if x0 == x1:
                    if board.board[y0 + 1][x1] == "  ":
                        if board.board[y0 + 2][x1] == "  ":
                            return True

        if y0 + 1 == y1:
            if x0 == x1:
                if board.board[y0 + 1][x1] == "  ":
                    return True

            if x0 + 1 == x1 or x0 - 1 == x1:
                if board.board[y1][x1][0] == "W":
                    return True

                if board.board[y0][x1] == "WP":
                    if moved_pieces[-1] == "WP":
                        if moves[-1][0] == str(x1) and moves[-1][2] == str(x1):
                            if moves[-1][1] == "6":
                                #Also, they originate from the 7th rank instead of the 2nd
                                board.board[y0][x1] = "  "
                                extras.insert(move_count, "WP" + str(x1) + str(y0))
                                return True

    #If a move is not accounted for above then it is invalid
    #That concludes this pawn move function ... except for one more thing: Promotion
    return False

def Promotion(colour, y0, x0, y1, x1, move_count):
    global promo_flag, ai_flag, ai_colour_flag, ai_duel_flag
    #As previously discussed, a pawn undergoes promotion when it reaches the final rank
    if (ai_flag == True and bool(move_count % 2) == ai_colour_flag) or ai_duel_flag == True:
        #If the user is playing against an AI and if it is the AI's turn then randomly choose a promotion piece
        promo_choice = random.choice(["R", "N", "B", "Q"])
        board.board[y1][x1] = colour + promo_choice
        promo_flag = True
        return None

    while True:
        try:
            #If it is the user's turn then they can choose the piece
            promo_choice = str(enput("\nEnter promotion piece: ")).upper()
            if promo_choice == "R":
                break

            elif promo_choice == "N":
                break

            elif promo_choice == "B":
                break

            elif promo_choice == "Q":
                break

            else:
                raise TypeError

            break

        except TypeError:
            #If the piece is not valid then the error is handled and the user can try again
            brint("Enter a valid piece (R, N, B, Q): ")

    #The pawn on the square is replaced
    board.board[y1][x1] = colour + promo_choice
    #A flag is also raised
    promo_flag = True

def checkCheck(piece, y, x, move_count):
    #This function checks if a given square is in check from an enemy piece
    #This is equivalent to asking: Can an enemy piece move to this square?
    colour = piece[0]
    enemies = []
    positions = []
    #First the enemy colour is determined
    enemy_colour = "W"
    if colour == "W":
        #The enemy colour is black is the allies are white, otherwise the enemies are white
        enemy_colour = "B"

    for j in range(len(board.board)):
        for i in range(len(board.board)):
            #For every square on the board, if there is an enemy piece
            if board.board[j][i][0] == enemy_colour:
                #Append the enemy pieces and their positions to the lists
                enemies.append(board.board[j][i])
                positions.append(str(j) + str(i))

    for n in range(len(enemies)):
        #Checks if the enemy piece can move to the given position from the function call
        if enemies[n][1] == "P":
            if pawnMove(enemy_colour, int(positions[n][0]), int(positions[n][1]), y, x, move_count) == True:
                return False

        elif enemies[n][1] == "R":
            if rookMove(enemy_colour, int(positions[n][0]), int(positions[n][1]), y, x) == True:
                return False

        elif enemies[n][1] == "N":
            if knightMove(int(positions[n][0]), int(positions[n][1]), y, x) == True:
                return False

        elif enemies[n][1] == "B":
            if bishopMove(enemy_colour, int(positions[n][0]), int(positions[n][1]), y, x) == True:
                return False

        elif enemies[n][1] == "Q":
            if queenMove(enemy_colour, int(positions[n][0]), int(positions[n][1]), y, x) == True:
                return False

        elif enemies[n][1] == "K":
            if kingMove(enemies[n], int(positions[n][0]), int(positions[n][1]), y, x, move_count) == True:
                return False

    #If no piece can move to the given position then there is no check
    return True

def drawCheck(move_count):
    global ai_flag, ai_colour_flag, ai_duel_flag
    #This function checks if there is a draw
    Vmoves = generateLegalMoves()
    #A list of valid moves are generated and then the colour is determined
    colour = "B"
    if move_count % 2 == 0:
        colour = "W"

    if len(Vmoves) == 0:
        #If there are no valid moves
        if checkCheck(colour + "K", int(Kings[colour + "K"][0]), int(Kings[colour + "K"][1]), move_count) != False:
            #If the king is not in check, then there is stalemate
            brint("\n\nStalemate\n")
            return True

    #Now the check for threefold repetition
    if move_count > 5:
        #There must be at least six moves for this check to come into play
        tf1 = moves[-3][2] + moves[-3][3] + moves[-3][0] + moves[-3][1]
        tf2 = moves[-4][2] + moves[-4][3] + moves[-4][0] + moves[-4][1]
        #Effectively, if the position is the same as it was 6 moves ago or 3 turns ago, then there is a draw
        if tf1 == moves[-1] and tf1 == moves[-5]:
            #As such, the penultimate turn is the same as the last and the third last, except that it occurs in the opposite direction
            if tf2 == moves[-2] and tf2 == moves[-6]:
                #For example, g1h3 then h3g1 then g1h3 again
                if moved_pieces[-1] == moved_pieces[-3] == moved_pieces[-5]:
                    if moved_pieces[-2] == moved_pieces[-4] == moved_pieces[-6]:
                        #In other words, if the last three pairs of moves are the same (involving the same pieces)
                        brint("\n\nThreefold repetition\n")
                        if (ai_flag == True and bool(move_count % 2) == ai_colour_flag) or ai_duel_flag == True:
                            return True

                        tf_choice = enput("\nDo you want to claim the draw? (Y/N): ")
                        #The AI automatically accepts and the user has a choice
                        if tf_choice == "Y":
                            return True

    if imCheck() == True:
        #If there is insufficient material for mate
        return True

    if move_count > 50:
        for n in range(move_count - 50, move_count):
            #This rule only considers the last 50 moves
            if moved_pieces[n][1] == "P" or taken_pieces[n] != "  ":
                #If there was no capture or pawn move in last 50
                return False

        brint("\n\n50 move rule\n")
        if (ai_flag == True and bool(move_count % 2) == ai_colour_flag) or ai_duel_flag == True:
            return True

        fd_choice = enput("\nDo you want to claim the draw? (Y/N): ")
        #Again the AI automatically accepts and the user has a choice
        if fd_choice == "Y":
            return True

    if move_count > 75:
        #The 75 move rules is the same as the 50 move rules, but it is a forced draw
        for n in range(move_count - 75, move_count):
            if moved_pieces[n][1] == "P" or taken_pieces[n] != "  ":
                #No capture or pawn move in last 75
                return False

        brint("\n\n75 move rule\n")
        return True

    #If the board state has none of the above draws then it is not a draw
    return False

def imCheck():
    #This is the insufficient material check function
    wpieces = []
    bpieces = []
    wknight_count = 0
    wbishop_count = 0
    bknight_count = 0
    bbishop_count = 0
    #All the pieces currently on the board are appended to lists depending on colour
    for j in range(len(board.board)):
        for i in range(len(board.board)):
            if board.board[j][i][0] == "W":
                wpieces.append(board.board[j][i])

            if board.board[j][i][0] == "B":
                bpieces.append(board.board[j][i])

    for wpiece in wpieces:
        #If there are any of these pieces then mate is still possible (in the majority of cases)
        if wpiece[1] == "P":
            return False

        if wpiece[1] == "R":
            return False

        if wpiece[1] == "Q":
            return False

        #However, we need to keep track of the number of knights and bishops since this is somewhat more complicated
        if wpiece[1] == "N":
            wknight_count += 1

        if wpiece[1] == "B":
            wbishop_count += 1

        if wbishop_count > 1 or wknight_count > 2:
            #If there at least 2 bishops or 3 knights then _forced_ mate is possible
            return False

        if wbishop_count > 0 and wknight_count > 0:
            #If there are both a knight and a bishop then it is possible to mate
            return False

    for bpiece in bpieces:
        #Then the same checks are done for black
        if bpiece[1] == "P":
            return False

        if bpiece[1] == "R":
            return False

        if bpiece[1] == "Q":
            return False

        if bpiece[1] == "N":
            bknight_count += 1

        if bpiece[1] == "B":
            bbishop_count += 1

        if bbishop_count > 1 or bknight_count > 2:
            return False

        if bbishop_count > 0 and bknight_count > 0:
            return False

    #It is possible to mate with a knight and a bishop or two bishops, but not two knights
    brint("\n\nInsufficient material to force mate\n")
    if (ai_flag == True and bool(move_count % 2) == ai_colour_flag) or ai_duel_flag == True:
        return True

    im_choice = enput("\nDo you want to claim the draw? (Y/N): ")
    #As before, the user has a choice to accept, but the AI does not    
    if im_choice == "Y":
        return True

def mateCheck(move_count):
    #This is the mate check function that checks for checkmate
    Pmoves = generateLegalMoves()
    #Possible moves are generated and colour is determined
    colour = "B"
    if move_count % 2 == 0:
        colour = "W"

    if len(Pmoves) == 0:
        if checkCheck(colour + "K", int(Kings[colour + "K"][0]), int(Kings[colour + "K"][1]), move_count) == False:
            #If there are no legal moves and the king is in check, then it is checkmate
            return True

    #Otherwise, there is no checkmate
    return False

def End(move_count = 0):
    global end_flag, nameUser, ai_flag, ai_colour_flag, ai_duel_flag
    #This function is called when the game ends (draw, checkmate, forfeit)
    if end_flag == True:
        #If the user has called this function previously during this game then don't run the algorithm
        return None

    end_flag = True
    #If move_count is given with the function call then brint the win string
    if move_count != 0:
        colour = "Black"
        #Colour is determined of the winning side
        if (move_count - 1) % 2 == 0:
            colour = "White"

        #A score for the game is generated and the end string is brinted
        finalScore = getFinalScore()
        end_string = "\n" + colour + " Player wins! Final score: " + str(finalScore)
        brint(end_string)

        #If the game was an AI demo then highscores aren't updated
        if ai_duel_flag == True:
            return None

        if ai_flag == True:
            if bool((move_count + 1) % 2) == ai_colour_flag:
                #Similarly, if the computer beat the user then highscores aren't updated
                return None

        with open("highscores.txt") as f:
            #The current highscore data is read
            h_data = f.read()

        #Then the new data is appended to the file
        h_data += str(finalScore) + ","
        #If the user is logged in then their username is appended with the highscore
        if nameUser != "":
            h_data += " by " + nameUser

        h_data += "\n"
        #The data is then written to the file
        f = open("highscores.txt", "w")
        f.write(h_data)
        f.close()

def fakeUndo(move_count):
    #This function resets the obscure rules that are in individual piece functions (en passant and castling)
    #This is so that no unexpected errors occur (for instance, when taking a move back or checking whether the king is in check)
    #It is essentially the Undo function, but only with the extra parts
    enemy_colour = "B"
    if extras[move_count][0] == "W":
        enemy_colour = "W"

    if extras[move_count][1] == "P":
        board.board[int(extras[move_count][3])][int(extras[move_count][2])] = enemy_colour + "P"

    if extras[move_count][1] == "R":
        x0 = int(extras[move_count][2])
        y0 = int(extras[move_count][3])
        x1 = int(extras[move_count][4])
        y1 = int(extras[move_count][5])
        moved_rook = str(board.board[y1][x1])
        board.board[y1][x1] = "  "
        board.board[y0][x0] = moved_rook

    extras[move_count] = "  "

def getAIMove(Lmoves):
    global difficulty_level, move_count
    #This function gets an AI move depending on the difficulty level
    random.shuffle(Lmoves)
    if difficulty_level == 0:
        #The level 0 AI just picks a random legal move
        return Lmoves[0]

    #Here some constants are initialised
    INFINITY = 9999
    depthMinMax = 2
    depthAB = 3
    #The equal moves list is also created as well as the bestMove string
    Emoves = []
    bestMove = ""
    #The bestValue is set to be as low as possible
    bestValue = -INFINITY
    #The colour is also determined
    colour = "B"
    if move_count % 2 == 0:
        colour = "W"

    if difficulty_level == 1:
        #The first level picks the best moves out of all the possible moves with no look ahead other than this (depth 1)
        for move in Lmoves:
            #Iterates through all the legal moves without changing overall state irreversibly
            y0 = int(move[0])
            x0 = int(move[1])
            y1 = int(move[2])
            x1 = int(move[3])
            moved_piece = board.board[y0][x0]
            taken_piece = board.board[y1][x1]
            #Each move is played and evaluated
            board.board[y1][x1] = moved_piece
            board.board[y0][x0] = "  "
            #Only looks one move ahead and picks the best move from legal moves
            moveValue = evalBoard(colour)
            if moveValue > bestValue:
                #If the move improves the board state for this player, then the best move and value are updated
                bestMove = move
                bestValue = moveValue
                #Then the equally strong moves list is emptied and new strongest move is added to it
                Emoves = []
                Emoves.append(move)

            #If there are more equally strong moves, then add them to Emoves
            elif moveValue == bestValue:
                Emoves.append(move)

                #This stops the first occuring move always being picked in such a situation
                bestMove = random.choice(Emoves)

            #The board is reset at the end of each iteration
            board.board[y0][x0] = moved_piece
            board.board[y1][x1] = taken_piece
            fakeUndo(move_count)

    #Adapted from: https://byanofsky.com/2017/07/06/building-a-simple-chess-ai/
    if difficulty_level == 2:
        #The next level is minimax at depth 2
        bestMove = minimax(depthMinMax, colour, True, True)[1]
        if bestMove == "":
            #If no better move is found then a random move it chosen
            bestMove = Lmoves[0]

    if difficulty_level == 3:
        #The final level is minimax with alpha beta pruning at depth 3
        bestMove = alphabeta(depthAB, colour, -INFINITY, INFINITY, True, True)[1]
        if bestMove == "":
            bestMove = Lmoves[0]

    #At the end of the function the best move found is returned
    return bestMove

def minimax(depth, colour, max_flag, king_flag):
    global move_count
    #Base case: when the depth is zero the algorithm has reached a leaf node and evaluates the board
    if depth == 0:
        #The board value is returned as well as a placeholder for the bestMove
        return [evalBoard(colour), ""]

    #Recursive case: continue moving down the tree
    INFINITY = 9999
    bestMove = ""
    Lmoves = generateLegalMoves()
    #The moves are shuffled again for the same reason as above (all bad moves)
    random.shuffle(Lmoves)
    #A temporary copy of the max flag is created since this will be passed recursively back into the function
    temp_flag = bool(max_flag)
    if max_flag == True:
        #If it is the turn of the AI (maximiser) then the best value should be as low as possible
        bestValue = -INFINITY
        #The temporary flag is toggled so that it indicates that the minimiser will be playing next
        temp_flag = False

    else:
        #If it is the turn of the user (minimiser) then the best value should be as high as possible
        bestValue = INFINITY
        #The temporary flag is toggled again so that it is the maximiser's turn
        temp_flag = True

    #Iterates through all the legal moves without changing overall state irreversibly
    for move in Lmoves:
        #The king flag is initialised as False, this tracks whether the king has moved
        king_flag = False
        y0 = int(move[0])
        x0 = int(move[1])
        y1 = int(move[2])
        x1 = int(move[3])
        moved_piece = board.board[y0][x0]
        taken_piece = board.board[y1][x1]
        board.board[y1][x1] = moved_piece
        board.board[y0][x0] = "  "
        #The move is played and then move_count and extras are updated so that fakeUndo works correctly
        extras.append("  ")
        move_count += 1
        if moved_piece[1] == "K":
            #The Kings dictionary is updated so that checkCheck works properly
            Kings[moved_piece] = str(y1) + str(x1)
            #The aforementioned king flag is also updated if the king moves, again so fakeUndo works
            king_flag = True

        #The algorithm then recursively calls itself at a lower depth (further down in the tree)
        value = minimax(depth - 1, colour, temp_flag, king_flag)[0]
        if max_flag == True:
            #If it is the maximiser's turn
            if value > bestValue:
                #Then find the maximum values
                bestValue = value
                bestMove = move

        elif value < bestValue:
            #If it is the minimiser's turn then find the minimum values
            bestValue = value
            bestMove = move

        if king_flag == True:
            #The Kings position is reset if the king was moved earlier
            Kings[moved_piece] = str(y0) + str(x0)

        #The rest of the board state is then reset
        board.board[y0][x0] = moved_piece
        board.board[y1][x1] = taken_piece
        fakeUndo(move_count)
        extras.pop(-1)
        move_count -= 1

    #Finally, the best move - with its value - is returned
    return [bestValue, bestMove]

def alphabeta(depth, colour, alpha, beta, max_flag, king_flag):
    global move_count
    #Here is the alpha beta algorithm, it is just an adapted version of the minimax algorithm, I shall comment on any changes
    if depth == 0:
        return [evalBoard(colour), ""]

    INFINITY = 9999
    bestMove = ""
    Lmoves = generateLegalMoves()
    random.shuffle(Lmoves)
    temp_flag = bool(max_flag)
    if max_flag == True:
        bestValue = -INFINITY
        temp_flag = False

    else:
        bestValue = INFINITY
        temp_flag = True

    for move in Lmoves:
        #Iterates through all the legal moves without changing overall state irreversibly
        king_flag = False
        y0 = int(move[0])
        x0 = int(move[1])
        y1 = int(move[2])
        x1 = int(move[3])
        moved_piece = board.board[y0][x0]
        taken_piece = board.board[y1][x1]
        board.board[y1][x1] = moved_piece
        board.board[y0][x0] = "  "
        extras.append("  ")
        move_count += 1
        if moved_piece[1] == "K":
            Kings[moved_piece] = str(y1) + str(x1)
            king_flag = True
        
        #The alpha and beta values are reset when the algorithm recursively calls itself
        value = alphabeta(depth - 1, colour, -INFINITY, INFINITY, temp_flag, king_flag)[0]
        if max_flag == True:
            if value > bestValue:
                bestValue = value
                bestMove = move

            if alpha < value:
                #The alpha value is updated if it is lower than the current value
                alpha = value

        else:
            if value < bestValue:
                #Find min values
                bestValue = value
                bestMove = move

            if beta > value:
                #The beta value is updated if it is greater than the current value
                beta = value

        if king_flag == True:
            Kings[moved_piece] = str(y0) + str(x0)

        board.board[y0][x0] = moved_piece
        board.board[y1][x1] = taken_piece
        fakeUndo(move_count)
        extras.pop(-1)
        move_count -= 1

        if beta <= alpha:
            #Skip the rest of the leaf nodes in this branch if the condition is satisfied
            break

    #Alpha-beta speeds up the time taken to run the algorithm so that deeper depths can be achieved
    return [bestValue, bestMove]

def evalBoard(ally_colour):
    #This is the board evaluation function, it generates a score depending on the material on the board
    active_pieces = []
    piece_score = 0
    total_score = 0
    #All the pieces on the board are found and appended to the active pieces list
    for j in range(len(board.board)):
        for i in range(len(board.board)):
            if board.board[j][i] != "  ":
                active_pieces.append(board.board[j][i])

    #For each of the pieces on the board a value is added to the total score
    for piece in active_pieces:
        if piece[1] == "P":
            piece_score = 10

        elif piece[1] == "R":
            piece_score = 50

        elif piece[1] == "B":
            piece_score = 30

        elif piece[1] == "N":
            piece_score = 30

        elif piece[1] == "Q":
            piece_score = 90

        elif piece[1] == "K":
            piece_score = 1000

        if piece[0] == ally_colour:
            total_score += piece_score

        else:
            #If the piece is not an ally then its value is subtracted instead
            total_score -= piece_score

    #The total score is returned when all the active pieces have been accounted for
    return total_score

def getFinalScore():
    global difficulty_level, ai_flag, move_count
    #This function returns the final score when a game has ended
    colour = "W"
    if move_count % 2 == 0:
        colour = "B"

    finalScore = evalBoard(colour)
    #If the user played against an AI their score is multiplied by a multiplier
    if ai_flag == True:
        #This multiplier is one plus the level (so that even if the user plays against random AI they still gets some points)
        multiplier = difficulty_level + 1
        finalScore *= multiplier

    #Finally, the final score is returned
    return finalScore

def generateLegalMoves():
    global move_count
    #This is the generate legal moves algorithm
    legal_flag = True
    #These flags keep track of whether a move is legal and whether the king has moved, respectively
    king_flag = False
    Lmoves = []
    allies = []
    positions = []
    Lemoves = []
    #Various lists are declared and the colour is found
    ally_colour = "B"
    if move_count % 2 == 0:
        ally_colour = "W"

    for j in range(len(board.board)):
        for i in range(len(board.board)):
            if board.board[j][i][0] == ally_colour:
                #Finds the ally pieces and their positions
                allies.append(board.board[j][i])
                positions.append(str(j) + str(i))

    for n in range(len(allies)):
        for y in range(len(board.board)):
            for x in range(len(board.board)):
                #Sees if a given ally piece can move to a given position and appends to legal_moves
                legal_flag = True
                if int(positions[n][0]) == y and int(positions[n][1]) == x:
                    #If the piece has not moved then the move is illegal
                    legal_flag = False

                elif allyCheck(ally_colour, y, x) == False:
                    #If the destination square contains an ally piece then the move is also illegal
                    legal_flag = False

                #Next the moves are checked against the individual piece functions to see if they are legal
                if legal_flag == True:
                    if allies[n][1] == "P":
                        if pawnMove(ally_colour, int(positions[n][0]), int(positions[n][1]), y, x, move_count) == True:
                            Lmoves.append(str(positions[n][0]) + str(positions[n][1]) + str(y) + str(x))
                            #The fake undo function is called to reset en passent
                            fakeUndo(move_count)

                    elif allies[n][1] == "R":
                        if rookMove(ally_colour, int(positions[n][0]), int(positions[n][1]), y, x) == True:
                            Lmoves.append(str(positions[n][0]) + str(positions[n][1]) + str(y) + str(x))

                    elif allies[n][1] == "N":
                        if knightMove(int(positions[n][0]), int(positions[n][1]), y, x) == True:
                            Lmoves.append(str(positions[n][0]) + str(positions[n][1]) + str(y) + str(x))

                    elif allies[n][1] == "B":
                        if bishopMove(ally_colour, int(positions[n][0]), int(positions[n][1]), y, x) == True:
                            Lmoves.append(str(positions[n][0]) + str(positions[n][1]) + str(y) + str(x))

                    elif allies[n][1] == "Q":
                        if queenMove(ally_colour, int(positions[n][0]), int(positions[n][1]), y, x) == True:
                            Lmoves.append(str(positions[n][0]) + str(positions[n][1]) + str(y) + str(x))

                    elif allies[n][1] == "K":
                        if kingMove(allies[n], int(positions[n][0]), int(positions[n][1]), y, x, move_count) == True:
                            Lmoves.append(str(positions[n][0]) + str(positions[n][1]) + str(y) + str(x))
                            #The fake undo function is called to reset castling
                            fakeUndo(move_count)

    #A temporary copy of the legal moves list is made so that the list can be edited whilst being iterated over
    Tempmoves = list(Lmoves)
    #The next for loop deals with check; whether the board is in check after a move has been played
    for move in Lmoves:
        #Tries all the legal moves and sees if any solve (or result in) check
        king_flag = False
        y0 = int(move[0])
        x0 = int(move[1])
        y1 = int(move[2])
        x1 = int(move[3])
        moved_piece = board.board[y0][x0]
        taken_piece = board.board[y1][x1]
        board.board[y1][x1] = moved_piece
        board.board[y0][x0] = "  "
        #The move is played and then extras and move_count are updated so that fakeUndo still works correctly
        extras.append("  ")
        move_count += 1
        if moved_piece[1] == "K":
            #The Kings dictionary is updated if the king has moved so that checkCheck works
            Kings[moved_piece] = str(y1) + str(x1)
            king_flag = True

        if checkCheck(ally_colour + "K", int(Kings[ally_colour + "K"][0]), int(Kings[ally_colour + "K"][1]), move_count) == False:
            #If a given move does not fix the check, then remove the move
            Tempmoves.remove(move)

        if king_flag == True:
            #The Kings dictionary is reset if the king has moved
            Kings[moved_piece] = str(y0) + str(x0)

        board.board[y0][x0] = moved_piece
        board.board[y1][x1] = taken_piece
        fakeUndo(move_count)
        #The board is reset and so is the board state
        extras.pop(-1)
        move_count -= 1

    Lmoves = list(Tempmoves)
    #The updated legal moves list is then returned for further use
    return Lmoves

def Move(tkinterMove):
    global move_count, learner_flag, promo_flag, ai_flag, ai_colour_flag, ai_duel_flag, end_flag
    #Here is the main move function, responsible for moving pieces and other general game flow features
    try:
        if end_flag == True:
            #If the user tries to make a move when the game is over then this error is raised
            raise endError

        #The coordinates if the user move are sent from the GUI file
        y0 = int(tkinterMove[0])
        x0 = int(tkinterMove[1])
        y1 = int(tkinterMove[2])
        x1 = int(tkinterMove[3])
        legal_moves = generateLegalMoves()
        if ai_flag == True:
            #If the user is playing against an AI ... 
            if bool(move_count % 2) == ai_colour_flag:
                #... and if it is the AI's move then get the AI's move
                ai_move = getAIMove(legal_moves)
                y0 = int(ai_move[0])
                x0 = int(ai_move[1])
                y1 = int(ai_move[2])
                x1 = int(ai_move[3])

        if ai_duel_flag == True:
            #If the game is in demo mode then this function gets the AI's move for every turn
            ai_move = getAIMove(legal_moves)
            y0 = int(ai_move[0])
            x0 = int(ai_move[1])
            y1 = int(ai_move[2])
            x1 = int(ai_move[3])

        #The piece at the user's coordinates is found
        piece = board.board[y0][x0]
        #The colour is obtained from this (the first of the two characters)
        colour = piece[0]

        if learner_flag == True:
            #If the user is in learner mode then print the legal moves for the piece at the given coordinates
            printLearnerMoves(y0, x0)

        if turnCheck(colour, move_count) == False:
            #If the wrong colour piece is chosen on a given turn then
            raise turnError

        elif coordCheck(y0, x0, y1, x1) == False:
            #If the given coordinates are outside the chessboard's boundaries then raise this error
            raise oobError

        elif y0 == y1 and x0 == x1:
            #If the original coordinates match the destination coordinates then raise this error
            raise stillError

        elif board.board[y0][x0] == "  ":
            #If the selected square is empty then raise this error
            raise existError

        elif allyCheck(colour, y1, x1) == False:
            #If the destination square contains an ally piece then raise this error
            raise allyError

        elif piece[1] == "P":
            if pawnMove(colour, y0, x0, y1, x1, move_count) == False:
                #If the selected piece is pawn, but it does not pass the valid move check then raise this error
                raise illegalError

        elif piece[1] == "R":
            if rookMove(colour, y0, x0, y1, x1) == False:
                #If the selected piece is rook, but it does not pass the valid move check then raise this error
                raise illegalError

        elif piece[1] == "N":
            if knightMove(y0, x0, y1, x1) == False:
                #If the selected piece is knight, but it does not pass the valid move check then raise this error
                raise illegalError

        elif piece[1] == "B":
            if bishopMove(colour, y0, x0, y1, x1) == False:
                #If the selected piece is bishop, but it does not pass the valid move check then raise this error
                raise illegalError

        elif piece[1] == "Q":
            if queenMove(colour, y0, x0, y1, x1) == False:
                #If the selected piece is queen, but it does not pass the valid move check then raise this error
                raise illegalError

        elif piece[1] == "K":
            if kingMove(piece, y0, x0, y1, x1, move_count) == False:
                #If the selected piece is king, but it does not pass the valid move check then raise this error
                raise illegalError

        if str(piece[1]) == "K":
            if kingMove(piece, y0, x0, y1, x1, move_count) == True:
                #If the moved piece is a king then update the Kings position dictionary
                Kings[piece] = str(y1) + str(x1)

        if board.board[y1][x1][1] == "K":
            #If the taken piece was a king then raise the checkmate error (never actually used)
            #This is not possible in theory, but it is another potential way for the rules of Chess to be implemented
            #Checkmate is just a position where the capture of the king is inevitable
            raise mateError

        #The lists that monitor the board state are updated
        moves.append(str(x0) + str(y0) + str(x1) + str(y1))
        moved_pieces.append(piece)
        #This includes the list of: played moved; moved pieces; taken pieces; and extras
        taken_pieces.append(board.board[y1][x1])
        #The extras list is used for special cases such as castling or en passent which are within individual piece move functions
        extras.append("  ")
        if str(piece[1]) == "P":
            if y1 == 7 and colour == "B" or y1 == 0 and colour == "W":
                #If the piece is a pawn and has moved from the penultimate rank the call the Promotion function
                Promotion(colour, y0, x0, y1, x1, move_count)

        #The move_count (how many moves there have been) is incremented
        move_count += 1
        if promo_flag != True:
            #If there has not been a promotion in this turn then move the piece to the destination square
            board.board[y1][x1] = piece

        #Empty the origin square
        board.board[y0][x0] = "  "
        #Reset the promotion flag
        promo_flag = False

        if checkCheck(colour + "K", int(Kings[colour + "K"][0]), int(Kings[colour + "K"][1]), move_count) == False:
            #Checks if the move results in check for the ally king and (hard) undos the move so that the player can try again
            Undo()
            raise checkError

        if drawCheck(move_count) == True:
            #If there is a draw then raise this error
            raise drawError

        if mateCheck(move_count) == True:
            #If there has been checkmate then raise this error
            raise mateError

    except endError:
        #This error is raised if the game has previously ended, but the user makes another input
        brint("\nThe game has ended\n")

    except turnError:
        #This error is raised if the wrong colour piece is chosen to move
        brint("\nIt is not your turn\n")

    except oobError:
        #This error is raised if the piece is dragged off of the board
        brint("\nThe coordinates are out of bounds\n")

    except stillError:
        #This error is raised if the piece has not moved from its origin square
        if learner_flag == False:
            #Don't brint the error message if the user is a learner
            brint("\nPlease move a piece\n")

    except existError:
        #This error is raised if the origin square is empty
        brint("\nThere is no piece on the original square\n")

    except allyError:
        #This error is raised if the destination square contains an ally piece
        brint("\nThe destination square is occupied by an ally piece\n")

    except illegalError:
        #This error is raised if any of the individual piece move functions return False (i.e. that the move is illegal)
        brint("\nIllegal move\n")

    except checkError:
        #This error is raised if the king is in check after having played the user's move
        brint("\nThe king is in check\n")

    except drawError:
        #This error is raised if there is a draw, the End function is then called
        brint("\nDraw\n")
        End()

    except mateError:
        #This error is raised if there is checkmate
        brint("\nCheckmate!\n")
        #The End function is called with move_count so that a highscore will be submitted
        End(move_count)

def initTerminalChess():
    #This function initialises this file's program with lots of global variables to keep track of the board state and many other functions
    global board, Kings, move_count, learner_flag, promo_flag, ai_flag, ai_colour_flag, ai_duel_flag, end_flag, moves, moved_pieces, taken_pieces, extras, options, incr, buttons, encr, popups, difficulty_level
    #The Kings dictionary keeps track of the position of the two kings on the board
    Kings = {"WK" : "74", "BK" : "04"}
    #The move_count integer is incremented everytime there is a move (it counts the number of moves)
    move_count = 0
    #These two increment integers are used in the brint and enput functions to create buttons and pop-ups respectively
    incr = 0
    encr = 0
    #The difficulty level integer is the level of AI difficulty in the program, this ranges from 0 to 3
    difficulty_level = 3
    #The learner flag boolean is raised if learner mode is activated, see the printLearnerMoves function for more details about learner mode
    learner_flag = False
    #The promotion flag boolean is raised if there has been promotion during a given turn
    promo_flag = False
    #The ai flag boolean is raised if the user chooses to play in 'Against Computer' mode
    ai_flag = False
    #The ai colour flag boolean is raised if the user chooses to change the colour that the AI opponent is playing as
    ai_colour_flag = False
    #The ai duel flag boolean is raised if the user chooses to play in the demo mode
    ai_duel_flag = False
    #The end flag boolean is raised if a given game ends
    end_flag = False
    #The buttons and popups lists are also used in brint and enput so that widgets can be created with unique variable names
    buttons = []
    popups = []
    #The moves list tracks the played moves in a game
    moves = []
    #The moved pieces list tracks the pieces that have been moved in a game
    moved_pieces = []
    #The taken pieces list tracks the pieces that have been taken in a game
    taken_pieces = []
    #The extras list tracks information to do with special moves (involving two pieces) like en passent or castling so that they can be undone
    extras = ["  "]
    #This instantiates the Board class
    board = TerminalBoard()
    board.initTerminalBoard()
    #The options list contains the functions that can be called within the menu to allow dynamic calling, rather than lots of if statements
    options = [seeMoves, seeTakenPieces, seeLegalMoves, seeHighscores, toggleLearnerMode, Save, Load]
