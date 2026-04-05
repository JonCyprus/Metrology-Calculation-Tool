import streamlit as st

import gum
import utilities as utils
from monteCarlo import calcMonteCarlo

st.set_page_config(
    page_title="Measurement Uncertainty Calculator",
    page_icon="📐",
    layout="wide"
)

st.title("Measurement Uncertainty Calculator")

# Model input
modelStr = st.text_input("Measurement model (equation)", placeholder = "d = m/(L*W*H)", help="Input an equation, e.g. d= m/v. Use appropriate parenthesis")
if modelStr and "=" not in modelStr:
    st.write("Please ensure that equation has '=' ")
elif modelStr:
    outputName, symbols, expr = gum.parseModel(modelStr)
    st.session_state ["outputName"] = outputName
    st.session_state ["expr"] = expr
    st.session_state ["symbols"] = symbols

# Variable inputs
if "symbols" in st.session_state:
    symbols = st.session_state["symbols"]
    inputs = {}

    # iterate over each variable
    for var in symbols.keys():
        st.subheader(f"Measurement Data for {var}")
        eval_type = st.radio("Type", ["A", "B"], key=f"type{var}", horizontal=True)

    # Taking type A inputs from user
        if eval_type == "A":
            rawCSV = st.file_uploader("Upload CSV of data", type="csv", key=f"data{var}", help="One column with or without header of data.")
            inputs[var] = {"type": "A", "raw": rawCSV, "distribution": "-"}
            for key, value in inputs[var].items():
                st.session_state[f"{var}{key}"] = value

    # Taking type B inputs from user
        elif eval_type == "B":
            nominal = st.number_input(f"Nominal of {var}", key=f"nominal{var}", help="Best estimate of the measurement")
            halfWidth = st.number_input(f"Half width of {var}", key=f"halfWidth{var}", help="e.g. 0.5 +/- 0.1 would have a half width of 0.1")
            distribution = st.selectbox("Distribution Type", utils.DISTRIBUTIONS, key=f"distribution{var}")
            if distribution == "normal":
                confidence = st.number_input(f"Confidence of {var} as a %", key=f"confidence{var}", placeholder="as %", help="The confidence level if applicable as a %")
            else:
                confidence = 100.
            inputs[var] = {"type": "B", "nominal": nominal, "halfWidth": halfWidth, "distribution": distribution, "confidence": confidence}
            for key, value in inputs[var].items():
                st.session_state[f"{var}{key}"] = value

    st.subheader("Sample size for Monte Carlo Approach")
    mcSampleSize = st.number_input("Sample Size for Monte Carlo Calculation.",
                                   min_value=1, value=1000, step=1,
                                   help="The number of times MC will be run for estimating the uncertainty in the output. Must be an integer")
    st.session_state["mcSampleSize"] = mcSampleSize


# Calculate
if st.button("Calculate"):
    #parse inputs, call gum + monte carlo, show results
    symbols = st.session_state["symbols"]
    inputNominals = {}
    inputUncerts = {}
    inputDistributions = {}

    budgetData = {}
    # Calculate for inputs
    for var in symbols.keys():
        uncType = st.session_state[f"{var}type"]
        st.subheader(f"Statistics of {var} using Type {uncType}")
        if uncType == "A":
            data = utils.loadCSV(st.session_state[f"{var}raw"])
            mean, unc = utils.calculateTypeAUncertainty(data)
            st.session_state[f"{var}nominal"] = mean
            st.session_state[f"{var}uncertainty"] = unc
        elif uncType == "B":
            mean = st.session_state[f"{var}nominal"]
            unc = utils.calculateTypeBUncertainty(st.session_state[f"{var}halfWidth"],
                                                  st.session_state[f"{var}distribution"],
                                                  st.session_state[f"{var}confidence"])
            st.session_state[f"{var}uncertainty"] = unc
        # Collect nominals and uncertainties for GUM calculations
        # For GUM and MC Calculation Function
        inputNominals[symbols[var]] = st.session_state[f"{var}nominal"]
        inputUncerts[symbols[var]] = st.session_state[f"{var}uncertainty"]
        inputDistributions[symbols[var]] = st.session_state[f"{var}distribution"]

        budgetData[var] = {
            "nominal": st.session_state[f"{var}nominal"],
            "uncertainty": st.session_state[f"{var}uncertainty"],
            "coeff": 0,
            "type": st.session_state[f"{var}type"],
            "distribution": st.session_state[f"{var}distribution"],
        }
        st.write(f"Mean Value: {st.session_state[f"{var}nominal"]: .6f}") # round to 6 digits
        st.write(f"Standard Uncertainty: {st.session_state[f"{var}uncertainty"]: .6f}") # round to 6 digits

    # Calculate GUM uncertainty
    outputUncert, outputResult, sensitivityCoeffs = gum.calculateGUM(st.session_state["expr"], inputNominals, inputUncerts)
    for var in budgetData.keys():
        budgetData[var]["coeff"] = sensitivityCoeffs[symbols[var]]
    st.subheader("GUM Calculation Results")
    st.metric(f"Output Mean Value of {st.session_state["outputName"]}", f"{outputResult:.6f}")
    st.metric(f"Combined Uncertainty (uc) of {st.session_state["outputName"]}", f"{outputUncert:.6f}")
    st.metric(f"Expanded Uncertainty (U) of {st.session_state["outputName"]} (95% Confidence)", f"{outputUncert * 2:.6f}")

    # Uncertainty Budget (Table)
    st.subheader("Uncertainty Budget")
    budgetTable = utils.buildBudgetTable(budgetData, outputResult, st.session_state["outputName"])
    st.dataframe(budgetTable, width='stretch')

    # Calculate Uncertainty using Monte Carlo Approach

    mcMean, mcUnc = calcMonteCarlo(st.session_state["expr"], inputNominals, inputUncerts, inputDistributions, st.session_state["mcSampleSize"])
    st.subheader(f"Monte Carlo Results (Sample Size: {st.session_state['mcSampleSize']})")
    st.metric(f"Output Mean Value of {st.session_state["outputName"]}", f"{mcMean:.6f}")
    st.metric(f"Combined Uncertainty (uc) of {st.session_state["outputName"]}", f"{mcUnc:.6f}")
    st.metric(f"Expanded Uncertainty (U) of {st.session_state["outputName"]}", f"{mcUnc * 2:.6f}")
