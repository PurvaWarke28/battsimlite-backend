import pybamm
import numpy as np

# List of allowed time-dependent variables for y-axis
TIME_DEPENDENT_VARIABLES = [
    "Voltage [V]",
    "Terminal voltage [V]",
    "Current [A]",
    "Current variable [A]",
    "C-rate",
    "Discharge capacity [A.h]",
    "Throughput capacity [A.h]",
    "Discharge energy [W.h]",
    "Throughput energy [W.h]",
    "X-averaged cell temperature [K]",
    "Volume-averaged cell temperature [K]",
    "X-averaged electrolyte concentration [mol.m-3]",
    "X-averaged battery solid phase ohmic losses [V]",
    "X-averaged battery electrolyte ohmic losses [V]",
    "Resistance [Ohm]",
    "Power [W]",
    "Terminal power [W]",
    "Loss of capacity to positive SEI [A.h]",
    "Loss of capacity to negative SEI [A.h]",
    "Loss of capacity to positive SEI on cracks [A.h]",

    "Loss of capacity to positive lithium plating [A.h]",
    "Loss of capacity to negative lithium plating [A.h]",
    "LLI [%]",
    "LAM_ne [%]",
    "LAM_pe [%]",
    "X-averaged positive electrode temperature [K]",
    "X-averaged negative electrode temperature [K]",
    "X-averaged separator temperature [K]",
    "Volume-averaged reversible heating [W.m-3]",
    "Volume-averaged irreversible electrochemical heating [W.m-3]",
    "Volume-averaged Ohmic heating [W.m-3]",
    "X-averaged reaction overpotential [V]",
    "X-averaged SEI film overpotential [V]",
    "X-averaged electrolyte potential [V]",
    "X-averaged electrolyte ohmic losses [V]",
    "X-averaged total heating [W.m-3]",
    "X-averaged positive particle surface concentration [mol.m-3]",
    "X-averaged positive electrode interfacial current density [A.m-2]",
    "X-averaged positive electrode exchange current density [A.m-2]",
    "X-averaged negative electrode exchange current density [A.m-2]",
    "X-averaged negative electrode interfacial current density [A.m-2]",
    "X-averaged negative particle surface concentration [mol.m-3]",
    "X-averaged positive electrode reaction overpotential [V]",
    "X-averaged negative electrode reaction overpotential [V]",
    "X-averaged positive electrode potential [V]",
    "X-averaged negative electrode potential [V]",
    "X-averaged solid phase ohmic losses [V]",
    "X-averaged positive electrode ohmic losses [V]",
    "X-averaged negative electrode ohmic losses [V]",
    "X-averaged positive electrode active material volume fraction",
    "X-averaged negative electrode active material volume fraction",
]

def build_experiment(C_rate_charge, C_rate_discharge, Vmax, Vmin, rest_mins, cycles, mode):
    rest_step = f"Rest for {rest_mins} minutes"

    if mode == "CC":
        steps = [
            f"Charge at {C_rate_charge}C until {Vmax}V",
            rest_step,
            f"Discharge at {C_rate_discharge}C until {Vmin}V",
            rest_step,
        ] * cycles

    elif mode == "CV":
        steps = [
            f"Charge at {C_rate_charge}C until {Vmax}V",
            f"Hold at {Vmax}V until C/50",
            rest_step,
            f"Discharge at {C_rate_discharge}C until {Vmin}V",
            rest_step,
        ] * cycles

    elif mode == "CCCV":
        steps = [
            f"Discharge at {C_rate_discharge}C until {Vmin}V",
            rest_step,
            f"Charge at {C_rate_charge}C until {Vmax}V",
            f"Hold at {Vmax}V until C/50",
            rest_step,
        ] * cycles

    else:
        raise ValueError("Unsupported mode: choose from CC, CV, CCCV")

    return pybamm.Experiment(steps)

def run_simulation(current, cycles, mode, sei_model, x_variable, y_variable):
    # Validate y_variable
    if y_variable not in TIME_DEPENDENT_VARIABLES:
        return {"error": f"'{y_variable}' is not a valid y-axis variable."}

    # Only include SEI model option if it's not None
    if sei_model is not None:
        model_options = {"SEI": sei_model}
        model = pybamm.lithium_ion.DFN(model_options)
    else:
        model = pybamm.lithium_ion.DFN()

    param = pybamm.ParameterValues("Mohtat2020")
    param.update({"SEI kinetic rate constant [m.s-1]": 1e-14})
    param.set_initial_stoichiometries(1)

    experiment = build_experiment(
        C_rate_charge=current,
        C_rate_discharge=current,
        Vmax=4.2,
        Vmin=3.0,
        rest_mins=5,
        cycles=cycles,
        mode=mode
    )

    sim = pybamm.Simulation(model, parameter_values=param, experiment=experiment)
    solution = sim.solve()

    try:
        x = solution[x_variable].entries
        y = solution[y_variable].entries
    except KeyError as e:
        return {"error": f"Variable not found: {str(e)}"}

    return {
        "x_variable": x_variable,
        "y_variable": y_variable,
        "x_data": x.tolist(),
        "y_data": y.tolist()
    }
