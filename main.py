# Simple shooter game
# rewrite the suite if it shows error and it was fine,you have to manually write it

# lets make the window not resizable
import kivy
kivy.config.Config.set('graphics','resizable',0)

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty,NumericProperty,\
BooleanProperty,ListProperty

from kivy.core.audio import SoundLoader # for shooting sound
from kivy.storage.jsonstore import JsonStore # for score saving
from kivy.clock import Clock
from kivy.uix.image import Image

from kivy.core.window import Window
from random import randint,randrange
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager,Screen

# lets make the cursor visible
Window.show_cursor = True

# The game background and it will contain all the game elements
class Background(Image):
    def __init__(self,**kwargs):
        super(Background,self).__init__(**kwargs)
        self.size = self.texture_size
        self.add_widget(Player())  # adds the player to the game screen
        
    def stop(self):               # stops when left the screen
        self.remove_widget(Player())

# The player class this will contain enemy also
class Player(Widget):
    enmy_1 = ObjectProperty(None)   # enemy_1 refference
    enmy_2 = ObjectProperty(None)   # enemy_2 reference
    enmy_3 = ObjectProperty(None)   # enemy_3 refernce

    game_over = BooleanProperty(False) #makes the gun not shootable

    countdown_going_on = BooleanProperty(True)
    #parent = ObjectProperty(None)

    put_limit_to_countdown_timer = BooleanProperty(False)

    sound = ObjectProperty(None,allownone = True)

    enemies = ListProperty([])

    image_1 = ObjectProperty(None)  # player ship body
    image_2 = ObjectProperty(None)  # ships bullet

    go = ObjectProperty()           # this will make ship move
    score = ObjectProperty(None)    # this will display score on screen
    popup = ObjectProperty(None)

    bullet_speed = ListProperty([0,50])  # the speed of bullet
    velocity = ListProperty([5,10])      # the movement speed of player
    
    time_count = NumericProperty()
    points = NumericProperty()           # point earned

    check_if_ship_collide = BooleanProperty(False)  # check to see if ourship collides with rocks
    check_if_ship_collide_timer = ObjectProperty(None)

    l_enabled = BooleanProperty(False)   # if left is pressed,bcomes True
    r_enabled = BooleanProperty(False)   # if right is pressed,becomes True
    moving = BooleanProperty(False)      # if the player is moving,bcomes True

    shooting = BooleanProperty(False)    # if it is shooting,becomes True 
    
    # makes sure that this runs no matter what happens
    def __init__(self,**kwargs):
        super(Player,self).__init__(**kwargs)
        #register the keyboard
        self._keyboard = Window.request_keyboard(self._keyboard_closed,self,'text')
        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down = self._on_keyboard_down,on_key_up=self._on_key_up)
        # add the score display to the screen
        self.score = Score()
        self.add_widget(self.score)
        
        # points counter
        self.points = 0
        self.score.text = str(self.points)

        #get set go
        self.timer = Label(text = '')
        self.timer.font_size = '80sp'
        self.timer.x = 100
        self.timer.y = 300
        self.add_widget(self.timer)

        self.put_limit_to_countdown_timer = True

        if self.put_limit_to_countdown_timer == True:
            #update time
            self.timer_schedule = Clock.schedule_interval(self.timer_update,1.0)

    # this will update timer
    def timer_update(self,*args):
        self.time_count += 1
        self.timer.text = str(self.time_count)

        if self.time_count >= 4:
            self.timer.font_size = '100sp'
            self.timer.text = str('GO!')

        if self.time_count >= 5:
            self.countdown_going_on = False
            if self.sound == None:
                self.sound = SoundLoader.load('shoot.wav')
            #self.parent = Game()
            #print "done............ "
            Clock.unschedule(self.timer_schedule)
            self.remove_widget(self.timer)
            # add the enemy_1 to the screen
            self.enmy_1 = Enmy_1()
            self.add_widget(self.enmy_1)
            # start the enemy movement
            self.enmy_1.run = Clock.schedule_interval(self.enmy_1.update,1.0/60.0)
            self.enemies.append(self.enmy_1)

            # add the enemy_2 to the screen
            self.enmy_2 = Enmy_2()
            self.add_widget(self.enmy_2)
            # start the enemy movement
            self.enmy_2.run = Clock.schedule_interval(self.enmy_2.update,1.0/60.0)
            self.enemies.append(self.enmy_2)

            # add the enemy_2 to the screen
            self.enmy_3 = Enmy_3()
            self.add_widget(self.enmy_3)
            # start the enemy movement
            self.enmy_3.run = Clock.schedule_interval(self.enmy_3.update,1.0/60.0)
            self.enemies.append(self.enmy_3)

            self.check_if_ship_collide_timer = Clock.schedule_interval(self.check_ship_collide,1.0/60.0)
            #print 'countdown timer strted'

    # checks to see if ship collide with rocks
    def check_ship_collide(self,*args):
        for self.enmy in self.enemies:
            if self.image_1.collide_widget(self.enmy):
                Clock.unschedule(self.enmy_1.run)
                Clock.unschedule(self.enmy_2.run)
                Clock.unschedule(self.enmy_3.run)
                self.game_over = True # makes it true so that we cannot shoot
                self.score.text = 'GAME OVER'
                self.Score_count()
                break  # break out of loop

    # this will save the score
    def Score_count(self):
        self.old_points = self.points

        self.score = JsonStore("score.json")
        if not self.score:
            self.score.put("score",score = self.old_points)
        else:
            if self.points >= self.score.get('score')['score']:
                self.old_points = self.points
                self.score.put("score",score = self.old_points)
                #self.menu.score_points.text = self.menu.score_points.text


    # check keyboard closed event
    def _keyboard_closed(self):
        #print "keyboard is closed"
        self._keyboard.unbind(on_key_down = self._on_keyboard_down)
        self._keyboard.unbind(on_key_up = self._on_key_up)
        self._keyboard = None

    # if key is pressed on keyboard then do the folowing...
    def _on_keyboard_down(self,keyboard,keycode,text,modifiers):
    	#if left is pressed and right is not presed
        if keycode[1] == "left" and self.r_enabled is False: 
        	#if the ship is not moving & it is not shooting...
            if self.moving == False and self.shooting == False:
            	self.moving = True # makes it true so that right cannot be pressed

            	#move the player
                self.go = Clock.schedule_interval(self.go_left,1.0/60.0)
            else:
            	pass
                #print "you cant move left"
                
        if keycode[1] == "right" and self.l_enabled is False:
            if self.moving == False and self.shooting == False:
            	self.moving = True
                self.go = Clock.schedule_interval(self.go_right,1.0/60.0)
            else:
            	pass
                #print "You cant move right"

        if keycode[1] == "spacebar" and self.countdown_going_on == False:
            if self.shooting == False and self.moving == False:
                if self.game_over == False:
            	    self.moving = True
                    if self.sound == None:
                        self.sound = SoundLoader.load('shoot.wav')
                    if self.sound.status != 'stop':
                        self.sound.stop()
                    self.sound.play()
                    Clock.schedule_once(self.shoot,1.0/60.0)

    #if the key is just pressed and released then do the following...
    def _on_key_up(self, keyboard, keycode, *args):
        if self.moving == True:        # if movng is True,
            Clock.unschedule(self.go)  # stop the player movement
            self.moving = False        # make it false
        if self.go:                    # if any movement then stop it
        	Clock.unschedule(self.go)
            
        if self.l_enabled is True:     # if left_pressed is true 
            self.l_enabled = False     # then make it false
        if self.r_enabled is True:     # same as just above
            self.r_enabled = False
    
    # move the player to the right
    def go_right(self,dt):
        self.x += self.velocity[0]
        if self.x >= 255:
        	Clock.unschedule(self.go)
    
    # move plater to the left
    def go_left(self,dt):
        self.x -= self.velocity[0]
        if self.x <= -35:
        	Clock.unschedule(self.go)
    
    # make it shoot 
    def shoot(self,dt):
        self.bullet_move = Clock.schedule_interval(self.move_bullet,1.0/60.0)
    
    # make the bullet move
    def move_bullet(self,dt):
        self.image_2.y += self.bullet_speed[1]
        self.shooting = True
        self.check_collision()
    
    # check if it collides with enemy or boundary
    def check_collision(self):

        if self.enmy_1 in self.children:
            if self.image_2.collide_widget(self.enmy_1):  # if it collides with enemy_1
                self.points += 1    # increment the score
                self.score.text = str(self.points)  
                Clock.unschedule(self.bullet_move) # stop the bullet movement
                self.remove_widget(self.image_2)   # remove the bullet
                Clock.unschedule(self.enmy_1.run)  # stop the enemy movement
                #self.children.remove(self.enmy_1)
                self.remove_widget(self.enmy_1)    # remove the enemy
                self.shooting = False              # make the shooting false
                #self.enmy_1.reload()
                #print "reloaded....."
                self.add_bullet()      # add the bullet again

        if self.enmy_2 in self.children:
            if self.image_2.collide_widget(self.enmy_2):  # if it collides with enemy_1
                self.points += 1    # increment the score
                self.score.text = str(self.points)  
                Clock.unschedule(self.bullet_move) # stop the bullet movement
                self.remove_widget(self.image_2)   # remove the bullet
                Clock.unschedule(self.enmy_2.run)  # stop the enemy movement
                #self.children.remove(self.enmy_1)
                self.remove_widget(self.enmy_2)    # remove the enemy
                self.shooting = False              # make the shooting false
                #self.enmy_1.reload()
                #print "reloaded....."

                self.add_bullet()      # add the bullet again

        if self.enmy_3 in self.children:
            if self.image_2.collide_widget(self.enmy_3):  # if it collides with enemy_1
                self.points += 1    # increment the score
                self.score.text = str(self.points)  
                Clock.unschedule(self.bullet_move) # stop the bullet movement
                self.remove_widget(self.image_2)   # remove the bullet
                Clock.unschedule(self.enmy_3.run)  # stop the enemy movement
                #self.children.remove(self.enmy_1)
                self.remove_widget(self.enmy_3)    # remove the enemy
                self.shooting = False              # make the shooting false
                #self.enmy_1.reload()
                #print "reloaded....."

                self.add_bullet()      # add the bullet again

        if self.image_2.y >= 600:      # if bullet goes out of boundary
            #print "beyond 600"
            Clock.unschedule(self.bullet_move)   # stop the movement
            self.remove_widget(self.image_2)     # remove the bullet
            self.shooting = False                # make shooting false 
            self.add_bullet()                    # add bullet
    
    # function to add the bullet       
    def add_bullet(self):
        self.add_widget(self.image_2)   # add the bullet
        self.x += 0.1                   # update it
        if not self.enmy_1 in self.children:  # if there is no enemy_1
            self.add_widget(self.enmy_1)      # add it 
            self.enmy_1.x = randint(50,250)
            self.enmy_1.y = randint(550,600)
            self.enmy_1.run = Clock.schedule_interval(self.enmy_1.update,1.0/60.0)

        if not self.enmy_2 in self.children:  # if there is no enemy_1
            self.add_widget(self.enmy_2)      # add it 
            self.enmy_2.x = randint(50,250)
            self.enmy_2.y = randint(550,600)
            self.enmy_2.run = Clock.schedule_interval(self.enmy_2.update,1.0/60.0)

        if not self.enmy_3 in self.children:  # if there is no enemy_1
            self.add_widget(self.enmy_3)      # add it 
            self.enmy_3.x = randint(50,250)
            self.enmy_3.y = randint(550,600)
            self.enmy_3.run = Clock.schedule_interval(self.enmy_3.update,1.0/60.0)


    def stop(self):
        Background().stop()

# the enemy for the game              
class Enmy_1(Image):
    run = ObjectProperty(None)     # run reference holder
    image_load = ObjectProperty(None) # may be will be needed later

    # makes sure this is workingcorrectly
    def __init__(self,**kwargs):
        super(Enmy_1,self).__init__(**kwargs)
        self.source = "meteorSmall.png"        # sprite of enemy
        self.size = self.texture_size          # size it to its original
        self.x = 150                             # its default x pos
        self.y = 500                           # its default y pos

    def update(self,dt):                      #update the movement
        self.y -= 2
        if self.y <= 0:
            self.y = 500

# the enemy for the game              
class Enmy_2(Image):
    run = ObjectProperty(None)     # run reference holder
    image_load = ObjectProperty(None) # may be will be needed later

    # makes sure this is workingcorrectly
    def __init__(self,**kwargs):
        super(Enmy_2,self).__init__(**kwargs)
        self.source = "meteorSmall.png"        # sprite of enemy
        self.size = self.texture_size          # size it to its original
        self.x = 250                             # its default x pos
        self.y = 500                           # its default y pos

    def update(self,dt):                      #update the movement
        self.y -= 1
        if self.y <= 0:
            self.y = 500

# the enemy for the game              
class Enmy_3(Image):
    run = ObjectProperty(None)     # run reference holder
    image_load = ObjectProperty(None) # may be will be needed later

    # makes sure this is workingcorrectly
    def __init__(self,**kwargs):
        super(Enmy_3,self).__init__(**kwargs)
        self.source = "meteorSmall.png"        # sprite of enemy
        self.size = self.texture_size          # size it to its original
        self.x = 0                             # its default x pos
        self.y = 500                           # its default y pos

    def update(self,dt):                      #update the movement
        self.y -= 2
        if self.y <= 0:
            self.y = 500

#score class   
class Score(Label):
    pass

# Menu class
class Menu(Screen):
    score_points = ObjectProperty(None)   # score label

    def __init__(self,**kwargs):
        super(Menu,self).__init__(**kwargs)
        #self.app = App.get_running_app()
        self.score_ = JsonStore('score.json')
        self.real_points = self.score_.get('score')['score']
        self.score_points.text = str(self.real_points)

    #This happens after just entering the game screen
    def on_enter(self):
        self.score_ = JsonStore('score.json')
        self.real_points = self.score_.get('score')['score']
        self.score_points.text = str(self.real_points)
    
    # This happens when leaving the game screen
    # do some garbage collection
    def on_leave(self):
        self.score = None
        self.real_points = None


# Game entry point
class Game(Screen):
    backg = ObjectProperty(None)    # reference for background class
    bg = ObjectProperty(None)       # reference for background in kv file
    back = ObjectProperty(None)     # reference for back button in kv file
    
    # makes sure that this runs no matter what
    def __init__(self,**kwargs):
        super(Game,self).__init__(**kwargs)
    
    #This happens after just entering the game screen
    def on_enter(self):
        self.backg = Background()   # stores it in self.backg
        self.add_widget(self.backg) # show it to the screen
    
    # This happens when leaving the game screen
    def on_leave(self):
        self.remove_widget(self.backg)
        #print 'removed backg'

# The main menu screen,first display
class UI(ScreenManager):
    def __init__(self,**kwargs):
        super(UI,self).__init__(**kwargs)
        self.size_hint = None,None
        self.size = 300,600
        Window.size = self.size
        self.add_widget(Menu(name = 'Menu')) # Menu added
        self.add_widget(Game(name = 'Game')) # game added
        #print self.app.menu

# Starts the game       
class MainApp(App):
	#when pause dont quite
    def on_pause(self):
        return True
    
    #returns the main screen
    def build(self):
        return UI()
        
if __name__ == '__main__':
    MainApp().run()