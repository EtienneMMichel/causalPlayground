import numpy as np
import pandas as pd
from collections import defaultdict
from math import log2
from src import utils
import yaml

def lz78_compression(sequence):
    """
    Implémente l'algorithme de LZ78.
    Retourne le nombre de phrases (i.e., la complexité de LZ78).
    """
    dictionary = {}
    current = ''
    index = 1
    output = []
    
    for char in sequence:
        current += char
        if current not in dictionary:
            dictionary[current] = index
            output.append((0 if len(current) == 1 else dictionary[current[:-1]], char))
            index += 1
            current = ''
    
    # Ajouter la dernière entrée si non vide
    if current:
        output.append((dictionary.get(current[:-1], 0), current[-1]))
    
    # La complexité est le nombre de phrases distinctes
    return len(output), output

def compute_lz78_complexity(sequence):
    dictionary = {}
    current = ''
    index = 1
    phrases = 0
    
    for char in sequence:
        current += char
        if current not in dictionary:
            dictionary[current] = index
            index += 1
            phrases += 1
            current = ''
    
    if current:  # dernière phrase
        phrases += 1

    return phrases


# Fonction pour calculer la complexité de Lempel-Ziv (LZC)
def lempel_ziv_complexity(s):
    i, k, l = 0, 1, 1
    complexity = 1
    n = len(s)
    while True:
        if i + k > n - 1:
            complexity += 1
            break
        if s[i:i + k] == s[l:l + k]:
            k += 1
            if l + k > n:
                complexity += 1
                break
        else:
            complexity += 1
            i += 1
            if i == l:
                l += 1
                i = 0
                k = 1
    return complexity

# Calcul de l'entropie de Shannon
def shannon_entropy(sequence):
    counts = defaultdict(int)
    for char in sequence:
        counts[char] += 1
    probs = [count / len(sequence) for count in counts.values()]
    return -sum(p * log2(p) for p in probs)

if __name__ == "__main__":
    config = yaml.safe_load(open("./config.yaml", "r"))
    symbols = config['data']['symbols']
    data = utils.preprocess(config)
    prices = data[[f"{s}-close_price" for s in symbols]]
    data = prices.to_numpy()

    log_returns = np.log(data[1:]) - np.log(data[:-1])
    log_returns = np.nan_to_num(log_returns)
    discrete_returns = (log_returns > 0).astype(int).astype(str) # Discrétisation des rendements : codage binaire (1 si r > 0, 0 sinon)
    binary_sequences = [''.join(discrete_returns[:,i]) for i in range(len(symbols))]
    binary_sequence = binary_sequences[0]
    for binary_sequence in binary_sequences:
        max_lempel_ziv = len(binary_sequence)/log2(len(binary_sequence))
        lz78_complexity = compute_lz78_complexity(binary_sequence)
        print("lz78_complexity: ", lz78_complexity)
        print("max_lempel_ziv: ", max_lempel_ziv)
        lz_complexity = lz78_complexity/max_lempel_ziv
        entropy = shannon_entropy(binary_sequence)
        max_entropy = log2(len(set(binary_sequence)))
        redundancy = 1 - (entropy / max_entropy)

        print("Complexité de Lempel-Ziv :", lz_complexity)
        print("Entropie de Shannon :", entropy)
        print("Redondance :", redundancy)
        print("---------------------")