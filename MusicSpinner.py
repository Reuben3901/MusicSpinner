import pygame, re, random, os, sys

# Set directory information
game_folder = os.path.dirname(__file__)
met_path = os.path.join(game_folder, 'metronomes_folder')

WIDTH = 700
HEIGHT = 700
genre = [
            "hiphop",
            "motown",
            "funk",
            "jazz",
            "punk",
            "blues",
            "EDM",
            "classical",
            "orchestral",
            "pop",
            "folk"
        ]

# Define colors
WHITE  = (255,255,255)
BLACK  = (0,0,0)
RED    = (255,0,0)
GREEN  = (100,200,100)
BLUE   = (100,155,205)
YELLOW = (255,255,0)

# Font
font_name = pygame.font.match_font('arial')

# Lists
rotated_Record_Img_List = []
rotated_Record_Rect_List = []

# Dictionaries
bpm_dict = {}

# Bools
is_blue = True
set_met = False

# Variables
num = 0
music = 0
last_update = 0
rot = 0

# Import metronome mp3s
for folderName, subfolders, filenames in os.walk(met_path):
    for filename in filenames:
        if "mp3" in filename:
            metTitle = filename.replace(".mp3","")
            bpm_dict[str(metTitle)] = (folderName + "\\" + filename)

# Initialize pygame and create window
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Music Spinner")

SONG_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(SONG_END)

# Image of record to be used in rotating
# record.png source:
#    https://pixabay.com/vectors/vinyl-record-sound-music-retro-308761/
original_image = pygame.image.load('record.png').convert()
original_image = pygame.transform.scale(original_image, (320, 320))
original_image.set_colorkey(WHITE)
original_rect = original_image.get_rect()
original_rect.center = (WIDTH/2,HEIGHT/2)
old_center = (350, 350)

# Generate rotated images at 30 degree increments
for i in range(0,360,30):
    new_image = pygame.transform.rotate(original_image, -1*i)
    new_image.set_colorkey(WHITE)
    new_image_rect = new_image.get_rect()
    new_image_rect.center = old_center
    rotated_Record_Img_List.append(new_image)
    rotated_Record_Rect_List.append(new_image_rect)
numberOfImages = len(rotated_Record_Img_List)

# FUNCTIONS
def random_bpm():
    global num, bpmButton
    n = 1
    # Make sure the bpm exists.
    #    Increments of 5 up to 220 then increments of 10 above
    while n != 0:
        num = random.randint(60, 260)
        if n > 220:
            n = num % 5
        else:
            n = num % 10
    g = random.randint(0, len(genre)-1)
    bpmButton = Button(genre[g]+": "+str(num),
                       (WIDTH/2, HEIGHT/6), metronome_music)
    return str(num)

def metronome_music():
    global set_met
    pygame.mixer.music.load(bpm_dict[random_bpm()])
    pygame.mixer.music.set_volume(0.7)
    set_met = False

def rotate_record_img():
    global rot, music, set_met, is_blue, last_update
    now = pygame.time.get_ticks()
    if now-last_update >= 60000/num/numberOfImages:
        rot = (1+rot) % numberOfImages
        last_update = now

    # Alternate background color
    if now - music >= 60000/num:
            if is_blue:
                screen.fill(BLUE)
                if not set_met:
                    pygame.mixer.music.play()
                    set_met = True
                is_blue = False
            else:
                screen.fill(GREEN)
                is_blue = True
            music = now

class Button():
    def __init__(self, txt, location, action, bg=RED, fg=BLACK,
                 size=(150, 30), font_name="Segoe Print", font_size=16):
        self.color = bg  # the static (normal) color
        self.bg = bg  # actual background color, can change on mouseover
        self.fg = fg  # text color
        self.size = size

        self.font = pygame.font.SysFont(font_name, font_size)
        self.txt = txt
        self.txt_surf = self.font.render(self.txt, 1, self.fg)
        self.txt_rect = self.txt_surf.get_rect(center=[s//2 for s in self.size])

        self.surface = pygame.surface.Surface(size)
        self.rect = self.surface.get_rect(center=location)

        self.call_back_ = action

    def draw(self):
        self.mouseover()

        self.surface.fill(self.bg)
        self.surface.blit(self.txt_surf, self.txt_rect)
        screen.blit(self.surface, self.rect)

    def mouseover(self):
        self.bg = self.color
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.bg = YELLOW  # mouseover color

    def call_back(self):
        self.call_back_()

def mouse_button_down():
    pos = pygame.mouse.get_pos()
    if bpmButton.rect.collidepoint(pos):
        bpmButton.call_back()

# Initialize button, starting genre, and bpm
bpmButton = Button(str(num) + " BPMs", (WIDTH/2, HEIGHT/6), metronome_music)
metronome_music()

# GAME LOOP
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bpmButton.call_back()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_button_down()
        elif event.type == pygame.QUIT:
            running = False
        if event.type == SONG_END:
            pygame.mixer.music.set_endevent(SONG_END)
            set_met = False

    bpmButton.draw()
    screen.blit(rotated_Record_Img_List[rot], rotated_Record_Rect_List[rot])
    rotate_record_img()
    pygame.display.flip()

pygame.quit()
sys.exit()

print("Program Ended")
