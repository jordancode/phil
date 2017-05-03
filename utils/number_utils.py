import itertools
izip = itertools.zip_longest
chain = itertools.chain.from_iterable
compress = itertools.compress

class NumberUtils:
    
    
    @staticmethod
    def get_primes_less_than(n):
        """ Input n>=6, Returns a list of primes, 2 <= p < n """
        """ From  http://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n/33356284#33356284"""
        zero = bytearray([False])
        size = n//3 + (n % 6 == 2)
        sieve = bytearray([True]) * size
        sieve[0] = False
        for i in range(int(n**0.5)//3+1):
            if sieve[i]:
                k=3*i+1|1
                start = (k*k+4*k-2*k*(i&1))//3
                sieve[(k*k)//3::2*k]=zero*((size - (k*k)//3 - 1) // (2 * k) + 1)
                sieve[  start ::2*k]=zero*((size -   start  - 1) // (2 * k) + 1)
        ans = [2,3]
        poss = chain(izip(*[range(i, n, 6) for i in (1,5)]))
        ans.extend(compress(poss, sieve))
        
        return ans