#! /usr/bin/env python
from fractions import Fraction
from typing import Sequence, TypeVar

from utils import iterinput, logger
from common24 import Array, Hailstone

T = TypeVar("T")


def cross(a: Array[T], b: Array[T]) -> Array[T]:
    assert len(a) == 3
    assert len(b) == 3

    return Array(
        [
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        ]
    )


def get_uijk(stones: Sequence[Hailstone], i: int, j: int, k: int) -> Array[int]:
    x0i = stones[i].position
    x0j = stones[j].position
    x0k = stones[k].position

    vi = stones[i].velocity
    vj = stones[j].velocity
    vk = stones[k].velocity

    dxij = x0j - x0i
    dxkj = x0j - x0k

    dvij = vj - vi
    dvkj = vj - vk

    cross_ij = cross(dxij, dvij)
    cross_kj = cross(dxkj, dvkj)

    return cross(cross_ij, cross_kj)


def get_ratio(numerator: Array[int], denominator: Array[int]) -> Fraction:
    assert len(numerator) == len(denominator)

    alpha = None
    for n, d in zip(numerator, denominator):
        if d != 0:
            if alpha is None:
                alpha = Fraction(n, d)
            else:
                assert alpha == Fraction(n, d)

    assert alpha is not None
    return alpha


def get_ti(
    stone_i: Hailstone, stone_j: Hailstone, propto_vj_minus_w: Array[int]
) -> Fraction:
    dx = stone_j.position - stone_i.position
    dv = stone_j.velocity - stone_i.velocity

    numerator = cross(propto_vj_minus_w, dx)
    denominator = -cross(propto_vj_minus_w, dv)

    t = get_ratio(numerator, denominator)
    return t


def get_w(
    stone_i: Hailstone,
    stone_j: Hailstone,
    propto_vj_minus_w: Array[Fraction],
    dt: Fraction,
):
    dx = stone_j.position - stone_i.position
    dv = stone_j.velocity - stone_i.velocity

    numerator = cross(dv, dx)
    denominator = -cross(dv, propto_vj_minus_w)
    theta_dt = get_ratio(numerator, denominator)

    theta = theta_dt / dt
    vj_minus_w = propto_vj_minus_w * theta
    w = stone_j.velocity - vj_minus_w
    return w


if __name__ == "__main__":
    # Let the hailstone positions as a function of time be given by
    #   x[i](t) = x0[i] + v[i] * t ,
    # where x[i], x0[i], and v[i] are 3d vectors (with integer components).

    # Let our rock obey
    #   z(t) = z0 + w * t .

    # Suppose the rock meets rock i at time t[i]; then:
    #   x0[i] + v[i] * t[i] = z0 + w * t[i] .

    # Choosing two hailstones i and j with i != j and subtracting, we have
    #   x0[j] - x0[i] + v[j] * t[j] - v[i] * t[i] = w * (t[j] - t[i]) ,
    # or
    #   dx0[i, j] + dv[i, j] * t[i] + (v[j] - w) * dt[i, j] = 0 ,
    # where d<quantity>[i, j] = quantity[j] - quantity[i].

    # This shows that (v[j] - w) is in span(dx0[i, j], dv[i, j]). Consider now a
    # different index k != j. By the same token, (v[j] - w) is also in
    # span(dx0[k, j], dv[k, j]). Then it must be that
    #   v[j] - w = alpha * u[i, j, k] ,
    # where
    #   u[i, j, k] = cross(cross(dx0[i, j], dv[i, j]), cross(dx0[k, j], dv[k, j]))
    # and `cross` is the cross product. This holds because
    #   perp[i, j] = cross(dx0[i, j], dv[i, j])
    # is perpendicular to the plane generated by those two vectors, and
    #   cross(perp[i, j], perp[k, j])
    # is perpendicular to both perp[i, j] and perp[k, j], and thus it is contained in
    # both span(dx0[i, j], dv[i, j]) and span(dx0[k, j], dv[k, j]).

    # Consider again the equation
    #   dx0[i, j] + dv[i, j] * t[i] + (v[j] - w) * dt[i, j] = 0 .
    # Taking the cross product with u[i, j, k] will make the last term vanish, since
    # v[j] - w is proportional to u[i, j, k]. Thus,
    #   cross(u[i, j, k], dv[i, j]) * t[i] = -cross(u[i, j, k], dx0[i, j]) .
    # This can be used to calculate t[i]. Similarly, by exchanging i and j we can
    # calculate t[j]:
    #   cross(u[j, i, k], dv[j, i]) * t[j] = -cross(u[j, i, k], dx0[j, i]) ,
    # which is equivalent to
    #   cross(u[j, i, k], dv[i, j]) * t[j] = -cross(u[j, i, k], dx0[i, j]) ,
    # since dv[j, i] = -dv[i, j], dx[j, i] = -dx[i, j].

    # Thus, we now have t[i], t[j], dt[i, j] = t[j] - t[i], and we know that
    #   v[j] - w = theta[i, j, k] * u[i, j, k]
    # for some scalar theta[i, j, k]. Using again the same equation as above,
    #   dx0[i, j] + dv[i, j] * t[i] + theta[i, j, k] * u[i, j, k] * dt[i, j] = 0 .
    # This implies
    #   theta[i, j, k] * dt[i, j] * cross(dv[i, j], u[i, j, k]) = -cross(dv[i, j], dx0[i, j]) ,
    # which allows us to calculate theta[i, j, k] (since we know dt[i, j]), and thus we
    # can finally evaluate w:
    #   w = v[j] - theta[i, j, k] * u[i, j, k] .

    # Now finding z0 is straightforward given
    #   x0[i] + v[i] * t[i] = z0 + w * t[i] .

    # Note that any choice of i, j, k will give us the answer (with some assumptions
    # about the trajectories of the hailstones that are almost certain to apply,
    # especially given that we know no two of them ever collide). We can then check that
    # the rock trajectory given by z0 and w indeed collides with all the hailstones.

    hailstones = []
    for line in iterinput():
        pos_str, vel_str = line.split("@")
        pos = [int(_) for _ in pos_str.split(",", maxsplit=2)]
        vel = [int(_) for _ in vel_str.split(",", maxsplit=2)]

        hailstones.append(Hailstone(Array(pos), Array(vel)))

    n = len(hailstones)
    logger.info(f"There are {len(hailstones)} hailstones.")
    logger.debug(f"{hailstones=}")

    propto_v1_minus_w = get_uijk(hailstones, 0, 1, 2)
    propto_v0_minus_w = get_uijk(hailstones, 1, 0, 2)
    assert not all(propto_v1_minus_w == 0)
    assert not all(propto_v0_minus_w == 0)

    t0 = get_ti(hailstones[0], hailstones[1], propto_v1_minus_w)
    t1 = get_ti(hailstones[1], hailstones[0], propto_v0_minus_w)

    w = get_w(hailstones[0], hailstones[1], propto_v1_minus_w, t1 - t0)
    z0 = hailstones[0].position + (hailstones[0].velocity - w) * t0

    for stone in hailstones:
        # this will raise AssertionError if there is no collision
        _ = get_ratio(stone.position - z0, w - stone.velocity)

    print(f"Sum of initial x, y, z is {sum(z0)}")
