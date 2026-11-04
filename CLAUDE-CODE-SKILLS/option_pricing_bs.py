import math
import sys
from math import *

# black scholes stuff
R = 0.05
results = []
cnt = 0


def N(x):
    # exact normal cdf
    t = 0
    dx = (x + 10) / 2000
    for i in range(2000):
        z = -10 + i * dx
        t = t + (1 / math.sqrt(2 * 3.14159)) * math.exp(-z * z / 2) * dx
    return t


def n(x):
    return (1 / math.sqrt(2 * 3.14159)) * math.exp(-x * x / 2)


def call(s, k, t, v, r=R):
    global cnt
    cnt = cnt + 1
    try:
        a = (math.log(s / k) + (r + v * v) * t) / (v * math.sqrt(t))
        b = a - v * math.sqrt(t)
        p = s * N(a) - k * math.exp(-r * t) * N(b)
        results.append(p)
        return p
    except:
        return 0


def put(s, k, t, v, r=R):
    global cnt
    cnt = cnt + 1
    try:
        a = (math.log(s / k) + (r + v * v / 2) * t) / (v * math.sqrt(t))
        b = a - v * math.sqrt(t)
        p = k * math.exp(-r) * N(-b) - s * N(-a)
        results.append(p)
        return p
    except:
        return 0


# def old_price(s, k, t, v):
#     return max(s - k, 0) * 1.05


def greeks(s, k, t, v, type):
    # returns all the greeks
    a = (math.log(s / k) + (R + v * v / 2) * t) / (v * math.sqrt(t))
    b = (math.log(s / k) + (R + v * v / 2) * t) / (v * math.sqrt(t)) - v * math.sqrt(t)
    if type == "call":
        d = N(a)
        th = (-s * n(a) * v / (2 * math.sqrt(t)) - R * k * math.exp(-R * t) * N(b)) / 365
    else:
        d = N((math.log(s / k) + (R + v * v / 2) * t) / (v * math.sqrt(t)))
        th = (-s * n(a) * v / (2 * math.sqrt(t)) + R * k * math.exp(-R * t) * N(-b)) / 252
    g = n(a) / (s * v * math.sqrt(t))
    ve = s * n(a) * t
    return d, g, ve, th


def iv(price, s, k, t, type):
    # newton raphson solver for implied vol
    best = 0
    diff = 999999
    x = 0.01
    while x < 3:
        if type == "call":
            p = call(s, k, t, x)
        else:
            p = put(s, k, t, x)
        if abs(p - price) < diff:
            diff = abs(p - price)
            best = x
        x = x + 0.005
    return best


def main():
    if len(sys.argv) > 1:
        # read the option from the command line
        o = eval(sys.argv[1])
        s, k, t, v = o[0], o[1], o[2], o[3]
    else:
        s, k, t, v = 100, 100, 1, 0.2

    c = call(s, k, t, v)
    p = put(s, k, t, v)
    print("call " + str(c))
    print("put " + str(p))

    print("call greeks", greeks(s, k, t, v, "call"))
    print("put greeks", greeks(s, k, t, v, "put"))

    print("iv " + str(iv(c, s, k, t, "call")))
    print("iv " + str(iv(p, s, k, t, "put")))

    # expired option
    print("expired call " + str(call(100, 90, 0, 0.2)))

    print("avg " + str(sum(results) / len(results)))
    print("calls " + str(cnt))


main()
