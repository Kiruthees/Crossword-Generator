import random
from cluesfinal import clues

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.words = []

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word, clue):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.words.append((word, clue))
        node.is_end_of_word = True

    def search(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return node.words
    
class CrosswordPuzzle:
    def __init__(self, trie, randomness=0):
        self.randomness = randomness
        self.trie = trie
        self.puzzle = [[' ']*5 for _ in range(5)]  # 5x5 blank puzzle
        self.clues = [[' ']*5 for _ in range(2)]   # 2x5 blank clues
        self.max_tries = 500
        self.complete = False

        # Extract all words for choosing them randomly
        self.words = []
        self._collect_all_words(self.trie.root)
    
    def _collect_all_words(self, node):
        """Helper method to collect all words from the trie"""
        if node.is_end_of_word:
            self.words.extend(node.words)
        
        for child in node.children.values():
            self._collect_all_words(child)
    
    def get_random_word(self):
        """Get a random 5-letter word"""
        five_letter_words = [word for word in self.words if len(word[0]) == 5]
        if not five_letter_words:
            raise Exception("No 5-letter words available")
        return random.choice(five_letter_words)[0]

    def generate(self):
        tries = 0
        while not self.fill_puzzle() and tries < self.max_tries:
            tries += 1

        if not self.complete:
            raise Exception(f"Could not complete in {self.max_tries} re-tries")

        self.fill_clues()
        print(f"Finished in {tries + 1} tries")

    def fill_puzzle(self):
        self.puzzle = [[' ']*5 for _ in range(5)]
        first_word = self.get_random_word()
        self.place_word(first_word, (0, 0), (0, 1))

        for row in range(1, 5):
            next_word = self.choose_next_word(row)
            if next_word is None:
                return False
            self.place_word(next_word, (row, 0), (0, 1))

        self.complete = True
        return True

    def choose_next_word(self, row):
        if row == 4:
            last_words = [word[0] for word in self.words if len(word[0]) == 5 and self.evaluate_word(word[0], row) > 0]
            if last_words:
                return random.choice(last_words)
            return None

        max_score = 0
        max_word = ""
        possible_words = []

        for word_tuple in self.words:
            word = word_tuple[0]
            if len(word) != 5:  # Only consider 5-letter words
                continue
            score = self.evaluate_word(word, row)
            if score > 0:
                possible_words.append(word)
            if score > max_score:
                max_score = score
                max_word = word

        if max_score > 0:
            if random.random() >= self.randomness:
                return max_word
            return random.choice(possible_words) if possible_words else None

        return None

    def evaluate_word(self, word, row):
        if len(word) != 5:
            return 0
            
        vertical_prefixes = [""] * 5
        for i in range(row):
            for j in range(5):
                vertical_prefixes[j] += self.puzzle[i][j]
        
        for j in range(5):
            vertical_prefixes[j] += word[j]

        prefix_sums = [self.evaluate_vertical_possibilities(prefix) for prefix in vertical_prefixes]

        total = 0
        for s in prefix_sums:
            if s == 0:
                return 0
            total += s

        return total

    def evaluate_vertical_possibilities(self, prefix):
        """Evaluate how many words could complete this vertical prefix"""
        if len(prefix) == 5:
            # Check if this is a complete valid word
            matches = self.trie.search(prefix)
            return 1 if matches else 0
        else:
            # Count how many words start with this prefix
            matches = self.trie.search(prefix)
            five_letter_matches = [word for word in matches if len(word[0]) == 5]
            return len(five_letter_matches)

    def place_word(self, word, start, direction):
        for i, char in enumerate(word):
            x, y = start[0] + direction[0]*i, start[1] + direction[1]*i
            self.puzzle[x][y] = char

    def fill_clues(self):
        if not self.complete:
            raise Exception("Can't fill clues if puzzle has not been filled")
        
        vertical_words = [""] * 5
        horizontal_words = [""] * 5

        for i, row in enumerate(self.puzzle):
            for j, char in enumerate(row):
                horizontal_words[i] += char
                vertical_words[j] += self.puzzle[i][j]  # Fixed this line
        
        for i, word in enumerate(horizontal_words):
            matches = self.trie.search(word)
            self.clues[0][i] = matches[0][1] if matches else "No clue found"
        
        for i, word in enumerate(vertical_words):
            matches = self.trie.search(word)
            self.clues[1][i] = matches[0][1] if matches else "No clue found"

    def display_puzzle(self):
        """Display the crossword puzzle"""
        print("\nCrossword Puzzle:")
        print("=" * 21)
        for row in self.puzzle:
            print("|", end="")
            for cell in row:
                print(f" {cell} |", end="")
            print()
            print("-" * 21)

    def display_clues(self):
        """Display the clues"""
        print("\nHorizontal Clues (Across):")
        for i, clue in enumerate(self.clues[0]):
            print(f"{i+1}. {clue}")
        
        print("\nVertical Clues (Down):")
        for i, clue in enumerate(self.clues[1]):
            print(f"{i+1}. {clue}")

# Sample word database
def create_sample_trie():
    trie = Trie()
    
    # Add 5-letter words with clues
    words_and_clues = clues
    
    for word, clue in words_and_clues:
        trie.insert(word, clue)
    
    return trie

# Example usage
def main():
    print("Creating word database...")
    trie = create_sample_trie()
    
    print("Generating crossword puzzle...")
    puzzle = CrosswordPuzzle(trie, randomness=0.3)  # 30% randomness
    
    try:
        puzzle.generate()
        puzzle.display_puzzle()
        puzzle.display_clues()
        
        print("\n" + "="*50)
        print("SOLUTION:")
        for i, row in enumerate(puzzle.puzzle):
            print(f"Row {i+1}: {''.join(row)}")
        
    except Exception as e:
        print(f"Error generating puzzle: {e}")
        print("Try running again - generation uses randomness!")

if __name__ == "__main__":
    main()
