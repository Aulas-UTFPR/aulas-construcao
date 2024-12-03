class Calculator:
    """A simple calculator class."""

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b


class CalculatorApp:
    """The interface for using the Calculator."""

    def __init__(self):
        self.calculator = Calculator()

    def display_menu(self):
        """Displays the main menu."""
        print("\nPython Calculator")
        print("1. Addition")
        print("2. Subtraction")
        print("3. Multiplication")
        print("4. Division")
        print("5. Exit")

    def get_user_input(self):
        """Gets and validates user input for operation selection."""
        while True:
            try:
                choice = int(input("Enter your choice (1-5): "))
                if 1 <= choice <= 5:
                    return choice
                print("Invalid choice. Please enter a number between 1 and 5.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def get_numbers(self):
        """Gets two numbers from the user."""
        while True:
            try:
                num1 = float(input("Enter the first number: "))
                num2 = float(input("Enter the second number: "))
                return num1, num2
            except ValueError:
                print("Invalid input. Please enter numeric values.")

    def execute_choice(self, choice):
        """Executes the user's selected operation."""
        if choice == 5:
            print("Exiting the calculator. Goodbye!")
            return False

        num1, num2 = self.get_numbers()

        try:
            if choice == 1:
                result = self.calculator.add(num1, num2)
                operation = "addition"
            elif choice == 2:
                result = self.calculator.subtract(num1, num2)
                operation = "subtraction"
            elif choice == 3:
                result = self.calculator.multiply(num1, num2)
                operation = "multiplication"
            elif choice == 4:
                result = self.calculator.divide(num1, num2)
                operation = "division"

            print(f"The result of {operation} is: {result}")
        except ValueError as e:
            print(e)
        return True

    def run(self):
        """Runs the calculator application."""
        while True:
            self.display_menu()
            choice = self.get_user_input()
            if not self.execute_choice(choice):
                break


if __name__ == "__main__":
    app = CalculatorApp()
    app.run()
