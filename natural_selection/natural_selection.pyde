class Cell():
    def __init__(self, x=None, y=None, v=5, sensing_dist=50):
        if x is None and y is None:
            r = random(0, 1)
                
            if r < 0.25: # top
                self.x = random(50, W - 50)
                self.y = random(50, 100)
            elif r < 0.5: # bottom
                self.x = random(50, W - 50)
                self.y = random(H - 100, H - 50)
            elif r < 0.75: # right
                self.x = random(W - 100, W - 50)
                self.y = random(50, H - 50)
            else: # left
                self.x = random(50, 100)
                self.y = random(50, H - 50)
        else:
            self.x = x
            self.y = y

        # gene
        self.v = v
        self.sensing_dist = sensing_dist
        
        self.status = 'stopped' # (stopped, moving, staying)
        self.staying_time = 0
        self.n_foods = 0
        
    def move_to(self, dst_x, dst_y):
        dist = sqrt((dst_x - self.x) ** 2 + (dst_y - self.y) ** 2)
        
        if dist < self.v:
            self.x = dst_x
            self.y = dst_y
        else:
            dist_x = (dst_x - self.x) * self.v
            dist_y = (dst_y - self.y) * self.v
            
            self.x += dist_x / dist
            self.y += dist_y / dist
                
    def move(self):
        if self.status == 'moving':
            dist = sqrt((self.dst_x - self.x) ** 2 + (self.dst_y - self.y) ** 2)
        
            if dist < self.v:
                self.x = self.dst_x
                self.y = self.dst_y
                
                self.status = 'stopped'
            else:
                dist_x = (self.dst_x - self.x) * self.v
                dist_y = (self.dst_y - self.y) * self.v
                
                self.x += dist_x / dist
                self.y += dist_y / dist
                
    def decide_status(self):
        if self.status == 'stopped':
            r = random(0, 1)
            if r < 0.9:
                self.status = 'moving'
                self.dst_x = random(50, W - 50)
                self.dst_y = random(50, H - 50)
            else:
                self.status = 'staying'
                self.staying_time = millis() + int(random(500, 1500))
                
        elif self.status == 'staying':
            if millis() > self.staying_time:
                self.status = 'stopped'
                
    def check_collision(self):
        for food in foods:
            if food.status == 'eaten':
                continue

            dist = sqrt((food.x - self.x) ** 2 + (food.y - self.y) ** 2)
            
            if dist <= self.sensing_dist:
                self.status = 'moving'
                self.dst_x = food.x
                self.dst_y = food.y
            
            if dist < 30:
                food.status = 'eaten'
                self.n_foods += 1
                manager.alive_foods -= 1
                break
            
    def evolve(self):
        if random(0, 1) < 0.5:
            if random(0, 1) < 0.5:
                self.v += 1
            else:
                self.sensing_dist += 10
        else:
            if random(0, 1) < 0.5:
                self.v -= 1
            else:
                self.sensing_dist -= 10 
        
    def display(self):
        stroke(255)
        ellipseMode(CENTER)
        noFill()
        ellipse(self.x, self.y, self.sensing_dist * 2, self.sensing_dist * 2)

        noStroke()
        ellipseMode(CENTER)
        fill(255, 255, 0)
        ellipse(self.x, self.y, 50, 50)
        
        fill(0)
        textSize(20)
        textAlign(CENTER)
        text('%d' % (self.v), self.x, self.y)
        
class Food():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.status = 'alive'
        
    def display(self):
        if self.status != 'eaten':
            shapeMode(CENTER)
            fill(0, 240, 100)
            triangle(self.x, self.y - 10, self.x - 10, self.y + 10, self.x + 10, self.y + 10)
            
class Manager():
    def __init__(self):
        self.alive_cells = N_CELLS
        self.alive_foods = N_FOODS
        self.generation = 0
        self.avg_speed = 5
        self.avg_sensing_dist = 50
    
    def reset(self):
        global foods, cells, N_FOODS
        
        self.generation += 1
        N_FOODS -= 1
        self.alive_foods = N_FOODS

        foods = []
        
        for i in range(N_FOODS):
            foods.append(Food(x=random(200, W - 200), y=random(200, H - 200)))
        
        if manager.generation > 1:
            new_cells = []

            for i, cell in enumerate(reversed(cells)):
                if cell.n_foods == 0: # dead
                    del cells[self.alive_cells - i - 1]
                    continue

                if cell.n_foods >= 2: # replicate
                    new_cells.append(Cell(
                        v=cell.v,
                        sensing_dist=cell.sensing_dist
                    ))

                if cell.n_foods >= 1:
                    cell.evolve()
                    
                    
                cell.n_foods = 0
                
                r = random(0, 1)
                
                if r < 0.25:
                    cell.x = random(50, W - 50)
                    cell.y = random(50, 100)
                elif r < 0.5:
                    cell.x = random(50, W - 50)
                    cell.y = random(H - 100, H - 50)
                elif r < 0.75:
                    cell.x = random(W - 100, W - 50)
                    cell.y = random(50, H - 50)
                else:
                    cell.x = random(50, 100)
                    cell.y = random(50, H - 50)
                    
            cells.extend(new_cells)

            self.alive_cells = len(cells)
        else:
            for i in range(N_CELLS):
                cells.append(Cell())
                
        self.compute_avgs()
                
    def compute_avgs(self):
        sum_speed = 0
        sum_sensing_dist = 0

        for cell in cells:
            sum_speed += cell.v
            sum_sensing_dist += cell.sensing_dist
        
        if len(cells):
            self.avg_speed = float(sum_speed) / float(len(cells))
            self.avg_sensing_dist = float(sum_sensing_dist) / float(len(cells))

# main
N_FOODS = 20
N_CELLS = 20
W, H = 1920, 1080

manager = Manager()

foods, cells = [], []
manager.reset()

def setup():
    frameRate(60)
    size(W, H)
    
def draw():
    background(127)
    
    fill(255)
    textAlign(LEFT)
    textSize(24)
    text('Generation %d' % manager.generation, 20, 30)
    text('Cells %d' % manager.alive_cells, 20, 60)
    text('Avg. Speed %.2f' % manager.avg_speed, 20, 90)
    text('Avg. Sensing Dist %.2f' % manager.avg_sensing_dist, 20, 120)

    if manager.alive_foods == 0:
        manager.reset()

    for food in foods:
        food.display()
        
    for cell in cells:
        cell.decide_status()
        cell.move()
        cell.check_collision()
        cell.display()
