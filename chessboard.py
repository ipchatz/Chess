import chess
import tkinter as tk
from PIL import ImageTk, Image
from chess import initTerminalChess, Move, brint, enput

class Board(tk.Frame):
    #This is the Board class (Operates the interactive tkinter GUI)
    #Adapted from: https://stackoverflow.com/questions/4954395/create-board-game-like-grid-in-python/4959995#4959995
    def __init__(self, parent, rows = 8, columns = 8, size = 64, colour1 = "olive drab", colour2 = "dark orchid"):
        #This function initialises the class with all the parameters
        self.rows = rows
        self.columns = columns
        #Size is the size of an individual square in pixels
        self.size = size
        self.colour1 = colour1
        self.colour2 = colour2
        #The pieces dictionary stores the positions of pieces, indexed by their names
        self._pieces = {}

        #The width and height of the board is calculated using size
        canvas_width = columns * size
        canvas_height = rows * size

        #Create the canvas for the board
        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth = 0, highlightthickness = 0, width = canvas_width, height = canvas_height, background = "goldenrod")
        self.canvas.pack(side = "top", fill = "both", expand = True, padx = 2, pady = 2)

        #Refreshes the window size
        self.canvas.bind("<Configure>", self._redrawBoard)

        #Add bindings for clicking and releasing any object with the "token" tag
        self.canvas.tag_bind("token", "<ButtonPress-1>", self._onTokenPress)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self._onTokenRelease)
        #Adapted from: https://stackoverflow.com/questions/44887576/how-make-drag-and-drop-interface

        #Tracks the piece being moved
        self._moveData = {"c0" : 0, "r0" : 0, "c1" : 0, "r1" : 0}

        #Stores the image data of the pieces
        self._piecePics = {
        "BP" : tk.PhotoImage(file='P.png'),
        "WP" : tk.PhotoImage(file='p.png'),
        "BR" : tk.PhotoImage(file='R.png'),
        "WR" : tk.PhotoImage(file='r.png'),
        "BN" : tk.PhotoImage(file='N.png'),
        "WN" : tk.PhotoImage(file='n.png'),
        "BB" : tk.PhotoImage(file='B.png'),
        "WB" : tk.PhotoImage(file='b.png'),
        "BQ" : tk.PhotoImage(file='Q.png'),
        "WQ" : tk.PhotoImage(file='q.png'),
        "BK" : tk.PhotoImage(file='K.png'),
        "WK" : tk.PhotoImage(file='k.png')}

        #A place to save to photos so Python’s garbage collector doesn't discard them
        self._photos = []

    def addPiece(self, name, image, column = 0, row = 0):
        #Keeps a reference of the image so it is not thrown in the trash
        self._photos.append(image)

        #This function adds a piece to the playing board
        self.canvas.create_image(0, 0, image = image, tags = (name, "piece", "token"), anchor = "c")
        self._placePiece(name, column, row)

    def _placePiece(self, name, column, row):
        #This function places a piece at the given row/column on the board
        self._pieces[name] = (column, row)
        #Updates the pieces dictionary and calculates the pixel position of the piece
        y0 = (column * self.size) + int(self.size / 2)
        x0 = (row * self.size) + int(self.size / 2)
        #Then place the piece at the given position
        self.canvas.coords(name, x0, y0)

    def _redrawBoard(self, event):
        #This function redraws the board (e.g. when the window is resized)
        xsize = int((event.width - 1) / self.columns)
        ysize = int((event.height - 1) / self.rows)
        #For instance, when the window is resized either the x or y size will be smaller
        self.size = min(xsize, ysize)
        #The board is a square so the smallest of these sizes is used
        self.canvas.delete("square")
        #The squares are half colour1 and half colour2
        colour = self.colour2
        for row in range(self.rows):
            #This for loop iterates over every row in the board
            colour = self.colour1 if colour == self.colour2 else self.colour2
            #The colour is toggled for every iteration
            for col in range(self.columns):
                #This for loop iterates over every column in the board
                x1 = (col * self.size)
                y1 = (row * self.size)
                #The pixel coordinates of the board are determined
                x2 = x1 + self.size
                y2 = y1 + self.size
                #Then the board is created with this data
                self.canvas.create_rectangle(x1, y1, x2, y2, outline = "black", fill = colour, tags = ("square", "token"))
                #The colour is toggled again for every iteration
                colour = self.colour1 if colour == self.colour2 else self.colour2

        for name in self._pieces:
            #This for loop iterates through all the pieces and places them on the board
            self._placePiece(name, self._pieces[name][0], self._pieces[name][1])

        #Finally, the pieces are raised a level above the squares so that they can be clicked by the user
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")

    def _refreshBoard(self):
        #This function refreshes the board (for instance, after a move)
        self._pieces.clear()
        self.canvas.delete("piece")
        #The pieces dictionary is cleared and then the pieces are deleted from the board
        board_size = len(chess.board.board)
        for y in range(board_size):
            for x in range(board_size):
                #These nested for loops iterate through all the squares in the logical board
                if chess.board.board[y][x] != "  ":
                    #If the square is not empty then place the piece on the board
                    piece = chess.board.board[y][x]
                    #The name of the piece is used to look up the picture from the piecePics dictionary
                    self.addPiece((y,x), self._piecePics[piece], y, x)

    def _onTokenPress(self, event):
        #This function is called when the left mouse button is clicked
        #This line of code changes the cursor to the watch style so the user knows that the move is loading
        root.config(cursor = "watch")
        #Records the original square location, with respect to the mouse click location event (i.e. conversion of user input to board coordinates)
        c0 = round((event.y - round(self.size / 2)) / self.size)
        r0 = round((event.x - round(self.size / 2)) / self.size)
        #Updates the moveData with these positions
        self._moveData["c0"] = c0
        self._moveData["r0"] = r0
        self._moveData["c1"] = 0
        self._moveData["r1"] = 0

    def _onTokenRelease(self, event):
        #This function is called when the left mouse button is released
        c1 = round((event.y - round(self.size / 2)) / self.size)
        r1 = round((event.x - round(self.size / 2)) / self.size)
        #Records the destination square location, with respect to the mouse release location event
        self._moveData["c1"] = c1
        self._moveData["r1"] = r1

        #Initialises the tkinter move with the move
        tkinterMove = str(self._moveData["c0"]) + str(self._moveData["r0"]) + str(self._moveData["c1"]) + str(self._moveData["r1"])

        #Moves the piece from the original square to the destination square
        Move(tkinterMove)
        #Refreshes the board so the user can see the move
        self._refreshBoard()

        #Resets the move data
        self._moveData["c0"] = 0
        self._moveData["r0"] = 0
        #Resets the cursor style
        root.config(cursor = "arrow")

def initTkinterBoard():
    #This function initialises the tkinter board
    tkBoard = Board(root)
    tkBoard.pack(side = "top", fill = "both", expand = "true", padx = 4, pady = 4)
    #Resets the board to the opening state
    tkBoard.canvas.delete("piece")
    #All of the pieces are loaded from image files and placed onto the board
    bpawn = tk.PhotoImage(file='P.png')
    wpawn = tk.PhotoImage(file='p.png')
    #Lower case characters are white pieces and upper case characters are black pieces
    for x in range(8):
        tkBoard.addPiece((1,x), bpawn, 1, x)
        tkBoard.addPiece((6,x), wpawn, 6, x)

    brook = tk.PhotoImage(file='R.png')
    wrook = tk.PhotoImage(file='r.png')
    tkBoard.addPiece((0,0), brook, 0, 0)
    tkBoard.addPiece((0,7), brook, 0, 7)
    tkBoard.addPiece((7,0), wrook, 7, 0)
    tkBoard.addPiece((7,7), wrook, 7, 7)

    bknight = tk.PhotoImage(file='N.png')
    wknight = tk.PhotoImage(file='n.png')
    tkBoard.addPiece((0,1), bknight, 0, 1)
    tkBoard.addPiece((0,6), bknight, 0, 6)
    tkBoard.addPiece((7,1), wknight, 7, 1)
    tkBoard.addPiece((7,6), wknight, 7, 6)

    bbishop = tk.PhotoImage(file='B.png')
    wbishop = tk.PhotoImage(file='b.png')
    tkBoard.addPiece((0,2), bbishop, 0, 2)
    tkBoard.addPiece((0,5), bbishop, 0, 5)
    tkBoard.addPiece((7,2), wbishop, 7, 2)
    tkBoard.addPiece((7,5), wbishop, 7, 5)

    bqueen = tk.PhotoImage(file='Q.png')
    wqueen = tk.PhotoImage(file='q.png')
    tkBoard.addPiece((0,3), bqueen, 0, 3)
    tkBoard.addPiece((7,3), wqueen, 7, 3)

    bking = tk.PhotoImage(file='K.png')
    wking = tk.PhotoImage(file='k.png')
    tkBoard.addPiece((0,4), bking, 0, 4)
    tkBoard.addPiece((7,4), wking, 7, 4)

def mainMenu(event = None):
    #This function creates the main menu window
    clearWindow()
    #The window is cleared of all widgets in the mainFrame and then the new widgets are packed
    labelTitle = tk.Label(mainFrame, text = "CHESS")
    labelTitle.config(font = ("Comic Sans MS", 24, "bold"))
    labelTitle.pack()
    #This includes the title as a label, the chess background image
    imageChessBG = ImageTk.PhotoImage(Image.open('Chess.png'))
    labelChessBG = tk.Label(mainFrame, image = imageChessBG)
    labelChessBG.photo = imageChessBG
    labelChessBG.place(x = 0, y = 0, width = 1, height = 1)
    labelChessBG.pack()
    labelBlank = tk.Label(mainFrame)
    labelBlank.pack()
    #There is a blank label so the spacing is nicer and some buttons to access other windows
    buttonPlay = tk.Button(mainFrame, command = selectOpponentWindow, text = "Play a Game")
    buttonPlay.pack()
    #These buttons access the select opponent window and account window respectively
    buttonAccount = tk.Button(mainFrame, command = accountWindow, text = "Access Account")
    buttonAccount.pack()
    #Finally, the root widgets are cleared (this is so there are not multiple exit labels - mentioned later)
    while len(root.winfo_children()) > 1:
        root.winfo_children()[-1].destroy()

def accountWindow(event = None):
    #This function creates the account window
    clearWindow()
    #Most windows are relatively similar, all of them feature a title label
    labelAccount = tk.Label(mainFrame, text = "Access Account")
    labelAccount.config(font = ("Comic Sans MS", 12, "bold"))
    labelAccount.pack()
    #This image is also used in several windows
    imageChessBG = ImageTk.PhotoImage(Image.open('Chess.png'))
    labelChessBG = tk.Label(mainFrame, image = imageChessBG)
    labelChessBG.photo = imageChessBG
    labelChessBG.place(x = 0, y = 0, width = 1, height = 1)
    labelChessBG.pack()
    labelBlank = tk.Label(mainFrame)
    labelBlank.pack()
    #This button takes the user to the login window
    buttonLogin = tk.Button(mainFrame, command = loginWindow, text = "Login to Account")
    buttonLogin.pack()
    #This button takes the user to the create account window
    buttonCreate = tk.Button(mainFrame, command = createAccountWindow, text = "Create Account")
    buttonCreate.pack()
    #This is the exit label, the mainMenu function is binded to the escape key
    labelExit = tk.Label(text = "Press <ESC> to return to the main menu at any time")
    labelExit.pack(side = "bottom")
    #This while loop clears all root widgets apart from this exit label and the root frame itself
    while len(root.winfo_children()) > 2:
        root.winfo_children()[-1].destroy()

def loginWindow(event = None):
    #This function creates the login window
    clearWindow()
    #This label is the title
    labelLogin = tk.Label(mainFrame, text = "Login to Account")
    labelLogin.config(font = ("Comic Sans MS", 12, "bold"))
    labelLogin.pack()
    #Here is an image of a chessboard
    imageChessBG = ImageTk.PhotoImage(Image.open('Chess.png'))
    labelChessBG = tk.Label(mainFrame, image = imageChessBG)
    labelChessBG.photo = imageChessBG
    labelChessBG.place(x = 0, y = 0, width = 1, height = 1)
    labelChessBG.pack()
    #Here is a blank label
    labelBlank = tk.Label(mainFrame)
    labelBlank.pack()
    #This is an entry box where the user can enter their username to login
    entryUsername = tk.Entry(mainFrame)
    entryUsername.pack()
    entryUsername.focus_set()
    #This focus_set function makes the entry box usable multiple times
    def getUsername():
        #This function gets the username and logs the user in with it
        username = entryUsername.get()
        if username == "":
            #If the user leaves the entry blank when the button is pressed then the function ends early and the user can try again
            brint("\nPlease enter a username\n")
            return None

        with open("usernames.txt") as f:
            #If the username is valid then the usernames file is read
            u_data = f.read()

        #The username data is then split by line
        u_split = u_data.split("\n")
        valid_flag = False
        for name in u_split:
            if name == username:
                #If the username that the user entered is found in the file then the valid flag is raised
                valid_flag = True

        if valid_flag == False:
            #If the username was not found then the user is not logged in
            brint("\nPlease enter a valid username.\n")

        else:
            #Otherwise the user is logged in
            chess.nameUser = username
            #The variable nameUser (a global variable from the chess.py) is assigned the username, thus loggin the user in
            login_string = "\nLogged in as " + username + ".\n"
            #A message is brinted to tell the user that the log in was successful
            brint(login_string)

    buttonEnter = tk.Button(mainFrame, text = "Enter", command = getUsername)
    buttonEnter.pack()
    #When the user presses this button the getUsername function is run
    labelExit = tk.Label(text = "Press <ESC> to return to the main menu at any time")
    labelExit.pack(side = "bottom")
    #Here is the exit label and the while loop to clear any other root widgets
    while len(root.winfo_children()) > 2:
        root.winfo_children()[-1].destroy()

def createAccountWindow(event = None):
    #This function creates the create account window
    clearWindow()
    #Here is the title
    labelAccount = tk.Label(mainFrame, text = "Create Account")
    labelAccount.config(font = ("Comic Sans MS", 12, "bold"))
    labelAccount.pack()
    #The window is the same as the previous one apart from the getUsername function
    imageChessBG = ImageTk.PhotoImage(Image.open('Chess.png'))
    labelChessBG = tk.Label(mainFrame, image = imageChessBG)
    labelChessBG.photo = imageChessBG
    labelChessBG.place(x = 0, y = 0, width = 1, height = 1)
    labelChessBG.pack()
    labelBlank = tk.Label(mainFrame)
    labelBlank.pack()
    entryUsername = tk.Entry(mainFrame)
    entryUsername.pack()
    entryUsername.focus_set()
    #The order in which the wigets are created does affect the appearance of the GUI, so it is difficult to design a general window function
    def getUsername():
        #This time the function gets the username and adds it to the usernames file if it does not already exist
        username = entryUsername.get()
        if username == "":
            #Same error handling as before, if the entry box is blank then exit the function
            brint("\nPlease enter a username\n")
            return None
        
        with open("usernames.txt") as f:
            u_data = f.read()

        u_split = u_data.split("\n")
        #The data is read from the file and split by line
        for name in u_split:
            if name == username:
                #If a duplicate is found then the username is not added
                brint("\nThis user already exists.\n")
                return None

        u_data += username + "\n"
        #Otherwise the username is added with a new line character and a message is brinted to provide feedback to the user
        f = open("usernames.txt", "w")
        f.write(u_data)
        f.close()
        brint("\nUsername added.\n")

    buttonEnter = tk.Button(mainFrame, text = "Enter", command = getUsername)
    buttonEnter.pack()
    labelExit = tk.Label(text = "Press <ESC> to return to the main menu at any time")
    labelExit.pack(side = "bottom")
    while len(root.winfo_children()) > 2:
        root.winfo_children()[-1].destroy()

def selectOpponentWindow(event = None):
    #This function creates the select opponent window
    clearWindow()
    #Here the window is cleared from all previous widgets and the title is packed
    labelOpponent = tk.Label(mainFrame, text = "Select Opponent")
    labelOpponent.config(font = ("Comic Sans MS", 12, "bold"))
    labelOpponent.pack()
    #Here is the chess image
    imageChessBG = ImageTk.PhotoImage(Image.open('Chess.png'))
    labelChessBG = tk.Label(mainFrame, image = imageChessBG)
    labelChessBG.photo = imageChessBG
    labelChessBG.place(x = 0, y = 0, width = 1, height = 1)
    labelChessBG.pack()
    labelBlank = tk.Label(mainFrame)
    labelBlank.pack()
    #Here the user has some options, which opponent do they want to play against?
    buttonHuman = tk.Button(mainFrame, command = pvpWindow, text = "Against Human Opponent")
    buttonHuman.pack()
    #They can either play against a local friend or against an AI opponent
    buttonCPU = tk.Button(mainFrame, command = cpuWindow, text = "Against AI Opponent")
    buttonCPU.pack()
    #Blank label for nicer spacing
    labelBlank = tk.Label(mainFrame)
    labelBlank.pack()
    #The user could also choose to watch an AI vs AI demo
    buttonDemo = tk.Button(mainFrame, command = demoWindow, text = "Run Demo (AI vs AI)")
    buttonDemo.pack()
    #Each of these buttons takes the user to the respective window
    labelExit = tk.Label(text = "Press <ESC> to return to the main menu at any time")
    labelExit.pack(side = "bottom")
    while len(root.winfo_children()) > 2:
        root.winfo_children()[-1].destroy()

def pvpWindow(event = None):
    #This function creates the human sub window
    clearWindow()
    #The window is cleared and the title is packed
    labelPlayer = tk.Label(mainFrame, text = "Versus Player")
    labelPlayer.config(font = ("Comic Sans MS", 11, "bold"))
    labelPlayer.pack()
    #The entry box does not do anything, but it is here so that the windows have a consistent look to them
    entryMove = tk.Entry(mainFrame)
    entryMove.pack()
    entryMove.focus_set()
    def getEntry(): return entryMove.get()
    #In the other modes this button runs more useful functions
    buttonEnter = tk.Button(mainFrame, text = "Enter", command = getEntry)
    buttonEnter.pack()
    #These buttons are always available to be pressed by the user
    buttonMenu = tk.Button(text = "Menu", command = lambda : chess.Menu())
    buttonMenu.pack(side = "right")
    #The Menu button brints the menu and opens a pop-up for enput, the menu contains more functions that can be run
    buttonResign = tk.Button(text = "Resign", command = lambda : chess.Resign())
    buttonResign.pack(side = "right")
    #These buttons are used to resign, to offer a draw, or to offer a takeback respectively
    buttonDraw = tk.Button(text = "Draw", command = lambda : chess.offerDraw())
    buttonDraw.pack(side = "right")
    #By packing the buttons to the right, they appear to the right of the chessboard, rather than underneath
    buttonTakeback = tk.Button(text = "Takeback", command = lambda : chess.offerTakeback())
    buttonTakeback.pack(side = "right")
    #Then the logical and physical chess boards are initialised
    initTerminalChess()
    initTkinterBoard()
    #There is also a back button which returns the user to the previous window
    buttonBack = tk.Button(mainFrame, command = selectOpponentWindow, text = 'Back')
    buttonBack.pack(side = "bottom")
    #Here are some instructions to help the user get familiar with the software
    brint("Click the 'Menu' button to view the menu options")
    brint("Click the board to make the AI move")
    brint("Click instructions to make them disappear!")

def cpuWindow(event = None):
    #This function creates the AI sub window
    clearWindow()
    #This window is the same as the human sub window except for the entry widget which is actually used here
    labelCPU = tk.Label(mainFrame, text = "Versus Computer")
    labelCPU.config(font = ("Comic Sans MS", 11, "bold"))
    labelCPU.pack()
    entryMove = tk.Entry(mainFrame)
    entryMove.pack()
    entryMove.focus_set()
    def getAIChoice():
        #This function is used to change certain in game features
        ai_choice = entryMove.get()
        if ai_choice == "B":
            #The user can change the colour of piece that the AI opponent plays as
            chess.ai_colour_flag = True
            #The ai colour flag in chess.py is raised and a message is outputted to confirm the colour change
            brint("AI colour changed")

        elif ai_choice == "W":
            #This feature could be used as a form of a hint system
            chess.ai_colour_flag = False
            #If the user does not know what to play they can make the AI play for them
            brint("AI colour changed")

        elif ai_choice == "0" or ai_choice == "1" or ai_choice == "2" or ai_choice == "3":
            #The user can also change the ai difficulty level whilst playing
            chess.difficulty_level = int(ai_choice)
            d_string = "AI difficulty level: " + str(ai_choice)
            #A message is outputted to provide feedback to the user
            brint(d_string)

        else:
            #If a valid input is not given then some instructions are brinted to help the user
            brint("\nEnter W/B to change the AI colour\n")
            brint("\nEnter a number from 0 to 3 to change AI difficulty\n")

    buttonEnter = tk.Button(mainFrame, text = "Enter", command = getAIChoice)
    buttonEnter.pack()
    buttonMenu = tk.Button(text = "Menu", command = lambda : chess.Menu())
    buttonMenu.pack(side = "right")
    buttonResign = tk.Button(text = "Resign", command = lambda : chess.Resign())
    buttonResign.pack(side = "right")
    buttonDraw = tk.Button(text = "Draw", command = lambda : chess.offerDraw())
    buttonDraw.pack(side = "right")
    buttonTakeback = tk.Button(text = "Takeback", command = lambda : chess.offerTakeback())
    buttonTakeback.pack(side = "right")
    initTerminalChess()
    initTkinterBoard()
    chess.ai_flag = True
    #The ai flag is raised so that the Move function in chess.py allows the AI to play every other turn
    buttonBack = tk.Button(mainFrame, command = selectOpponentWindow, text = "Back")
    buttonBack.pack(side = "bottom")
    brint("Click the 'Menu' button to view the menu options")
    brint("Click the board to make the AI move")
    brint("Click instructions to make them disappear!")

def demoWindow(event = None):
    #This function creates the Demo sub window
    clearWindow()
    #This is the same as the cpu window except colour cannot be changed
    labelCPU = tk.Label(mainFrame, text = "AI vs AI Demo")
    labelCPU.config(font = ("Comic Sans MS", 11, "bold"))
    labelCPU.pack()
    entryMove = tk.Entry(mainFrame)
    entryMove.pack()
    entryMove.focus_set()
    def getAIChoice():
        ai_choice = entryMove.get()
        if ai_choice == "0" or ai_choice == "1" or ai_choice == "2" or ai_choice == "3":
            #The user is able to change difficulty in this mode, but not colour
            chess.difficulty_level = int(ai_choice)
            #If the user were to change the colour it would have no effect since it is AI vs AI
            d_string = "AI difficulty level: " + str(ai_choice)
            brint(d_string)

        else:
            brint("\nEnter a number from 0 to 3 to change AI difficulty\n")

    buttonEnter = tk.Button(mainFrame, text = "Enter", command = getAIChoice)
    buttonEnter.pack()
    buttonMenu = tk.Button(text = "Menu", command = lambda : chess.Menu())
    buttonMenu.pack(side = "right")
    buttonResign = tk.Button(text = "Resign", command = lambda : chess.Resign())
    buttonResign.pack(side = "right")
    buttonDraw = tk.Button(text = "Draw", command = lambda : chess.offerDraw())
    buttonDraw.pack(side = "right")
    buttonTakeback = tk.Button(text = "Takeback", command = lambda : chess.offerTakeback())
    buttonTakeback.pack(side = "right")
    initTerminalChess()
    initTkinterBoard()
    chess.ai_duel_flag = True
    #Here a difficult flag is raised to indicate that the user wants to play in the demo mode
    buttonBack = tk.Button(mainFrame, command = selectOpponentWindow, text = "Back")
    buttonBack.pack(side = "bottom")
    brint("Click the 'Menu' button to view the menu options")
    brint("Click the board to make the AI move")
    brint("Click instructions to make them disappear!")

def clearWindow(event = None):
    #This function clears widgets from the mainFrame
    for widget in mainFrame.winfo_children():
        widget.destroy()

def Escape(event):
    #This function returns the user to the main menu if the escape key is pressed
    mainMenu()

if __name__ == "__main__":
    #Here is the only code in the whole program that is not within a function or a separate file
    root = tk.Tk()
    #The root is created and the window geometry is set
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    #The window takes the height of the user's screen as well as the width divided by the golden ratio
    root.geometry("%dx%d+0+0" % (screen_width / 1.618, screen_height))
    #Here the escpape key is binded to the Escape function
    root.bind("<Escape>", Escape)

    #These lines of code create the usernames and highscores files in case they do not exist
    with open("usernames.txt", "a+") as f:
        with open("highscores.txt", "a+") as f:
            #For instance, if it is the user's first time running the software
            pass

    #The main frame is created
    mainFrame = tk.Frame(root)
    mainFrame.pack()
    #Then some more frames are created, these frames allow the buttons to go next to the board in the opponent windows
    topFrame = tk.Frame(root)
    bottomFrame = tk.Frame(root)
    #The top frame is packed to the top
    topFrame.pack(side = "top")
    #The bottom frame is packed to the botttom and expands to fill the rest of the screen
    bottomFrame.pack(side = "bottom", fill = "both", expand = True)
    #The logical side of the Chess program is initialised (for instance, if the user wants to log-in before starting a game)
    initTerminalChess()
    #The name of the user is initialised separately, so that it is not overwritten everytime the init function is called
    chess.nameUser = ""
    #Finally, the mainMenu function is run and the whole program begins
    mainMenu()
    #This mainloop is required for tkinter GUI programs to function correctly
    root.mainloop()
