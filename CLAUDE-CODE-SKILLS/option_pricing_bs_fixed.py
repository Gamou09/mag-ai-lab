"""Black-Scholes pricing, Greeks and implied volatility for European options.

Units used throughout:
    time_to_expiry            years
    volatility, rate,
    dividend_yield            decimals, so 0.05 means 5%

Example:
    python3 option_pricing_bs_fixed.py 100,100,1,0.2 --rate 0.05 --dividend-yield 0.01
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import Callable, Sequence

CALL = "call"
PUT = "put"

DAYS_PER_YEAR = 365
DEFAULT_RATE = 0.05
DEFAULT_OPTION = (100.0, 100.0, 1.0, 0.2)

IV_LOWER_BOUND = 1e-6
IV_UPPER_BOUND = 10.0
IV_TOLERANCE = 1e-8


@dataclass(frozen=True)
class Greeks:
    """Option sensitivities.

    Attributes:
        delta: Price change per 1.00 change in spot.
        gamma: Delta change per 1.00 change in spot.
        vega: Price change per 1.00 (100 percentage points) change in volatility.
        theta: Price change per calendar day.
        rho: Price change per 1.00 (100 percentage points) change in rate.
    """

    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float


def norm_cdf(x: float) -> float:
    """Return the standard normal cumulative distribution function at x."""
    return 0.5 * math.erfc(-x / math.sqrt(2))


def norm_pdf(x: float) -> float:
    """Return the standard normal probability density function at x."""
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


def _validate_inputs(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    rate: float,
    dividend_yield: float,
) -> None:
    """Raise ValueError unless the inputs describe a valid option."""
    values = (spot, strike, time_to_expiry, volatility, rate, dividend_yield)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("all inputs must be finite numbers")
    if spot <= 0 or strike <= 0 or volatility <= 0:
        raise ValueError("spot, strike and volatility must be positive")
    if time_to_expiry < 0:
        raise ValueError("time to expiry cannot be negative")


def _validate_option_type(option_type: str) -> None:
    """Raise ValueError unless option_type is CALL or PUT."""
    if option_type not in (CALL, PUT):
        raise ValueError(f"unknown option type: {option_type!r}")


def _d1_d2(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    rate: float,
    dividend_yield: float,
) -> tuple[float, float]:
    """Return the Black-Scholes d1 and d2 terms for an unexpired option."""
    vol_root_time = volatility * math.sqrt(time_to_expiry)
    drift = rate - dividend_yield + volatility * volatility / 2
    d1 = (math.log(spot / strike) + drift * time_to_expiry) / vol_root_time
    return d1, d1 - vol_root_time


def call_price(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    rate: float,
    dividend_yield: float = 0.0,
) -> float:
    """Return the price of a European call, or its intrinsic value at expiry."""
    _validate_inputs(spot, strike, time_to_expiry, volatility, rate, dividend_yield)
    if time_to_expiry == 0:
        return max(spot - strike, 0.0)
    d1, d2 = _d1_d2(spot, strike, time_to_expiry, volatility, rate, dividend_yield)
    discounted_spot = spot * math.exp(-dividend_yield * time_to_expiry)
    discounted_strike = strike * math.exp(-rate * time_to_expiry)
    return discounted_spot * norm_cdf(d1) - discounted_strike * norm_cdf(d2)


def put_price(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    rate: float,
    dividend_yield: float = 0.0,
) -> float:
    """Return the price of a European put, or its intrinsic value at expiry."""
    _validate_inputs(spot, strike, time_to_expiry, volatility, rate, dividend_yield)
    if time_to_expiry == 0:
        return max(strike - spot, 0.0)
    d1, d2 = _d1_d2(spot, strike, time_to_expiry, volatility, rate, dividend_yield)
    discounted_spot = spot * math.exp(-dividend_yield * time_to_expiry)
    discounted_strike = strike * math.exp(-rate * time_to_expiry)
    return discounted_strike * norm_cdf(-d2) - discounted_spot * norm_cdf(-d1)


def calculate_greeks(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    option_type: str,
    rate: float,
    dividend_yield: float = 0.0,
) -> Greeks:
    """Return the Greeks of an unexpired option.

    Raises:
        ValueError: If the inputs are invalid or the option has expired, since
            the Greeks are undefined at expiry.
    """
    _validate_option_type(option_type)
    _validate_inputs(spot, strike, time_to_expiry, volatility, rate, dividend_yield)
    if time_to_expiry == 0:
        raise ValueError("Greeks are undefined at expiry")

    d1, d2 = _d1_d2(spot, strike, time_to_expiry, volatility, rate, dividend_yield)
    root_time = math.sqrt(time_to_expiry)
    discounted_spot = spot * math.exp(-dividend_yield * time_to_expiry)
    discounted_strike = strike * math.exp(-rate * time_to_expiry)
    time_decay = -discounted_spot * norm_pdf(d1) * volatility / (2 * root_time)

    if option_type == CALL:
        delta = math.exp(-dividend_yield * time_to_expiry) * norm_cdf(d1)
        annual_theta = (
            time_decay
            - rate * discounted_strike * norm_cdf(d2)
            + dividend_yield * discounted_spot * norm_cdf(d1)
        )
        rho = time_to_expiry * discounted_strike * norm_cdf(d2)
    else:
        delta = math.exp(-dividend_yield * time_to_expiry) * (norm_cdf(d1) - 1)
        annual_theta = (
            time_decay
            + rate * discounted_strike * norm_cdf(-d2)
            - dividend_yield * discounted_spot * norm_cdf(-d1)
        )
        rho = -time_to_expiry * discounted_strike * norm_cdf(-d2)

    return Greeks(
        delta=delta,
        gamma=discounted_spot * norm_pdf(d1) / (spot * spot * volatility * root_time),
        vega=discounted_spot * norm_pdf(d1) * root_time,
        theta=annual_theta / DAYS_PER_YEAR,
        rho=rho,
    )


def implied_volatility(
    price: float,
    spot: float,
    strike: float,
    time_to_expiry: float,
    option_type: str,
    rate: float,
    dividend_yield: float = 0.0,
) -> float:
    """Return the volatility that reproduces price, found by bisection.

    Raises:
        ValueError: If the option has expired, or no volatility between
            IV_LOWER_BOUND and IV_UPPER_BOUND matches the price.
    """
    _validate_option_type(option_type)
    if time_to_expiry == 0:
        raise ValueError("implied volatility is undefined at expiry")

    pricer: Callable[..., float] = call_price if option_type == CALL else put_price

    def price_at(volatility: float) -> float:
        return pricer(spot, strike, time_to_expiry, volatility, rate, dividend_yield)

    low, high = IV_LOWER_BOUND, IV_UPPER_BOUND
    if not price_at(low) <= price <= price_at(high):
        raise ValueError("no implied volatility matches this price")

    while high - low > IV_TOLERANCE:
        middle = (low + high) / 2
        if price_at(middle) < price:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def _parse_option(text: str) -> tuple[float, float, float, float]:
    """Parse 'spot,strike,time_to_expiry,volatility' into four numbers."""
    parts = text.split(",")
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(
            "expected four comma-separated values: spot,strike,time_to_expiry,volatility"
        )
    try:
        spot, strike, time_to_expiry, volatility = (float(part) for part in parts)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"values must be numbers: {text!r}") from error
    return spot, strike, time_to_expiry, volatility


def _build_parser() -> argparse.ArgumentParser:
    """Return the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Price a European option with the Black-Scholes model."
    )
    parser.add_argument(
        "option",
        nargs="?",
        type=_parse_option,
        default=DEFAULT_OPTION,
        help="spot,strike,time_to_expiry,volatility (default: 100,100,1,0.2)",
    )
    parser.add_argument(
        "--rate", type=float, default=DEFAULT_RATE, help="risk-free rate as a decimal"
    )
    parser.add_argument(
        "--dividend-yield", type=float, default=0.0, help="dividend yield as a decimal"
    )
    return parser


def _print_report(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    rate: float,
    dividend_yield: float,
) -> None:
    """Print prices, Greeks and implied volatility for one option."""
    for option_type, pricer in ((CALL, call_price), (PUT, put_price)):
        label = option_type.capitalize()
        price = pricer(spot, strike, time_to_expiry, volatility, rate, dividend_yield)
        print(f"{label} price: {price:.4f}")
        if time_to_expiry == 0:
            continue
        greeks = calculate_greeks(
            spot, strike, time_to_expiry, volatility, option_type, rate, dividend_yield
        )
        print(f"{label} greeks: {greeks}")
        implied = implied_volatility(
            price, spot, strike, time_to_expiry, option_type, rate, dividend_yield
        )
        print(f"{label} implied volatility: {implied:.6f}")

    expired_call = call_price(spot, strike, 0, volatility, rate, dividend_yield)
    print(f"Call value at expiry at the current spot: {expired_call:.4f}")


def main(argv: Sequence[str] | None = None) -> None:
    """Run the command-line interface."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    spot, strike, time_to_expiry, volatility = args.option
    try:
        _print_report(
            spot, strike, time_to_expiry, volatility, args.rate, args.dividend_yield
        )
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
