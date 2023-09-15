import array
import re
import struct

def saveBGR(BGRhex):
	splitted = re.findall('..?', BGRhex)
	bgrDict = {0: 0, 1: 0, 2: 0} # 0 is blue, 1 is green, 2 is red
	for index, byte in enumerate(splitted):
		value = int(byte, base=16)
		bgrDict[index] = value

	return bgrDict


# Short information about Bitmap (sorry for wrong info, it is just a reminder for myself to understand in the future)
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


# Test
# filepath = 'images/stadium.bmp'
# with open(filepath, 'rb') as file:
# 	myImage = Bitmap(file)
# 	print(myImage.grayscale())