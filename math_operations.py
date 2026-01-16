"""Math Operations: Mathematical operations normalizer and evaluator.

Supports equivalent operations in Pidgin, English, and mixed usage.
"""


class MathOperations:
    """
    Normalizer and evaluator for mathematical expressions.
    Supports equivalent operations in Pidgin, English, and mixed usage.
    """

    # OPERATOR NORMALIZATION MAP
    # Maps all English and Pidgin synonyms to canonical internal operators
    OPERATOR_MAP = {
        # ADDITION
        'plus': 'plus',
        'added to': 'plus',
        'add': 'plus',
        'sum of': 'plus',
        'and': 'plus',  # Pidgin: "2 and 3" can mean addition

        # SUBTRACTION
        'minus': 'minus',
        'subtract': 'minus',
        'subtracted from': 'minus',
        'difference between': 'minus',
        'take away': 'minus',

        # MULTIPLICATION
        'times': 'times',
        'multiplied by': 'times',
        'multiply': 'times',
        'product of': 'times',
        'of': 'times',  # As in "half of x" → "0.5 times x"

        # DIVISION
        'divided by': 'divided_by',
        'divided_by': 'divided_by',  # Canonical form as self-reference
        'over': 'divided_by',
        'quotient of': 'divided_by',
        'share': 'divided_by',  # Pidgin: to share/distribute

        # POWER
        'raised to': 'power',
        'power': 'power',
        'to the power of': 'power',
        'to power': 'power',
        'exponent': 'power',

        # SQUARE ROOT
        'square root of': 'sqrt',
        'square root': 'sqrt',
        'sqrt': 'sqrt',  # Canonical form too

        # CUBE ROOT
        'cube root of': 'cbrt',
        'cube root': 'cbrt',
        'third root of': 'cbrt',
        'cbrt': 'cbrt',  # Canonical form too


        # OTHER ROOTS (generalized)
        'root': 'nroot',
    }

    # STROUD-STYLE FORMAL DECLARATIONS
    FORMAL_KEYWORDS = {
        'let': 'let',
        'be equal to': 'eq',
        'be': 'be',
        'is': 'is',
        'equals': 'eq',
    }

    @staticmethod
    def normalize_operator(operator_phrase: str) -> tuple[str, bool]:
        """
        Normalize any English or Pidgin operator phrase to canonical internal form.
        
        Args:
            operator_phrase: Raw operator phrase (e.g., "added to", "times", "divided by")
            
        Returns:
            Tuple of (canonical_operator, is_valid)
            
        Examples:
            "added to" → ("plus", True)
            "multiplied by" → ("times", True)
            "square root of" → ("sqrt", True)
            "invalid_op" → ("", False)
        """
        normalized = operator_phrase.strip().lower()
        canonical = MathOperations.OPERATOR_MAP.get(normalized)
        
        if canonical:
            return (canonical, True)
        return ("", False)

    @staticmethod
    def evaluate_operation(operand1: float | int, operator: str, 
                          operand2: float | int) -> tuple[float | int | None, str | None]:
        """
        Evaluate a binary mathematical operation.
        
        Args:
            operand1: First operand
            operator: Operator phrase (will be normalized internally)
            operand2: Second operand
            
        Returns:
            Tuple of (result, error_message)
            Returns (result, None) on success
            Returns (None, error_message) on failure
        """
        try:
            operand1 = float(operand1)
            operand2 = float(operand2)
        except (TypeError, ValueError):
            return (None, f"Wahala! Numbers must be proper numbers, not '{operand1}' and '{operand2}'")

        # Normalize the operator first
        canonical_op, is_valid = MathOperations.normalize_operator(operator)
        if not is_valid:
            return (None, f"Wahala! I no know dis operator: {operator}")

        if canonical_op == 'plus':
            return (operand1 + operand2, None)
        elif canonical_op == 'minus':
            return (operand1 - operand2, None)
        elif canonical_op == 'times':
            return (operand1 * operand2, None)
        elif canonical_op == 'divided_by':
            if operand2 == 0:
                return (None, "Wahala! Person no dey divide by zero, dat one go break things!")
            return (operand1 / operand2, None)
        elif canonical_op == 'power':
            try:
                result = operand1 ** operand2
                return (result, None)
            except OverflowError:
                return (None, "Wahala! Dat power too big, e no fit compute am!")
        else:
            return (None, f"Wahala! I no know dis operator: {canonical_op}")


    @staticmethod
    def evaluate_unary_operation(operand: float | int, 
                                 operator: str) -> tuple[float | int | None, str | None]:
        """
        Evaluate a unary mathematical operation (powers, roots).
        
        Args:
            operand: The value to operate on
            operator: Operator phrase (will be normalized internally)
            
        Returns:
            Tuple of (result, error_message)
        """
        try:
            operand = float(operand)
        except (TypeError, ValueError):
            return (None, f"Wahala! '{operand}' no be proper number!")

        # Normalize the operator first
        canonical_op, is_valid = MathOperations.normalize_operator(operator)
        if not is_valid:
            return (None, f"Wahala! I no know dis operator: {operator}")

        if canonical_op == 'sqrt':
            if operand < 0:
                return (None, "Wahala! No negative numbers for square root, abeg!")
            return (operand ** 0.5, None)
        elif canonical_op == 'cbrt':
            # Cube root works for negative numbers
            if operand < 0:
                result = -(-operand) ** (1/3)
            else:
                result = operand ** (1/3)
            return (result, None)
        else:
            return (None, f"Wahala! I no know dis operator: {canonical_op}")


    @staticmethod
    def is_formal_declaration(keyword: str) -> tuple[bool, str]:
        """
        Check if a keyword is a formal mathematical declaration.
        
        Checks for keywords like 'let', 'be equal to', etc.
        
        Args:
            keyword: The keyword to check
            
        Returns:
            Tuple of (is_formal, normalized_keyword)
        """
        normalized = keyword.strip().lower()
        if normalized in MathOperations.FORMAL_KEYWORDS:
            return (True, MathOperations.FORMAL_KEYWORDS[normalized])
        return (False, "")

    @staticmethod
    def get_all_operator_synonyms(canonical_op: str) -> list[str]:
        """
        Get all synonyms for a canonical operator.
        
        Useful for documentation purposes.
        
        Args:
            canonical_op: The canonical operator (plus, minus, times, etc.)
            
        Returns:
            List of all synonyms for that operator
        """
        return [k for k, v in MathOperations.OPERATOR_MAP.items() if v == canonical_op]

    @staticmethod
    def explain_operator(operator_phrase: str) -> str:
        """
        Explain what an operator does in Stroud's mathematical language.
        
        Args:
            operator_phrase: The operator to explain
            
        Returns:
            Human-readable explanation of the operator
        """
        canonical, is_valid = MathOperations.normalize_operator(operator_phrase)
        
        if not is_valid:
            return f"I no know '{operator_phrase}', abeg try 'help operations'"
        
        explanations = {
            'plus': 'Addition: combining two quantities together',
            'minus': 'Subtraction: finding the difference between two quantities',
            'times': 'Multiplication: repeated addition of a quantity',
            'divided_by': 'Division: splitting a quantity into equal parts',
            'power': 'Exponentiation: repeated multiplication of a quantity by itself',
            'sqrt': 'Square root: finding the quantity that when multiplied by itself gives the original',
            'cbrt': 'Cube root: finding the quantity that when multiplied by itself three times gives the original',
        }
        
        return explanations.get(canonical, f"Operation: {canonical}")
