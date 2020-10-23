import numpy as np
import pygame
import pygame_gui

# Most of the underlying structure taken from an early version of Adam's 
# percolation.py code - this is the first time I've used GUIs in Python 
# and the first time I've used pygame/pygame_gui, so there are probably loads 
# of mistakes. In some places I didn't really understand what Adam had written
# so just left it alone....

class ForestFire:
    def __init__(self,gui_manager,window_size):
        (window_width,window_height) = window_size
        self.gui_manager = gui_manager
        self.window_size = window_size
        self.grid_size = (self.grid_width,self.grid_height) = (180,180)
        self.max_array_length = self.grid_width*self.grid_height
        self.sites = np.array([])
        self.draw_call = False
        # firegrid_array will have elements 1 where fire, 0 where no fire
        self.firegrid_array = np.zeros([self.grid_height,self.grid_width])
        # treegrid_array will have elements 1 where tree, 0 where no tree.
        # Note: a tree that is on fire is counted as a fire rather than a
        # tree (i.e. it appears in firegrid_array but not treegrid_array)
        self.treegrid_array = np.zeros([self.grid_height,self.grid_width])
        
        # Text entry box for initial tree coverage fraction
        self.initial_textentry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((350,670),(100,20)),gui_manager)
        #self.initial_textentry.set_allowed_characters('numbers')
        self.initial_textentry.set_text('0.2')
        self.initial_textentry_label = pygame_gui.elements.UILabel(
           pygame.Rect((10,670),(300,20)), 'Initial tree coverage fraction: ',
           gui_manager)
        
        # Text entry box for probability of tree growth
        self.p_grow_textentry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((350,710),(100,20)),gui_manager)
        #self.initial_textentry.set_allowed_characters('numbers')
        self.p_grow_textentry.set_text('0.01')
        self.p_grow_textentry_label = pygame_gui.elements.UILabel(
           pygame.Rect((10,710),(300,20)), 'Growth probability: ',
           gui_manager)
        
        # Text entry box for probability of spontaneous tree fire
        self.p_fire_textentry = pygame_gui.elements.UITextEntryLine(
            pygame.Rect((350,750),(100,20)),gui_manager)
        #self.initial_textentry.set_allowed_characters('numbers')
        self.p_fire_textentry.set_text('0.0001')
        self.p_fire_textentry_label = pygame_gui.elements.UILabel(
           pygame.Rect((10,750),(300,20)), 'Spontaneous fire probability: ',
           gui_manager)
        
        self.draw_surface = pygame.Surface(self.grid_size)
        self.font = pygame.font.SysFont(None, 25)
        
        # Draws trees/fires using treegrid and firegrid
    def Draw(self, window_surf):
        if self.draw_call:
            self.draw_surface.fill((44,20,1))
            for index in self.treegrid:
                self.draw_surface.set_at((index%self.grid_height,
                                          index//self.grid_width),(0,100,0))
            for index in self.firegrid:
                self.draw_surface.set_at((index%self.grid_height,
                                          index//self.grid_width),(255,40,7))
            self.draw_call = False
        window_surf.blit(pygame.transform.scale(self.draw_surface, 
                                                (600, 600)), (10, 60))
         
        # Generate initial tree distribution 
    def GenRandomStart(self):
        # Define 1d array treegrid which contains the randomly-generated 
        # indices/positions of trees. This will be used to draw trees
        self.treegrid = np.where(np.random.rand(self.max_array_length) < \
                                 float(self.initial_textentry.get_text()))[0]
        # Use treegrid to produce treegrid_array
        for index in self.treegrid:
            self.treegrid_array[index%self.grid_height,index//self.grid_width] = 1
            # Outer edges of treegrid_array set to be empty - this simplifies 
            # fire spread code (see Burning)
        self.treegrid_array[0,:] = self.treegrid_array[:,0] = \
            self.treegrid_array[self.grid_height-1,:] = \
                self.treegrid_array[:,self.grid_width-1] = 0
        # Define 1d array firegrid which will contain the indices/positions 
        # of fires - will be filled by Burning function. Used to draw fires
        self.firegrid = np.array([])
        self.draw_call = True
        
        # Reset variables (called when text entry changed)
    def Reset_model(self,window_surf):
        self.draw_surface.fill((40,20,1))
        window_surf.blit(pygame.transform.scale(self.draw_surface, 
                                                (600, 600)), (10, 60))
        self.treegrid_array = np.zeros([self.grid_height,self.grid_width])
        self.firegrid_array = np.zeros([self.grid_height,self.grid_width])
       
       # Grow trees, set fires and allow them to spread
    def Burning(self): 
        # Get probability of spontaneous fire
        f = float(self.p_fire_textentry.get_text())
        # Get probability of tree growth
        p = float(self.p_grow_textentry.get_text())
        # Look through every point in the fire and tree arrays
        for dx in range(0,self.grid_width):
            for dy in range(0,self.grid_height):
                # Spontaneous growth
                if self.treegrid_array[dy,dx] == 0 and \
                    self.firegrid_array[dy,dx] == 0 and np.random.random() < p:
                    # Grown tree corresponds to +1, but set to -1 here so that 
                    # the element is ignored through rest of the loops, 
                    # otherwise a tree could catch fire before it existed
                    self.treegrid_array[dy,dx] = -1 
                # Spontaneous fire
                if self.treegrid_array[dy,dx] == 1:
                    if np.random.random() < f:
                        self.treegrid_array[dy,dx] = 0 
                        self.firegrid_array[dy,dx] = 1
                # Fire spread
                if self.firegrid_array[dy,dx] == 1:
                    # Up, down, left, right neighbours of burning tree. New 
                    # fires are set to -1 so that they are ignored by further
                    # loop iterations
                    if self.treegrid_array[dy+1,dx] == 1: 
                        self.firegrid_array[dy+1,dx] = -1
                        self.treegrid_array[dy+1,dx] = 0
                    if self.treegrid_array[dy-1,dx] == 1:
                        self.firegrid_array[dy-1,dx] = -1
                        self.treegrid_array[dy-1,dx] = 0
                    if self.treegrid_array[dy,dx+1] == 1:
                        self.firegrid_array[dy,dx+1] = -1
                        self.treegrid_array[dy,dx+1] = 0
                    if self.treegrid_array[dy,dx-1] == 1:
                        self.firegrid_array[dy,dx-1] = -1
                        self.treegrid_array[dy,dx-1] = 0
                    # Diagonal neighbours of burning tree
                    if self.treegrid_array[dy+1,dx+1] == 1:
                        self.firegrid_array[dy+1,dx+1] = -1
                        self.treegrid_array[dy+1,dx+1] = 0
                    if self.treegrid_array[dy+1,dx-1] == 1:
                        self.firegrid_array[dy+1,dx-1] = -1
                        self.treegrid_array[dy+1,dx-1] = 0
                    if self.treegrid_array[dy-1,dx+1] == 1:
                        self.firegrid_array[dy-1,dx+1] = -1
                        self.treegrid_array[dy-1,dx+1] = 0
                    if self.treegrid_array[dy-1,dx-1] == 1:
                        self.firegrid_array[dy-1,dx-1] = -1
                        self.treegrid_array[dy-1,dx-1] = 0
                    # Original burning tree burns itself out
                    self.firegrid_array[dy,dx] = 0
                        
        # Set outer edges of treegrid_array and firegrid_array to zero,
        # otherwise 'dx+1' etc will cause errors on next iteration
        self.treegrid_array[0,:] = self.treegrid_array[:,0] = \
            self.treegrid_array[self.grid_height-1,:] = self.treegrid_array[:,self.grid_width-1] = 0
        self.firegrid_array[0,:] = self.firegrid_array[:,0] = \
            self.firegrid_array[self.grid_height-1,:] = self.firegrid_array[:,self.grid_width-1] = 0
        # Take absolute value of elements in treegrid_array so that the 
        # newly-grown trees have element +1 rather than -1
        self.treegrid_array = np.absolute(self.treegrid_array)
        # Do the same for firegrid_array to deal with new fires
        self.firegrid_array = np.absolute(self.firegrid_array)
        # Produce 1d treegrid and firegrid from treegrid_array and 
        # firegrid_array
        self.treegrid = np.ravel_multi_index(np.nonzero(self.treegrid_array),
                                             (self.grid_height,self.grid_width))
        self.firegrid = np.ravel_multi_index(np.nonzero(self.firegrid_array),
                                             (self.grid_height,self.grid_width))
        self.draw_call = True

# Complicated gui stuff that I don't completely understand (mostly Adam's work)
pygame.init()
pygame.display.set_caption('Forest Fire Model')
window_size = (window_width,window_height) = (720,850)
window_surface = pygame.display.set_mode(window_size)
gui_manager = pygame_gui.UIManager(window_size)

button_play = pygame_gui.elements.UIButton(pygame.Rect(620,120,90,50),"Play",gui_manager)

perc_manager = ForestFire(gui_manager, window_size)
perc_manager.GenRandomStart()

is_running = True
is_playing = False
time_start = 0
time_end = 0.01
time_delta = 0.01

time_timer = 0.0

while is_running:
    time_end = pygame.time.get_ticks()
    time_delta = (time_end - time_start)/1000.0
    time_start = time_end
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == button_play:
                    is_playing = not is_playing
                    if is_playing: button_play.set_text("Pause")
                    else: button_play.set_text("Play")
            if event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                is_playing = False
                button_play.set_text('Play')
                perc_manager.Reset_model(window_surface)
                perc_manager.GenRandomStart()
                    
    if is_playing:
        perc_manager.Burning()
    gui_manager.process_events(event)

    time_timer += time_delta
    if time_timer > 0.5:
        time_timer -= 0.5

    gui_manager.update(time_delta)

    window_surface.fill((44, 47, 51))
    perc_manager.Draw(window_surface)
    gui_manager.draw_ui(window_surface)
    pygame.display.update()

pygame.quit()