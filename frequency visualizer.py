import sys, math, wave,struct,pygame,time,pylab,pickle,winsound
from pygame.locals import * 
import numpy as np
import matplotlib.pyplot as plt
 
class testii():

	def __init__(self):
		
		pygame.init()
		self.debugging = False
		pygame.display.set_mode((1400,800))
		self.screen = pygame.display.get_surface()
		self.clock = pygame.time.Clock()
		self.background = pygame.Surface((1400,800))
		pygame.display.set_caption("frequency visualizer")
		self.a = 0
		self.background.fill((self.a,self.a,self.a))
		self.clock = pygame.time.Clock()
		self.data_size = 1764
		self.fname = "1khz.wav" # Add your wav file path here
		self.wav_file=wave.open(self.fname,'r')
		print("nframes:",self.wav_file.getnframes())
		self.frames = self.wav_file.getnframes() 
		self.frate = self.wav_file.getframerate()
		pygame.mixer.init(44100)
		self.sound = pygame.mixer.Sound(self.fname)
		self.allBricks = pygame.sprite.Group()
		self.listOfBricks = []
		barwidth = 5 # 26
		self.freqbarsno = 401
		for i in range(1,self.freqbarsno):
			if i == 3:
				self.bass = Brick(barwidth*i,i*25)
				self.allBricks.add(self.bass)
				self.listOfBricks.append(self.bass)
				self.allBricks.add(self.bass)
			else:
				self.brick = Brick(barwidth*i,i*25)
				self.listOfBricks.append(self.brick)
				self.allBricks.add(self.brick)
		
	def run(self):
		self.x = 0
		self.secs = 0
		self.mins = 0
		self.pytime = 0
		suurin = 0
		channels = self.ifStereo()
		valo = 2
		snapshot = False
		eka = True
		self.sound.play()
		start_time = time.time()

		while self.x < self.frames-self.data_size:
			self.time = time.time() - start_time
						
			if self.time - self.pytime >= 0:
				self.secs = self.secs + 0.04#0,04
				self.pytime = self.pytime + 0.04#0,04
				self.x = self.x+self.data_size
				if self.secs >= 60:
					self.secs = 0
					self.mins = self.mins + 1
					### uses FFT algorithm to calculate frequency ###			
				self.data=self.wav_file.readframes(self.data_size)
				self.data =struct.unpack('{n}h'.format(n=self.data_size*channels), self.data)
				self.data=np.array(self.data)
				self.w=np.fft.fft(self.data)
				freqs = np.fft.fftfreq(len(self.w))
				fre = freqs
				fre = abs(fre*self.frate)
			
				idx=np.argmax(np.abs(self.w[:self.freqbarsno])**2)*channels #temporary fix
				coefficients = (np.abs(self.w)**2)
				if self.debugging:
					print("idx:",idx)
				freq=freqs[idx]
				loudestFreq=abs(freq*self.frate)
				if snapshot:
					np.savetxt("freqs.txt",fre)
					np.savetxt("coefficients.txt",coefficients)
					plt.plot(fre, coefficients)
					plt.show()
					snapshot = False
				
				#..........Update bricks..........#every brick reflects one frequency
				for i in range(1,self.freqbarsno):
					self.listOfBricks[i-1].update(coefficients[i])
					if coefficients[i] > suurin:
						suurin = coefficients[i]
					if (loudestFreq == i*25):
						self.listOfBricks[i-1].changeColor()
					

			#.................EVENTS.................#
			for event in pygame.event.get():
				if event.type == QUIT:
					sys.exit(0)
						
						#..........KEY DOWNS.......#
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:	#Exit
						sys.exit(0)
					elif event.key==pygame.K_s:
						snapshot = True
					elif event.key==pygame.K_RIGHT:
						if valo < 99:
							valo = valo+1
					elif event.key==pygame.K_LEFT:
						if valo > 0:
							valo = valo -1
			
				
			##Set brightness according to the bass (50hz) you can change this using the arrow keys##	
			self.lights(valo)	
			##Draw background##
			self.screen.blit(self.background,(0,0))
			##Blit text on screen##
			self.blitTexts(loudestFreq)
			##Draw bricks on screen## 
			self.allBricks.draw(self.screen)

			pygame.display.flip()
			self.clock.tick(55)
			
		self.wav_file.close()
		elapsed_time = time.time() - start_time
		print(elapsed_time)


	def lights(self, valo):
		self.a = int((self.listOfBricks[valo].get()-15)*1.5)
		self.listOfBricks[valo].changeColor((198,59,101))
		if self.a > 255:
			self.a = 255
		self.background.fill((self.a,self.a,self.a))
	
	def blitTexts(self,loudestFreq):
		if pygame.font:
				self.font = pygame.font.Font(None, 36)
				self.pytext = self.font.render("pyTime: %.2f " % (self.pytime), 2, (0, 0, 225))
				self.text = self.font.render("Elapsed time: %.2f " % (self.time), 2, (0, 0, 225))
				self.difference = self.font.render("Difference: %.2f " % (self.time - self.pytime), 2, (0, 0, 225))
				self.freqtext = self.font.render("Frequency: %.2f " % loudestFreq, 2, (0, 0, 225))
				self.screen.blit(self.pytext, (800,600))
				self.screen.blit(self.text, (800,640))
				self.screen.blit(self.difference, (800,680))
				self.screen.blit(self.freqtext, (500,680))
	
	def ifStereo(self):
		return self.wav_file.getnchannels()
	
class Brick(pygame.sprite.Sprite):
	
	def __init__(self,x,target,tolerance = 0):
		pygame.sprite.Sprite.__init__(self)
		self.width = 5 #25
		self.height = 30
		self.image = pygame.Surface([self.width, self.height])
		self.image.fill((255,0,0))
		self.image.set_colorkey((255,255,255))
		self.rect = self.image.get_rect()
		self.target = target
		self.x = x
		self.tolerance = tolerance
		self.rect.x = x
		self.rect.y = 400
		print(target)
	
	def update(self,coef):
		if coef < 10**10:
			coef = 0
		else:
			coef = (math.log((coef / 10**9),2))*10
		if(coef >0):
			self.height = int(coef)
		elif self.height > 255:
			self.height = 255
		elif self.height < 30:
			self.height = 30
		else:
			self.height = 30
		self.image.fill((int(self.height/2),int(self.height/1.5),self.height))
		self.image = pygame.transform.scale(self.image,(int(self.width),int(self.height)))
		self.rect.y = 430-self.height
		
	def get(self):
		return self.height
		
	def changeColor(self, color =(0,255,0)):
		self.image.fill(color)
	
class Palkki(pygame.sprite.Sprite):

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("palkki.png").convert()
		self.image.set_colorkey((255,255,255))
		self.rect = self.image.get_rect()
		self.rect.x = 26
		self.rect.y = 430
		
	def update(self,x):
		pass
		
def main():
	testii().run()
	
if __name__=="__main__":
	main()
		