import argparse
import math
import turtle


def koch_curve(t: turtle.Turtle, order: int, length: float) -> None:
    """Малює одну ламану Коха рекурсивно."""
    if order == 0:
        t.forward(length)
    else:
        for angle in (60, -120, 60, 0):
            koch_curve(t, order - 1, length / 3)
            t.left(angle)


def draw_snowflake(order: int, size: float = 300) -> None:
    """Малює сніжинку Коха (3 сторони)."""
    window = turtle.Screen()
    window.title(f"Сніжинка Коха — рівень {order}")
    window.bgcolor("white")

    t = turtle.Turtle(visible=False)
    t.speed(0)
    turtle.tracer(False)  # швидке малювання без анімації

    # Спробуємо відцентрувати фігуру вікні
    h = size * math.sqrt(3) / 2
    t.penup()
    t.goto(-size / 2, h / 2)  # легке центрування
    #t.goto(-size / 2, 0)
    t.setheading(0)
    t.pendown()

    for _ in range(3):
        koch_curve(t, order, size)
        t.right(120)

    
    turtle.update()
    turtle.exitonclick()  # закрити кліком


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Візуалізація сніжинки Коха з рекурсією."
    )
    parser.add_argument(
        "-o", "--order", type=int, help="Рівень рекурсії (ціле число ≥ 0)"
    )
    parser.add_argument(
        "-s", "--size", type=float, default=300.0, help="Довжина сторони базового трикутника (пікселі)"
    )
    args = parser.parse_args()

    # Якщо аргументи не передано — запитаємо користувача
    if args.order is None:
        while True:
            try:
                val = input("Вкажіть рівень рекурсії (ціле число ≥ 0): ").strip()
                args.order = int(val)
                if args.order < 0:
                    raise ValueError
                break
            except ValueError:
                print("Будь ласка, введіть коректне ціле число ≥ 0.")
    return args


def main() -> None:
    args = parse_args()

    # обмежимо «занадто великі» рівні, щоб не зависнути
    if args.order > 7:
        print("Попередження: рівень > 7 може малюватися дуже довго. Зменшу до 7.")
        args.order = 7

    draw_snowflake(order=args.order, size=args.size)
   

if __name__ == "__main__":
    main()