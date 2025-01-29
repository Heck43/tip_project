# Архитектура игры "Морской бой"

## Диаграмма классов

```mermaid
classDiagram
    class Game {
        -player1: Player
        -player2: Player
        -current_state: GameState
        +handle_events()
        +update()
        +draw()
        +switch_turn()
        +check_game_over()
    }
    
    class Player {
        -board: Board
        -ships: List[Ship]
        -is_first_player: bool
        +initialize_ships()
        +handle_mouse_down()
        +handle_mouse_up()
        +handle_mouse_motion()
        +place_ship()
        +shoot()
    }
    
    class Board {
        -cells: List[List[Cell]]
        -size: int
        +place_ship()
        +can_place_ship()
        +shoot()
        +mark_around_destroyed_ship()
        +is_all_ships_placed()
    }
    
    class Ship {
        -length: int
        -x: int
        -y: int
        -horizontal: bool
        -hits: int
        -board: Board
        +draw()
        +update_position()
        +rotate()
        +is_destroyed()
        +get_all_cells()
    }
    
    class Cell {
        -x: int
        -y: int
        -state: CellState
        -ship: Ship
        +draw()
        +set_state()
        +has_ship()
        +was_shot()
    }
    
    Game "1" *-- "2" Player
    Player "1" *-- "1" Board
    Player "1" *-- "*" Ship
    Board "1" *-- "*" Cell
    Cell "1" o-- "0..1" Ship
```

## Диаграмма состояний игры

```mermaid
stateDiagram-v2
    [*] --> PLACEMENT
    PLACEMENT --> PLAYER1_TURN: Все корабли размещены
    PLAYER1_TURN --> PLAYER2_TURN: Промах
    PLAYER1_TURN --> PLAYER1_TURN: Попадание
    PLAYER2_TURN --> PLAYER1_TURN: Промах
    PLAYER2_TURN --> PLAYER2_TURN: Попадание
    PLAYER1_TURN --> GAME_OVER: Все корабли уничтожены
    PLAYER2_TURN --> GAME_OVER: Все корабли уничтожены
    GAME_OVER --> [*]
```

## Диаграмма последовательности размещения корабля

```mermaid
sequenceDiagram
    participant U as User
    participant G as Game
    participant P as Player
    participant B as Board
    participant S as Ship
    
    U->>G: Mouse Down
    G->>P: handle_mouse_down()
    P->>S: start_dragging()
    
    U->>G: Mouse Motion
    G->>P: handle_mouse_motion()
    P->>S: update_position()
    P->>B: can_place_ship()
    
    U->>G: Mouse Up
    G->>P: handle_mouse_up()
    P->>B: can_place_ship()
    alt valid position
        P->>B: place_ship()
        B->>S: set_placed()
    else invalid position
        P->>S: reset_position()
    end
```

## Диаграмма последовательности выстрела

```mermaid
sequenceDiagram
    participant U as User
    participant G as Game
    participant P as Player
    participant B as Board
    participant C as Cell
    participant S as Ship
    
    U->>G: Click Cell
    G->>P: shoot(x, y)
    P->>B: shoot(x, y)
    B->>C: get_state()
    
    alt has ship
        C->>S: hit()
        S->>S: check_destroyed()
        alt ship destroyed
            B->>B: mark_around_destroyed_ship()
        end
        G->>P: keep_turn()
    else no ship
        C->>C: set_state(MISS)
        G->>G: switch_turn()
    end
```

## Структура данных

```mermaid
graph TD
    Game --> |contains| Player1
    Game --> |contains| Player2
    Player1 --> |has| Board1[Board]
    Player2 --> |has| Board2[Board]
    Board1 --> |contains| Cells1[Cells Matrix]
    Board2 --> |contains| Cells2[Cells Matrix]
    Player1 --> |has| Ships1[Ships List]
    Player2 --> |has| Ships2[Ships List]
    Cells1 --> |reference| Ships1
    Cells2 --> |reference| Ships2
```

## Схема взаимодействия компонентов

```mermaid
flowchart TD
    Game[Game Controller] --> |manages| GameState[Game State]
    Game --> |controls| Player1[Player 1]
    Game --> |controls| Player2[Player 2]
    
    Player1 --> |owns| Board1[Board 1]
    Player2 --> |owns| Board2[Board 2]
    
    Board1 --> |contains| Ships1[Ships]
    Board2 --> |contains| Ships2[Ships]
    
    Board1 --> |made of| Cells1[Cells]
    Board2 --> |made of| Cells2[Cells]
    
    Ships1 --> |occupies| Cells1
    Ships2 --> |occupies| Cells2
    
    Game --> |handles| Events[User Events]
    Events --> |triggers| Actions[Game Actions]
    
    Actions --> |updates| GameState
    GameState --> |affects| Rendering[Screen Rendering]
```
