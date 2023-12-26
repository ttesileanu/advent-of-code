from fractions import Fraction
from typing import List, Optional, Sequence

from memo import memo


def diff(v: Sequence[int]) -> Sequence[int]:
    d = []
    last = v[0]
    for x in v[1:]:
        d.append(x - last)
        last = x

    return d


@memo
def binom(n: int, k: int) -> int:
    """Binomial coefficient."""
    assert k >= 0
    assert n > 0
    assert k <= n

    if k == 0 or k == n:
        return 1

    return binom(n - 1, k - 1) + binom(n - 1, k)


@memo
def bernoulli(m: int) -> Fraction:
    """Negative Bernoulli coefficient.

    https://en.wikipedia.org/wiki/Bernoulli_number#Recursive_definition
    """
    assert m >= 0
    if m == 0:
        return Fraction(1)

    s = 0
    for k in range(m):
        s += binom(m, k) * bernoulli(k) / (m - k + 1)

    return -s


class Polynomial:
    coeffs: List[Fraction]

    def __init__(self, c: Sequence[Fraction]):
        if len(c) == 0:
            c = [Fraction()]

        self.coeffs = [Fraction(_) for _ in c]

    def __call__(self, n: int) -> Fraction:
        value = 0
        nk = 1
        for coeff in self.coeffs:
            value += coeff * nk
            nk *= n

        return value

    @property
    def degree(self) -> int:
        return len(self.coeffs) - 1

    def to_sequence(self, count: int) -> Sequence[Fraction]:
        """Find the sequence of values of the given polynomial.

        Parameters
        ----------
        coefficients : sequence of fractions
            Polynomial coefficients `c[i]`, so that the sequence is given by
                a[k] = c[0] + c[1] * k + ... + c[n - 1] * k^{n-1} .
        count : int
            Number of sequence elements to generate.

        Returns
        -------
        Sequence[Fraction]
            Sequence values `a[0]`, ..., `a[count - 1]`.
        """
        assert count > 0

        values = [self.coeffs[0]]
        for i in range(1, count):
            value = values[-1]
            for k in range(1, self.degree + 1):
                value += self.coeffs[k] * (i**k - (i - 1) ** k)

            values.append(value)

        return values

    def cumsum(self, start: Optional[Fraction] = None) -> "Polynomial":
        """Find the polynomial obtained by taking the cumulative sum from a sequence
        obtained from a polynomial.

        Parameters
        ----------
        coefficients : sequence of int
            Polynomial coefficients `c[i]`, so that the original sequence is given by
                a[k] = c[0] + c[1] * k + ... + c[n - 1] * k^{n-1} .
        start : int, optional
            First value of cumulative sum. Defaults to 0.

        Returns
        -------
        Polynomial
            The cumulative sum polynomial, with coefficients `d[i]` such that the
            obtained sequence
                b[k] = d[0] + d[1] * k + ... + d[n] * k^n
            obeys
                b[0] = start
                a[k] = b[k + 1] - b[k] .
        """
        # Each monomial can be transformed using Faulhaber's formula,
        #       sum_{k=1}^{n-1} k^p = sum_{k=0}^p 1/{k+1} * (p-choose-k) * B^-_{p-k} * n^{k + 1} ,
        # where B^-_k are the negative Bernoulli numbers.
        # (https://en.wikipedia.org/wiki/Faulhaber%27s_formula#Variations)
        if start is None:
            start = 0

        result = Polynomial(
            [Fraction(start)] + [Fraction() for _ in range(self.degree + 1)]
        )
        for p in range(self.degree + 1):
            if p == 0:
                result.coeffs[1] += self.coeffs[0]
                continue

            for k in range(p + 1):
                prefactor = binom(p, k) * bernoulli(p - k) / (k + 1)
                result.coeffs[k + 1] += prefactor * self.coeffs[p]

        return result

    @staticmethod
    def from_sequence(seq: Sequence[int]) -> "Polynomial":
        if len(seq) == 0:
            raise ValueError("Cannot convert empty sequence")

        starts = []
        while any(_ != seq[0] for _ in seq[1:]):
            starts.append(seq[0])
            seq = diff(seq)

        starts.append(seq[0])
        p = Polynomial([starts[-1]])
        for start in starts[-2::-1]:
            p = p.cumsum(start=start)

        return p

    def __repr__(self) -> str:
        s = ""
        for i, coeff in enumerate(self.coeffs):
            if coeff == 0:
                # don't display zero terms
                continue

            if i == 0:
                power = ""
            elif i == 1:
                power = "n"
            else:
                power = f"n^{i}"

            sign = "+" if coeff > 0 else "-"
            if not s:
                term = "-" if sign == "-" else ""
            else:
                term = f" {sign} "

            if abs(coeff) == 1 and power:
                factor = ""
            else:
                factor = str(abs(coeff))

            term += f"{factor}{power}"
            s += term

        if not s:
            s = "0"

        r = f"<{s}>"
        return r
