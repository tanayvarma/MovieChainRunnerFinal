from pygraph.classes.graph import graph
from pygraph.classes.digraph import digraph
import copy

# IMPORTANT - Change this path so that it points to where MOVIES.LST is located on your computer
movieFileLoc = "/Users/tanayvarma/Desktop/MOVIES.LST"

NUM_MOVIES = 6561
print "Started"
Max_Recursion_Calls = 10

movieGraph = digraph()
movieArray = []
moviesToCheck = []
preProcessMovies = []


def readMovies():
	movieNum = 0
	with open(movieFileLoc) as movieList:
		for line in movieList:
			movieGraph.add_node(movieNum)
			movieArray.append(line[:-1])
			movieNum += 1

def preProcess():
	for i in xrange(NUM_MOVIES):
		split = movieArray[i].split(" ")
		preString = ""
		postString = ""
		preSubStrings = []
		postSubStrings = []
		l = len(split)
		for i in xrange(l):
			preString = split[l - 1 -i] + preString
			postString += split[i]
			preSubStrings.append(preString)
			postSubStrings.append(postString)
			preString = " " + preString
			postString += " "
		preProcessMovies.append((preSubStrings,postSubStrings,len(split)))



def overlap(f,s):
	if f == s:
		return False

	postStrings = preProcessMovies[f][0]
	preStrings = preProcessMovies[s][1]

	i = 0

	while( i < min(preProcessMovies[f][2],preProcessMovies[s][2])):
		if preStrings[i] == postStrings[i]:
			return True
		i += 1

	return False

def addEdges():
	ctr = 0
	for prevMovie in xrange(NUM_MOVIES):
		for nextMovie in xrange(NUM_MOVIES):
			if prevMovie != nextMovie:
				if overlap(prevMovie,nextMovie):
					movieGraph.add_edge((prevMovie,nextMovie))


def moviesToStartSearchWith():
	
    for i in xrange(NUM_MOVIES):
        nextMovies = movieGraph.neighbors(i)
        prevMovies = movieGraph.incidents(i)

        if (nextMovies == []):
            continue

        if (len(nextMovies) == 1 and len(prevMovies) == 1):
            continue

        moviesToCheck.append(i)



def makeInitialChains(startMovie):

	#Implementing incomplete breadth first search from start movie to get 
	# a decently long chain
	workingSet = set([startMovie])
	nextSet = set([])
	count = 0
	distance = [-NUM_MOVIES] * NUM_MOVIES 
	chains = [[]] * NUM_MOVIES
	chains[startMovie].append(startMovie)
	while (count < NUM_MOVIES and len(workingSet) != 0):
		for currMovie in workingSet:
			for nextMovie in movieGraph.neighbors(currMovie):
				currDistance = distance[currMovie];
				maxDistance = 19
				if (distance[nextMovie] > currDistance + maxDistance):
					if nextMovie in nextSet:
						continue

				if (distance[nextMovie] == -NUM_MOVIES or nextMovie not in chains[currMovie]):
					distance[nextMovie] = currDistance + 1
					chains[nextMovie] = copy.deepcopy(chains[currMovie])
					chains[nextMovie].append(nextMovie)
					nextSet.add(nextMovie)
		
		(workingSet,nextSet) = (nextSet,workingSet)
		nextSet = set([])
		count += 1


	return extendMax(chains)


def find(l,x):
	if x in l:
		return l.index(x)
	else:
		return -1


def findLongerChain(first_movie,chainSegment,alreadyInChain,currChain):
	
	# chainSegment is a list of movies starting with movie first_movie, and alreadyInChain
	# has all the movies that were in the original longChain
	#Current chain is what we are trying to maximise, to longer than the chainSegment
	
	# if we have recursed Max_Recursion_Calls times stop recursing
	if len(currChain) == Max_Recursion_Calls:
		return currChain

	#currChain keeps track of recursion depth
	currChain.append(first_movie)

	currDepth = len(currChain)

	neighbors = movieGraph.neighbors(first_movie)

	bestList = []

	for i in xrange(len(neighbors)):
		#movie that connects from first_movie
		nextMovie = neighbors[i]


		# checks if nextMovie is in our chainSegment
		last_index = find(chainSegment,nextMovie)

		# if movie not in current segment but in longer chain do nothing
		# because there are at least Max_Recursion_Calls movies in the middle of first_movie and next movie
		# in longer chain it doesnt make sense to change that here so do nothing
		if alreadyInChain[nextMovie] and last_index == -1:
			continue

		#We already put nextMovie in current chain and there is a cycle here so do nothing
		if nextMovie in currChain:
			continue

		if currDepth < len(chainSegment) and chainSegment[currDepth] == nextMovie:
			continue

		


		temp = []

		if last_index >= 0 and last_index < currDepth:
	
			temp = copy.deepcopy(currChain)
			#Add all the movies from nextMovie in chainSegment to end of currChain
			for j in xrange(last_index , len(chainSegment)):
				#However if any movie already in currChain reset temp and break
				n = chainSegment[j]

				if n not in temp:
					temp.append(n)
				else:
					temp = []
					break
				

			#update bestList if temp is better
			if len(temp) > len(bestList):
				bestList = copy.deepcopy(temp)

		#call findLongerChain again with nextMovie as first_movie and currChain having startMovie
		temp = findLongerChain(nextMovie,chainSegment,alreadyInChain,copy.deepcopy(currChain))


		#update bestList if temp is better
		if len(temp) > len(bestList):
			bestList = copy.deepcopy(temp)

	return bestList



def extendChain(chainToExtend):
	segment_length = Max_Recursion_Calls

	alreadyInChain = [False] * NUM_MOVIES

	# update all the movies already in longerChain to 1
	for x in chainToExtend:
		alreadyInChain[x] = True

	i = 0
	while( i < len(chainToExtend) - segment_length -1 ):
		i += 1
		nextChain = []
		# Create a chain of length segment_length starting from index i
		nextChain.extend(chainToExtend[i:i+segment_length])
		
		#current movie to find a new chain from
		first_movie = chainToExtend[i]

		#retChain is the best possible Chain starting from Start and ending the last element of nextChain
		retChain = findLongerChain(first_movie,nextChain,alreadyInChain,[])

		if len(retChain) > len(nextChain):

			#We remove the nextChain segment from longerList
			for j in xrange(segment_length):
				alreadyInChain[chainToExtend[i+j]] = False
			chainToExtend = chainToExtend[:i] + chainToExtend[i+segment_length:]

			#Add the chain segment back to longerChain and update AlreadyInChain
			for j in xrange(len(retChain)):
				alreadyInChain[retChain[j]] = True
				chainToExtend = chainToExtend[:i+j] + [retChain[j]] + chainToExtend[i+j:]

	return chainToExtend
	
def extendMax(chains):

	chains.sort(lambda x,y: cmp(len(y),len(x)))
	longChain = copy.deepcopy(chains[0])

	if(len(longChain) > 150):
		longerChain = extendChain(longChain)

		while(len(longerChain) > len(longChain)):
			longChain = copy.deepcopy(longerChain)
			longerChain = extendChain(longChain)

	chains[0] = copy.deepcopy(longChain)

	chains.sort(lambda x,y: cmp(len(y),len(x)))

	longChain = chains[0]
	return longChain




def printMovies(l):
	a = ""
	for x in l:
		a += movieArray[x] + " | "
	return a



# DONT CHANGE/COMMENT OUT ANY OF THE BELOW 4 LINES OF CODE
readMovies()
preProcess()
addEdges()
moviesToStartSearchWith()



print "Number of start movies = " + str(len(moviesToCheck))
print




# UNCOMMENT THE CODE SEGMENT BELOW TO SEARCH THE ENTIRE GRAPH


# print "Computing all chains...."
# print "Printing Intermediate Results in the form <movie> = <longest chain starting at that movie>"
# print "This code will take a long time to run completely...."
# print
# moviesToCheck2 = moviesToCheck
# maxLen = 0
# retVal = 0
# for movie in moviesToCheck2:
# 	b = makeInitialChains(movie)
# 	len_b = len(b)
# 	print movieArray[movie], "-", len_b
# 	if(len_b > maxLen):
# 		maxLen = len_b
# 		retVal = b

# print
# print
# print len(retVal)
# print printMovies(retVal)


# RUN THE CODE AS IT IS TO COMPUTE THE LONGEST CHAIN OF 305 MOVIES



print "Computing Longest Chain...."

moviesToCheck3 = [3661]
maxLen = 0
retVal = 0

for movie in moviesToCheck3:
	b = makeInitialChains(movie)
	len_b = len(b)
	print movieArray[movie], "-", len_b
	if(len_b > maxLen):
		maxLen = len_b
		retVal = b

print
print
print len(retVal)
print printMovies(retVal)


