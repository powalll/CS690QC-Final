import numpy as np
import math


def main():
    ##### Simulation Variables

    #simulation number of trials
    number_attempts = 10 ** 6

    #specified in km, total distance between two endpoints
    link_length = 100

    #whether we have symmetric repeater chain lengths
    is_symmetric = False

    num_repeaters = 10

    #Option to generate randomized asymmetric repeater chains given number of repeaters and links, only used if is_symmetric is False
    use_randomized_asymmetric = True

    #only used if not using randomized asymmetric, lets you hardcode asymmetric_link_lengths - number of elements should be # of quantum repeaters + 1
    asymmetric_link_lengths = np.array([])

    #boolean for deciding whether to use custom fidelity or allow link length to determine initial values
    use_initial_fidelity = True

    #initial fidelity for werner states
    initial_fidelity = 0.85

    #link_length = np.sum(asymmetric_link_lengths)

    simulator(number_attempts, link_length, is_symmetric, num_repeaters, use_randomized_asymmetric, asymmetric_link_lengths, use_initial_fidelity, initial_fidelity)


def simulator(number_attempts, link_length, is_symmetric, num_repeaters, use_randomized_asymmetric, asymmetric_link_lengths, use_initial_fidelity, initial_fidelity):
    ##### Variables which will be calculated based on above inputs

    #success_rate based on link distance between member in chain, will be float if symmetric and list of floats if asymmetric
    success_rate = 0

    #delay between two members in quantum chain
    time_entanglement = 0
    
    #standard constants for ket 0 and 1 
    zero = np.array([1, 0])
    one = np.array([0, 1])
    
    # Define phi plus Bell state
    phi_plus = (np.kron(zero, zero) + np.kron(one, one)) / np.sqrt(2)
    phi_plus_dm = np.outer(phi_plus, phi_plus)
    
    # generate Werner state with fidelity f
    def werner_state(f):
        p = (4 * f - 1) / 3
        identity = np.eye(4)
        return p * phi_plus_dm + (1 - p) * identity / 4

    # Tensor product of Werner states ρ_AB ⊗ ρ_BC (total 4 qubits: A,B,C,D)
    def rho_ABCD(rho_AB, rho_BC):
        return np.kron(rho_AB, rho_BC)

    # Define Bell state projector |Φ⁺⟩⟨Φ⁺| on qubits B and C (1 and 2)
    def bell_projector_BC():
        phi = (np.kron(zero, zero) + np.kron(one, one)) / np.sqrt(2)
        return np.outer(phi, phi)

    # Build full projection operator: I_A ⊗ P_BC ⊗ I_D
    def full_projector_BC():
        P_BC = bell_projector_BC()
        I_A = np.eye(2)
        I_D = np.eye(2)
        return np.kron(np.kron(I_A, P_BC), I_D)

    # Apply projection and normalize
    def apply_projection(rho_ABCD, P_full):
        rho_proj = P_full @ rho_ABCD @ P_full
        prob = np.trace(rho_proj)
        return rho_proj / prob if prob != 0 else rho_proj

    # Partial trace over qubits B and C (indices 1 and 2)
    def partial_trace_two(rho, dims, keep):
        reshaped = rho.reshape(dims + dims)
        trace_axes = [i for i in range(len(dims)) if i not in keep]
        for axis in sorted(trace_axes, reverse=True):
            reshaped = np.trace(reshaped, axis1=axis, axis2=axis + len(dims))
        final_dim = int(np.prod([dims[i] for i in keep]))
        return reshaped.reshape((final_dim, final_dim))

    # Fidelity with |Φ⁺⟩
    def fidelity_with_phi_plus(rho):
        return np.real(np.vdot(phi_plus, rho @ phi_plus))

    # Run full procedure for a chain with Werner states
    def entanglement_swapping_chain(rho_AB, rho_BC):
        # Step 1: Generate the 4-qubit state
        rho_4q = rho_ABCD(rho_AB, rho_BC)
        # Step 2: Define the Bell-state projector on qubits B and C
        P_full = full_projector_BC()
        # Step 3: Apply Bell-state measurement and projection
        rho_projected = apply_projection(rho_4q, P_full)
        # Step 4: Trace out qubits B and C (indices 1 and 2)
        rho_AD = partial_trace_two(rho_projected, [2,2,2,2], keep=[0,3])

        # Step 5: Compute fidelity with |Φ⁺⟩
        fidelity = fidelity_with_phi_plus(rho_AD)
        return fidelity, rho_AD

    #based on link length, initialize each werner state with different fidelity
    def entanglement_fidelity(L, F0=1.0, alpha=0.01, F_noise=0.25):
        return F0 * np.exp(-alpha * L) + (1 - np.exp(-alpha * L)) * F_noise
    
    initial_fidelity_values = []

    #creates randomized array for asymmetric link lengths 
    def generate_links_with_sum(num_links, link_length):
        arr = np.random.rand(num_links)
        arr = arr / arr.sum() * link_length
        return arr

    if use_randomized_asymmetric:
        asymmetric_link_lengths = generate_links_with_sum(num_repeaters + 1, link_length)

    for i in range(num_repeaters + 1):
        if use_initial_fidelity:
            initial_fidelity_values.append(initial_fidelity)
        elif is_symmetric:
            initial_fidelity_values.append(entanglement_fidelity(link_length / (num_repeaters + 1)))
        else:
            initial_fidelity_values.append(entanglement_fidelity(asymmetric_link_lengths[i]))

    werner_state_list = []
    fidelity_values = []

    print("Initial fidelity of werner states based on link length: ", end="")
    print(initial_fidelity_values)

    fidelity_values.append(initial_fidelity_values[0])

    #generate list of werner states for each link
    for i in range(num_repeaters + 1):
        werner_state_list.append(werner_state(initial_fidelity_values[i]))

    #sequentially perform entanglement swapping with each werner state in chain and calculate fidelity after
    for i in range(num_repeaters):
        fidelity, rho_AD = entanglement_swapping_chain(werner_state_list[i], werner_state_list[i + 1])
        werner_state_list[i + 1] = rho_AD
        fidelity_values.append(2 * fidelity)

    print("Fidelity values after # of repeaters: ", end="")
    print(fidelity_values)

    #Function to get Success Rate of Entanglement from Barrett-Kok based on Link Length - L_att is 22 km
    def get_success_rate(link_length):
        L_att = 22
        #divide by number of repeaters that split the overall distance
        transmissitivity_link = math.exp(-link_length / L_att)
        success_rate = (transmissitivity_link ** 2) / 2
        return success_rate

    #function to get list of success success rates for asymmetric link lengths, list of floats with length = # of repeaters + 1
    def get_list_of_success_rate(link_lengths):
        success_rate = []
        for link in link_lengths:
            success_rate.append(get_success_rate(link))
        return success_rate

    if is_symmetric:
        #use symmetric link length to get probability - divide by two because Barret-Kok scheme is used
        distance_from_repeater = (link_length / 2) / (num_repeaters + 1)
        success_rate = get_success_rate(distance_from_repeater)
        print("Success Rate: " + str(success_rate))
        #get time in seconds by dividing distance by speed of light 
        time_entanglement = (link_length / (num_repeaters + 1) * 1000) / (2*10 ** 8)
    else:
        #divide by two because Barret-Kok scheme is used
        success_rate = get_list_of_success_rate(asymmetric_link_lengths / 2)
        print("Success Rates for each link: ", end="")
        print(success_rate)
        print("Asymmetric link lengths: ", end="")
        print(asymmetric_link_lengths)
        print("Asymmetric total length: ", end="")
        print(np.sum(asymmetric_link_lengths))

    #Simulate the number of entanglement attempts for each link - the provided p will either be a float if symmetric or a list of floats if asymmetric
    entanglement_attempts = np.random.geometric(p=success_rate, size=(number_attempts, num_repeaters + 1))

    #get overall success rate of quantum repeater chain by taking successful generations over total attempts
    overall_entanglement_success_rate = (num_repeaters + 1) / np.sum(entanglement_attempts, axis=1)
    print("Mean of overall chain success rate: " + str(np.mean(overall_entanglement_success_rate)))
    print("Variance of overall chain success rate: " + str(np.var(overall_entanglement_success_rate)))

    #Use maximal tries which will be the holdover in time
    print("Maximum of entanglement attempts: ", end="")
    max_entangle_attempts = np.max(entanglement_attempts, axis=1)
    print(max_entangle_attempts)
    print("Number of runs: " + str(len(max_entangle_attempts)))

    #print variance and mean of entanglement attempts
    attempts_array = np.array(max_entangle_attempts)
    print("Variance of attempts: " + str(np.var(attempts_array)))
    print("Mean attempts: " + str(np.mean(attempts_array)))
    if is_symmetric:
        #convert attempts to time buy multiplying by time of entanglement with attempts and adding classical communication time
        final_entanglement_time = attempts_array * 2.0
        final_entanglement_time *= time_entanglement

        #add classical time to send message
        final_entanglement_time += time_entanglement 
    else:
        #time for each entanglement attempt
        time_entanglement = (asymmetric_link_lengths * 1000) / (2*10 ** 8)
        total_entanglement_time = entanglement_attempts * 1.0
        #multiply by number of attempts with respective time_entanglement to link_length
        for i in range(len(entanglement_attempts)):
            total_entanglement_time[i] = np.multiply(entanglement_attempts[i], 2 * time_entanglement) + time_entanglement
        #get largest time for entanglement which is blocker
        final_entanglement_time = np.max(total_entanglement_time, axis=1)

    print("Variance of time: " + str(np.var(final_entanglement_time)))
    print("Mean time (seconds): " + str(np.mean(final_entanglement_time)))

    results = {
        #intitialized variables
        "number_attempts": number_attempts,
        "link_length": link_length,
        "is_symmetric": is_symmetric,
        "num_repeaters": num_repeaters,
        "use_randomized_asymmetric": use_randomized_asymmetric,
        "asymmetric_link_lengths": asymmetric_link_lengths,

        #fidelity values of werner states based on initial link length
        "initial_fidelity_values": initial_fidelity_values,

        #fideility after entangling each repeater sequentially
        "fidelity_values": fidelity_values,

        #success rate of entanglement based on link length
        "link_success_rate":success_rate,
        "overall_success_rate": overall_entanglement_success_rate,
        "mean_overall_success_rate": np.mean(overall_entanglement_success_rate),
        "variance_overall_success_rate": np.var(overall_entanglement_success_rate),
        "entanglement_attempts": entanglement_attempts,

        "mean_attempts": np.mean(attempts_array),
        "variance_attempts": np.var(attempts_array),
        "mean_time": np.mean(final_entanglement_time),
        "variance_time": np.var(final_entanglement_time)
    }

    return results

if __name__=="__main__":
    main()