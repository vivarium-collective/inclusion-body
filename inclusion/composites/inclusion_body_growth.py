"""
========================
Inclusion body composite
========================
"""

import os

from vivarium.core.process import Composer
from vivarium.core.experiment import Experiment
from vivarium.core.composition import (
    simulate_composite,
    COMPOSITE_OUT_DIR,
)
from vivarium.plots.agents_multigen import plot_agents_multigen
from vivarium.plots.topology import plot_topology

# processes
from vivarium.processes.meta_division import MetaDivision
from vivarium.processes.ecoli_shape_deriver import EcoliShape
from vivarium.processes.growth_rate import GrowthRate
from vivarium.processes.divide_condition import DivideCondition

from inclusion.processes.inclusion_body import InclusionBody



NAME = 'inclusion_body_growth'


class InclusionBodyGrowth(Composer):

    defaults = {
        'inclusion_process': {},
        'growth_rate': {
            'variables': ['biomass']},
        'divide_condition': {
            'threshold': 3000},
        'mass': {},
        'boundary_path': ('boundary',),
        'agents_path': ('..', '..', 'agents',),
        'daughter_path': tuple(),
        'initial_state_config': {
            'inclusion_process': {
                'initial_mass': 10},
            'growth_rate': {
                'initial_mass': 1200}}}

    def __init__(self, config):
        super().__init__(config)

    def generate_processes(self, config):
        # division config
        daughter_path = config['daughter_path']
        agent_id = config['agent_id']
        division_config = dict(
            config.get('division', {}),
            daughter_path=daughter_path,
            agent_id=agent_id,
            composer=self)

        return {
            'inclusion_process': InclusionBody(config['inclusion_process']),
            'growth_rate': GrowthRate(config['growth_rate']),
            'globals_deriver': EcoliShape({}),
            'divide_condition': DivideCondition(config['divide_condition']),
            'division': MetaDivision(division_config)
        }

    def generate_topology(self, config):
        boundary_path = config['boundary_path']
        agents_path = config['agents_path']
        return {
            'inclusion_process': {
                'front': ('front',),
                'back': ('back',),
                'inclusion_body': ('inclusion_body',),
                'molecules': ('molecules',),
            },
            'growth_rate': {
                'variables': ('molecules',),  # TODO -- should this be something specific within molecules?
                'rates': ('rates',),
            },
            'globals_deriver': {
                'global': boundary_path
            },
            'divide_condition': {
                'variable': ('molecules', 'biomass',),
                'divide': boundary_path + ('divide',),
            },
            'division': {
                'global': boundary_path,
                'agents': agents_path
            },
        }


def test_inclusion_body(
        total_time=1000,
        initial_biomass=1000,
):
    agent_id = '0'
    parameters = {
        'agent_id': agent_id,
        'inclusion_process': {
            'damage_rate': 1e-4,  # rapid damage
        },
        'growth_rate': {
            'growth_rate': 0.001  # fast growth
        },
    }
    composer = InclusionBodyGrowth(parameters)
    composite = composer.generate(path=('agents', agent_id))

    initial_state = composite.initial_state()
    initial_state['agents'][agent_id]['molecules'] = {'biomass': initial_biomass}

    # make the experiment
    inclusion_experiment = Experiment({
        'processes': composite['processes'],
        'topology': composite['topology'],
        'initial_state': initial_state
    })

    # run the experiment
    inclusion_experiment.update(total_time)

    # get the data
    data = inclusion_experiment.emitter.get_data()

    return data

def run_composite(out_dir='out'):
    data = test_inclusion_body(total_time=4000)
    plot_settings = {}
    plot_agents_multigen(data, plot_settings, out_dir)

def plot_inclusion_topology(out_dir='out'):
    agent_id = '1'
    # make a topology network plot
    plot_topology(
        composite=InclusionBodyGrowth({
            'agent_id': agent_id,
        }).generate(path=('agents', agent_id)),
        settings={},
        out_dir=out_dir,
        filename='inclusion_topology.pdf')


if __name__ == '__main__':
    out_dir = os.path.join(COMPOSITE_OUT_DIR, NAME)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    plot_inclusion_topology(out_dir=out_dir)
    run_composite(out_dir=out_dir)
