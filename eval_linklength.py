import numpy as np
import matplotlib.pyplot as plt
from simulator import simulator

def evaluate_linklength_successrate(min_length=50, max_length=400, step=50, num_repeaters=2):
    """
    Evaluate how the success rate changes with link length in the symmetric case.
    
    Parameters:
    min_length: Minimum total link length (km)
    max_length: Maximum total link length (km)
    step: Step size for link length (km)
    num_repeaters: Number of repeaters (fixed)
    """
    link_lengths = np.arange(min_length, max_length + 1, step)
    success_rates = []
    
    print(f"\nEvaluating success rate vs link length (Repeaters: {num_repeaters})")
    print("=" * 60)
    
    for link_length in link_lengths:
        print(f"Simulating with link length: {link_length} km")
        results = simulator(
            number_attempts=10**6,
            link_length=link_length,
            is_symmetric=True,
            num_repeaters=num_repeaters,
            use_randomized_asymmetric=False,
            use_initial_fidelity=True,
            initial_fidelity=0.85,
            asymmetric_link_lengths=np.array([])
        )
        mean_success_rate = np.mean(results['overall_success_rate'])
        success_rates.append(mean_success_rate)
        print(f"Mean Success Rate: {mean_success_rate:.4f}")
    
    # Plot results
    plt.figure(figsize=(7, 5))
    plt.plot(link_lengths, success_rates, 'b-o')
    plt.xlabel('Total Link Length (km)')
    plt.ylabel('Mean Success Rate')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('successrate_vs_linklength.png')
    plt.close()


if __name__ == "__main__":
    evaluate_linklength_successrate() 