# from random import choice, randint

import pygame
import random

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# центр поля
GRID_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Настройки яблока
APPLE_COLOR = (255, 0, 0)
APPLE_COUNT = 3

# Настройки яда
POISON_COLOR = (0, 0, 255)
POISON_COUNT = 2

# Настройки камня
STONE_COLOR = (255, 255, 255)
STONE_COUNT = 5

# Скорость движения змейки:
SPEED = 16

# Константа для всех ячеек
ALL_CELLS = {(x * GRID_SIZE, y * GRID_SIZE) for x in range(GRID_WIDTH) for y in
             range(GRID_HEIGHT)}

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс объекта игры"""

    def __init__(self, position=GRID_CENTER):
        self.position = position
        self.body_color = None

    @staticmethod
    def draw_cell(position, color, border_color=BORDER_COLOR):
        """Метод для отрисовки одной ячейки"""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, border_color, rect, 1)

    def draw(self):
        """Метод для отрисовки объекта"""
        pass

    def randomize_position(self, occupied_cells):
        """Метод для установки случайной позиции объекта"""
        available_cells = ALL_CELLS - occupied_cells
        self.position = random.choice(tuple(available_cells))


class Apple(GameObject):
    """Класс объекта яблоко"""

    def __init__(self, ):
        super().__init__()
        self.body_color = APPLE_COLOR

    def draw(self):
        """Рисует яблоко на игровой поверхности"""
        GameObject.draw_cell(self.position, self.body_color)


class Poison(GameObject):
    """Класс объекта яд"""

    def __init__(self, ):
        super().__init__()
        self.body_color = POISON_COLOR

    def randomize_position(self, occupied_cells):
        """Метод для установки случайной позиции яда"""
        available_cells = ALL_CELLS - occupied_cells
        self.position = random.choice(tuple(available_cells))

    def draw(self):
        """Рисует яд на игровой поверхности"""
        GameObject.draw_cell(self.position, self.body_color)


class Stone(GameObject):
    """Класс объекта камень"""

    def __init__(self, ):
        super().__init__()
        self.body_color = STONE_COLOR

    def draw(self):
        """Рисует камень на игровой поверхности"""
        GameObject.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Класс объекта змейка"""

    def __init__(self):
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.positions = [self.position]
        self.last = None

    def draw(self):
        """Рисует змейку на игровой поверхности"""
        for position in self.positions[:-1]:
            GameObject.draw_cell(position, self.body_color)

        # Отрисовка головы змейки
        GameObject.draw_cell(self.get_head_position(), self.body_color)

        # Затирание последнего сегмента
        if self.last:
            GameObject.draw_cell(self.last,
                                 BOARD_BACKGROUND_COLOR,
                                 BOARD_BACKGROUND_COLOR)

    def update_direction(self):
        """Обновляет направление движения змейки"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает текущую позицию головы змейки"""
        return self.positions[0]

    def move(self):
        """Обновление позиции змейки"""
        head_x, head_y = self.get_head_position()
        new_head_x = (head_x + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        new_head_y = (head_y + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT

        new_head = (
            new_head_x,
            new_head_y,
        )

        if new_head in self.positions[2:]:
            self.reset()
            return

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

        else:
            self.last = None

    def reset(self):
        """Сброс змейки в начальное значение"""
        self.length = 1
        self.position = GRID_CENTER
        self.positions = [self.position]
        self.direction = random.choice((LEFT, RIGHT, UP, DOWN))
        self.next_direction = None


def get_random_free_cell(occupied_cells):
    """Возвращает случайную свободную ячейку"""
    free_cells = ALL_CELLS - set(occupied_cells)
    return random.choice(tuple(free_cells))


def check_collapse(snake, scraps, stones, apples):
    """Функция для проверки столкновения головы змейки с другими объектами"""
    occupied_cells = (set(snake.positions)
                      | {scrap.position for scrap in scraps}
                      | {stone.position for stone in stones}
                      | {apple.position for apple in apples})

    # Проверка столкновения с яблоком
    for apple in apples:
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied_cells)
            break

    # Проверка столкновения с мусором
    for scrap in scraps:
        if snake.get_head_position() == scrap.position:
            snake.length -= 1
            if snake.length < 1:
                snake.reset()
            else:
                snake.positions.pop()
            scrap.randomize_position(occupied_cells)
            break

    # Проверка столкновения с камнем
    for stone in stones:
        if snake.get_head_position() == stone.position:
            snake.reset()
            stone.randomize_position(occupied_cells)
            break


def handle_keys(game_object):
    """Функция обработки действий пользователя"""
    # Словарь для обработки новых направлений в зависимости от нажатой клавиши
    direction_dict = {
        (pygame.K_UP, LEFT): UP,
        (pygame.K_UP, RIGHT): UP,
        (pygame.K_DOWN, LEFT): DOWN,
        (pygame.K_DOWN, RIGHT): DOWN,
        (pygame.K_LEFT, UP): LEFT,
        (pygame.K_LEFT, DOWN): LEFT,
        (pygame.K_RIGHT, UP): RIGHT,
        (pygame.K_RIGHT, DOWN): RIGHT
    }

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            # Если нажата клавиша Esc, выходим из игры
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

            new_direction = direction_dict.get(
                (event.key, game_object.direction), game_object.direction)
            if new_direction != game_object.direction:
                game_object.next_direction = new_direction


def get_record():
    """Функция получения рекорда"""
    try:
        with open("record.txt", 'r') as file:
            data = file.read()
        score = int(data)
    except (FileNotFoundError,
            ValueError):
        score = 0
    return score


def update_record(snake_length, record=0):
    """Функция обновления рекорда"""
    if snake_length > record:
        with open("record.txt", 'w') as file:
            file.write(str(snake_length))


def generate_objects(objects, occupied_cells):
    """Функция для генерации объектов"""
    for obj in objects:
        for ex in obj:
            ex.randomize_position(occupied_cells)
            occupied_cells.add(ex.position)


def draw_objects(objects):
    """Функция для отрисовки объектов"""
    for obj in objects:
        for ex in obj:
            ex.draw()


def main():
    """Главная функция"""
    pygame.init()

    # Создаём объекты
    snake = Snake()
    apples = [Apple() for _ in range(APPLE_COUNT)]
    poisons = [Poison() for _ in range(POISON_COUNT)]
    stones = [Stone() for _ in range(STONE_COUNT)]

    # Сгенерируем начальные позиции учитывая друг друга поочерёдно
    objects = [apples, poisons, stones]
    occupied_cells = set(snake.position)
    generate_objects(objects, occupied_cells)

    while True:
        record = get_record()
        clock.tick(SPEED)
        handle_keys(snake)

        snake.update_direction()
        snake.move()
        check_collapse(snake, poisons, stones, apples)

        # отображение счетчика длины и рекорда
        pygame.display.set_caption(f"ВАШИ ОЧКИ: {snake.length} || "
                                   f"РЕКОРД: {record}")
        update_record(snake.length, record)

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        draw_objects(objects)
        pygame.display.update()


if __name__ == '__main__':
    main()
