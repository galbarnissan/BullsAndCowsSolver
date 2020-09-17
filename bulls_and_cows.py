from itertools import permutations, combinations
from collections import defaultdict, namedtuple
from random import randint
from copy import deepcopy

SECRET_LENGTH = 4
ps = list(permutations([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], SECRET_LENGTH))
def random_code():
    return ps[randint(0, len(ps)-1)]

class Coder:

    def __init__(self, secret, manual):
        self.secret = secret
        self.tries = 0
        self.manual = manual

    def check(self, guess):
        self.tries += 1
        bulls = 0
        cows = 0
        guesses = defaultdict(list)
        secrets = defaultdict(list)
        for i in range(len(guess)):
            if self.secret[i] == guess[i]:
                bulls +=1
            else:
                if secrets[guess[i]]:
                    cows += 1
                    secrets[guess[i]].pop()
                else:
                    guesses[guess[i]].append(1)
                if guesses[self.secret[i]]:
                    cows += 1
                    guesses[self.secret[i]].pop()
                else:
                    secrets[self.secret[i]].append(1)
        if self.manual:
            print("Try: %s, bulls: %s, cows: %s" % (self.tries, bulls, cows))
        return {
            "bs": bulls,
            "cs": cows
        }

class Solver(object):

    def __init__(self, coder: Coder):
        self.coder = coder
        self.solution = None

    def apply_combination_on_guess(self, guess, combs, status):
        new_guesses = []
        for comb in combs:
            new_guess = deepcopy(guess)
            for position in comb:
                new_guess[position][1] = status
            new_guesses.append(new_guess)
        return new_guesses

    def get_next_guesses(self, guess, score):
        initial_extended_guess = [[c, 'o'] for c in guess]
        extended_guesses = [initial_extended_guess]
        bulls = score["bs"]
        cows = score["cs"]
        missing_cows = SECRET_LENGTH - bulls - cows

        # map bulls - consider global data
        if bulls:
            new_guesses = []
            for extended_guess in extended_guesses:
                other_pos = [p for p in range(SECRET_LENGTH) if extended_guess[p][1] == 'o']
                combs = combinations(other_pos, bulls)
                new_guesses.extend(self.apply_combination_on_guess(extended_guess, combs, 'b'))
            extended_guesses = new_guesses

        # map cows 
        if cows:
            new_guesses = []
            for extended_guess in extended_guesses:
                other_pos = [p for p in range(SECRET_LENGTH) if extended_guess[p][1] == 'o']
                combs = combinations(other_pos, cows)
                new_guesses.extend(self.apply_combination_on_guess(extended_guess, combs, 'c'))
            extended_guesses = new_guesses

        if missing_cows:
            new_guesses = []
            for extended_guess in extended_guesses:
                other_pos = [p for p in range(SECRET_LENGTH) if extended_guess[p][1] == 'o']
                current_cows = [p[0] for p in extended_guess]
                potential_cows = [n for n in range(10) if n not in current_cows]
                new_cows = combinations(potential_cows, missing_cows)
                guess_with_new_cows_combs = []
                for comb in new_cows:
                    g = deepcopy(extended_guess)
                    for i in range(len(other_pos)):
                        g[other_pos[i]][0] = comb[i]
                        g[other_pos[i]][1] = 'c'
                    guess_with_new_cows_combs.append(g)
                new_guesses.extend(guess_with_new_cows_combs)
        extended_guesses = new_guesses

        # permutate cows
        if cows or missing_cows:
            new_guesses = []
            for extended_guess in extended_guesses:
                cows_pos = [p for p in range(SECRET_LENGTH) if extended_guess[p][1] == 'c']
                perm_cows = permutations(cows_pos, len(cows_pos))
                guess_with_cows_perm = []
                for new_perm in perm_cows:
                    g = deepcopy(extended_guess)
                    for i in range(len(cows_pos)):
                        g[cows_pos[i]][0] = extended_guess[new_perm[i]][0]
                    guess_with_cows_perm.append(g)
                new_guesses.extend(guess_with_cows_perm)        
        extended_guesses = new_guesses

        guesses = [[n[0] for n in g] for g in extended_guesses]
        return guesses

    def check_score(self, score, prev_score):
        bulls = score["bs"]
        cows = score["cs"]
        prev_bulls = prev_score["bs"]
        prev_cows = prev_score["cs"]
        initial_guess = prev_score.get("initial_guess", False)
        if bulls == 4:
            return "solved"
        elif initial_guess or bulls > prev_bulls or (bulls == prev_bulls and cows > prev_cows):
            return "continue"
        else:        
            return "bad_move"

    def rec_solve(self, prev_guess, prev_score):
        if prev_score:
            next_guesses = self.get_next_guesses(prev_guess, prev_score)
        else: # no score yet - initial guess
            prev_score = {
                "initial_guess": True,
                "bs": 0,
                "cs": 0
            }
            next_guesses = [prev_guess]

        for guess in next_guesses:
            score = self.coder.check(guess)
            guess_status = self.check_score(score, prev_score)
            if guess_status == "continue":
                res = self.rec_solve(guess, score)
                if res:
                    return True
            elif guess_status == "solved":
                self.solution = guess
                return True
        return False

    def solve(self):
        initial_guess = [0, 1, 2, 3] # random_code()
        #print("Initial guess: %s" % ("".join([str(i) for i in initial_guess])))
        self.rec_solve(initial_guess, None)
        return self.solution

if __name__ == "__main__":
    manual = False
    if manual: 
        code = random_code()
        coder = Coder(code, manual)    
        print("Code: %s" % ("".join([str(i) for i in code])))
        solver = Solver(coder)
        solver.solve()
        print("Solution; code: %s, tries: %s" % (("".join([str(i) for i in code])), coder.tries))
    else:
        codes = 0 
        tries = 0 
        for code in ps:
            codes += 1
            print("Starting code: %s" % str(codes))
            coder = Coder(code, manual)
            solver = Solver(coder)
            solver.solve()
            tries += coder.tries 
        print("Avg: %s" % (str(tries/codes)))




