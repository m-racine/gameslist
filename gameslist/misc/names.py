# -*- coding: utf-8 -*-
#needs roman numeral check
#and just number check
#and checking sans a 1 at the end?
#all lower, all caps, mixed, lowercase on SOME words?

import re
import logging
import traceback
LOGGER = logging.getLogger('MYAPP')
# product = reduce((lambda x, y: x * y), [1, 2, 3, 4])
# print product 
#start_string = "arbitrary string of words and maybe a & symbol"
#ills = [': ', ' - ']
FILLS = [' ', ': ', ' - ', '-', ', ']
#& is not a standard fill, but a swap for and

def roman_to_arabic_or_false(test_string):
	#so anything outside of that, return false
	#I V X L C D M
	#1 5 10 50 100 500 1000
	return False

def fixGame(game):
    # to replace \ that's what you need in the re, \\\\
    game = re.sub(r"[:\/\?'\(;\.\)#&$,\\\\']","",game)
    game = game.replace("<","lt").replace(">","gt")
    game = game.replace(" ","-").lower();
    game = game.replace(u"\xe2\x80\x99","")
    game = re.sub(r"[\-]{2}", "-", game)
    game = re.sub(r"[\-]{2}", "---", game)
    return game

def helper(array,fills):
	output = []
	for fill in fills:
		if len(array) > 1:
				output.append([array[0],fill,array[1:]])
		else:
			output.append(array[0])
	return output

def check_nested(array):
	for a in array:
		for x in a:
			if isinstance(x, list):
				return True
	return False

def main(input_array, fills):
	array = helper(input_array,fills)
	if isinstance(array[0][2], list):
		for arr in array:
			if len(arr[2]) == 1:
				return array
			else:
				#print arr[2]
				arr[2] = main(arr[2],fills)
				#print arr[2]
			#print arr[2]
	#else:
	#print array
	return array

def flatten(input_array):
	if len(input_array) == 1:
		return input_array[0]
	return input_array[0] + input_array[1] + flatten(input_array[2])

def squash(input_array):
	output = []
	for x in input_array:
		if isinstance(x, str) or isinstance(x, unicode):
			return x
		if isinstance(x[2], list) and len(x[2]) > 1:
			for r in squash(x[2]):
				output.append([x[0],x[1],r])
		else:
			output.append([x[0],x[1],x[2]])
	return output

def fuse_fills(naive_split):
	array_len = len(naive_split)
	x = 0
	while x < array_len:
		#print naive_split[x]
		if naive_split[x] == "-":
			if x > 0 and x < (array_len -1):
				naive_split[x-1] = naive_split[x-1] + " - " + naive_split[x+1]
				naive_split.pop(x+1)
				naive_split.pop(x)
				x = 0
				array_len -= 2
				continue
			elif x > 0:
				naive_split[x-1] = naive_split[x-1] + " -"
				naive_split.pop(x)
				array_len -= 1
				x = 0
				continue
			elif x == 0:
				naive_split[x+1] = "- " + naive_split[x+1]
				naive_split.pop(x)
				array_len -= 1
				x = 0
				continue
		elif naive_split[x][-1:] in [":",",","."]:
			if x < (array_len -1):
				naive_split[x] = naive_split[x] + " " + naive_split[x+1]
				naive_split.pop(x+1)
				array_len -= 1
				x = 0
				continue
		elif naive_split[x] == "&":
			if x > 0 and x < (array_len -1):
				naive_split[x-1] = naive_split[x-1] + " & " + naive_split[x+1]
				naive_split.pop(x+1)
				naive_split.pop(x)
				x = 0
				array_len -= 2
				continue
			elif x > 0:
				naive_split[x-1] = naive_split[x-1] + " &"
				naive_split.pop(x)
				array_len -= 1
				x = 0
				continue
			elif x == 0:
				naive_split[x+1] = "& " + naive_split[x+1]
				naive_split.pop(x)
				array_len -= 1
				x = 0
				continue
		elif re.match("and",naive_split[x],re.IGNORECASE):
			if x > 0 and x < (array_len -1):
				naive_split[x-1] = naive_split[x-1] + " " + naive_split[x] + " " + naive_split[x+1]
				naive_split.pop(x+1)
				naive_split.pop(x)
				x = 0
				array_len -= 2
				continue
			elif x > 0:
				naive_split[x-1] = naive_split[x-1] + " " + naive_split[x]
				naive_split.pop(x)
				array_len -= 1
				x = 0
				continue
			elif x == 0:
				naive_split[x+1] = naive_split[x] + " " + naive_split[x+1]
				naive_split.pop(x)
				array_len -= 1
				x = 0
				continue
		elif re.search(r" and$",naive_split[x],re.IGNORECASE):
			if x > 0 and x < (array_len -1):
				naive_split[x-1] = naive_split[x-1]  + naive_split[x] + " " + naive_split[x+1]
				naive_split.pop(x+1)
				naive_split.pop(x)
				x = 0
				array_len -= 2
				continue
			elif x > 0:
				naive_split[x-1] = naive_split[x-1] + naive_split[x]
				naive_split.pop(x)
				array_len -= 1
				x = 0
				continue
			elif x == 0:
				naive_split[x+1] = naive_split[x] + " " + naive_split[x+1]
				naive_split.pop(x)
				array_len -= 1
				x = 0
				continue
		elif naive_split[x].startswith(", "):
			if x > 0:
				naive_split[x-1] = naive_split[x-1] + naive_split[x]
				naive_split.pop(x)
				array_len -= 1
				x = 0
				print naive_split
				continue
		x += 1
	return naive_split

def sub_and_helper(and_split):
	array_len = len(and_split)
	for x in range(0, array_len-1):
		if isinstance(and_split[x],list):
			#print and_split[x]
			var_0 = and_split[:]
			var_0[x] = var_0[x][0]
			var_1 = and_split[:]
			#print var_1
			var_1[x] = var_1[x][1]
			var_2 = and_split[:]
			#print var_1
			var_2[x] = var_2[x][2]
			return [sub_and_helper(var_0), sub_and_helper(var_1), sub_and_helper(var_2)]
	return and_split

def sub_and(naive_split):
	#print naive_split
	#LOGGER.debug(naive_split)
	and_splits = []
	for x in naive_split:
		if x == "&":
			and_splits.append(["&","and",", and"])
		elif re.match("and",x,re.IGNORECASE):
			and_splits.append(["&",x, ", "+x])
		else:
			and_splits.append(x)
	#LOGGER.debug(and_splits)
	and_splits = sub_and_helper(and_splits)
	#LOGGER.debug(and_splits)
	output_splits = []
	#print and_splits
	for a in and_splits:
		if isinstance(a[0],list):
			for x in a:
				and_splits.append(x)
		elif isinstance(a[0],str):
			output_splits.append(a)
		elif isinstance(a[0],unicode):
			output_splits.append(a)
	#print output_splits
	#LOGGER.debug(output_splits)
	if isinstance(output_splits[0], str):
		return [output_splits]
	elif isinstance(output_splits[0],unicode):
		return [output_splits]
	return output_splits

def add_endings(array_list):
	output = []
	for arr in array_list:
		if arr[-1:] in [".","!","?"]:
			pass
		else:
			output.append(arr+".")
			output.append(arr+"!")
			output.append(arr+"?")
		output.append(arr)
	return output

def gen_names(input_string):
	#print input_string
	if " " in input_string:
		LOGGER.debug(input_string)
		true_splits = []
		and_splits = sub_and(input_string.split(" "))
		for x in and_splits:
			true_splits.append(fuse_fills(x))
		cap_string = ' '.join(w.lower().capitalize() for w in input_string.split())
		if cap_string == input_string:
			pass
		else:
			and_splits = sub_and(cap_string.split(" "))
			for x in and_splits:
				true_splits.append(fuse_fills(x))
		output = []
		#print true_splits
		if len(true_splits[0]) == 1:
			return true_splits[0]
		for true in true_splits:
			array = main(true, FILLS)
			dest = squash(array)
			#print dest
			for d in dest:
				#print d
				output.append("".join(flatten(d)))
		#print output
		return add_endings(output)
	return [input_string]

def gen_metacritic_names(input_string):
	naive_list = gen_names(input_string)
	for x in range(0,len(naive_list)):
		naive_list[x] = fixGame(naive_list[x])
	return list(set(naive_list))

#print gen_names("Locked Hear  -- Typo")