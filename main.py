import array
import re
import struct

# Helper Functions

# Convert 6 characters long hex value of a pixel to decimals
# Then, save it to a dictionary called bgrDict
# Sample input: '0d0e0f', Output: {0: 13, 1: 14, 2: 15}
def saveBGR(BGRhex):
	splitted = re.findall('..?', BGRhex)

	bgrDict = {0: 0, 1: 0, 2: 0} # 0 is blue, 1 is green, 2 is red
	for index, byte in enumerate(splitted):
		value = int(byte, base=16)
		bgrDict[index] = value

	return bgrDict

# Return hex equivalent of decimal values up to 255
def dec2hex(decimal):
	if decimal > 255 or decimal < 0:
		return None

	elif decimal < 16:
		hexStr = str(0) + hex(decimal).lstrip('0x')

	else:
		hexStr = hex(decimal).lstrip('0x')
	
	return hexStr


# Returns True for positive odd numbers otherwise returns False 
def check_odd(number):
	if number % 2 == 1 and number > 0:
		return True

	return False


# Short information about Bitmap (sorry for wrong info, it is just a reminder for myself to understand Bitmap in the future)
# Bitmap stores pixels' color values as BGR, Blue Green Red
# First 14 Bytes are the first header, next 40 bytes are the second and last header
# Byte 19-22 give the width, Byte 23-26 give you the height which is needed for calculation of total pixels
# Since one hexadecimal character is 4 bits, two of them are equal to 1 byte
# As a result, first 108 hexadecimal characters of a bitmap file are metadata about the file.

class Bitmap:
	def __init__(self, image):
		# Bitmap image
		self.image = image

		# First Header, 14 bytes
		self.type = image.read(2).decode() # Always BM in ASCII
		self.size = struct.unpack('I', self.image.read(4))[0]
		self.reserved1 = struct.unpack('H', self.image.read(2))[0]
		self.reserved2 = struct.unpack('H', self.image.read(2))[0]
		self.offset = struct.unpack('I', self.image.read(4))[0] # Sum of the size of two headers. Always 54 in decimal

		# Second Header, 40 bytes
		self.DIBHeaderSize = struct.unpack('I', self.image.read(4))[0] # Always 40 in decimal
		self.width = abs(struct.unpack('i', self.image.read(4))[0])
		self.height = abs(struct.unpack('i', self.image.read(4))[0])
		self.colorPlanes = struct.unpack('H', self.image.read(2))[0]
		self.bitsPerPixel = struct.unpack('H', self.image.read(2))[0]
		self.CompressionMethod = struct.unpack('I', self.image.read(4))[0]
		self.RawImageSize = struct.unpack('I', self.image.read(4))[0]
		self.HorizontalResolution = struct.unpack('I', self.image.read(4))[0]
		self.VerticalResolution = struct.unpack('I', self.image.read(4))[0]
		self.NumColors = struct.unpack('I', self.image.read(4))[0]
		self.importantColors = struct.unpack('I', self.image.read(4))[0]

	# Save Blue, Green, Red values of pixels to a list in decimal numbers
	# So. length of this list is equal to self.width * self.height * 3
	# Example: 149, 92, 1 for a pixel 
	# p.s. This code is unfortunately ugly. I will try to change it later
	def pixelData(self):
		lines = self.image.readlines()
		actualData = ''
		for line in lines:
			actualData += line.hex()

		# Regex splits every 6 character a.k.a BGR
		BGRList = re.findall('......?', actualData) # Hex values of pixels
		pixelList = []
		for pixel in BGRList:
			pixelDict = saveBGR(pixel)
			for i in range(self.bitsPerPixel // 8): # range(3) always (not needed dynamically coding but i dont like hardcoding) 
				pixelList.append(pixelDict[i])

		return pixelList

	# One of the common ways to grayscale is summing up BGR values and updating them with the average values
	# Example: (200, 45, 55) becomes (100, 100, 100)
	def grayscale(self):
		pixels = self.pixelData()
		for index in range(0, len(pixels), 3):
			average = (pixels[index] + pixels[index + 1] + pixels[index + 2]) // 3

			# Updating pixels list with the new values 
			for i in range(3):
				pixels[index + i] = average

		return pixels


	# Grid size must be a positive odd number
	def blur(self, grid_size = 3):
		pixels = self.pixelData()
		bytesPerPixel = self.bitsPerPixel // 8

		# Split pixels list for every bytesPerPixel and store it in a new list called temp
		# Example: [[149, 92, 1], [15, 20, 25], [38, 38, 38] ...]
		temp = []
		for i in range(0, len(pixels), bytesPerPixel):
			temp.append(pixels[i:i + bytesPerPixel])

		# Split temp for every row and store it in a new list called BGRpixels
		# New list's length becomes self.height
		# Example
		# [
		#	[[149, 92, 1], [15, 20, 25], [38, 38, 38] ...],
		#	[[172, 72, 5], [25, 20, 15], [39, 39, 39] ...],
		#	[[195, 52, 9], [45, 50, 55], [40, 40, 40] ...],
		#	...
		# ]
		BGRpixels = []
		for j in range(0, len(temp), self.width):
			BGRpixels.append(temp[j:j + self.width])


		if check_odd(grid_size):
			distance = (grid_size - 1) // 2
		else:
			raise Exception('grid_size must be a positive odd number')

		newPixels = []
		for row_index, row in enumerate(BGRpixels):
			for pixel_index, pixel in enumerate(row):
				# Create a grid for every pixel
				# Example : if grid_size == 3 then distance becomes 1
				# create grid for indexes [0, 0, 0
				#						   0, 1, 0
				#						   0, 0, 0]
				# 1 is center pixel which this grid is created for 0s are others
				# creating this grid by adding values to center pixel's index 
				# every number between (-1 * distance, distance)
				# of course it must be checked there are no index 'overflows'
				blurred = [0, 0, 0]
				totalColors = [0, 0, 0]
				counter = 0
				for i in range(-1 * distance, distance + 1):
					if i + row_index < 0 or i + row_index >= self.height:
						continue

					for j in range(-1 * distance, distance + 1):
						if j + pixel_index < 0 or j + pixel_index >= self.width:
							continue
						counter += 1

						for k in range(3):
							totalColors[k] += BGRpixels[row_index + i][pixel_index + j][k]

				for i in range(3):
					blurred[i] = totalColors[i] // counter

				newPixels.append(blurred)

		return newPixels

# Test
# filepath = 'images/stadium.bmp'
# with open(filepath, 'rb') as file:
# 	myImage = Bitmap(file)
# 	blurred = myImage.blur()
# 	print(blurred)
