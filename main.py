"""GIANT Language REPL: Interactive programming environment."""

import sys
from syntax_loader import SyntaxLoader
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter


def run_file(filename: str) -> None:
    """Execute a .naija file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        syntax_loader = SyntaxLoader()
        lexer = Lexer(code, syntax_loader)
        parser = Parser(syntax_loader)
        ast = parser.parse(lexer.tokens)
        interpreter = Interpreter()
        interpreter.interpret(ast)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def run_repl() -> None:
    """Run interactive Read-Eval-Print Loop for GIANT Language."""
    syntax_loader = SyntaxLoader()
    parser = Parser(syntax_loader)
    interpreter = Interpreter()

    print("Welcome to Naija Pidgin Programming Language REPL! Type 'stop' to quit.")

    while True:
        try:
            line = input(">>> ").strip()
            if line.lower() == "stop":
                break
            if not line:  # Skip empty lines
                continue
            
            tokens = Lexer(line, syntax_loader).tokens
            ast = parser.parse(tokens)
            interpreter.interpret(ast)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        run_repl()
