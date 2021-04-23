"""
==========================
Inclusion body experiments
==========================
"""

from vivarium.core.experiment import Experiment
from vivarium.core.control import Control
from vivarium.core.composition import (
    EXPERIMENT_OUT_DIR,
)

# composites
from vivarium_multibody.composites.lattice import (
    Lattice,
    make_lattice_config,
)
from inclusion.composites.inclusion_body_growth import InclusionBodyGrowth

# plots
from vivarium.plots.agents_multigen import plot_agents_multigen
from vivarium_multibody.plots.snapshots import (
    plot_snapshots, plot_tags, format_snapshot_data)

LATTICE_CONFIG = make_lattice_config(
    time_step=30,
    jitter_force=1e-4,
    bounds=[30, 30],
    n_bins=[10, 10])


def run_experiment(
        initial_biomass=1000,
        total_time=3000,
):
    agent_id = '1'
    parameters = {
        'agent_id': agent_id,
        'inclusion_process': {
            'damage_rate': 1e-4,  # rapid damage
        },
        'growth_rate': {
            'growth_rate': 0.001  # fast growth
        },
    }

    # make the agent
    agent_composer = InclusionBodyGrowth(parameters)
    agent_composite = agent_composer.generate()

    # make the environment
    composer = Lattice(LATTICE_CONFIG)
    composite = composer.generate()

    # merge in the agent
    composite.merge(
        composite=agent_composite,
        path=('agents', agent_id))

    # get initial state
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


def inclusion_plots_suite(data=None, out_dir=EXPERIMENT_OUT_DIR):
    n_snapshots = 5
    tagged_molecules = [
        ('inclusion_body',),
        ('front', 'aggregate',),
        ('back', 'aggregate',)]

    # multigen plot
    plot_settings = {}
    plot_agents_multigen(data, plot_settings, out_dir)

    # extract data for snapshots
    bounds = LATTICE_CONFIG['multibody']['bounds']
    agents, fields = format_snapshot_data(data)

    # snapshots plot
    plot_snapshots(
        bounds=bounds,
        agents=agents,
        fields=fields,
        n_snapshots=n_snapshots,
        out_dir=out_dir,
        filename='inclusion_snapshots'
    )

    # tags plot
    plot_tags(
        data=data,
        bounds=bounds,
        tagged_molecules=tagged_molecules,
        n_snapshots=n_snapshots,
        convert_to_concs=False,
        out_dir=out_dir,
    )



# libraries for control
experiments_library = {
    '1': {
        'name': 'inclusion_lattice',
        'experiment': run_experiment,
        'kwargs': {
            'total_time': 12000,
        }},
}
plots_library = {
    '1': inclusion_plots_suite
}
workflow_library = {
    '1': {
        'name': 'inclusion_body_experiment',
        'experiment': '1',
        'plots': ['1'],
    }
}

if __name__ == '__main__':
    c = Control(
        experiments=experiments_library,
        plots=plots_library,
        workflows=workflow_library,
        )
    c.run_workflow('1')
