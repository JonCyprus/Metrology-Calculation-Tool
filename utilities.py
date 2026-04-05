### This file is to create utility functions that are to be used in the streamlit app.

import numpy as np
from scipy.stats import norm
import io
import pandas as pd

def calculateTypeAUncertainty(data: np.ndarray) -> tuple[float, float]:
    """
    Computes the mean and standard uncertainty from repeated measurements.

    Parameters
    ------------
    data: np.ndarray
        1D array of repeated measurements for a single input variable

    Returns
    ----------
    tuple[float, float]
        mean: float
            The sample mean fo the measurements.
        std_uncertainty: float
            The standard uncertainty of the mean (std / sqrt(n))
    """
    if data.ndim != 1:
        raise ValueError("Data must be 1D array with more than 1 element")
    if data.size < 2: raise ValueError("Data must have at least 2 elements")
    return float(np.mean(data)), float(np.std(data, ddof=1)/np.sqrt(data.size))

DIVISORS = {
    "uniform": np.sqrt(3),
    "triangular": np.sqrt(6),
}

DISTRIBUTIONS = [*DIVISORS.keys(), "normal"]

def calculateTypeBUncertainty(halfWidth: float, distribution: str, confidence: float = 95.) -> float:
    """

    Parameters
    ----------
    halfWidth:
        the half width of the uncertainty, e.g, 9 +/- 0.1 the half width is 0.1
    distribution:
        type, uniform, triangular, or normal
    confidence:
        The confidence level of the measurement as a percent e.g. 95% confidence

    Returns
    -------

    """
    dist = distribution.strip().lower()
    if dist == "normal":
        return float(halfWidth / kFromConfidence(confidence))
    divisor = DIVISORS[dist]
    return float(halfWidth / divisor)

def kFromConfidence(confidence: float) -> float:
    """

    Parameters
    ----------
    confidence: confidence level as a percentage 95% -> 95

    Returns
    -------
    k: float, the standard
    """
    return float(norm.ppf((1+(confidence/100))/2))

def loadCSV(file):
    content = file.read().decode("utf-8")
    file.seek(0)
    firstLine = content.split("\n")[0]
    try:
        float(firstLine.split(",")[0])
        skip = 0
    except ValueError:
        skip = 1
    return np.loadtxt(io.StringIO(content), delimiter=",", skiprows=skip)

def buildBudgetTable(budgetData, outputNominal, outputVar):
    """

    Parameters
    ----------
    budgetData entries are keyed by variable - dictionary. Dictionary entries are
        nominal, uncertainty, coeff, type, distribution
    outputNominal the nominal of the output based on the standard model equation
    Returns
    -------

    """
    rows = []
    result = 0
    for var, d in budgetData.items():
        contribution = abs(d["coeff"]) * d["uncertainty"]
        result += contribution **2
        rows.append({
            "Variable":       var,
            "Value":          d["nominal"],
            "u(xi)":          d["uncertainty"],
            "ci = dy/dxi":    d["coeff"],
            "|ci|·u(xi)":     contribution,
            "|ci|²·u(xi)²":  contribution ** 2,
            "Type":           d["type"],
            "Distribution":   d["distribution"],
        })

    unc = np.sqrt(result)
    totalRow = pd.DataFrame([{
        "Variable":      f"{outputVar}",
        "Value":         outputNominal,
        "|ci|²·u(xi)²": unc ** 2,
        "Type":          "—",
        "Distribution":  "—",
    }])

    return pd.concat([pd.DataFrame(rows), totalRow], ignore_index=True)