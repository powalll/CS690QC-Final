import numpy as np
import matplotlib.pyplot as plt
from simulator import simulator

def evaluate_repeater_performance(link_length, max_repeaters=10):
    repeater_numbers = range(1, max_repeaters + 1)
    
    # Symmetric results
    sym_fidelities = []
    sym_times = []
    sym_success_rates = []
    
    # Asymmetric results
    asym_fidelities = []
    asym_times = []
    asym_success_rates = []
    
    print(f"\nEvaluating Repeater Chains (Link Length: {link_length} km)")
    print("=" * 60)
    
    # Simulate for each repeater number
    for num_repeaters in repeater_numbers:
        print(f"\nSimulating with {num_repeaters} repeaters")
        print("-" * 40)
        
        # Symmetric 
        print("Symmetric")
        sym_results = simulator(
            number_attempts=10**6,
            link_length=link_length,
            is_symmetric=True,
            num_repeaters=num_repeaters,
            use_randomized_asymmetric=False,
            asymmetric_link_lengths=np.array([]),
            use_initial_fidelity=True,
            initial_fidelity=0.85
        )
        
        sym_fidelities.append(sym_results['fidelity_values'][-1])
        sym_times.append(sym_results['mean_time'])
        sym_success_rates.append(np.mean(sym_results['overall_success_rate']))
        
        print(f"Final Fidelity: {sym_fidelities[-1]:.4f}")
        print(f"Mean Time: {sym_times[-1]:.4f} seconds")
        print(f"Success Rate: {sym_success_rates[-1]:.4f}")
        
        # Asymmetric 
        print("\nRandom Asymmetric")
        asym_results = simulator(
            number_attempts=10**6,
            link_length=link_length,
            is_symmetric=False,
            num_repeaters=num_repeaters,
            use_randomized_asymmetric=True,
            asymmetric_link_lengths=np.array([]),
            use_initial_fidelity=True,
            initial_fidelity=0.85
        )
        
        asym_fidelities.append(asym_results['fidelity_values'][-1])
        asym_times.append(asym_results['mean_time'])
        asym_success_rates.append(np.mean(asym_results['overall_success_rate']))
        
        print(f"Final Fidelity: {asym_fidelities[-1]:.4f}")
        print(f"Mean Time: {asym_times[-1]:.4f} seconds")
        print(f"Success Rate: {asym_success_rates[-1]:.4f}")
    
    # Plot results
    plt.figure(figsize=(15, 5))
    
    # Final Fidelity
    plt.subplot(131)
    plt.plot(repeater_numbers, sym_fidelities, 'b-o', label='Symmetric')
    plt.plot(repeater_numbers, asym_fidelities, 'r-o', label='Random Asymmetric')
    plt.xlabel('Number of Repeaters')
    plt.ylabel('Final Fidelity')
    plt.grid(True)
    plt.legend()
    
    # Mean Time
    plt.subplot(132)
    plt.plot(repeater_numbers, sym_times, 'b-o', label='Symmetric')
    plt.plot(repeater_numbers, asym_times, 'r-o', label='Random Asymmetric')
    plt.xlabel('Number of Repeaters')
    plt.ylabel('Mean Time (seconds)')
    plt.grid(True)
    plt.legend()
    
    # Success Rate
    plt.subplot(133)
    plt.plot(repeater_numbers, sym_success_rates, 'b-o', label='Symmetric')
    plt.plot(repeater_numbers, asym_success_rates, 'r-o', label='Random Asymmetric')
    plt.xlabel('Number of Repeaters')
    plt.ylabel('Mean Success Rate')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('repeater_comparison_analysis.png')
    plt.close()

if __name__ == "__main__":
    link_length = 100.0
    evaluate_repeater_performance(link_length)
