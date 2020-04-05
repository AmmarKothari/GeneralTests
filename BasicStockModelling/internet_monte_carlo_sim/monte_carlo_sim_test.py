from internet_monte_carlo_sim import monte_carlo_sim
import numpy as np


def test_basic():
    # prepare the data
    configuration = monte_carlo_sim.MonteCarloConfig(10, 1)  # config
    trade = monte_carlo_sim.OptionTrade(200, 200, 0.15, 0.1, 1)  # trade
    model = monte_carlo_sim.GBMModel(configuration)
    simulator = monte_carlo_sim.MonteCarloEngineSimulator(configuration, model)

    # simulate price
    price = simulator.simulate(trade)
    assert not np.isclose(price, 0.0)
