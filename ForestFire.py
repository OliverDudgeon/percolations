import numpy as np
import pygame
import pygame_gui

class ForestFire:
    def __init__(self,gui_manager,window_size):
        (window_width,window_height) = window_size
        self.gui_manager = gui_manager
        self.window_size = window_size
        self.grid_size = (self.grid_width,self.grid_height) = (200,200)
        self.max_array_length = self.grid_width*self.grid_height
        self.sites = np.array([])
        self.draw_call = False
        self.firegrid = np.array([])
        
        self.initial_slider = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect((10, 670), (600, 20)),0.25,(0.0, 1.0),gui_manager,)
        self.initial_slider_label = pygame_gui.elements.UILabel(
            pygame.Rect((10,690),(300,20)),f'Initial tree coverage fraction = {self.initial_slider.current_value}',
            gui_manager)
        
        self.p_grow_slider = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect((10,730),(600,20)),0.25,(0.0,1.0),gui_manager)
        self.grow_slider_label = pygame_gui.elements.UILabel(
            pygame.Rect((10,750),(300,20)),f'Growth probability = {self.p_grow_slider.current_value}',
            gui_manager)
        
        self.p_fire_slider = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect((10,790),(600,20)),0.25,(0.0,1.0),gui_manager)
        self.fire_slider_label = pygame_gui.elements.UILabel(
            pygame.Rect((10,810),(300,20)),f'Spontaneous fire probability = {self.p_fire_slider.current_value}',
            gui_manager)
        
        self.draw_surface = pygame.Surface(self.grid_size)
        self.font = pygame.font.SysFont(None, 25)
        
    def Draw(self, window_surf):
        if self.draw_call:
            self.draw_surface.fill((255,255,255))
            for index in self.treegrid:
                self.draw_surface.set_at((index%self.grid_width,index//self.grid_width),(0,0,0))
                # self.trees_array = pygame.surfarray.array2d(self.draw_surface)
                # self.trees_array = np.divide(trees_array,np.amax(trees_array))
                # trees = 0, empty = 1
            for index in self.firegrid:
                self.draw_surface.set_at((index%self.grid_width,index//self.grid_width),(0,0,1))
            global testvar
            testvar = self.firegrid
            
            self.draw_call = False
        window_surf.blit(pygame.transform.scale(self.draw_surface, (600, 600)), (10, 60))
        
    def GenRandomStart(self):
        self.treegrid = np.where(np.random.rand(self.max_array_length) < self.initial_slider.current_value)[0]
        # self.grid[0,:] = self.grid[:,0] = self.grid[self.grid_height,:] = self.grid[:,self.grid_width] = 0
        self.draw_call = True
        
    def Burning(self):
        neighbourhood = ((-1,-1), (-1,0), (-1,1), (0,-1), (0, 1), (1,-1), (1,0), (1,1))
        EMPTY, TREE, FIRE = 0, 1, 2
        p = self.p_grow_slider.current_value
        f = self.p_fire_slider.current_value
        for dx in range(0,np.size(self.treegrid)):
            if np.random.random() < f:
                np.append(self.firegrid,self.treegrid[dx])
                treegrid2 = self.treegrid[self.treegrid != self.treegrid[dx]]
                
        self.treegrid = treegrid2
        self.daw_call = True
        global test_firegrid
        test_firegrid = self.firegrid
        global test_treegrid
        test_treegrid = self.treegrid

                
        # for dx in range(0,self.max_array_length):
        #     if dx in self.treegrid and np.random.random() <= f:
        #         np.append(self.firegrid,dx)
        #         self.treegrid = self.treegrid[self.treegrid != dx]
        #     if dx not in self.treegrid and np.random.random() <= p:
        #         np.append(self.treegrid,dx)
        # global testvar
        # testvar = self.firegrid
        # self.draw_call = True
        

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
                    #perc_manager.Burning()
            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == perc_manager.initial_slider:
                    ISVal = format(perc_manager.initial_slider.current_value,'.2f')
                    perc_manager.initial_slider_label.set_text(f'Initial tree coverage fraction = {ISVal}')
                    is_playing = False
                    button_play.set_text("Play")
                    perc_manager.GenRandomStart()
                if event.ui_element == perc_manager.p_grow_slider:
                    GSVal = format(perc_manager.p_grow_slider.current_value,'.2f')
                    perc_manager.grow_slider_label.set_text(f'Growth probability = {GSVal}')
                    is_playing = False
                    button_play.set_text("Play")
                    perc_manager.GenRandomStart()
                if event.ui_element == perc_manager.p_fire_slider:
                    FSVal = format(perc_manager.p_fire_slider.current_value,'.2f')
                    perc_manager.fire_slider_label.set_text(f'Spontaneous fire probability = {FSVal}')
                    is_playing = False
                    button_play.set_text("Play")
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