import numpy as np
import matplotlib.pyplot as plt
from simulator import simulator

def evaluate_initfidelity_performance(link_length=100, num_repeaters=2, min_init=0.5, max_init=1.0, step=0.02):
    init_fidelities = np.arange(min_init, max_init + step, step)
    final_fidelities = [] 
    for init_f in init_fidelities:
        print(f"Simulating with initial fidelity: {init_f:.2f}")
        results = simulator(
            number_attempts=10**6,
            link_length=link_length,
            is_symmetric=True,
            num_repeaters=num_repeaters,
            use_randomized_asymmetric=False,
            asymmetric_link_lengths=np.array([]),
            use_initial_fidelity=True,
            initial_fidelity=init_f
        )
        final_fidelities.append(results['fidelity_values'][-1])
        print(f"Final Fidelity: {final_fidelities[-1]:.4f}")
        print()
    # Plot results
    plt.figure(figsize=(7, 5))
    plt.plot(init_fidelities, final_fidelities, 'b-o')
    plt.xlabel('Initial Fidelity')
    plt.ylabel('Final Fidelity')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('finalfidelity_vs_initfidelity.png')
    plt.close()


if __name__ == "__main__":
    evaluate_initfidelity_performance() 