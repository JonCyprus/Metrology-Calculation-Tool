# This file is to contain all the logic to do a monte carlo method of error propagation.

import numpy as np
from utilities import DIVISORS
import gum
from sympy import lambdify

def sampleUniform (generator, nominal, uncertainty, sampleSize):
    halfWidth = uncertainty * DIVISORS["uniform"]
    return generator.uniform(nominal - halfWidth, nominal + halfWidth, sampleSize)

def sampleTriangular(generator, nominal, uncertainty, sampleSize):
    halfWidth = uncertainty * DIVISORS["triangular"]
    return generator.triangular(nominal - halfWidth, nominal, nominal + halfWidth, size=sampleSize)

def sampleNormal (generator, nominal, uncertainty, sampleSize):
    return generator.normal(nominal, uncertainty, size=sampleSize)

def sampleDispatch(generator, data):
    match data["distribution"]:
        case "uniform":
            return sampleUniform(generator, data["nominal"], data["uncertainty"], data["sampleSize"])
        case "triangular":
            return sampleTriangular(generator, data["nominal"], data["uncertainty"], data["sampleSize"])
        case "normal":
            return sampleNormal(generator, data["nominal"], data["uncertainty"], data["sampleSize"])
        case "-":
            return sampleNormal(generator, data["nominal"], data["uncertainty"], data["sampleSize"])
        case _:
            print("Unknown distribution")

def calcMonteCarlo(model, nominals, uncertainties, distributions, sampleSize):
    generator = np.random.default_rng() # Make a numpy generator object for MC sampling
    # Get the numpy arrays for calculations
    samplingResults = {}
    for var in model.free_symbols:
        data = {
            "nominal": nominals[var],
            "uncertainty": uncertainties[var],
            "distribution": distributions[var],
            "sampleSize": sampleSize
        }
        samplingResults[var] = sampleDispatch(generator, data)

    # Generate results by evaluating the model expression
    orderedSymbols = list(model.free_symbols) # internally consistent list
    f = lambdify(orderedSymbols, model, modules="numpy")
    output = f(*[samplingResults[var] for var in orderedSymbols])

    mcUncertainty = float(np.std(output, ddof=1))
    mcMean = float(np.mean(output))

    return mcMean, mcUncertainty