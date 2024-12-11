import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog

# Generate a random probability matrix --------->
def generate_random_matrix(size):
    """
    Generate a random matrix with normalized probabilities.
    Each row sums to 1.
    """
    matrix = np.random.rand(size, size)
    matrix = matrix / matrix.sum(axis=1, keepdims=True)  # Normalize each row to sum to 1
    return matrix


# Cartesian Product function to generate all state paths
def cartesian_product(states, length):
    paths = [[]]
    for _ in range(length):
        new_paths = []
        for path in paths:
            for state in states:
                new_paths.append(path + [state])
        paths = new_paths
    return paths

def calculate_probability(seq_states, seq_emissions, states, emissions, transition_matrix, emission_matrix, initial_probabilities):
    # will calculate the probability of a specific path of states given a sequence of emissions

    # Find the index of the first state in the sequence
    first_state_index = states.index(seq_states[0])

    # Find the index of the first emission in the sequence
    first_emission_index = emissions.index(seq_emissions[0])

    # Initialize probability with the initial state and emission probability
    probability_of_path = initial_probabilities[first_state_index] * emission_matrix[first_state_index][first_emission_index]

    # go through each sequence to calculate the total probability
    for i in range(1, len(seq_states)):
        current_state = seq_states[i - 1]
        next_state = seq_states[i]
        current_emission = seq_emissions[i]
        
    for i in range(1, len(seq_states)):
        current_state = seq_states[i - 1]
        next_state = seq_states[i]
        current_emission = seq_emissions[i]

        current_state_index = states.index(current_state)
        next_state_index = states.index(next_state)
        emission_index = emissions.index(current_emission)

        # Update probability with scaling
        transition_prob = transition_matrix[current_state_index][next_state_index]
        emission_prob = emission_matrix[next_state_index][emission_index]
        if transition_prob == 0 or emission_prob == 0:
            return 0  # If zero probability, stop further calculations
        probability_of_path *= transition_prob * emission_prob

        # Scaling for stability
        if probability_of_path < 1e-10:
            probability_of_path *= 1e10


    return probability_of_path

# Calculate all paths and their probabilities
def calculate_all_paths(emission_sequence, states, emissions, transition_matrix, emission_matrix, initial_probabilities):
    # Generate all possible state sequences of the same length as the emission sequence
    all_paths = cartesian_product(states, len(emission_sequence))
    paths_with_probs = []

    # Calculate probability for each path
    for path in all_paths:
        # removed the check if transition is possible
        prob = calculate_probability(path, emission_sequence, states, emissions, transition_matrix, emission_matrix, initial_probabilities)
        paths_with_probs.append((path, prob))
    
    # Sort paths by probability in descending order
    paths_with_probs.sort(key=lambda x: x[1], reverse=True)

    return paths_with_probs

# adjust the matrix per the rubric of the homework
def adjust_matrix(matrix, row, col, value):
    matrix[row][col] = value
    return matrix

# Display matrices
def display_matrix(matrix, matrix_name):
    print(f"{matrix_name}:")
    for row in matrix:
        print(" ".join(f"{val:.3f}" for val in row))
    print("\n")

# GUI
def main():
    # Generate and save 100 test emission and state sequences
    
    #file_path = "hmm_data_structure.txt"
    #num_states, num_emissions, initial_probabilities, transition_matrix, emission_matrix = read_hmm_data_structure(file_path)
    #states = ["S1", "S2", "S3"]  # the allowed states
    #emissions = ["rainy", "sunny", "cloudy"]  # the allowed emissions
    root = tk.Tk()
    root.title("HMM Probability Calculator")

    #----------------------------------> dialogue box stuff
    tk.Label(root, text="Enter any State Sequence (e.g., S1 S2 S3):").grid(row=0, column=0)
    state_entry = tk.Entry(root, width=30)
    state_entry.grid(row=0, column=1)

    tk.Label(root, text="Enter Emission Sequence (e.g., rainy sunny cloudy or x y z etc):").grid(row=1, column=0)
    emission_entry = tk.Entry(root, width=30)
    emission_entry.grid(row=1, column=1)

    paths_label = tk.Label(root, text="", fg="blue", wraplength=700)
    paths_label.grid(row=3, column=0, columnspan=2)
    #----------------------------------> end of dialogue box stuff

    def calculate():
        seq_states = state_entry.get().strip().split()
        seq_emissions = emission_entry.get().strip().split()
        global transition_matrix, emission_matrix

        if not seq_states or not seq_emissions:
            messagebox.showerror("Error", "Please provide both states and emissions.")
            return

        if len(seq_emissions) != len(seq_states):
            messagebox.showerror("Error", "The number of emissions must match the number of states.")
            return

        # Get the number of states and emissions
        num_states = len(seq_states)
        num_emissions = len(seq_emissions)

        # Generate random initial probabilities and matrices
        initial_probabilities = np.random.rand(num_states)
        initial_probabilities += 1e-5 # to avaid really small numbers
        initial_probabilities /= initial_probabilities.sum()  # Normalize to sum to 1
        print("my initial probabilities", initial_probabilities)

        transition_matrix = generate_random_matrix(num_states)
        emission_matrix = generate_random_matrix(num_states)

        # Display matrices
        display_matrix(transition_matrix, "Transition Matrix")
        display_matrix(emission_matrix, "Emission Matrix")

        # Calculate all paths
        paths_with_probs = calculate_all_paths(seq_emissions, seq_states, seq_emissions, transition_matrix, emission_matrix, initial_probabilities)
        print("Most probable path", paths_with_probs[0])
        # Display results
        result_text = "All Paths with Probabilities:\n"
        for path, prob in paths_with_probs:
            result_text += f"{' -> '.join(path)}: {prob:.5f}\n"

        if paths_with_probs:
            most_probable_path = paths_with_probs[0]
            result_text += f"\nMost Probable Path: {' -> '.join(most_probable_path[0])} with Probability {most_probable_path[1]:.5f}"
        else:
            result_text += "\nNo valid paths found."

        paths_label.config(text=result_text)

    #---------------------------------> UI stuff to adjust the matrix
    def prompt_adjust_matrix():
        adjustment = simpledialog.askstring("Adjust Matrix", "Enter matrix type (transition/emission), row, col, value (e.g., 'transition 1 2 0.5'):")
        if adjustment:
            try:
                matrix_type, row, col, value = adjustment.split()
                row, col = int(row), int(col)
                value = float(value)
                if matrix_type.lower() == "transition":
                    adjusted_matrix = adjust_matrix(transition_matrix, row, col, value)
                    display_matrix(adjusted_matrix, "Adjusted Transition Matrix")
                elif matrix_type.lower() == "emission":
                    adjusted_matrix = adjust_matrix(emission_matrix, row, col, value)
                    display_matrix(adjusted_matrix, "Adjusted Emission Matrix")

                else:
                    messagebox.showerror("Error", "Invalid matrix type. Use 'transition' or 'emission'.")
                    return
                messagebox.showinfo("Success", f"{matrix_type.capitalize()} Matrix updated at ({row}, {col}) with {value}.")
            except ValueError:
                messagebox.showerror("Error", "Invalid format. Use (matrix type, row, col, value).")
        #---------------------------------> UI stuff to adjust the matrix
        
    calculate_button = tk.Button(root, text="Calculate All Paths", command=calculate)
    calculate_button.grid(row=2, column=0, columnspan=2, pady=5)
    adjust_button = tk.Button(root, text="Adjust Matrix", command=prompt_adjust_matrix)
    adjust_button.grid(row=2, column=1, pady=5)
    root.mainloop()

if __name__ == "__main__":
    main()
