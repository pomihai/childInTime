import copy
import string

#This class only a bag of arithmetic functions
class arithmetycs:
	def between(self, a,b,m):
		if a >= b:
			return (a >= m and m >= b)
		if b >= a:
			return (b >= m and m >= a)
	def distance(self, a, b): # a,b are integers
		return abs(a-b)

class momentStringParser(arithmetycs):
	def __init__(self, sFormatTimeStamp = 'D/M/YYYY H:MM:SS AM/PM'):
		self.timeConfigError = "Timestamp error"
		self.timeValueError = "Value parsing error"
		self.sFormatTimeStamp = sFormatTimeStamp
		self.__parseTimeStampFormat()

	def timeStampError(self):	raise RuntimeError(self.timeConfigError)
	def timeStampParsingError(self):	raise RuntimeError(self.timeValueError)

	def __testInputErrors(self):
	# this function tests for erroneus input in self.sFormatTimeStamp
	# and populates the a dictionary which gives primary
	# information about the timestamp like how many 'Y's we have.
	# for the default value, the dictionary looks like that:
	#		{'Y': 4, 'H': 1, 'S': 2, 'M': 3, 'D': 1}

		def __testAMPM():
			if self.sFormatTimeStamp.count('AM/PM') > 1:
				raise RuntimeError(self.timeConfigError)

		def __testMyLetter(weSrch, sLetters, arThrNumbers):
			letterCount = sLetters.count(weSrch)
			if not letterCount in arThrNumbers:
				raise RuntimeError(self.timeConfigError)
			if weSrch in 'DYHS' and letterCount > 1:
				# in this case we have letterCount of weSrch
				# next to eachother, like 'DD' or 'SS'
				nextSrch = ''
				for i in range(letterCount): nextSrch += weSrch
				if not nextSrch in sLetters:
					raise RuntimeError(self.timeConfigError)
			if weSrch == 'M':
				# in ths case we have more work to do :(
				# M could stand for minutes or months
				# we break the cases by the letterCount
				# if letterCount == 3 we must have MM and M
				# if letterCount == 4 we must have MM and MM

				if letterCount == 4 and \
					( sLetters.count('MM') != 2 or
						'MMM' in sLetters) :
					raise RuntimeError(self.timeConfigError)

				if letterCount == 3 and \
					( 'MMM' in sLetters or
						not 'MM' in sLetters ):
						raise RuntimeError(self.timeConfigError)
			return letterCount

		__testAMPM()
		# here the AM/PM part does no good
		formatString = self.sFormatTimeStamp.replace('AM/PM', '_____')

		weSrch = 'Y' # one of DMYHS
		iFound = __testMyLetter(weSrch, formatString, [0,2,4])
		dFound = {weSrch: iFound}
		iSumFound = iFound

		for weSrch in "HSD":
			iFound = __testMyLetter(weSrch, formatString, [0,1,2])
			dFound.update({weSrch: iFound})
			iSumFound += iFound

		weSrch = 'M' # one of DMYHS
		iFound = __testMyLetter(weSrch, formatString, [0,1,2,3,4])
		dFound.update({weSrch: iFound})
		iSumFound += iFound

		# a discussion: should we test further ?
		# up to here we tested for only singles
		# now we could test for combos, for example:
		# we could allow DD/YY for some weird usecase
		# but make HH/YY be erroneus.
		# in other words maybe it's a bad idea to allow mixing
		# of time (H:M) with date (D/M/YYYY)
		# for now we allow any combo, but
		# we note that it will be hard to know how to interpret
		# something like 'M' without proper context,
		# and we will throw errors down the pipe

		if iSumFound < 1: __testMyLetter('F', 'ME', [1]) # raise err
		return dFound

	# The input for this function: has both date and time parts
	def __parseTimeStampFormat(self):

	# here we gather info about the given format
	# and store it in a sorted list: self.decodedFormat
	# self.decodedFormat is a list of dictionaries and for the default
	# value: "D/M/YYYY H:MM:SS AM/PM" will have this structure:
	#	self.decodedFormat =
	# 		[
	# 				{'len': 1, 'type': 'date', 		'pos': 0,	'letter': 'D'},
	# 				{'len': 1, 'type': 'delimiter', 'pos': 1,	'letter': '/'},
	# 				{'len': 1, 'type': 'date', 		'pos': 2,	'letter': 'M'},
	# 				{'len': 1, 'type': 'delimiter', 'pos': 3,	'letter': '/'},
	# 				{'len': 4, 'type': 'date', 		'pos': 4,	'letter': 'Y'},
	# 				{'len': 1, 'type': 'white_sp', 	'pos': 8,	'letter': ' '},
	# 				{'len': 1, 'type': 'time', 		'pos': 9,	'letter': 'H'},
	# 				{'len': 1, 'type': 'delimiter', 'pos': 10,	'letter': ':'},
	# 				{'len': 2, 'type': 'time', 		'pos': 11,	'letter': 'M'},
	# 				{'len': 1, 'type': 'delimiter', 'pos': 13,	'letter': ':'},
	# 				{'len': 2, 'type': 'time', 		'pos': 14,	'letter': 'S'},
	# 				{'len': 1, 'type': 'white_sp',	'pos': 16,	'letter': ' '},
	# 				{'len': 2, 'type': 'time', 		'pos': 17,	'letter': 'P'}
	# 		]
	# observation:	we sort the list by the 'pos' key as it will be useful when
	#				we will decode or encode a value by the given format
	#				also we keep in mind that 'pos' could be -1
		letterInfo = self.__testInputErrors()
		DateLetterInfo = self.__getDateFormat(copy.deepcopy(letterInfo))
		TimeLetterInfo = self.__getTimeFormat(copy.deepcopy(letterInfo))
		timeBits = self.__getTimeBitsOrder()
		dateBits = self.__getDateBitsOrder()

		for aBit in timeBits: aBit["len"] = TimeLetterInfo[aBit["letter"]]
		for aBit in dateBits: aBit["len"] = DateLetterInfo[aBit["letter"]]

		numberBits = sorted(timeBits + dateBits,\
									key= lambda dBit: dBit['pos'])
		delimiters = self.__getDelimiters(numberBits)

		self.decodedFormat = sorted(numberBits + delimiters,\
									key= lambda dBit: dBit['pos'])

	def __getDelimiters(self, lNumberBits):
		iThisPos = 0
		iNumberBitsWalker = 0
		bHaveNumBits = True
		lMyBits = []

		# lNumberBits comes ordered by 'pos'
		# and could have 'pos' == -1
		dThisBit = lNumberBits[iNumberBitsWalker]
		while dThisBit['pos'] == -1:
			iNumberBitsWalker += 1
			dThisBit = lNumberBits[iNumberBitsWalker]

		while iThisPos < len(self.sFormatTimeStamp):
			if bHaveNumBits and iThisPos == dThisBit['pos']:
				iThisPos += dThisBit['len']
				try:
					iNumberBitsWalker += 1
					dThisBit = lNumberBits[iNumberBitsWalker]
				except:
					bHaveNumBits = False
			else:
				if self.sFormatTimeStamp[iThisPos] in string.whitespace:
					dBit = {'type': 'white_sp', \
							'letter': self.sFormatTimeStamp[iThisPos],
							'pos': iThisPos}
					iThisPos += 1
					while self.sFormatTimeStamp[iThisPos] == dBit['letter']:
						iThisPos += 1
					dBit['len'] = iThisPos - dBit['pos']
					lMyBits.append(dBit)
				else: # here it must be delimiter :)
					dBit = {'type': 'delimiter', \
							'letter': self.sFormatTimeStamp[iThisPos],
							'pos': iThisPos,
							'len': 1}
					if len(lMyBits) > 0:
						dLastDelim = lMyBits[len(lMyBits) - 1]
						if (dLastDelim['pos'] == iThisPos - 1) and \
							(dLastDelim['type'] == 'delimiter'):
							self.timeStampError()
							return False
					lMyBits.append(dBit)
					iThisPos += 1
		return lMyBits

	def __getDateFormat(self, letterInfo):
		if letterInfo['Y'] == 4:
			self.DateYPos = self.sFormatTimeStamp.find('YYYY')
		else:
			self.DateYPos = self.sFormatTimeStamp.find('YY') # could be -1
		if letterInfo['D'] == 2:
			self.DateDPos = self.sFormatTimeStamp.find('DD')
		else:
			self.DateDPos = self.sFormatTimeStamp.find('D') # could be -1

		# 'M' it's tricky
		if letterInfo['M'] == 0:
			self.DateMPos = -1
			return
		# so we have at least one 'M'
		bGood = False
		self.DateMPos = self.sFormatTimeStamp.find('M')
		if self.DateDPos == -1 and self.DateYPos == -1:
			SPos = self.sFormatTimeStamp.find('S')
			HPos = self.sFormatTimeStamp.find('H')
			# we only have 'M' and we need more context
			if SPos == -1 and HPos == -1 : self.timeStampError()
			if SPos != -1 and HPos != -1 :
				bGood = not self.between(SPos, HPos, self.DateMPos)
				if letterInfo['M'] == 2:
					if self.DateMPos != self.sFormatTimeStamp.find('MM'):
						if bGood : letterInfo.update({'M' : 1})
						else: # we try the other M
							self.DateMPos = \
								self.sFormatTimeStamp.find('M', \
															self.DateMPos + 1)
							bGood = not self.between(SPos, HPos, self.DateMPos)
							if bGood : letterInfo.update({'M' : 1})
				if letterInfo['M'] == 3:
					if self.DateMPos == self.sFormatTimeStamp.find('MM'):
						if bGood : letterInfo.update({'M' : 2})
						else: # we try with the solo
							self.DateMPos = \
								self.sFormatTimeStamp.find('M', \
															self.DateMPos + 2)
							bGood = not self.between(SPos,
													HPos, self.DateMPos)
							if bGood : letterInfo.update({'M' : 1})
					else:
						if bGood : letterInfo.update({'M' : 1})
						else: # we try with the pair
							self.DateMPos = \
								self.sFormatTimeStamp.find('MM', \
															self.DateMPos + 1)
							bGood = not self.between(SPos, HPos, self.DateMPos)
							if bGood : letterInfo.update({'M' : 2})
				if letterInfo['M'] == 4:
					if bGood : letterInfo.update({'M' : 2})
					else: # we try with the other pair
						self.DateMPos = \
							self.sFormatTimeStamp.find('MM', self.DateMPos + 2)
						bGood = not self.between(SPos, HPos, self.DateMPos)
						if bGood : letterInfo.update({'M' : 2})
			else : # here we have only one of H or S
				if SPos == -1:
					EPos = HPos
					sLetterWeHv = 'H'
				if HPos == -1:
					EPos = SPos
					sLetterWeHv = 'S'
				# EPos stands for Enemy Position
				iEnemyRadius = letterInfo[sLetterWeHv] + 1
				iEnemyDistance = self.distance(EPos, self.DateMPos)
				bGood = iEnemyDistance > iEnemyRadius
				if letterInfo['M'] == 2:
					if self.DateMPos != self.sFormatTimeStamp.find('MM'):
						if bGood:  letterInfo.update({'M' : 1})
						else: # we try the other solo
							self.DateMPos = \
								self.sFormatTimeStamp.find('M', \
															self.DateMPos + 1)
							iEnemyDistance = self.distance(EPos, self.DateMPos)
							bGood = iEnemyDistance > iEnemyRadius
							if bGood : letterInfo.update({'M' : 1})
				if letterInfo['M'] == 3:
					if self.DateMPos == self.sFormatTimeStamp.find('MM'):
						if bGood :  letterInfo.update({'M' : 2})
						else: # we try the solo
							self.DateMPos = \
								self.sFormatTimeStamp.find('M', \
															self.DateMPos + 2)
							iEnemyDistance = self.distance(EPos, self.DateMPos)
							bGood = iEnemyDistance > iEnemyRadius
							if bGood : letterInfo.update({'M' : 1})
					else: # we found first the solo
						if bGood :  letterInfo.update({'M' : 1})
						else: # we try the pair
							self.DateMPos = \
								self.sFormatTimeStamp.find('MM', \
															self.DateMPos + 1)
							iEnemyDistance = self.distance(EPos, self.DateMPos)
							bGood = iEnemyDistance > iEnemyRadius
							if bGood : letterInfo.update({'M' : 2})
				if letterInfo['M'] == 4:
					if bGood :  letterInfo.update({'M' : 2})
					else: # we try the other pair
						self.DateMPos = \
							self.sFormatTimeStamp.find('MM', self.DateMPos + 2)
						iEnemyDistance = self.distance(EPos, self.DateMPos)
						bGood = iEnemyDistance > iEnemyRadius
						if bGood : letterInfo.update({'M' : 2})
		else: # here we have at least one of D or Y
			if (self.DateDPos != -1 and self.DateYPos == -1) or \
				(self.DateDPos == -1 and self.DateYPos != -1):
				if self.DateDPos != -1 :
					FPos = self.DateDPos
					sLetterWeHv = 'D'
				else:
					FPos = self.DateYPos
					sLetterWeHv = 'Y'
				# FPos stands for Friend Position
				iFriendRadius = letterInfo[sLetterWeHv] + 1
				iFriendDistance = self.distance(FPos, self.DateMPos)
				bGood = iFriendDistance <= iFriendRadius
				if letterInfo['M'] == 1:
					if not bGood: # we lost the M to the other side
						letterInfo.update({'M': 0})
						self.DateMPos = -1
						bGood = True # and we're OK with it
				if letterInfo['M'] == 2:
					if self.sFormatTimeStamp.find('MM') == self.DateMPos:
						if not bGood: # we lost the M to the other side
							letterInfo.update({'M': 0})
							self.DateMPos = -1
							bGood = True # and we're OK with it
					else: # we have splitted M's
						if bGood: letterInfo.update({'M': 1})
						else: # we try the other M
							self.DateMPos = \
								self.sFormatTimeStamp.find('M', \
															self.DateMPos + 1)
							iFriendDistance = self.distance(FPos, self.DateMPos)
							bGood = iFriendDistance <= iFriendRadius
							if bGood: letterInfo.update({'M': 1})
				if letterInfo['M'] == 3:
					if self.sFormatTimeStamp.find('MM') == self.DateMPos:
						if bGood : letterInfo.update({'M': 2})
						else: # we try with the solo
							self.DateMPos = \
								self.sFormatTimeStamp.find('M', \
															self.DateMPos + 2)
							iFriendDistance = self.distance(FPos, self.DateMPos)
							bGood = iFriendDistance <= iFriendRadius
							if bGood: letterInfo.update({'M': 1})
					else: # we got the solo first
						if bGood : letterInfo.update({'M': 1})
						else: # we try the pair
							self.DateMPos = \
								self.sFormatTimeStamp.find('MM', \
															self.DateMPos + 1)
							iFriendDistance = self.distance(FPos, self.DateMPos)
							bGood = iFriendDistance <= iFriendRadius
							if bGood: letterInfo.update({'M': 2})
				if letterInfo['M'] == 4:
					if bGood : letterInfo.update({'M': 2})
					else: # we try the other pair
						self.DateMPos = \
							self.sFormatTimeStamp.find('MM', self.DateMPos + 2)
						iFriendDistance = self.distance(FPos, self.DateMPos)
						bGood = iFriendDistance <= iFriendRadius
						if bGood: letterInfo.update({'M': 2})
			else: # here we have both D and Y
				# we had a usecase where M(onth) was actually between D(ays) and Y(ear)
				bGood = self.between(self.DateDPos, self.DateYPos, \
							self.DateMPos) or \
					self.between(self.DateMPos, self.DateYPos, \
							self.DateDPos) or \
					self.between(self.DateMPos, self.DateDPos, \
							self.DateYPos)
				if letterInfo['M'] == 1:
					if not bGood: # we lost the M to the other side
						letterInfo.update({'M': 0})
						self.DateMPos = -1
						bGood = True # and we're OK with it
				if letterInfo['M'] == 2:
					if self.sFormatTimeStamp.find('MM') == self.DateMPos:
						if not bGood: # we lost the MM to the other side
							letterInfo.update({'M': 0})
							self.DateMPos = -1
							bGood = True # and we're OK with it
					else: # we have split M's
						if bGood : letterInfo.update({'M': 1})
						else: # other M:
							self.DateMPos = \
								self.sFormatTimeStamp.find('M', \
															self.DateMPos + 1)
							bGood = \
								self.between(self.DateDPos, \
												self.DateYPos, self.DateMPos)
							if bGood: letterInfo.update({'M': 1})
				if letterInfo['M'] == 3:
					if self.sFormatTimeStamp.find('MM') == self.DateMPos:
						# this would have been correct
						# if we were in __getTimeFormat function
						if bGood: letterInfo.update({'M': 2})
						else: # we try the solo M:
							self.DateMPos = \
								self.sFormatTimeStamp.find('M', \
															self.DateMPos + 2)
							bGood = \
								self.between(self.DateDPos, \
												self.DateYPos, self.DateMPos)
							if bGood : letterInfo.update({'M' : 1})
					else: # we got the solo first
						if bGood : letterInfo.update({'M':1})
						else: # we try with the pair
							self.DateMPos = \
								self.sFormatTimeStamp.find('MM', \
															self.DateMPos + 1)
							bGood = \
								self.between(self.DateDPos, \
											self.DateYPos, self.DateMPos)
							if bGood : letterInfo.update({'M': 2})
				if letterInfo['M'] == 4:
					if bGood : letterInfo.update({'M': 2})
					else: #try the other pair
						self.DateMPos = \
							self.sFormatTimeStamp.find('MM', self.DateMPos + 2)
						bGood = self.between(self.DateDPos, \
												self.DateYPos, self.DateMPos)
						if bGood : letterInfo.update({'M': 2})
		if not bGood: self.timeStampError()
		return letterInfo

	def __getTimeFormat(self, letterInfo):
		sFakeAM = 'PP'
		self.sFormatTimeStamp = \
			self.sFormatTimeStamp.replace('AM/PM', sFakeAM)
		self.TimeAMPos = self.sFormatTimeStamp.find(sFakeAM) # could be -1
		if self.TimeAMPos >= 0:
			letterInfo['P'] = 2
		else:
			letterInfo['P'] = 0
		if letterInfo['H'] == 2:
			self.TimeHPos = self.sFormatTimeStamp.find('HH')
		else:
			self.TimeHPos = self.sFormatTimeStamp.find('H') # could be -1
		if letterInfo['S'] == 2:
			self.TimeSPos = self.sFormatTimeStamp.find('SS')
		else:
			self.TimeSPos = self.sFormatTimeStamp.find('S') # could be -1
		if letterInfo['M'] == 0 :
			self.TimeMPos = -1
			return
		# so we have at least one 'M'
		# but we could be missing 'S''s and/or 'H''s
		bGood = False
		self.TimeMPos = self.sFormatTimeStamp.find('M')
		if (self.TimeHPos == -1 and self.TimeSPos == -1):
			DPos = self.sFormatTimeStamp.find('D')
			YPos = self.sFormatTimeStamp.find('Y')
			 # we only have 'M' and we need more context
			if DPos == -1 and YPos == -1 : self.timeStampError()
			if (DPos >= 0 and YPos >= 0) :
				if letterInfo['M'] == 1:
					bGood = not self.between(DPos, YPos, self.TimeMPos)
				if letterInfo['M'] == 2:
					if self.sFormatTimeStamp.find('MM') == self.TimeMPos:
						bGood = not self.between(DPos, YPos, self.TimeMPos)
					else: # we have split M's
						bGood = not self.between(DPos, YPos, self.TimeMPos)
						if not bGood:# we have another chance with the other M
							self.TimeMPos = \
							self.sFormatTimeStamp.find('M', self.TimeMPos + 1)
							bGood = not self.between(DPos, YPos, self.TimeMPos)
						if bGood : letterInfo.update({'M' : 1})
				if letterInfo['M'] == 3:
					if self.sFormatTimeStamp.find('MM') == self.TimeMPos:
						bGood = not self.between(DPos, YPos, self.TimeMPos)
						if bGood : letterInfo.update({'M' : 2})
						else: # we have another chance with the solo
							self.TimeMPos = \
							self.sFormatTimeStamp.find('M', self.TimeMPos + 2)
							bGood = not self.between(DPos, YPos, self.TimeMPos)
							if bGood : letterInfo.update({'M' : 1})
					else: # we first found the solo
						bGood = not self.between(DPos, YPos, self.TimeMPos)
						if bGood : letterInfo.update({'M' : 1})
						else: # we have another chance with the pair
							self.TimeMPos = \
							self.sFormatTimeStamp.find('MM', self.TimeMPos + 1)
							bGood = not self.between(DPos, YPos, self.TimeMPos)
							if bGood : letterInfo.update({'M' : 2})
				if letterInfo['M'] == 4:
					bGood = not self.between(DPos, YPos, self.TimeMPos)
					if not bGood:
						# we have another chance with the other pair
						self.TimeMPos = \
						self.sFormatTimeStamp.find('MM', self.TimeMPos + 2)
						bGood = not self.between(DPos, YPos, self.TimeMPos)
					if bGood : letterInfo.update({'M' : 2})
			# so this is if we have 'D' and 'Y'
			# if one is missing, we have to build a new concept of 'near'
			# and find out if the M's are closer to the D (or Y) which is bad
			else:
				if DPos == -1 :
					EPos = YPos
					sLetterWeHv='Y'
				if YPos == -1 :
					EPos = DPos
					sLetterWeHv='D'
				# EPos stands for Enemy Position
				iEnemyRadius = letterInfo[sLetterWeHv] + 1
				iEnemyDistance = self.distance(EPos, self.TimeMPos)
				if letterInfo['M'] == 1:
					bGood = iEnemyDistance > iEnemyRadius
				if letterInfo['M'] == 2:
					if self.TimeMPos == self.sFormatTimeStamp.find('MM'):
						bGood = iEnemyDistance > iEnemyRadius
					else: # we have splitted M's
						bGood = iEnemyDistance > iEnemyRadius
						if not bGood: # we have another chance with other solo
							self.TimeMPos = \
							self.sFormatTimeStamp.find('M', self.TimeMPos +1)
							iEnemyDistance = self.distance(EPos, self.TimeMPos)
							bGood = iEnemyDistance > iEnemyRadius
						if bGood: letterInfo.update({'M' : 1})
				if letterInfo['M'] == 3:
					if self.TimeMPos == self.sFormatTimeStamp.find('MM'):
						bGood = iEnemyDistance > iEnemyRadius
						if bGood: letterInfo.update({'M' : 2})
						else: # we have another chance with the solo
							self.TimeMPos = \
							self.sFormatTimeStamp.find('M', self.TimeMPos + 2)
							iEnemyDistance = self.distance(EPos, self.TimeMPos)
							bGood = iEnemyDistance > iEnemyRadius
							if bGood: letterInfo.update({'M' : 1})
					else: # first we found the solo
						bGood = iEnemyDistance > iEnemyRadius
						if bGood: letterInfo.update({'M' : 1})
						else: # we have another chance with the pair
							self.TimeMPos = \
							self.sFormatTimeStamp.find('MM', self.TimeMPos + 1)
							iEnemyDistance = self.distance(EPos, self.TimeMPos)
							bGood = iEnemyDistance > iEnemyRadius
							if bGood: letterInfo.update({'M' : 2})
				if letterInfo['M'] == 4:
					bGood = iEnemyDistance > iEnemyRadius
					if not bGood: # we have another chance with the other pair
						self.TimeMPos = \
							self.sFormatTimeStamp.find('MM', self.TimeMPos + 2)
						iEnemyDistance = self.distance(EPos, self.TimeMPos)
						bGood = iEnemyDistance > iEnemyRadius
					if bGood: letterInfo.update({'M' : 2})
		else:
		# here de don't need to test all the cases, because we could
		# be just missing the M's. but if we have two M fields:
		# letterInfo['M'] in [2(splitted),3,4]
		# one field should be 'near' the S or H
		# almost same reasoning when we'll test with both S and H present
			if (self.TimeHPos != -1 and self.TimeSPos == -1) or \
				(self.TimeHPos == -1 and self.TimeSPos != -1) :
				if self.TimeHPos != -1 :
					FPos = self.TimeHPos
					sLetterWeHv = 'H'
				else:
					FPos = self.TimeSPos
					sLetterWeHv = 'S'
				# FPos stands for Friend Position
				iFriendRadius = letterInfo[sLetterWeHv] + 1
				iFriendDistance = self.distance(FPos, self.TimeMPos)
				if letterInfo['M'] == 1:
					bGood = iFriendDistance <= iFriendRadius
					if not bGood:
						letterInfo.update({'M' : 1})
						self.TimeMPos = -1 # M is lost to the other side
						bGood = True   # but that's OK with us
				if letterInfo['M'] == 2:
					bGood = iFriendDistance <= iFriendRadius
					if self.TimeMPos == self.sFormatTimeStamp.find('MM'):
						if not bGood:
							letterInfo.update({'M' : 1})
							self.TimeMPos = -1 # MM is lost to the other side
							bGood = True   # but that's OK with us
					else: # we have splitted M's
						if bGood: letterInfo.update({'M' : 1})
						else: #we try the other M
							self.TimeMPos = \
								self.sFormatTimeStamp.find('M', \
															self.TimeMPos + 1)
							iFriendDistance = self.distance(FPos, self.TimeMPos)
							bGood = iFriendDistance <= iFriendRadius
							if bGood: letterInfo.update({'M' : 1})
				if letterInfo['M'] == 3:
					bGood = iFriendDistance <= iFriendRadius
					if self.TimeMPos == self.sFormatTimeStamp.find('MM'):
						if bGood: letterInfo.update({'M' : 2})
						else: # maybe the solo
							self.TimeMPos = \
								self.sFormatTimeStamp.find('M', \
															self.TimeMPos + 2)
							iFriendDistance = self.distance(FPos, self.TimeMPos)
							bGood = iFriendDistance <= iFriendRadius
							if bGood: letterInfo.update({'M' : 1})
					else :
						if bGood: letterInfo.update({'M' : 1})
						else: # maybe the pair
							self.TimeMPos = \
								self.sFormatTimeStamp.find('MM', \
															self.TimeMPos + 1)
							iFriendDistance = self.distance(FPos, self.TimeMPos)
							bGood = iFriendDistance <= iFriendRadius
							if bGood: letterInfo.update({'M' : 2})
				if letterInfo['M'] == 4:
					bGood = iFriendDistance <= iFriendRadius
					if bGood: letterInfo.update({'M' : 2})
					else: # maybe the other pair
						self.TimeMPos = \
							self.sFormatTimeStamp.find('MM', self.TimeMPos + 2)
						iFriendDistance = self.distance(FPos, self.TimeMPos)
						bGood = iFriendDistance <= iFriendRadius
						if bGood: letterInfo.update({'M' : 2})
			else:
			# here we have both S and H. we test for "our" M
			# to be between the S and H it could be S:M:H or H:M:S,
			# as long as M stays in the middle
				bGood = self.between(self.TimeHPos, self.TimeSPos, \
										self.TimeMPos)
				if letterInfo['M'] == 1:
					if not bGood:
						letterInfo.update({'M' : 0})
						self.TimeMPos = -1 # M is lost to the other side
						bGood = True   # but that's OK with us
				if letterInfo['M'] == 2:
					if self.TimeMPos == self.sFormatTimeStamp.find('MM'):
						if not bGood:
							letterInfo.update({'M' : 1})
							self.TimeMPos = -1 # MM is lost to the other side
							bGood = True   # but that's OK with us
					else: # we have splitted M's
						if bGood: letterInfo.update({'M' : 1})
						else: # we try the other M
							self.TimeMPos = \
								self.sFormatTimeStamp.find('M', \
															self.TimeMPos + 1)
							bGood = \
								self.between(self.TimeHPos, \
											self.TimeSPos, self.TimeMPos)
							if bGood: letterInfo.update({'M' : 1})
				if letterInfo['M'] == 3:
					if self.TimeMPos == self.sFormatTimeStamp.find('MM'):
						if bGood: letterInfo.update({'M' : 2})
						else: # we try the solo
							self.TimeMPos = \
								self.sFormatTimeStamp.find('M', \
															self.TimeMPos + 2)
							bGood = \
								self.between(self.TimeHPos, \
											self.TimeSPos, self.TimeMPos)
							if bGood: letterInfo.update({'M' : 1})
					else:
						if bGood: letterInfo.update({'M' : 1})
						else: # we try the pair
							self.TimeMPos = \
								self.sFormatTimeStamp.find('MM', \
															self.TimeMPos + 1)
							bGood = \
								self.between(self.TimeHPos, \
												self.TimeSPos, self.TimeMPos)
							if bGood: letterInfo.update({'M' : 2})
				if letterInfo['M'] == 4:
					if bGood: letterInfo.update({'M' : 2})
					else: # we try the other pair
						self.TimeMPos = \
							self.sFormatTimeStamp.find('MM', self.TimeMPos + 2)
						bGood = \
							self.between(self.TimeHPos, \
											self.TimeSPos, self.TimeMPos)
						if bGood: letterInfo.update({'M' : 2})
		if not bGood: self.timeStampError()
		return letterInfo

	def __getTimeBitsOrder(self):
		def letterByPos(iWhatPos):
			sWhatLetter = ''
			if iWhatPos == self.TimeHPos :
				sWhatLetter = 'H'
			else:
				if iWhatPos == self.TimeMPos :
					sWhatLetter = 'M'
				else:
					if iWhatPos == self.TimeSPos :
						sWhatLetter = 'S'
					else:
						sWhatLetter = 'P'
			return sWhatLetter

		# if we have nothing to seek, why bother
		if max(self.TimeHPos, self.TimeMPos, self.TimeSPos) == -1:
			self.timeStampParsingError()

		# Here we seek the order of the fields: Hour, Minute, Second
		# or any other order
		if self.TimeHPos == -1 or self.TimeMPos == -1 or self.TimeSPos == -1 :
			# we have one or two fields
			if self.TimeHPos >= 0:
				if self.TimeMPos >= 0:
					# here we have self.TimeSPos == -1
					if self.TimeAMPos == -1:
						sFourthLetter = 'P'
						sThirdLetter = 'S'
						iThirdPos = -1
						iFirstPos = min(self.TimeHPos, self.TimeMPos)
						sFirstLetter = letterByPos(iFirstPos)
						if sFirstLetter == 'H':
							sSecondLetter = 'M'
							iSecondPos = self.TimeMPos
						else:
							sSecondLetter = 'H'
							iSecondPos = self.TimeHPos
					else:
						sFourthLetter = 'S'
						iFirstPos = min(self.TimeHPos, self.TimeMPos, \
										self.TimeAMPos)
						sFirstLetter = letterByPos(iFirstPos)
						if sFirstLetter == 'H':
							iSecondPos = min(self.TimeMPos, self.TimeAMPos)
							sSecondLetter = letterByPos(iSecondPos)
							if sSecondLetter == 'M' :
								sThirdLetter = 'P'
								iThirdPos = self.TimeAMPos
							else:
								sThirdLetter = 'M'
								iThirdPos = self.TimeMPos
						else:
							if sFirstLetter == 'M':
								iSecondPos = min(self.TimeHPos, self.TimeAMPos)
								sSecondLetter = letterByPos(iSecondPos)
								if sSecondLetter == 'H':
									sThirdLetter = 'P'
									iThirdPos = self.TimeAMPos
								else:
									sThirdLetter = 'H'
									iThirdPos = self.TimeHPos
							else: # here 'P' is first
								iSecondPos = min(self.TimeHPos, self.TimeMPos)
								sSecondLetter = letterByPos(iSecondPos)
								if sSecondLetter == 'H':
									sThirdLetter = 'M'
									iThirdPos = self.TimeMPos
								else:
									sThirdLetter = 'H'
									iThirdPos = self.TimeHPos
				else:
					# here we have self.TimeMPos == -1
					sFourthLetter = 'M'
					if self.TimeAMPos == -1 :
						sThirdLetter = 'P'
						iThirdPos = -1
						if self.TimeSPos >= 0:
							if self.TimeHPos >= 0:
								iFirstPos = min(self.TimeSPos, self.TimeHPos)
								sFirstLetter = letterByPos(iFirstPos)
								if sFirstLetter == 'S':
									sSecondLetter = 'H'
									iSecondPos = self.TimeHPos
								else:
									sSecondLetter = 'S'
									iSecondPos = self.TimeSPos
							else: # here we have only self.TimeSPos
								sSecondLetter = 'H'
								iSecondPos = -1
								sFirstLetter = 'S'
								iFirstPos = self.TimeSPos
						else: # here we have only self.TimeHPos
							sSecondLetter = 'S'
							iSecondPos = -1
							sFirstLetter = 'H'
							iFirstPos = self.TimeHPos
					else: # here we have AM/PM or 'P'
						if self.TimeSPos >= 0 :
							iFirstPos = min(self.TimeHPos, self.TimeSPos, \
											self.TimeAMPos)
							sFirstLetter = letterByPos(iFirstPos)
							if sFirstLetter == 'H' :
								iSecondPos = min(self.TimeSPos, self.TimeAMPos)
								sSecondLetter = letterByPos(iSecondPos)
								if sSecondLetter == 'P' :
									sThirdLetter = 'S'
									iThirdPos = self.TimeSPos
								else :
									sThirdLetter = 'P'
									iThirdPos = self.TimeAMPos
							else:
								if sFirstLetter == 'S':
									iSecondPos = min(self.TimeAMPos, \
													self.TimeHPos)
									sSecondLetter = letterByPos(iSecondPos)
									if sSecondLetter == 'P' :
										sThirdLetter = 'H'
										iThirdPos = self.TimeHPos
									else :
										sThirdLetter = 'P'
										iThirdPos = self.TimeAMPos
								else: # it must be P
									iSecondPos = min(self.TimeSPos, \
													self.TimeHPos)
									sSecondLetter = letterByPos(iSecondPos)
									if sSecondLetter == 'S' :
										sThirdLetter = 'H'
										iThirdPos = self.TimeHPos
									else :
										sThirdLetter = 'S'
										iThirdPos = self.TimeSPos
						else:	# here we only have self.TimeHPos
							sThirdLetter = 'S'
							iThirdPos = -1
							iSecondPos = min(self.TimeAMPos, self.TimeHPos)
							sSecondLetter = letterByPos(iSecondPos)
							if sSecondLetter == 'P' :
								sThirdLetter = 'H'
								iThirdPos = self.TimeHPos
							else :
								sThirdLetter = 'P'
								iThirdPos = self.TimeAMPos
			else:
				# here we have self.TimeHPos == -1
				# and we __really__ don't care about AM/PM or 'P'
				sThirdLetter = 'H'
				sFourthLetter = 'P'
				iThirdPos = -1
				if self.TimeMPos >= 0:
					if self.TimeSPos >=0:
						iFirstPos = min(self.TimeMPos, self.TimeSPos)
						sFirstLetter = letterByPos(iFirstPos)
						if sFirstLetter == 'M':
							sSecondLetter = 'S'
							iSecondPos = self.TimeSPos
						else:
							sSecondLetter = 'M'
							iSecondPos = self.TimeMPos
					else:
						# here we have	self.TimeHPos == -1
						#				and
						#				self.TimeSPos == -1
						iFirstPos = self.TimeMPos
						sFirstLetter = 'M'
						sSecondLetter = 'S'
						iSecondPos = -1
				else:
					# here we have self.TimeHPos == -1 and self.TimeMPos == -1
						iFirstPos = self.TimeSPos
						sFirstLetter = 'S'
						sSecondLetter = 'M'
						iSecondPos = -1
			dFirstBit	= {"pos":iFirstPos,		"letter": sFirstLetter}
			dSecondBit	= {"pos":iSecondPos,	"letter": sSecondLetter}
			dThirdBit	= {"pos":iThirdPos,		"letter": sThirdLetter}
			dFourthBit	= {"pos":-1,			"letter": sFourthLetter}
		else:
			# we have all three fields: HMS
			if self.TimeAMPos == -1 :
				sFourthLetter = 'P'
				iFourthPos = -1
				# first "bit"
				iFirstPos = min(self.TimeHPos, self.TimeMPos, self.TimeSPos)
				sFirstLetter = letterByPos(iFirstPos)
				dFirstBit = {"pos":iFirstPos, "letter":sFirstLetter}
				# here second "bit"
				if sFirstLetter == 'H' :
					iSecondPos = min(self.TimeMPos, self.TimeSPos)
					sSecondLetter = letterByPos(iSecondPos)
				if sFirstLetter == 'M' :
					iSecondPos = min(self.TimeHPos, self.TimeSPos)
					sSecondLetter = letterByPos(iSecondPos)
				if sFirstLetter == 'S' :
					iSecondPos = min(self.TimeHPos, self.TimeMPos)
					sSecondLetter = letterByPos(iSecondPos)

				dSecondBit = {"pos":iSecondPos, "letter":sSecondLetter}
				# here third "bit"
				if "".join(sorted(sFirstLetter + sSecondLetter)) == "HM":
					sThirdLetter = 'S'
					iThirdPos = self.TimeSPos
				if "".join(sorted(sFirstLetter + sSecondLetter)) == "HS":
					sThirdLetter = 'M'
					iThirdPos = self.TimeMPos
				if "".join(sorted(sFirstLetter + sSecondLetter)) == "MS":
					sThirdLetter = 'H'
					iThirdPos = self.TimeHPos
				dThirdBit = {"pos": iThirdPos, "letter": sThirdLetter}
				dFourthBit = {"pos": -1, "letter": sFourthLetter}
			else:
				# first "bit"
				iFirstPos = min(self.TimeHPos, self.TimeMPos, self.TimeSPos, \
								self.TimeAMPos)
				sFirstLetter = letterByPos(iFirstPos)
				dFirstBit = {"pos":iFirstPos, "letter":sFirstLetter}
				# here second "bit"
				if sFirstLetter == 'H' :
					iSecondPos = min(self.TimeMPos, self.TimeSPos,
									self.TimeAMPos)
					sSecondLetter = letterByPos(iSecondPos)
				if sFirstLetter == 'M' :
					iSecondPos = min(self.TimeHPos, self.TimeSPos,
									self.TimeAMPos)
					sSecondLetter = letterByPos(iSecondPos)
				if sFirstLetter == 'S' :
					iSecondPos = min(self.TimeHPos, self.TimeMPos,
									self.TimeAMPos)
					sSecondLetter = letterByPos(iSecondPos)
				if sFirstLetter == 'P' :
					iSecondPos = min(self.TimeHPos, self.TimeMPos,\
									self.TimeSPos)
					sSecondLetter = letterByPos(iSecondPos)

				dSecondBit = {"pos":iSecondPos, "letter":sSecondLetter}
				# here third "bit" 'HMPS'
				if "".join(sorted(sFirstLetter + sSecondLetter)) == "HM":
					iThirdPos = min(self.TimeAMPos, self.TimeSPos)
					sThirdLetter = letterByPos(iThirdPos)
				if "".join(sorted(sFirstLetter + sSecondLetter)) == "HP":
					iThirdPos = min(self.TimeMPos, self.TimeSPos)
					sThirdLetter = letterByPos(iThirdPos)
				if "".join(sorted(sFirstLetter + sSecondLetter)) == "HS":
					iThirdPos = min(self.TimeAMPos, self.TimeMPos)
					sThirdLetter = letterByPos(iThirdPos)
				if "".join(sorted(sFirstLetter + sSecondLetter)) == "MP":
					iThirdPos = min(self.TimeHPos, self.TimeSPos)
					sThirdLetter = letterByPos(iThirdPos)
				if "".join(sorted(sFirstLetter + sSecondLetter)) == "MS":
					iThirdPos = min(self.TimeAMPos, self.TimeHPos)
					sThirdLetter = letterByPos(iThirdPos)
				if "".join(sorted(sFirstLetter + sSecondLetter)) == "PS":
					iThirdPos = min(self.TimeHPos, self.TimeMPos)
					sThirdLetter = letterByPos(iThirdPos)
				dThirdBit = {"pos": iThirdPos, "letter": sThirdLetter}
				# 'HMPS' here fourth "bit"
				if "".join(sorted(sFirstLetter + sSecondLetter + sThirdLetter))\
					== "HMP":
					sFourthLetter = 'S'
					iFourthPos = self.TimeSPos
				if "".join(sorted(sFirstLetter + sSecondLetter + sThirdLetter))\
					== "HMS":
					sFourthLetter = 'P'
					iFourthPos = self.TimeAMPos
				if "".join(sorted(sFirstLetter + sSecondLetter + sThirdLetter))\
					== "HPS":
					sFourthLetter = 'M'
					iFourthPos = self.TimeMPos
				if "".join(sorted(sFirstLetter + sSecondLetter + sThirdLetter))\
					== "MPS":
					sFourthLetter = 'H'
					iFourthPos = self.TimeHPos
				dFourthBit = {"pos": iFourthPos, "letter": sFourthLetter}
		dFirstBit["type"]	= "time"
		dSecondBit["type"]	= "time"
		dThirdBit["type"]	= "time"
		dFourthBit["type"]	= "time"
		return [dFirstBit, dSecondBit, dThirdBit, dFourthBit]

	def __getDateBitsOrder(self):
		def letterByPos(iWhatPos):
			sWhatLetter = ''
			if iWhatPos == self.DateYPos :
				sWhatLetter = 'Y'
			else:
				if iWhatPos == self.DateMPos :
					sWhatLetter = 'M'
				else:
					sWhatLetter = 'D'
			return sWhatLetter

		# if we have nothing to seek, why bother
		if max(self.DateYPos, self.DateMPos, self.DateDPos) == -1:
			self.timeStampParsingError()
		# Here we seek the order of the fields: Year, Month, Day
		if self.DateYPos == -1 or self.DateMPos == -1 or self.DateDPos == -1 :
			# we have one or two fields
			if self.DateYPos >= 0:
				if self.DateMPos >= 0:
					# here we have self.DateDPos == -1
					sThirdLetter = 'D'
					iFirstPos = min(self.DateYPos, self.DateMPos)
					sFirstLetter = letterByPos(iFirstPos)
					if sFirstLetter == 'Y':
						sSecondLetter = 'M'
						iSecondPos = self.DateMPos
					else:
						sSecondLetter = 'Y'
						iSecondPos = self.DateYPos
				else:
					# here we have self.DateMPos == -1
					sThirdLetter = 'M'
					if self.DateDPos >= 0:
						iFirstPos = min(self.DateYPos, self.DateDPos)
						sFirstLetter = letterByPos(iFirstPos)
						if sFirstLetter == 'Y':
							sSecondLetter = 'D'
							iSecondPos = self.DateDPos
						else:
							sSecondLetter = 'Y'
							iSecondPos = self.DateYPos
					else:
						# here we have both
						# 				self.DateMPos == -1
						#				and
						#				self.DateDPos == -1
						iFirstPos = self.DateYPos
						sFirstLetter = 'Y'
						sSecondLetter = 'D'
						iSecondPos = -1
			else:
				# here we have self.DateYPos == -1
				sThirdLetter = 'Y'
				if self.DateMPos >= 0:
					if self.DateDPos >=0:
						iFirstPos = min(self.DateMPos, self.DateDPos)
						sFirstLetter = letterByPos(iFirstPos)
						if sFirstLetter == 'M':
							sSecondLetter = 'D'
							iSecondPos = self.DateDPos
						else:
							sSecondLetter = 'M'
							iSecondPos = self.DateMPos
					else:
						# here we have both
						#				self.DateYPos == -1
						# 				and
						# 				self.DateDPos == -1
						iFirstPos = self.DateMPos
						sFirstLetter = 'M'
						sSecondLetter = 'D'
						iSecondPos = -1
				else:
					# here we have self.DateYPos == -1 and self.DateMPos == -1
					iFirstPos = self.DateDPos
					sFirstLetter = 'D'
					sSecondLetter = 'M'
					iSecondPos = -1
			dFirstBit	= {"pos":iFirstPos,		"letter": sFirstLetter}
			dSecondBit	= {"pos":iSecondPos,	"letter": sSecondLetter}
			dThirdBit	= {"pos": -1,			"letter": sThirdLetter}
		else :
			# Here if we have all three fields:
			# Here first "bit"
			iFirstPos = min(self.DateYPos, self.DateMPos, self.DateDPos)
			sFirstLetter = letterByPos(iFirstPos)
			dFirstBit = {"pos":iFirstPos, "letter":sFirstLetter}
			# here second "bit"
			if sFirstLetter == 'Y' :
				iSecondPos = min(self.DateMPos, self.DateDPos)
				sSecondLetter = letterByPos(iSecondPos)
			if sFirstLetter == 'M' :
				iSecondPos = min(self.DateYPos, self.DateDPos)
				sSecondLetter = letterByPos(iSecondPos)
			if sFirstLetter == 'D' :
				iSecondPos = min(self.DateYPos, self.DateMPos)
				sSecondLetter = letterByPos(iSecondPos)
			dSecondBit = {"pos":iSecondPos, "letter":sSecondLetter}
			# 'DMY' here third "bit"
			if "".join(sorted(sFirstLetter + sSecondLetter)) == "MY":
				sThirdLetter = 'D'
				iThirdPos = self.DateDPos
			if "".join(sorted(sFirstLetter + sSecondLetter)) == "DY":
				sThirdLetter = 'M'
				iThirdPos = self.DateMPos
			if "".join(sorted(sFirstLetter + sSecondLetter)) == "DM":
				sThirdLetter = 'Y'
				iThirdPos = self.DateYPos
			dThirdBit = {"pos": iThirdPos, "letter": sThirdLetter}
		dFirstBit["type"] = "date"
		dSecondBit["type"] = "date"
		dThirdBit["type"] = "date"
		someList = [dFirstBit, dSecondBit, dThirdBit]
		return someList

	def __str__(self):
		def printABit(aBit):
			sAline = str(aBit)
			sAline += '\n\r'
			return sAline
		sMyString = ''
		for aBit in self.decodedFormat:
			sMyString += printABit(aBit)
		return sMyString

class dateStringParser(momentStringParser):
	def __init__(self, sFormatTimeStamp = 'D/M/YYYY'):
			self.timeConfigError = "Timestamp error"
			self.timeValueError = "Value parsing error"
			self.sFormatTimeStamp = sFormatTimeStamp
			self.__parseTimeStampFormat()

	def __parseTimeStampFormat(self):
		letterInfo = self._momentStringParser__testInputErrors()
		DateLetterInfo = self._momentStringParser__getDateFormat(
													copy.deepcopy(letterInfo))
		dateBits = self._momentStringParser__getDateBitsOrder()
		for aBit in dateBits: aBit["len"] = DateLetterInfo[aBit["letter"]]
		numberBits = sorted(dateBits, key= lambda dBit: dBit['pos'])
		delimiters = self._momentStringParser__getDelimiters(numberBits)
		self.decodedFormat = sorted(numberBits + delimiters,\
									key= lambda dBit: dBit['pos'])

class timeStringParser(momentStringParser):
	def __init__(self, sFormatTimeStamp = 'H:MM:SS AM/PM'):
			self.timeConfigError = "Timestamp error"
			self.timeValueError = "Value parsing error"
			self.sFormatTimeStamp = sFormatTimeStamp
			self.__parseTimeStampFormat()
	def __parseTimeStampFormat(self):
		letterInfo = self._momentStringParser__testInputErrors()
		TimeLetterInfo = self._momentStringParser__getTimeFormat(
											copy.deepcopy(letterInfo))
		timeBits = self._momentStringParser__getTimeBitsOrder()
		for aBit in timeBits: aBit["len"] = TimeLetterInfo[aBit["letter"]]
		numberBits = sorted(timeBits, key= lambda dBit: dBit['pos'])
		delimiters = self._momentStringParser__getDelimiters(numberBits)
		self.decodedFormat = sorted(numberBits + delimiters,\
									key= lambda dBit: dBit['pos'])

class somewhereInTime:
	# this class works with the strings that come in the format given
	# to the momentStringParser class,
	# or its derivates 	timeStringParser and dateStringParser
	# and yes, since the name datetime was taken, it just makes sense
	# to reference a classic movie since we're writing in Python; look it up
	def __init__(self, sFormatTimeStamp, type = 'moment'):
		if type == 'moment':
			self.decodedFormat = \
				momentStringParser(sFormatTimeStamp).decodedFormat
		else:
			if type == 'date':
				self.decodedFormat = \
					dateStringParser(sFormatTimeStamp).decodedFormat
			else:
				if type == 'time':
					self.decodedFormat = \
						timeStringParser(sFormatTimeStamp).decodedFormat
				else: timeStringParser("somewhereintime") # error

		self.__myDict = {"Y": 0, "Mth": 0, "D": 0, \
							"H": 0, "Min": 0, "S": 0, "P": 0	}
	def encodeToString(self):
		iFormatWalker = 0
		dCurToken = self.decodedFormat[iFormatWalker]
		while dCurToken['pos'] == -1:
			iFormatWalker += 1
			dCurToken = self.decodedFormat[iFormatWalker]
		iHour = 0
		sAMPM = ''
		sHourPlaceHolder = 'HH'			# HH and SS are good placeholders
		sAMPMPlaceHolder = 'SS'			# because they could not be delimiters
		sMyLetter = ''
		sResult = ''

		for dCurToken in self.decodedFormat[iFormatWalker:]:
			if dCurToken['type'] in ['time', 'date']:
				if dCurToken['letter'] == 'P': sResult += sAMPMPlaceHolder
				else:
					if dCurToken['letter'] == 'M':
						if dCurToken['type'] == 'time': sMyLetter = 'Min'
						else: sMyLetter = 'Mth'
					else:
						sMyLetter = dCurToken['letter']
					if sMyLetter == 'H' :
						sResult += sHourPlaceHolder[0:dCurToken['len']] #H or HH
						iHour = self.__myDict[sMyLetter]
					else :
						sResult += str(self.__myDict[sMyLetter]). \
											zfill(dCurToken['len'])
			else:
				iLetterCount = dCurToken['len']
				while iLetterCount > 0:
					sResult += dCurToken['letter']
					iLetterCount -= 1
		if sResult.find(sAMPMPlaceHolder) >= 0:
			if iHour >= 12 :
				if iHour > 12:  iHour -= 12
				sAMPM = 'PM'
			else:
				sAMPM = 'AM'
			sResult = sResult.replace(sAMPMPlaceHolder, sAMPM)
		if sResult.find(sHourPlaceHolder) >= 0 : # we have HH
			sResult = sResult.replace(sHourPlaceHolder, str(iHour).zfill(2))
		else:  # we have H
			sResult = sResult.replace(
							sHourPlaceHolder[0:1], str(iHour).zfill(1) 		)
		return sResult

	def decodeString(self, sValue):
		# At some point, we thought that the return value for decodeString()
		# would be this:
		#		datetime.datetime(	self.__myDict['Y'],
		#							self.__myDict['Mth'],
		#							self.__myDict['D'],
		#							self.__myDict['H'],
		#							self.__myDict['Min'],
		#							self.__myDict['S']
		#							)
		# But that turned into this discussion:
		# datetime.datetime(...) wants year, month, day and the others
		# to be within certain limits.
		# That's because it gives back a numeric value with which one may do
		# some good math like add some days and get the correct year and month
		# back.
		#
		# But if someone just wants to "translate" a file from a format to
		# another, who are we to judge why they didn't use
		# months or days or years into their format?
		#
		# Our code is strong enough to identify the numeric parts with their
		# label (given a correct format) and return them (or zero) back.
		#
		# Down the pike, it's up to the users of this module to not mess up,
		# or do whatever they want !
		# And that includes contributing to this module to implement
		# "good math" with time and date values if they want.
		# so with this in mind, we chose to return only integers representing
		# individual fields like year, month, day and the rest.
		if len(sValue) == 0:
			self.timeStampParsingError()
		iSValuePos = 0
		iFormatWalker = 0
		dCurToken = self.decodedFormat[iFormatWalker]
		while dCurToken['pos'] == -1:
			iFormatWalker += 1
			dCurToken = self.decodedFormat[iFormatWalker]
		iCurValue = 0
		sCurValue = ''
		while iSValuePos < len(sValue):
			if dCurToken['type'] == 'time' or dCurToken['type'] == 'date':
				if dCurToken['type'] == 'time' and dCurToken['letter'] == 'P':
					sCurValue += sValue[iSValuePos:iSValuePos + \
											dCurToken['len']]
					if sCurValue == 'PM' : self.__myDict['P'] = 12
					if sCurValue == 'AM' : self.__myDict['P'] = -12
					# if you give hour > 12 and 'AM' you'll get -12
					iSValuePos += 2
				else:
					while iSValuePos < len(sValue) and \
							sValue[iSValuePos] in "0123456789":
						sCurValue += sValue[iSValuePos]
						iSValuePos += 1
					iCurValue = int(sCurValue)
					if dCurToken['letter'] == 'M' :
						if dCurToken['type'] == 'time' :
							self.__myDict['Min'] = iCurValue
						else:
							self.__myDict['Mth'] = iCurValue
					else :
						self.__myDict[dCurToken['letter']] = iCurValue
				sCurValue = ''
				iCurValue = 0
			else:
				iSValuePos += dCurToken['len']
			iFormatWalker += 1
			if iFormatWalker < len(self.decodedFormat):
				dCurToken = self.decodedFormat[iFormatWalker]
		# if you give hour > 12 and 'AM' you'll get -12
		# if you give hour < 11 and 'PM' you'll get +12
		if self.__myDict['H']  < 12 and self.__myDict['P'] == 12 :
								self.__myDict['H'] += self.__myDict['P']
		if self.__myDict['H'] >= 12 and self.__myDict['P'] == -12:
								self.__myDict['H'] += self.__myDict['P']

	def __getSomeField(self, sWhatBit):
			return self.__myDict[sWhatBit]
	def __setSomeField(self, iValue, sWhatBit):
			self.__myDict[sWhatBit] = iValue
	def __hasSomeField(self, sWhatBit):
		retVal = False
		if sWhatBit in ['Mth', 'Min']:
			if sWhatBit == 'Mth':
				for tf in map(
							lambda d: d['letter'] == 'M' and \
									  d['len'] >=0 and \
									  d['type'] == 'date'
							, self.decodedFormat):
					if tf == True :return True
			if sWhatBit == 'Min':
				for tf in  map(
							lambda d: d['letter'] == 'M' and \
									  d['len'] >=0 and \
									  d['type'] == 'time'
							, self.decodedFormat):
					if tf == True :return True
			return False
		for tf in map(lambda d: d['letter'] == sWhatBit and d['len'] >=0, \
						self.decodedFormat):
			if tf == True : return True
		return retVal

	def getDay(self):	 return self.__getSomeField('D')
	def getMonth(self):	 return self.__getSomeField('Mth')
	def getYear(self):	 return self.__getSomeField('Y')
	def getHour(self):	 return self.__getSomeField('H')
	def getMinute(self): return self.__getSomeField('Min')
	def getSecond(self): return self.__getSomeField('S')

	def setDay(self, iValue):	 self.__setSomeField(iValue, 'D')
	def setMonth(self, iValue):	 self.__setSomeField(iValue, 'Mth')
	def setYear(self, iValue):	 self.__setSomeField(iValue, 'Y')
	def setHour(self, iValue):	 self.__setSomeField(iValue, 'H')
	def setMinute(self, iValue): self.__setSomeField(iValue, 'Min')
	def setSecond(self, iValue): self.__setSomeField(iValue, 'S')

	def hasDay(self):	 return self.__hasSomeField('D')
	def hasMonth(self):	 return self.__hasSomeField('Mth')
	def hasYear(self):	 return self.__hasSomeField('Y')
	def hasHour(self):	 return self.__hasSomeField('H')
	def hasMinute(self): return self.__hasSomeField('Min')
	def hasSecond(self): return self.__hasSomeField('S')

# This is a poem by the rock band Deep Purple

# Sweet child in time
# You'll see the line
# The line that's drawn between
# Good and bad
# See the blind man
# Shooting at the world
# Bullets flying
# Oh, taking toll
# If you've been bad
# Oh, Lord, I bet you have
# And you've not been hit
# Oh, by flying lead
# You'd better close your eyes
# Oh
# Bow your head
# Wait for the ricochet
# Sweet child in time
# You'll see the line
# The line that's drawn between
# Good and bad
# See the blind man
# Shooting at the world
# Bullets flying
# Oh, taking toll
# If you've been bad
# Lord, I bet you have
# And you've not been hit
# Oh, by flying lead
# You'd better close your eyes
# Oh
# Bow your head
# Wait for the ricochet
#






# Thank you for reading this f1l3
