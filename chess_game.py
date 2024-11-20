import pygame
from math import sqrt
import random
import time
import cProfile
import re

pygame.init()


# Set up the drawing window
screen = pygame.display.set_mode([576, 512])

def fenDecoder(fen):
    global turn
    #rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8
    
    separated=[]
    newstring=""
    for x in fen:
        if(x=="/" or x==" "):
            separated.append(newstring)
            newstring=""
        else:
            newstring+=x

    del separated[11]
    #del separated[10]
    #del separated[9]
    #print(separated)
    
    for x in range(len(separated)):
        if(x<=7):
            j=0
            for y in separated[x]:
                j+=1
                if(y.isdigit()):
                    newstring=""
                    for z in range(int(y)):
                        newstring+="e"
                    separated[x]=separated[x].replace(y,newstring)
        elif(x==8):
            separated[x]=separated[x].replace("w","white")
            separated[x]=separated[x].replace("b","black")
        #elif(x==10):
            
            
        #if(x==9):

    turn=separated[8]
    
    i=0
    for x in range(len(separated)-4):
        j=0
        for y in separated[x]:
            val=j+i*8
            #print(val)
            if(y.isupper()):
                color="white"
            else:
                color="black"
            if(y.upper()=="E"):
                squares[val]=("empty","empty",False)
            elif(y.upper()=="N"):
                squares[val]=("knight",color,True)
            elif(y.upper()=="B"):
                squares[val]=("bishop",color,True)
            elif(y.upper()=="Q"):
                squares[val]=("queen",color,True)
            elif(y.upper()=="K"):
                squares[val]=("king",color,True)
            elif(y.upper()=="P"):
                #print(color,i,j)
                squares[val]=("pawn",color,True)
                if(color=="white" and i==6):
                    squares[val]=("pawn",color,False)
                    #print(squares[val])
                elif(color=="black" and i==1):
                    squares[val]=("pawn",color,False)
                #else:
                    
            elif(y.upper()=="R"):
                squares[val]=("rook",color,True)
            j+=1
        i+=1

    for x in separated[9]:
        if(x=="k"):
            squares[7]=(squares[7][0],squares[7][1],False)
            squares[4]=(squares[4][0],squares[4][1],False)
        elif(x=="q"):
            squares[0]=(squares[0][0],squares[0][1],False)
            squares[4]=(squares[4][0],squares[4][1],False)
        elif(x=="K"):
            squares[63]=(squares[63][0],squares[63][1],False)
            squares[60]=(squares[60][0],squares[60][1],False)
        elif(x=="Q"):
            squares[56]=(squares[56][0],squares[56][1],False)
            squares[60]=(squares[60][0],squares[60][1],False)

    if(separated[10]!="-"):
        xval=ord(separated[10][0]) - 97
        yval=8-int(separated[10][1])
        val=xval+(yval*8)
        if(yval==6):
            lastmove=(val+8,val-8,squares[val-8][0],squares[0],squares[0])
        elif(yval==2):
            lastmove=(val-8,val+8,squares[val+8][0],squares[0],squares[0])
                        
    
        
def pieceValue(piece):
    imbalance=0
    if(piece=="pawn"):
        return 1
    elif(piece=="knight"):
        return 3
    elif(piece=="bishop"):
        return 3
    elif(piece=="rook"):
        return 5
    elif(piece=="king"):
        return 100
    elif(piece=="queen"):
        return 9
    return 0

def calcValue():
    white=0
    black=0
    
    x=0
    for x in range(64):
        if(squares[x]!=("empty","empty",False)):
            if(squares[x][1]=="white"):
                if(squares[x][0])=="pawn":
                    white+=1
                if(squares[x][0])=="knight":
                    white+=3
                if(squares[x][0])=="bishop":
                    white+=3
                if(squares[x][0])=="rook":
                    white+=5
                if(squares[x][0])=="king":
                    white+=100
                if(squares[x][0])=="queen":
                    white+=9

            if(squares[x][1]=="black"):
                if(squares[x][0])=="pawn":
                    black+=1
                if(squares[x][0])=="knight":
                    black+=3
                if(squares[x][0])=="bishop":
                    black+=3
                if(squares[x][0])=="rook":
                    black+=5
                if(squares[x][0])=="king":
                    black+=100
                if(squares[x][0])=="queen":
                    black+=9

    return white,black

def legalMoveGen(color):
    pieces=[x for x in range(64) if squares[x]!=("empty","empty",False) and squares[x][1]==color]
    possiblemoves, finalmoves=[],[]

    #for x in range(64):
    #    if(squares[x]!=("empty","empty",False) and squares[x][1]==color):
    #        pieces.append(x)

    for piece in pieces:
        for x in range(64):
            if(isPossible(piece,x)):
                if((x<8 or x>57) and squares[piece][0]=="pawn"):
                    possiblemoves.append((piece,x,0))
                    possiblemoves.append((piece,x,1))
                    possiblemoves.append((piece,x,2))
                    possiblemoves.append((piece,x,3))
                else:
                    possiblemoves.append((piece,x,-1))

    for move in possiblemoves:
        prev,temp = squares[move[0]], squares[move[1]]
    
        legal = makeLegalMove(move[0],move[1],move[2])
        
        if(kingSafe(color)==True):
            finalmoves.append(move)
            
        unmakeMove(move[0],move[1],temp,prev)
                    
    return finalmoves

def calcMoves(color):
    pieces=[]
    possiblemoves=[]

    for x in range(64):
        if(squares[x]!=("empty","empty",False) and squares[x][1]==color):
            pieces.append(x)

    for piece in pieces:
        for x in range(64):
            if(isPossible(piece,x)):
                if((x<8 or x>57) and squares[piece][0]=="pawn"):
                    possiblemoves.append((piece,x,0))
                    possiblemoves.append((piece,x,1))
                    possiblemoves.append((piece,x,2))
                    possiblemoves.append((piece,x,3))
                else:
                    possiblemoves.append((piece,x,-1))
                    
    return possiblemoves

def kingSafe(color):
    # array with positions of all opposite color pieces
    attackers=[]
    kingpos=-1
    
    for x in range(64):
        if(squares[x]!=("empty","empty",False) and color!=squares[x][1]):
            attackers.append(x)
        if(squares[x][0]=="king" and squares[x][1]==color):
            kingpos=x

    for loc in attackers:
        if(isPossible(loc, kingpos)):
            return False
    return True

def isCheckmate(pos):
    defenders=[]
    color=squares[pos][1]
    possiblemoves=[]

    for x in range(64):
        if(squares[x]!=("empty","empty",False) and color==squares[x][1]):
            defenders.append(x)

    for piece in defenders:
        for x in range(64):
            if(isPossible(piece,x)):
                possiblemoves.append((piece,x))
    
    for x in possiblemoves:
        #Start, Target
        temporary=squares[x[1]]
        squares[x[1]]=squares[x[0]]
        squares[x[0]]=("empty","empty",False)
        
        if(kingSafe(squares[x[1]][1])):
           
           squares[x[0]]=squares[x[1]]
           squares[x[1]]=temporary
           
           return False
        
        squares[x[0]]=squares[x[1]]
        squares[x[1]]=temporary
    return True
    #for

def inCheck(color):
    if(color=="none"):
        return -1
    else:
        for x in range(64):
            if(squares[x][0]=="king" and squares[x][1]==color):
                return x

def pathCheck(pathType, start, target):
    dist=calcDistance(start,target)[1]
    
    if(pathType=="linear"):
        startpos=calcCoordinates(start)
        targetpos=calcCoordinates(target)
        
        if(dist%1==0):
            if(startpos[0]==targetpos[0]):
                if(startpos[1]>targetpos[1]):
                    for x in range(int((startpos[1]-targetpos[1])/64)-1):
                        temp=(startpos[0],startpos[1]-((x+1)*64))
                        if(squares[calcLoc(temp)]!=("empty","empty",False)):
                            if(temp!=start):
                                return False
                    return True
                else:
                    for x in range(int((targetpos[1]-startpos[1])/64)-1):
                        temp=(startpos[0],startpos[1]+((x+1)*64))
                        if(squares[calcLoc(temp)]!=("empty","empty",False)):
                            if(temp!=start):
                                return False
                    return True
                
            elif(startpos[1]==targetpos[1]):
                if(startpos[0]>targetpos[0]):
                    temp=start
                    while(temp>target+1):
                        temp-=1
                        if(squares[temp]!=("empty","empty",False)):
                            if(temp!=start):
                                return False
                        
                    return True
                else:
                    temp=start
                    while(temp<target-1):
                        temp+=1
                        if(squares[temp]!=("empty","empty",False)):
                            if(temp!=start):
                                return False
                    return True
                return True
            else:
                return False
        else:
            return False

    elif(pathType=="diagonal"):
        if(round(dist/sqrt2,5)%1==0.0):
            if(abs(target-start)%7==0):
                if(start>target):
                    temp=start
                    while temp>target+7:
                        temp-=7
                        if(squares[temp]!=("empty","empty",False)):
                            if(temp!=start):
                                return False
                    return True
                else:
                    temp=start
                    while temp<target-7:
                        temp+=7
                        if(squares[temp]!=("empty","empty",False)):
                            if(temp!=start):
                                return False
                    return True

            elif(abs(target-start)%9==0):
                if(start>target):
                    temp=start
                    while temp>target+9:
                        temp-=9
                        if(squares[temp]!=("empty","empty",False)):
                            if(temp!=start):
                                return False
                    return True
                else:   
                    temp=start
                    while temp<target-9:
                        temp+=9
                        if(squares[temp]!=("empty","empty",False)):
                            if(temp!=start):
                                return False
                    return True

            else:
                return False
        else:
            return False
        
    return True

def isAttacked(pos,color):
    attackers=[]
    
    for x in range(64):
        if(squares[x]!=("empty","empty",False) and color!=squares[x][1]):
            attackers.append(x)

    for loc in attackers:
        if(isPossible(loc, pos)):
            return True
        
    return False


def calcCoord(loc):
    return loc%8, loc//8

def calcDistance(start,target):
    s, t=calcCoord(start), calcCoord(target)
    xdiff,ydiff=abs(s[0]-t[0]),abs(s[1]-t[1])
    
    if(xdiff==0):
        return ydiff*ydiff,abs(t[1]-s[1])
    elif(ydiff==0):
        return xdiff*xdiff,abs(t[0]-s[0])
    elif(xdiff==ydiff):
        return 2*xdiff*xdiff,sqrt2*xdiff
    else:
        squaresum=xdiff*xdiff+ydiff*ydiff
        return squaresum,sqrt(squaresum)
    
# Piece Logic
def isPossible(start,target, *args):
    global toundo
    global touncastle
    global toenpassant

    #touncastle=(0,0,False)
    #print(*args)
    piece=squares[start]
    
    if(args!=()):
        piece=args[0]
        
        

    #print(piece)
    #if(args!=()):
    #    print("GOT HERE")
    
    if(target==start):
        return False
    if(piece[1]==squares[target][1]):
        return False
    
    if(piece[0]=="rook"):
        if(pathCheck("linear",start,target)==True):
            return True
        else:
            return False

    
    elif(piece[0]=="bishop"):
        
        if(pathCheck("diagonal",start,target)==True):
            return True
        else:
            return False

    elif(piece[0]=="queen"):
        if(pathCheck("diagonal",start,target)==True or pathCheck("linear",start,target)==True):
            return True
        else:
            return False

    elif(piece[0]=="king"):
        # Normal Movement
        distance = calcDistance(start,target)[1]
        if(distance<1.5):
            return True

        # Castling
        if(piece[2]==False and isAttacked(start, turn)==False):
            # Short Side
            if(target-start==2):
                #Rook hasn't moved
                if(squares[start+3][2]==False and squares[start+3][0]=="rook"):
                    # No pieces in between
                    if(squares[start+1][0]=="empty" and squares[start+2][0]=="empty"):
                        if(isAttacked(start+1,squares[start][1]) == False):
                            return True
            # Long Side   
            elif(target-start==-2):
                #Rook hasn't moved
                if(squares[start-4][2]==False and squares[start-4][0]=="rook"):
                    # No pieces in between
                    if(squares[start-1][0]=="empty" and squares[start-2][0]=="empty" and squares[start-3][0]=="empty"):
                        if(isAttacked(start-1,squares[start][1]) == False):
                            return True

        return False

    elif(piece[0]=="pawn"):
        squaresum = calcDistance(start,target)[0]
        # Takes
        if(piece[1]=="black"):
            #Takes
            if(squaresum==2 and start<target):
                # Normal Take
                if(squares[target][0]!="empty"):
                    return True

                # En Passant
                
                if(lastmove[2]=="pawn" and lastmove[1]==target-8 and abs(lastmove[1]-lastmove[0])==16):
                    #toundo=(squares[target-8],target-8)
                    return True
                
            # Hasnt moved
            if(piece[2]==False):
                if(target-start==16 and squares[target][0]=="empty" and pathCheck("linear",start,target)==True):
                    return True

            # Has Moved
            if(target-start==8 and squares[target][0]=="empty"):
                return True
            else:
                return False

        else:
            #Takes
            if(squaresum==2 and start>target):
                # Normal Take
                if(squares[target][0]!="empty"):
                    return True

                # En Passant
                if(lastmove[2]=="pawn" and lastmove[1]==target+8  and abs(lastmove[1]-lastmove[0])==16):
                    #print("HOLY SHIT ITS EN PASSANT!")
                    #toundo=(squares[target+8],target+8)
                    #squares[target+8]=("empty","empty",False)
                    toenpassant=True
                    return True
                
            # Hasnt moved
            if(piece[2]==False):
                if(target-start==-16 and squares[target][0]=="empty" and pathCheck("linear",start,target)==True):
                    return True
                
            #Has Moved
            if(target-start==-8 and squares[target][0]=="empty"):
                return True
            else:
                return False

        

    elif(piece[0]=="knight"):
        squaresum = calcDistance(start,target)[0]
        #if(abs(target-start)==17 or abs(target-start)==15  or abs(target-start)==10 or abs(target-start)==6):
        if(squaresum==5):
            return True
        else:
            return False
        
    return False

def makeLegalMove(start, target, promo):
    global lastmove
    global prevlastmove

    prev=squares[start]
    temp=squares[target]

    color=squares[start][1]
    castle(start,target)
    enPassant(start,target)

    squares[target]=squares[start]
    squares[start]=("empty","empty",False)

    if(squares[target][2]==False):
        squares[target]=(squares[target][0],squares[target][1],True)

    lastmove=(start,target,squares[target][0],temp,prev)
    promotionStuff(target,promo)

def makeMove(start, target, promo):
    global lastmove
    global prevlastmove
    
    prev=squares[start]
    temp=squares[target]

    if(isPossible(start,target)):
        color=squares[start][1]

        castle(start,target)
        
        enPassant(start,target)
        
        squares[target]=squares[start]
        squares[start]=("empty","empty",False)
        
        if(kingSafe(color)==False):
            unmakeMove(start,target,temp,prev)
            return False
        else:
            if(squares[target][2]==False):
                squares[target]=(squares[target][0],squares[target][1],True)
            lastmove=(start,target,squares[target][0],temp,prev)
            promotionStuff(target,promo)
            return True

    
    return False

def checkCheck():
    global incheck
    global turn
    
    incheck=inCheck("none")
                                
    if(turn=="white"):
        if(kingSafe("black") == False):
            incheck=inCheck("black")
        turn="black"
    else:
        if(kingSafe("white") == False):
            incheck=inCheck("white")
        turn="white"

def promotionStuff(pos, promo):
    global promoting
    global turn
    global mademove
    
    promoting = checkPromotion(pos)[0]
    if(promoting==True):
        if(aicolor == "testing" or aicolor=="both"):
            promopiece=piecetypes[promo]
            squares[lastmove[1]]=(promopiece,squares[lastmove[1]][1],True)
            incheck=inCheck("none")
            selected="none"
            promoting=False
            mademove=False
        elif(turn != aicolor):
            turn="promo"
        else:
            promopiece=piecetypes[promo]
            squares[lastmove[1]]=(promopiece,squares[lastmove[1]][1],True)
            incheck=inCheck("none")
            selected="none"
            promoting=False
            mademove=False
            
        
            #print("White king in check!" + str(incheck))

def unmakeMove(start,target,temp,prev):
    global toundo
    global touncastle
    global lastmove
    global prevlastmove
    
    unCastle(start, target)
    unEnPassant(start,target)
    
    squares[start]=prev
    squares[target]=temp

enpassanted=False
toenpassant=False
def enPassant(start, target):
    global enpassanted
    global toenpassant

    #lastmove=(start,target,squares[target][0],temp,prev)
    #print("Yay")
    if(squares[start][0]=="pawn"):
        startpos=(calcCoordinates(start)[0]//64,calcCoordinates(start)[1]//64)
        targetpos=(calcCoordinates(target)[0]//64,calcCoordinates(target)[1]//64)
        squaresum = ((targetpos[0]-startpos[0])**2)+((targetpos[1]-startpos[1])**2)
        if(squaresum==2):
            if(lastmove[2]=="pawn" and lastmove[1]==target-8 and abs(lastmove[1]-lastmove[0])==16):
                #print("Black En Passant")
                squares[target-8]=("empty","empty",False)
                enpassanted=False
            elif(lastmove[2]=="pawn" and lastmove[1]==target+8 and abs(lastmove[1]-lastmove[0])==16):
                #print("White En Passant")
                squares[target+8]=("empty","empty",False)
                enpassanted=False
                

def unEnPassant(start,target):
    global enpassanted
    
    color=squares[target][1]

    if(enpassanted==True):
        if(color=="black"):
            squares[target-8]=("pawn","white",True)
        elif(color=="white"):
            squares[target-8]=("pawn","black",True)
       
def castle(start, target):
    
    if(squares[start][0]=="king"):
        #print(start,target)
        if(start-target==2):
            squares[start-1]=(squares[start-4][0],squares[start-4][1],True)
            squares[start-4]=("empty","empty",False)
            
        elif(start-target==-2):
            squares[start+1]=(squares[start+3][0],squares[start+3][1],False)
            squares[start+3]=("empty","empty",False)
            
def unCastle(start, target):
    if(squares[target][0]=="king"):
        if(start-target==2):
            squares[start-4]=(squares[start-1][0],squares[start-1][1],False)
            squares[start-1]=("empty","empty",False)
        elif(start-target==-2):
            squares[start+3]=(squares[start+1][0],squares[start+1][1],False)
            squares[start+1]=("empty","empty",False)

def playOpening():
    global movehistory
    global openingphase
    
    openings=[
            # Kings Pawn Opening, Italian game
            [(52,36),(12,28),(62,45),(1,18),(61,34),(5,26),(51,43),(11,19),(58,51),(2,11),(60,62)],
            # Queens Pawn Opening, Queens Gambit, Slav Defense
            [(51,35),(11,27),(50,34),(10,18),(57,42),(6,21),(52,44),(2,38),(62,45),(12,20)],
            # Queens Pawn Opening, Queens Gambit Declined
            [(51,35),(11,27),(50,34),(12,20),(57,42),(5,33),(58,51),(6,21),(62,45),(4,6)],
            # Polish Opening
            [(49,33),(12,28),(58,49),(5,33),(49,28),(6,21),(52,44),(11,19),(28,49),(2,29)],
            # English Opening
            [(50,34),(12,28),(57,42),(6,21),(54,46),(11,27),(51,43),(5,33),(61,54),(33,42)],
        ]

    potentialmoves=[]
    
    for x in openings:
        #temp=
        print(movehistory)
        print(x[0:len(movehistory)])
        if(movehistory==x[0:len(movehistory)]):
            
            if(len(movehistory)<len(x)):
                potentialmoves.append(x[len(movehistory)])

    if(len(potentialmoves)==0):
        openingphase=False
        #return random.choice(potentialmoves)
    else:
        return random.choice(potentialmoves)
               
def evaluateMoves(moves):
    ##### HEURISTICAL APPROACH, WILL TRY NEURAL NETWORK LATER ON #####
    global movehistory
    
    bestmoves=[]
    maximum=0
    maxweight=-10000
    #print(moves)
    
    for x in range(len(moves)):
        weight=0
        move=moves[x]
        #print(squares[move[0]][0])
        if(lastmove[1]==move[0]):
            weight-=10
        if(squares[move[0]][0]=="knight"):
            if(squares[move[0]][2]==False):
                weight+=2
            if((move[0]<8 or move[0]>55) and (move[1]%8>=2 and move[1]%8<=6) and (move[1]//8>=2 & move[1]//8<=6)):
                weight+=1
        elif(squares[move[0]][0]=="bishop"):
            if(squares[move[0]][2]==False):
                weight+=2
            if((move[0]<8 or move[0]>55) and (move[1]%8>=2 and move[1]%8<=6) and (move[1]//8>=2 & move[1]//8<=6)):
                weight+=1
        elif(squares[move[0]][0]=="rook"):
            if(squares[move[0]][2]==True):
                weight+=0.5
            if(len(movehistory)<15):
                weight-=2
            #if(squares[move[1]+8][0]=="pawn" or squares[move[1]-8][0]):
            #    weight-=3
        elif(squares[move[0]][0]=="pawn"):
            if((move[1]%8==3 or move[1]%8==4) and abs(move[1]-move[0])==16):
                weight+=5
            if(abs(move[1]-move[0])==7 or abs(move[1]-move[0])==9):
                weight-=1
            if(len(movehistory)>35):
                weight+=1
        elif(squares[move[0]][0]=="queen"):
            if(len(movehistory)<10):
                weight-=3
        elif(squares[move[0]][0]=="king"):
            if(abs(move[1]-move[0])==2):
                weight+=5
            if(len(movehistory)<20):
                weight-=2

        
        if(weight>maxweight):
            maximum=x
            maxweight=weight

    return moves[maximum]

def orderMoves(moves):
    newlist = []
    
    qcaptures = []
    rcaptures = []
    lcaptures = []
    pcaptures = []
    piecemoves = []
    tcentermoves = []
    checks = []
    remainder = []

    if(turn=="black"):
        color="white"
    else:
        color="black"

    for x in range(64):
        if(squares[x][0]=="king" and squares[x][1]==color):
            kingpos=x
    
    #top=len(newlist)-1
    for x in range(len(moves)):
        if(squares[moves[x][1]]!=("empty","empty",False)):
            value=pieceValue(squares[moves[x][1]])
            if(value==9):
                qcaptures.append(moves[x])
            elif(value==5):
                rcaptures.append(moves[x])
            elif(value==3):
                lcaptures.append(moves[x])
            else:
                pcaptures.append(moves[x])
        elif(isPossible(moves[x][1], kingpos, squares[moves[x][0]])):
            #print("WOAH BUSTER!",moves[x])
            checks.append(moves[x])
        elif(squares[moves[x][0]][0]!="pawn"):
            if(moves[x][1]//8>1 and moves[x][1]//8<6 and moves[x][1]%8>1 and moves[x][1]%8<6):
                #print("WOAH BUSTER!",moves[x])
                tcentermoves.append(moves[x])
            else:
                piecemoves.append(moves[x])
        else:
            remainder.append(moves[x])

    

    newlist = qcaptures + checks + rcaptures + lcaptures + pcaptures + tcentermoves + piecemoves + remainder
    #print("OY: " + str(checks))
    return newlist
    
def testMoves(depth,color,alpha,beta):
    global lastmove
    global total
    global debuglevel
    global aicolor

    # Alpha is -10000, beta is 10000, alpha is maximizer, beta is minimizer
    
    if(color=="black"):
        color="white"
    else:
        color="black"

    cont=False
    moves=orderMoves(legalMoveGen(color))
    numPositions=0
    movelines=[]

    prevlastmove=lastmove
    
    for move in moves:
        tobreak=False
        temptarget=squares[move[1]]
        prevstart=squares[move[0]]
            
        makeLegalMove(move[0],move[1],move[2])
        
        for x in range(debuglevel):
            if(depth==aidepth-x):
                print(color+" Move: " + str(turnToLetters(move[0],move[1], move[2])))

        
        if(depth==1):
            # node is a leaf, return the utility value of the node
            john=[]
            temp=calcValue()[0]-calcValue()[1]
            if(color=="white"):
                alpha=max(alpha,temp)
            else:
                beta=min(beta,temp)
                    
        else:
            john=testMoves(depth-1,color,alpha,beta)

            # Minimizer
            if(color=="black"):
                temp=-10000
                for x in john:
                    temp=max(temp,x[2])
                beta=min(beta,temp)

            # Maximizer
            else:
                temp=10000
                for x in john:
                    temp=min(temp,x[2])
                
                alpha=max(alpha,temp)
                
        movelines.append((move,john,temp))
        lastmove=prevlastmove
        unmakeMove(move[0],move[1],temptarget,prevstart)
        
        if(beta<alpha):
            break
    
    return movelines
        

total=0

def moveGenTestBulk(depth,color):
    global lastmove
    global total
    global debuglevel
    
    if(color=="black"):
        color="white"
    else:
        color="black"

    cont=False
    moves=legalMoveGen(color)
    numPositions=0

    if(depth==1):
        return len(moves)

    prevlastmove=lastmove
    
    for move in moves:
        temptarget=squares[move[1]]
        prevstart=squares[move[0]]

        
        makeLegalMove(move[0],move[1],move[2])
        
        for x in range(debuglevel):
            if(depth==bobby-x):
                print(color+" Move: " + str(turnToLetters(move[0],move[1], move[2])))
        
        numPositions+=moveGenTestBulk(depth-1,color)
        lastmove=prevlastmove
        unmakeMove(move[0],move[1],temptarget,prevstart)

        

    return numPositions

    
def moveGenTest(depth,color):
    #global prevlastmove
    global lastmove
    global total
    global debuglevel

    #debuglevel=3
    
    if(depth==0):
        return 1
    
    if(color=="black"):
        color="white"
    else:
        color="black"

    cont=False
    moves=calcMoves(color)
    numPositions=0
    
    temp=0

    prevlastmove=lastmove
    
    for move in moves:
        temptarget=squares[move[1]]
        prevstart=squares[move[0]]
        cont=makeMove(move[0],move[1],move[2])
        
        if(cont==True):
            for x in range(debuglevel):
                if(depth==bobby-x):
                    print(color+" Move: " + str(turnToLetters(move[0],move[1], move[2])))
            numPositions+=moveGenTest(depth-1,color)
            lastmove=prevlastmove
            unmakeMove(move[0],move[1],temptarget,prevstart)
            temp+=1

    for x in range(debuglevel):
        if(depth==bobby-x-1):
            print("Depth: " + str(depth) + " Positions: " + str(numPositions))
            print("")
                    
    return numPositions

def checkValidity(num):
    for value in correctvalues:
        if(value==num):
            return str(num) + " positions: CORRECT"
    return str(num) + " positions: WRONG"

def turnToLetters(start,target,promo):
    letters = ["A","B","C","D","E","F","G","H"]
    piece=squares[target][0]
    letter1 = letters[start%8]
    letter2 = letters[target%8]
    number1 = 8-(start//8)
    number2 = 8-(target//8)
    promopiece=""
    if(promo!=-1):
        promopiece=piecetypes[promo]
        piece="pawn"
    return piece+" "+letter1+str(number1)+letter2+str(number2)+" "+promopiece
    

def checkPromotion(pos):
    # Start, target, type
    # White pawn
    if(squares[pos][0] == "pawn" and squares[pos][1]=="white" and pos//8==0):
        return True, pos
    elif(squares[pos][0] == "pawn" and squares[pos][1]=="black" and pos//8==7):
        return True, pos
    else:
        return False, -1
        

def promotionBox():
    if(squares[lastmove[1]][1]=="white"):
        screen.blit(w_queen_img,(512,0))
        screen.blit(w_rook_img,(512,64))
        screen.blit(w_bishop_img,(512,128))
        screen.blit(w_knight_img,(512,192))
    else:
        screen.blit(b_queen_img,(512,0))
        screen.blit(b_rook_img,(512,64))
        screen.blit(b_bishop_img,(512,128))
        screen.blit(b_knight_img,(512,192))
            
def drawBoard():
    for x in range(8):
        for y in range(8):
            if((x+y) % 2==0 or (x+y)==0):
                color = white
            else:
                color = brown
            
            if(x+8*y==incheck):
                color=orange
                
            pos=(64*x,64*y,64,64)
            pygame.draw.rect(screen, color, pos)



def drawPieces():
    for x in range(64):
        if((squares[x][0],squares[x][1])==("queen","black")):
            screen.blit(b_queen_img,calcCoordinates(x))
            
        if((squares[x][0],squares[x][1])==("king","black")):
            screen.blit(b_king_img,calcCoordinates(x))
            
        if((squares[x][0],squares[x][1])==("knight","black")):
            screen.blit(b_knight_img,calcCoordinates(x))
            
        if((squares[x][0],squares[x][1])==("bishop","black")):
            screen.blit(b_bishop_img,calcCoordinates(x))
            
        if((squares[x][0],squares[x][1])==("rook","black")):
            screen.blit(b_rook_img,calcCoordinates(x))
            
        if((squares[x][0],squares[x][1])==("pawn","black")):
            screen.blit(b_pawn_img,calcCoordinates(x))
            
        if((squares[x][0],squares[x][1])==("queen","white")):
            screen.blit(w_queen_img,calcCoordinates(x))
            
        if((squares[x][0],squares[x][1])==("king","white")):
            screen.blit(w_king_img,calcCoordinates(x))
            
        if((squares[x][0],squares[x][1])==("knight","white")):
            screen.blit(w_knight_img,calcCoordinates(x))
            
        if((squares[x][0],squares[x][1])==("bishop","white")):
            screen.blit(w_bishop_img,calcCoordinates(x))
            
        if((squares[x][0],squares[x][1])==("rook","white")):
            screen.blit(w_rook_img,calcCoordinates(x))
            
        if((squares[x][0],squares[x][1])==("pawn","white")):
            screen.blit(w_pawn_img,calcCoordinates(x))

def calcCoordinates(loc):
    xpos=(loc%8)*64
    ypos=(loc//8)*64
    return xpos, ypos

def calcLoc(coordinates):
    xloc=coordinates[0]//64
    yloc=coordinates[1]//64
    loc=xloc+8*yloc
    return loc

squares=[]
for x in range(64):
    empty=("empty","empty",False)
    squares.append(empty)

# Type, Color, Has Moved

squares[0]=("rook","black",False)
squares[1]=("knight","black",False)
squares[2]=("bishop","black",False)
squares[3]=("queen","black",False)
squares[4]=("king","black",False)
squares[5]=("bishop","black",False)
squares[6]=("knight","black",False)
squares[7]=("rook","black",False)

squares[8]=("pawn","black",False)
squares[9]=("pawn","black",False)
squares[10]=("pawn","black",False)
squares[11]=("pawn","black",False)
squares[12]=("pawn","black",False)
squares[13]=("pawn","black",False)
squares[14]=("pawn","black",False)
squares[15]=("pawn","black",False)

squares[48]=("pawn","white",False)
squares[49]=("pawn","white",False)
squares[50]=("pawn","white",False)
squares[51]=("pawn","white",False)
squares[52]=("pawn","white",False)
squares[53]=("pawn","white",False)
squares[54]=("pawn","white",False)
squares[55]=("pawn","white",False)

squares[56]=("rook","white",False)
squares[57]=("knight","white",False)
squares[58]=("bishop","white",False)
squares[59]=("queen","white",False)
squares[60]=("king","white",False)
squares[61]=("bishop","white",False)
squares[62]=("knight","white",False)
squares[63]=("rook","white",False)


brown=(200,100,100)
white=(200,175,175)
orange=(250,100,50)
beige=(225,200,150)



w_king_img=pygame.image.load("white_king.png")
w_queen_img=pygame.image.load("white_queen.png")
w_knight_img=pygame.image.load("white_knight.png")
w_bishop_img=pygame.image.load("white_bishop.png")
w_rook_img=pygame.image.load("white_rook.png")
w_pawn_img=pygame.image.load("white_pawn.png")

b_king_img=pygame.image.load("black_king.png")
b_queen_img=pygame.image.load("black_queen.png")
b_knight_img=pygame.image.load("black_knight.png")
b_bishop_img=pygame.image.load("black_bishop.png")
b_rook_img=pygame.image.load("black_rook.png")
b_pawn_img=pygame.image.load("black_pawn.png")

selected="none"


# Start, Target, MovePiece, temp
lastmove=(0,0,"king",squares[0],squares[0])
prevlastmove=lastmove

#-1 is neither, otherwise square of the king in check
incheck=-1

# Is a piece going through promotion?, location of the target square
promoting=False
piecetypes=["queen","rook","bishop","knight"]

# Optimization
sqrt2=sqrt(2)
sqrt5=sqrt(5)

# King, queen, rook, bishop, knight, pawn
#piecevalues=[1000,9,5,3,3,1]

# White, Black
totalvalue=(0,0)

# Run until the user asks to quit
running = True

# Set the color the ai plays as
aicolor="black"
turn="white"
openingphase=True
movehistory=[]
debuglevel=1

# Depth
bobby=3 # this is for movegentestbulk
aidepth=3 # this is for ai
repeat=1 # debugging tool (to measure avg time

mademove=False
toundo=("empty","empty",False,-1)
touncastle=(0,0,False)
curcolor="white"
        
#fenDecoder("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")


while running:
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    
            
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            totalvalue=calcValue()
            if(aicolor=="both"):
                if(openingphase==True):
                    move=playOpening()
                    if(move!=None):
                        makeLegalMove(move[0],move[1],-1)

                if(openingphase==False):
                    if(turn=="black"):
                        col="white"
                    else:
                        col="black"
                    movelines=testMoves(aidepth, col)

                    maximum=-10000
                    bestmoves=[]
                    move=random.choice(movelines[0])
                    for x in movelines[0]:
                        if(x[2]>maximum):
                            maximum=x[2]

                    for x in movelines[0]:
                        if(x[2]==maximum):
                            bestmoves.append(x[0])
                            
                    #move=random.choice(bestmoves)
                    move=evaluateMoves(bestmoves)
                    makeLegalMove(move[0],move[1],move[2])

                mademove=True
                    
             # Player
            # MOVE GENERATION TEST
            elif(aicolor=="testing"):
                start = time.process_time()
                if(turn=="black"):
                    turn="white"
                else:
                    turn="black"
                #print("Total moves found (Regular Counting): " + str(moveGenTest(bobby,turn)))
                #print("Time taken: " + str(time.process_time()-start) + "s")

                
                avgtime=0
                for x in range(repeat):
                    start = time.process_time()
                    temp=moveGenTestBulk(bobby,turn)
                    avgtime+=time.process_time()-start
                print("Found " + str(temp) + " moves")
                print("Average time: "+str(round(avgtime/repeat,5))+"s")
                #cProfile.run("moveGenTestBulk(bobby,turn)")
                
            elif(promoting==True):
                prevturn=turn
                xval = pygame.mouse.get_pos()[0]//64
                yval = pygame.mouse.get_pos()[1]//64
                if(xval==8 and yval<=3):
                    promopiece=piecetypes[yval]
                    squares[lastmove[1]]=(promopiece,squares[lastmove[1]][1],True)
                    incheck=inCheck("none")
                    selected="none"
                    promoting=False
                    mademove=False
                    checkCheck()
                    
            elif(turn!=aicolor):       
                if selected!="none" and event.button==1:
                    pos = calcLoc(pygame.mouse.get_pos())
                    if(pos<=63):
                        mademove=makeMove(selected,pos,-1)
                        selected="none"
                    
                if event.button == 1 and selected == "none":
                    pos = calcLoc(pygame.mouse.get_pos())
                    if(pos<=63):
                        if(squares[pos][1]==turn):
                            selected=pos

                if event.button == 3:
                    selected="none"
            
            # Ai
            elif(turn==aicolor):

                if(openingphase==True):
                    move=playOpening()
                    if(move!=None):
                        makeLegalMove(move[0],move[1],-1)

                if(openingphase==False):
                    if(turn=="black"):
                        col="white"
                    else:
                        col="black"

                    start=time.process_time()
                    movelines=testMoves(aidepth, col,-10000,10000)
                    print("Time taken: " + str(time.process_time()-start) + "s")

                    bestmoves=[]
                    move=random.choice(movelines)[0]
                    if(aicolor=="white"):
                        maximum=-10000
                        for x in movelines:
                            if(x[2]>maximum):
                                maximum=x[2]

                        for x in movelines:
                            if(x[2]==maximum):
                                bestmoves.append(x[0])
                    else:
                        maximum=10000
                        for x in movelines:
                            if(x[2]<maximum):
                                maximum=x[2]

                        for x in movelines:
                            if(x[2]==maximum):
                                bestmoves.append(x[0])
                            
                    #move=random.choice(bestmoves)
                    move=evaluateMoves(bestmoves)
                    #print(movelines)
                    print(move)
                    print(maximum)
                    makeLegalMove(move[0],move[1],move[2])

                mademove=True
                    
                    
                #bestmove=findBestMove(movelines, aidepth)
                                
            if(mademove==True):
                
                if(promoting == False):
                    # Is one of the kings in check?
                    checkCheck()
                    movehistory.append((lastmove[0],lastmove[1]))
                    selected="none"
                    mademove=False
                            
            if event.button == 1:
                print(calcLoc(pygame.mouse.get_pos()))
            
            if(incheck!=-1):
                if(isCheckmate(incheck)):
                    if(turn=="white"):
                        winner="black"
                    if(turn=="black"):
                        winner="white"
                    print("Checkmate! " + winner + " won!")
                    #running = False
                

            
            
    

    # Fill the background with white
    screen.fill((255, 255, 255))

    # Draw the board
    drawBoard();

    # Draw the pieces
    drawPieces();

    # Draw Promotion Box
    if(promoting == True):
        promotionBox();
    
    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()
