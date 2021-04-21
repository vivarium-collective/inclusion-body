"""
==========================
Inclusion body experiments
==========================
"""

from vivarium.core.control import Control
from vivarium.core.composition import (
    compose_experiment,
    COMPOSER_KEY,
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



lattice_config = make_lattice_config(
    jitter_force=1e-4,
    bounds=[30, 30],
    n_bins=[10, 10])



def run_experiment(config={}):
    agent_id = '1'
    time_total = 12000

    inclusion_config = {
        'agent_id': agent_id,
        'damage_rate': 5e-5,
    }

    # initial state
    compartment = InclusionBodyGrowth(inclusion_config)
    compartment_state = compartment.initial_state({
        'front': {
            'aggregate': 200},
        'back': {
            'aggregate': 10}
        })
    initial_state = {
        'agents': {
            agent_id: compartment_state}}

    # declare the hierarchy
    hierarchy = {
        COMPOSER_KEY: {
            'type': Lattice,
            'config': lattice_config},
        'agents': {
            agent_id: {
                COMPOSER_KEY: {
                    'type': InclusionBodyGrowth,
                    'config': inclusion_config}}}}

    # configure experiment
    experiment = compose_experiment(
        hierarchy=hierarchy,
        initial_state=initial_state)

    # run simulation
    experiment.update(time_total)
    data = experiment.emitter.get_data()
    experiment.end()

    return data


def inclusion_plots_suite(data=None, out_dir=EXPERIMENT_OUT_DIR):
    n_snapshots = 8
    tagged_molecules = [
        ('inclusion_body',),
        ('front', 'aggregate',),
        ('back', 'aggregate',)]

    # multigen plot
    plot_settings = {}
    plot_agents_multigen(data, plot_settings, out_dir)

    # extract data for snapshots
    bounds = lattice_config['multibody']['bounds']
    agents, fields = format_snapshot_data(data)

    # snapshots plot
    plot_snapshots(
        bounds=bounds,
        agents=agents,
        fields=fields,
        # phylogeny_names=phylogeny_colors,
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
        'experiment': run_experiment},
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
    Control(
        experiments=experiments_library,
        plots=plots_library,
        workflows=workflow_library,
        )
