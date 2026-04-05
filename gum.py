# This file encapsulates all functions to be used for the GUM calculation
import sympy
import math

def parseModel(modelStr: str) -> tuple[str, dict, any]:
    """

    Parameters
    ----------
    modelStr - the model string inputted by the user on the streamlit app.

    Returns
    -------
    outputName - the name of the output of the model (the variable being calculated from other inputs)
    symbols - a dictionary of string(symbol):symbolic object from the expression
    expr - the parsed expression that can be evaluated by plugging in symbol values.
    """
    safeStr = modelStr.replace("^", "**")
    lhs, rhs = safeStr.split('=')
    outputName = lhs.strip()
    expr = sympy.sympify(rhs.strip())
    symbols = {str(s): s for s in expr.free_symbols}
    return outputName, symbols, expr

def partialDerivModel(model: any, var: sympy.Symbol):
    """
    Parameters
    ----------
    model - the symbolic expression model (already converted by sympy) to be used for derivative calculation.
    var - the variable of differentiation

    Returns
    -------
    deriv - the symbolic derivative of the model w.r.t the variable.
    """
    if var not in model.free_symbols:
        raise ValueError('variable is not within the model')
    deriv = sympy.diff(model, sympy.sympify(var))
    return deriv

def evaluateExpr(expr: sympy.Expr, values: dict[sympy.Symbol, float]) -> float:
    """
    Parameters
    ----------
    expr - a sympy expression to be evaluated.
    values - a dictionary of sympy symbols with the floats to be evaluated with.

    Returns
    -------

    """
    return float(expr.subs(values))

def calculateGUM(model: sympy.Expr,
                 nominals: dict[sympy.Symbol, float],
                 uncerts: dict[sympy.Expr, float]) -> tuple[float, float, dict[sympy.Basic, float]]:
    """
    Parameters
    ----------
    model:
        the sympy expression of the model to be evaluated
    nominals:
        the nominals of each variable as a dictionary of sympy.symbol:float
    uncerts:
        the uncertanties of each variable as dictionary of sympy.symbol:float

    Returns
    -------
    the uncertainty in the output variable using the GUM method.
    """
    GUMresult = 0
    outputResult = evaluateExpr(model, nominals)
    sensitivityCoefficients = {}
    for var in model.free_symbols:
        partialDeriv = partialDerivModel(model, var)
        sensitivity = evaluateExpr(partialDeriv, nominals)
        sensitivityCoefficients[var] = sensitivity
        GUMresult += (sensitivity * uncerts[var])**2 # GUM calculation
    return math.sqrt(GUMresult), outputResult, sensitivityCoefficients


