import numpy as np
import math

def main():
    ##### Simulation Variables

    #simulation number of trials
    number_attempts = 10 ** 6

    #specified in km, total distance between two endpoints
    link_length = 50.0

    #whether we have symmetric repeater chain lengths
    is_symmetric = False

    num_repeaters = 1

    #Option to generate randomized asymmetric repeater chains given number of repeaters and links, only used if is_symmetric is False
    use_randomized_asymmetric = False

    #only used if not using randomized asymmetric, lets you hardcode asymmetric_link_lengths - number of elements should be # of quantum repeaters + 1
    asymmetric_link_lengths = np.array([25, 25])
    #link_length = np.sum(asymmetric_link_lengths)

    simulator(number_attempts, link_length, is_symmetric, num_repeaters, use_randomized_asymmetric, asymmetric_link_lengths)


def simulator(number_attempts, link_length, is_symmetric, num_repeaters, use_randomized_asymmetric, asymmetric_link_lengths):
    ##### Variables which will be calculated based on above inputs

    #success_rate based on link distance between member in chain, will be float if symmetric and list of floats if asymmetric
    success_rate = 0

    #delay between two members in quantum chain
    time_entanglement = 0

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

    #creates randomized array for asymmetric link lengths 
    def generate_links_with_sum(num_links, link_length):
        arr = np.random.rand(num_links)
        arr = arr / arr.sum() * link_length
        return arr
    if is_symmetric:
        #use symmetric link length to get probability - divide by two because Barret-Kok scheme is used
        distance_from_repeater = (link_length / 2) / (num_repeaters + 1)
        success_rate = get_success_rate(distance_from_repeater)
        print("Success Rate: " + str(success_rate))
        #get time in seconds by dividing distance by speed of light 
        time_entanglement = (link_length / (num_repeaters + 1) * 1000) / (2*10 ** 8)
    else:
        if use_randomized_asymmetric:
            asymmetric_link_lengths = generate_links_with_sum(num_repeaters + 1, link_length)
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
        total_entanglement_time = attempts_array * 2.0
        total_entanglement_time *= time_entanglement

        #add classical time to send message
        total_entanglement_time += time_entanglement 
    else:
        #time for each entanglement attempt
        time_entanglement = 2 * (asymmetric_link_lengths * 1000) / (2*10 ** 8)
        entanglement_attempts = entanglement_attempts * 1.0
        #multiply by number of attempts with respective time_entanglement to link_length
        for i in range(len(entanglement_attempts)):
            entanglement_attempts[i] = np.multiply(entanglement_attempts[i], time_entanglement) + time_entanglement
        #get largest time for entanglement which is blocker
        total_entanglement_time = np.max(entanglement_attempts, axis=1)

    print("Variance of time: " + str(np.var(total_entanglement_time)))
    print("Mean time (seconds): " + str(np.mean(total_entanglement_time)))

if __name__=="__main__":
    main()