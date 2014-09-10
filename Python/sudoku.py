#!/usr/bin/python
#
# Sudoku Generator and Solver in 250 lines of python
# Copyright (c) 2006 David Bau.  All rights reserved.
#
# Modified for the pi printer from the Phil Burgess version
# this takes the printer as a param

import sys, os, random, getopt, re
from PIL import Image

def print_sudoku(printer):
  bg      = Image.new("1", [384, 426], "white") # Working 'background' image
  img     = Image.open('gfx/sudoku.png')        # Source bitmaps
  xcoord  = [ 15, 55,  95,  139, 179, 219,  263, 303, 343 ]
  ycoord  = [ 56, 96, 136,  180, 220, 260,  304, 344, 384 ]
  numbers = []
  # Crop number bitmaps out of source image
  for i in range(9):
    numbers.append(img.crop([384, i*28, 410, (i+1)*28]))
  puzzles = [makepuzzle(solution([None] * 81))]
  for puzzle in puzzles:
    printboard(puzzle, bg, numbers, xcoord, ycoord)           # Doesn't print, just modifies 'bg' image
    printer.printImage(bg, True) # This does the printing
    printer.println("RATING:", ratepuzzle(puzzle, 4))
  printer.feed(3)

def makepuzzle(board):
  puzzle = []; deduced = [None] * 81
  order = random.sample(xrange(81), 81)
  for pos in order:
    if deduced[pos] is None:
      puzzle.append((pos, board[pos]))
      deduced[pos] = board[pos]
      deduce(deduced)
  random.shuffle(puzzle)
  for i in xrange(len(puzzle) - 1, -1, -1):
    e = puzzle[i]; del puzzle[i]
    rating = checkpuzzle(boardforentries(puzzle), board)
    if rating == -1: puzzle.append(e)
  return boardforentries(puzzle)

def ratepuzzle(puzzle, samples):
  total = 0
  for i in xrange(samples):
    state, answer = solveboard(puzzle)
    if answer is None: return -1
    total += len(state)
  return float(total) / samples

def checkpuzzle(puzzle, board = None):
  state, answer = solveboard(puzzle)
  if answer is None: return -1
  if board is not None and not boardmatches(board, answer): return -1
  difficulty = len(state)
  state, second = solvenext(state)
  if second is not None: return -1
  return difficulty

def solution(board):
  return solveboard(board)[1]

def solveboard(original):
  board = list(original)
  guesses = deduce(board)
  if guesses is None: return ([], board)
  track = [(guesses, 0, board)]
  return solvenext(track)

def solvenext(remembered):
  while len(remembered) > 0:
    guesses, c, board = remembered.pop()
    if c >= len(guesses): continue
    remembered.append((guesses, c + 1, board))
    workspace = list(board)
    pos, n = guesses[c]
    workspace[pos] = n
    guesses = deduce(workspace)
    if guesses is None: return (remembered, workspace)
    remembered.append((guesses, 0, workspace))
  return ([], None)

def deduce(board):
  while True:
    stuck, guess, count = True, None, 0
    # fill in any spots determined by direct conflicts
    allowed, needed = figurebits(board)
    for pos in xrange(81):
      if None == board[pos]:
        numbers = listbits(allowed[pos])
        if len(numbers) == 0: return []
        elif len(numbers) == 1: board[pos] = numbers[0]; stuck = False
        elif stuck:
          guess, count = pickbetter(guess, count, [(pos, n) for n in numbers])
    if not stuck: allowed, needed = figurebits(board)
    # fill in any spots determined by elimination of other locations
    for axis in xrange(3):
      for x in xrange(9):
        numbers = listbits(needed[axis * 9 + x])
        for n in numbers:
          bit = 1 << n
          spots = []
          for y in xrange(9):
            pos = posfor(x, y, axis)
            if allowed[pos] & bit: spots.append(pos)
          if len(spots) == 0: return []
          elif len(spots) == 1: board[spots[0]] = n; stuck = False
          elif stuck:
            guess, count = pickbetter(guess, count, [(pos, n) for pos in spots])
    if stuck:
      if guess is not None: random.shuffle(guess)
      return guess

def figurebits(board):
  allowed, needed = [e is None and 511 or 0 for e in board], []
  for axis in xrange(3):
    for x in xrange(9):
      bits = axismissing(board, x, axis)
      needed.append(bits)
      for y in xrange(9):
        allowed[posfor(x, y, axis)] &= bits
  return allowed, needed

def posfor(x, y, axis = 0):
  if axis == 0: return x * 9 + y
  elif axis == 1: return y * 9 + x
  else: return ((0,3,6,27,30,33,54,57,60)[x] + (0,1,2,9,10,11,18,19,20)[y])

def axisfor(pos, axis):
  if axis == 0: return pos / 9
  elif axis == 1: return pos % 9
  else: return (pos / 27) * 3 + (pos / 3) % 3

def axismissing(board, x, axis):
  bits = 0
  for y in xrange(9):
    e = board[posfor(x, y, axis)]
    if e is not None: bits |= 1 << e
  return 511 ^ bits
  
def listbits(bits):
  return [y for y in xrange(9) if 0 != bits & 1 << y]

def allowed(board, pos):
  bits = 511
  for axis in xrange(3):
    x = axisfor(pos, axis)
    bits &= axismissing(board, x, axis)
  return bits

def pickbetter(b, c, t):
  if b is None or len(t) < len(b): return (t, 1)
  if len(t) > len(b): return (b, c)
  if random.randint(0, c) == 0: return (t, c + 1)
  else: return (b, c + 1)

def entriesforboard(board):
  return [(pos, board[pos]) for pos in xrange(81) if board[pos] is not None]

def boardforentries(entries):
  board = [None] * 81
  for pos, n in entries: board[pos] = n
  return board

def boardmatches(b1, b2):
  for i in xrange(81):
    if b1[i] != b2[i]: return False
  return True

def printboard(board, bg, numbers, xcoord, ycoord):
  bg.paste(img, (0, 0)) # Numbers are cropped off right side
  for row in xrange(9):
    for col in xrange(9):
      n = board[posfor(row, col)]
      if n is not None:
        bg.paste(numbers[n], (xcoord[col], ycoord[row]))

def parseboard(str):
  result = []
  for w in str.split():
    for x in w:
      if x in '|-=+': continue
      if x in '123456789': result.append(int(x) - 1)
      else: result.append(None)
      if len(result) == 81: return result

def loadboard(filename):
  f = file(filename, 'r')
  result = parseboard(f.read())
  f.close()
  return result

def basedir():
  if hasattr(sys.modules[__name__], '__file__'):
    return os.path.split(__file__)[0]
  elif __name__ == '__main__':
    if len(sys.argv) > 0 and sys.argv[0] != '':
      return os.path.split(sys.argv[0])[0]
    else:
      return os.curdir

def loadsudokutemplate(ext):
  f = open(os.path.join(basedir(), 'sudoku-template.%s' % ext), 'r')
  result = f.read()
  f.close()
  return result
