from enum import Enum


class CreditRiskTier(Enum):
    VERY_LOW_RISK = [800, 850]
    LOW_RISK = [700, 799]
    MODERATE_RISK = [600, 699]
    HIGH_RISK = [500, 599]
    VERY_HIGH_RISK = [0, 499]


class CreditRiskFactor(Enum):
    VERY_LOW_RISK = 2.0
    LOW_RISK = 1.5
    MODERATE_RISK = 1.2
    HIGH_RISK = 0.8
    VERY_HIGH_RISK = 0.5
