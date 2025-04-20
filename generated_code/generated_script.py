def find_primes_in_list(numbers):
    """
    Finds all prime numbers within a given list of numbers.

    Args:
        numbers: A list of integers.

    Returns:
        A list containing only the prime numbers from the input list.  Returns an empty list if the input is invalid or contains no primes.
    """
    if not isinstance(numbers, list) or not all(isinstance(num, int) for num in numbers):
        return [] #Handle invalid input

    primes = []
    for num in numbers:
        if num > 1:  # Prime numbers are greater than 1
            is_prime = True
            for i in range(2, int(num**0.5) + 1):
                if num % i == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(num)
    return primes

def sieve_of_eratosthenes(limit):
    """
    Generates a list of all prime numbers up to a given limit using the Sieve of Eratosthenes.

    Args:
      limit: An integer representing the upper limit (inclusive).

    Returns:
      A list of prime numbers up to the limit. Returns an empty list if the limit is invalid.
    """
    if not isinstance(limit, int) or limit < 2:
        return []

    primes = [True] * (limit + 1)
    primes[0] = primes[1] = False

    for p in range(2, int(limit**0.5) + 1):
        if primes[p]:
            for i in range(p * p, limit + 1, p):
                primes[i] = False

    prime_numbers = [p for p in range(limit + 1) if primes[p]]
    return prime_numbers