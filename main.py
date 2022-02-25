import pygame
import os
import random
from pygame import mixer
pygame.init()
mixer.init()
pygame.font.init()

WIDTH,HEIGHT = 750,750
WINDOW= pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Shooter")

RED_SPACE_SHIP= pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
GREEN_SPACE_SHIP= pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
SPACE_SHIP= pygame.image.load(os.path.join("assets","pixel_ship.png"))

RED_LASER=pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
GREEN_LASER=pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
YELLOW_LASER=pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))

PLAYER_SHOOT_SOUND=mixer.Sound(os.path.join("assets","player_shoot.mp3"))
PLAYER_SHOOT_SOUND.set_volume(0.1)

BG= pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")),(WIDTH,HEIGHT))

class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img =img
        self.mask=pygame.mask.from_surface(self.img)
        
    def draw(self,window):
        window.blit(self.img,(self.x,self.y))
        
    def move(self,vel):
        self.y+=vel
        
    def off_screen(self,height):
        return not(self.y<=height and self.y>=0)
        
    def collision(self,obj):
        return collide(self,obj)
        
class Ship():
    COOLDOWN=30
    def __init__(self,x,y,health=100):
        self.x=x
        self.y=y
        self.health=health
        self.ship_img=None
        self.laser_img=None
        self.lasers=[]
        self.cooldown_counter=0
    
    def draw(self,window):
        window.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)
        
    def move_lasers(self,vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health-=15
                self.lasers.remove(laser)
    
    def cooldown(self):
        if self.cooldown_counter>=self.COOLDOWN:
            self.cooldown_counter=0
        elif self.cooldown_counter>0:
            self.cooldown_counter+=1
    
    def shoot(self):
        if self.cooldown_counter==0:
            laser=Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter=1
    
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
    
class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.ship_img=SPACE_SHIP
        self.laser_img=YELLOW_LASER
        self.mask=pygame.mask.from_surface(self.ship_img)
        self.max_health=health
        
    def move_lasers(self,vel,objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        main.score+=20
                        self.check_high_score()
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            
    def check_high_score(self):
        if main.score > int(main.high_score):
            main.high_score = main.score
            main.temp=main_menu.user_text+" "+str(main.score)
            high_score_file = open("high_score.txt", "w+")
            high_score_file.write(main.temp)
            high_score_file.close()
    
    def draw(self,window):
        super().draw(window)
        self.healthbar(window)
    
    def healthbar(self,window):
        pygame.draw.rect(window,(255,0,0),(self.x,self.y+self.ship_img.get_height(),self.ship_img.get_width(),10))
        pygame.draw.rect(window,(0,255,0),(self.x,self.y+self.ship_img.get_height(),self.ship_img.get_width()*(self.health/self.max_health),10))

class Enemy(Ship):
    COLOR_MAP={
        "red":(RED_SPACE_SHIP,RED_LASER),
        "green":(GREEN_SPACE_SHIP,GREEN_LASER)
    }
    
    def __init__(self,x,y,color,health=100):
        super().__init__(x,y,health)
        self.ship_img,self.laser_img=self.COLOR_MAP[color]
        self.mask=pygame.mask.from_surface(self.ship_img)
    
    def move(self,vel):
        self.y+=vel
    
    def shoot(self):
        if self.cooldown_counter==0:
            laser=Laser(self.x-15,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter=1   

def collide(obj1,obj2):
    offset_x=obj2.x-obj1.x
    offset_y=obj2.y-obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None
           
def main():
    run=True
    FPS=60
    level=0
    lives=5
    main.score=0
    high_score_file = open("high_score.txt", "r")
    main.temp = high_score_file.read()   
    main.high_score=main.temp.split(" ")[1:][0]
    main_font=pygame.font.SysFont("comicsans",30)
    lost_font=pygame.font.SysFont("comicsans",60)
    
    enemies=[]
    wave_length=4
    enemy_velocity=2
    laser_velocity_enemy=4
    laser_velocity_player=10
    player_velocity=8
    
    player=Player(375,630)
    
    clock=pygame.time.Clock()
    
    lost=False
    lost_count=0
        
    def redraw_window():
        WINDOW.blit(BG,(0,0))
        
        level_label= main_font.render(f" Level: {level}",1,(255,255,255))
        lives_label= main_font.render(f"Lives: {lives}",1,(255,255,255))  
        score_label=main_font.render(f"Score: {main.score}",1,(255,255,255)) 
        high_score_label = main_font.render(f"High Score: {main.temp}",1,(255,255,255))    
        WINDOW.blit(level_label,(5,5))
        WINDOW.blit(lives_label,(WIDTH-lives_label.get_width()-10,5))
        WINDOW.blit(score_label,(5,40))
        WINDOW.blit(high_score_label,(WIDTH-high_score_label.get_width()-5,40))
        
        for enemy in enemies:
            enemy.draw(WINDOW)
            
        player.draw(WINDOW)
        
        if lost:
            lost_label=lost_font.render("You Lost!!",1,(255,255,255))
            WINDOW.blit(lost_label,(WIDTH/2-lost_label.get_width()/2,350))
                  
        pygame.display.update()
    
    while run:
        clock.tick(FPS)
        redraw_window()
        
        if lives<=0 or player.health<=0:
            lost=True
            lost_count+=1
        
        if lost:
            if lost_count>FPS*3:
                run=False
            else:
                continue
        
        if len(enemies) == 0:
            level+=1
            wave_length+=3
            for i in range(wave_length):
                enemy=Enemy(random.randrange(50,WIDTH-100),random.randrange(-1500,-100),random.choice(["red","green"]))
                enemies.append(enemy)
                
       
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
        keys= pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x-player_velocity>0:
            player.x-= player_velocity
        if keys[pygame.K_d] and player.x+player_velocity+player.get_width()<WIDTH:
            player.x+= player_velocity
        if keys[pygame.K_s] and player.y+player_velocity+player.get_height()+15<HEIGHT:
            player.y+= player_velocity
        if keys[pygame.K_w] and player.y-player_velocity>0:
            player.y-= player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()
            PLAYER_SHOOT_SOUND.play()
        
        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity_enemy,player)
            if random.randrange(0,2*60)==1:
                enemy.shoot()
            
            if collide(enemy,player):
                player.health -= 15
                enemies.remove(enemy) 
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives-=1
                enemies.remove(enemy)
               
        player.move_lasers(-laser_velocity_player,enemies)    

def main_menu():
    main_menu.user_text=''
    input_rect=pygame.Rect(300,350,140,32)
    user_text_font=pygame.font.SysFont("comicsans",20)
    title_font=pygame.font.SysFont("comicsans",30)
    active=False
    run=True
    
    while run:
        WINDOW.blit(BG,(0,0))
        pygame.draw.rect(WINDOW,(255,0,0),input_rect,2)
        title_label=title_font.render('Enter your name -',1,(255,255,255))
        WINDOW.blit(title_label,(WIDTH/2-title_label.get_width()/2,300))
        user_text_label=user_text_font.render(main_menu.user_text,1,(255,255,255))  
        WINDOW.blit(user_text_label,(input_rect.x+10,input_rect.y))
        
        input_rect.w=max(140,user_text_label.get_width()+20)
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
            if event.type==pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active=True
                else:
                    active=False
            if event.type == pygame.KEYDOWN:
                if active==True:
                    if event.key==pygame.K_BACKSPACE:
                        main_menu.user_text=main_menu.user_text[:-1]
                    elif event.key==pygame.K_RETURN:
                        if main_menu.user_text !='':
                            main()
                            main_menu.user_text=''
                    else:
                        main_menu.user_text+=event.unicode
                        
    pygame.quit()
               
main_menu()
            
