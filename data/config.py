"""
Configuration file for stock baskets used in cointegration analysis.
"""

# Define stock baskets by sector/category
basket_1 = ["SNOW", "DDOG", "NET", "ESTC", "MDB"]  # Cloud Infrastructure
basket_2 = ["CRWD", "ZS", "PANW", "OKTA", "S"]  # Cloud Security
basket_3 = ["CRM", "NOW", "WDAY", "TEAM", "HUBS"]  # Enterprise SaaS Platforms
basket_4 = ["TTD", "MGNI", "PUBM", "RAMP"]  # Ad Tech (removed delisted TRADE)
basket_5 = ["TXN", "ADI", "MCHP", "ON", "NXPI"]  # Analog Semiconductors
basket_6 = ["AMD", "NVDA", "AVGO", "MRVL", "QCOM"]  # GPU/AI Accelerators
basket_7 = ["ZM", "TWLO", "DOCU", "RNG", "FIVN"]  # Communication/Collaboration SaaS
basket_8 = ["PYPL", "BILL", "SHOP", "MELI"]  # Payments/Fintech (removed delisted SQ)
basket_9 = ["GTLB", "FROG", "PD", "DOCN", "CFLT"]  # DevOps/Developer Tools
basket_10 = ["CSCO", "ANET", "CIEN"]  # Networking Infrastructure (removed delisted JNPR, VMW)
basket_11 = ["EBAY", "WIX", "AMZN", "U"]  # E-commerce Platforms (removed delisted BIGC)
basket_12 = ["SAIL", "VRNS", "CYBR", "TENB", "CHKP"]  # Security (Identity/Access)
basket_13 = ["LRCX", "KLAC", "AMAT", "ENTG", "MPWR"]  # Semiconductor Equipment
basket_14 = ["META", "PINS", "SNAP", "SPOT", "ROKU"]  # Social/Consumer Content
basket_15 = ["ASAN", "DOMO", "VEEV", "PCTY"]  # Productivity/Work Management (removed delisted SMAR)

# All baskets in a list
ALL_BASKETS = [
    basket_1, basket_2, basket_3, basket_4, basket_5,
    basket_6, basket_7, basket_8, basket_9, basket_10,
    basket_11, basket_12, basket_13, basket_14, basket_15
]

# Basket names for reference
BASKET_NAMES = [
    "Cloud Infrastructure",
    "Cloud Security",
    "Enterprise SaaS Platforms",
    "Ad Tech",
    "Analog Semiconductors",
    "GPU/AI Accelerators",
    "Communication/Collaboration SaaS",
    "Payments/Fintech",
    "DevOps/Developer Tools",
    "Networking Infrastructure",
    "E-commerce Platforms",
    "Security (Identity/Access)",
    "Semiconductor Equipment",
    "Social/Consumer Content",
    "Productivity/Work Management"
]
