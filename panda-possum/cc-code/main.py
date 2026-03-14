"""
Last modified by Lucas on Feb 4, 2026

Written and tested by Albert, Elorie, Folu, John, and Lucas (2T6 Hull & Structural Directors)
Used Claude Sonnet 4.5 for assistance with code optimization.

This module will serve as the main entry point for the PANDA-POSSUM 2T6 codebase.
It will import the necessary modeules/classes and coordinate the overall workflow.
This includes reading input files, initializing the Canoe class, and executing calculations.

"""

import canoe
import math_utils
import revised_possum_calc
import pandas as pd
import itertools
import numpy as np
from multiprocessing import Pool, cpu_count
from functools import partial

# import Path to make paths compatible across OS
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

def score(loadcase, canoe):                         # Should use Gaussian for scoring based on input weight, standard dev, and target value
    score = 0
    for weight in loadcase.weights_df.index:
        target_mean = loadcase.weights_df.loc[weight, "target value"]
        target_std = loadcase.weights_df.loc[weight, "std dev"]
        actual_value = loadcase.weights_df.loc[weight, "Actual Value"] 
        weight_factor = loadcase.weights_df.loc[weight, "weight"] 

        score += weight_factor * math_utils.gaussian(target_mean, target_std, actual_value)

        normalized_score = 10*(score / loadcase.weights_df["weight"].sum())  # Normalize by total weight to a score out of 10
    
    return normalized_score

def create_inputs(canoe_df):

    # add a column called step to the dataframe
    canoe_df['step'] = canoe_df.apply(
        lambda row: (row['Max'] - row['Min']) / (row['Iterations'] - 1) if row['Iterations'] > 1 else 0,
        axis=1
    )

    # add a column that holds a list of all possible values for that dimension
    canoe_df['values'] = canoe_df.apply(
        lambda row: [row['Min'] + i * row['step'] for i in range(int(row['Iterations']))],
        axis=1
    )

    # for each dimension, we now have a list of possible values
    print("\nCanoe DataFrame with step and values columns:")
    print(canoe_df)

    # now we loop through all combinations of these values to create canoe variants
    dimension_values = canoe_df['values'].tolist()
    all_combinations = list(itertools.product(*dimension_values))
    print(f"\nTotal canoe variants to process: {len(all_combinations)}")

    return all_combinations

def analyze_canoe_variant(variant, loadcases):
    """Helper function for parallel processing"""
    try:
        curr_canoe = canoe.Canoe(
            L=variant[0], 
            Lp=variant[1], 
            Ld=variant[2], 
            Lf=variant[3], 
            W=variant[4], 
            t1=variant[5], 
            t2=variant[6], 
            d=variant[7],
            b=variant[8], 
            s=variant[9], 
            f=variant[10],
            n=variant[11],
            density=variant[12],
            bowpower=4,
            sternpower=4
        )

        flag, outputs, loadcases_array, actualbeam, hull_weight, surfacearea, cmx = curr_canoe.analyze_all(loadcases)
        
        scores = []
        for loadcase in loadcases_array:
            curr_score = score(loadcase, curr_canoe)
            scores.append(curr_score if curr_score else 0)
        
        return {
            'variant': str(tuple(float(x) for x in variant)),
            'scores': scores,
            'success': flag == 0
        }
    
    except Exception as e:
        return {
            'variant': str(variant),
            'scores': [0] * len(loadcases),
            'success': False,
            'error': str(e)
        }

def process_loadcases():

    ### LOADCASES ###
    num_loadcases = 3 # TO BE CHANGED BASED ON INPUT
    loadcases = []  
    input_path = DATA_DIR / "input.xlsx"
    loadcase_data = pd.read_excel(input_path, "loadcase")
    for i in range(num_loadcases):
        # B3 : E7
        # defined as rows, cols
        loadcase_paddlers_df = loadcase_data.iloc[1:6, 1+i*5:5+i*5].dropna(how='all')
        loadcase_paddlers_df.columns = loadcase_paddlers_df.iloc[0]
        loadcase_paddlers_df = loadcase_paddlers_df.iloc[1:]
        loadcase_paddlers_df = loadcase_paddlers_df.reset_index(drop=True)
        
        # set the first column (assumed to be paddler name) as the index so .loc[...] by paddler label works
        if not loadcase_paddlers_df.empty:
            first_col = loadcase_paddlers_df.columns[0]
            loadcase_paddlers_df = loadcase_paddlers_df.set_index(first_col)

       
        loadcase_weights_df = loadcase_data.iloc[7:17, 1+i*5:5+i*5]
        loadcase_weights_df.columns = loadcase_weights_df.iloc[0]
        loadcase_weights_df = loadcase_weights_df.iloc[1:]
        loadcase_weights_df = loadcase_weights_df.reset_index(drop=True)

        if not loadcase_weights_df.empty:
            first_col = loadcase_weights_df.columns[0]
            loadcase_weights_df = loadcase_weights_df.set_index(first_col)


        loadcase_backwards_df = loadcase_data.iloc[18:21, 1+i*5:5+i*5]
        loadcase_backwards_df.columns = loadcase_backwards_df.iloc[0]
        loadcase_backwards_df = loadcase_backwards_df.iloc[1:]
        loadcase_backwards_df = loadcase_backwards_df.reset_index(drop=True)

        if not loadcase_backwards_df.empty:
            first_col = loadcase_backwards_df.columns[0]
            loadcase_backwards_df = loadcase_backwards_df.set_index(first_col)


        print("=====================")
        print(f"Loadcase {i+1}:")
        print(loadcase_paddlers_df)
        print(loadcase_weights_df)
        print(loadcase_backwards_df)  

        if loadcase_backwards_df.loc["Drag"].isnull().all():
            print(f"Loadcase {i+1} has no backwards drag data.")
            curr_loadcase = canoe.Loadcase(paddlers_df=loadcase_paddlers_df, 
                                       weights_df=loadcase_weights_df
                                    )
        else:
            curr_loadcase = canoe.Loadcase(paddlers_df=loadcase_paddlers_df, 
                                       weights_df=loadcase_weights_df,
                                       back_weights_df=loadcase_backwards_df # note that this still contain the true/false line
                                    )
        
        loadcases.append(curr_loadcase)

    return loadcases


def UserInterface():
    # prompt user to choose UI single or UI bulk
    input_type = input("Enter 'single' for single canoe analysis or 'bulk' for bulk canoe analysis: ").strip().lower()
    if input_type.lower() == 'single':single_canoe_UI()
    elif input_type.lower() == 'bulk':bulk_canoe_UI()
    else:
        print("Invalid input. Please enter 'single' or 'bulk'.")
        UserInterface()

def single_canoe_UI():
    print("Single canoe UI selected.")

    ### CANOE INPUTS ###
    length = float(input("Enter canoe length (L) in meters: "))
    Lp = float(input("Enter length of paddler box (Lp) in meters: "))
    Ld = float(input("Enter canoe length to deepest point (Ld) in meters: "))
    Lf = float(input("Enter canoe length to front of paddler box (Lf) in meters: "))
    width = float(input("Enter canoe width (W) in meters: "))
    t1 = float(input("Enter bow shape parameter (t1) in meters: "))
    t2 = float(input("Enter stern shape parameter (t2) in meters: "))
    d = float(input("Enter canoe depth (d) in meters: "))
    b = float(input("Enter canoe bow rocker (b) in meters: "))
    s = float(input("Enter canoe stern rocker (s) in meters: "))
    n = float(input("Enter canoe shape parameter (n): "))
    f = float(input("Enter canoe flare angle (f): "))
    density = float(input("Enter concrete density (kg/m^2): "))
    bowpower = float(input("Enter canoe bow power (bowpower) (if unsure use 4): "))
    sternpower = float(input("Enter canoe stern power (sternpower) (if unsure use 4): "))

    our_canoe = canoe.Canoe(
        L=length, 
        Lp=Lp, 
        Ld=Ld, 
        Lf=Lf, 
        W=width, 
        t1=t1, 
        t2=t2, 
        d=d,  
        b=b, 
        s=s, 
        f=f, 
        n=n,
        density=density, 
        bowpower=bowpower, 
        sternpower=sternpower
    )

    print("Canoe created. Proceeding to analysis...")

    ### ANALYSIS MENU ###
    user_input = input("(1) Analyze all aspects\n(2) Output mesh\n(3) Calculate resistance\n(4) Back to main menu\n\nEnter your choice: ").strip()

    if user_input == '1':
        print("Analyzing all aspects...")
        print("Taking in loadcases...")

        loadcases = process_loadcases()

        # TODO: clarify the way we are treating the output here
        try:
            flag, outputs, loadcases_array, actualbeam, hull_weight, surfacearea, cmx = our_canoe.analyze_all(loadcases)
            if flag == 1:
                print("LEAK - Analysis could not be completed due to errors.")
                return
        except Exception as e:
            print(f"Leak during analysis: {e}")
            return
        
        # print everything to output file
        print("Canoe Data:")
        print("Input Values:")
        print("Length (L): ", our_canoe.Length)
        print("Nominal Beam (W): ", our_canoe.Width)
        print("Depth (d): ", our_canoe.depth)
        print("Nominal Flare Angle: ", our_canoe.flare)
        print("Length to Deepest Point: ", our_canoe.Length_deepest)
        print("Length to First Paddler: ", our_canoe.Length_first)
        print("Length to Last Paddler: ", our_canoe.Length_paddler)
        print("Shape Parameter: ", our_canoe.shape_param)
        print("Bow Rocker: ", our_canoe.b_rocker)
        print("Stern Rocker: ", our_canoe.s_rocker)
        print("Area Density: ", our_canoe.density)

        print("Loadcases")
        for idx, lc in enumerate(loadcases_array):
            print(f"Loadcase {idx+1} Paddlers:")
            print(lc.paddlers_df)
            print("Centre of mass: ", lc.vertCenterMass())
            print(f"Loadcase {idx+1} Weights:")
            print(lc.weights_df)
            if lc.back_weights_df is not None:
                print(f"Loadcase {idx+1} Backward Weights:")
                print(lc.back_weights_df)
    
        print("Outputs:")
        print("Surface Area: ", surfacearea)
        print("Actual Beam: ", actualbeam)
        print("Hull Weight: ", hull_weight)
        print("Hull Center of Mass (Longitudinal): ", cmx)              # This will vary based on each loadcase? maybe it needs to be in the for loop below?
        
        # outputting results for loadcases, actual values (from weights_df)
        for idx, lc in enumerate(loadcases):
            print(f"Loadcase {idx+1} Actual Values:")
            print(lc.weights_df["Actual Value"])

        single_canoe_UI()


    elif user_input == '2':
        print("Outputting mesh...")
        try:
            our_canoe.output_mesh("canoe_mesh_output.obj")
            print("Mesh output complete. Check canoe_mesh_output.obj file.")
        except Exception as e:
            print(f"Error outputting mesh: {e}")
        
        single_canoe_UI()

    elif user_input == '3':
        print("Calculating resistance...")
        speed = float(input("Enter speed in m/s: "))
        freeboard = float(input("Enter freeboard in meters: "))
        resistance = our_canoe.get_friction(freeboard, speed)
        print(f"Calculated resistance at {speed} m/s and {freeboard} m freeboard: {resistance} N")

        single_canoe_UI()

    elif user_input == '4':
        print("Returning to main menu...")
        UserInterface()

    else:
        print("Invalid input. Returning to main menu...")
        
    return


def bulk_canoe_UI():
    print("Bulk canoe UI selected.")
    
    user_input = input("(1) Analyze from an existing input setup file\n(2) Back to main menu\n\n")

    if user_input == '1':
        print("Analyzing from existing input setup file...")

        loadcases = process_loadcases()

        counter = 1
        user_input_possum = '1'
        
        while user_input_possum == '1':
            
            input_path = DATA_DIR / "input.xlsx"
            canoe_df = pd.read_excel(input_path, "canoe")

            if not canoe_df.empty:
                print(f"\nStarting iteration {counter}")
            
                first_col = canoe_df.columns[0]
                canoe_df = canoe_df.set_index(first_col)
                print("\n")
                print("Canoe DataFrame loaded successfully:")
                print(canoe_df.head())

                all_combinations = create_inputs(canoe_df)
                total_variants = len(all_combinations)
                print(f"\nAnalyzing {total_variants} canoe variants using {cpu_count()} CPU cores...")

                # Parallel processing
                scores_data = []
            
                # Use partial to pass loadcases to the worker function
                analyze_func = partial(analyze_canoe_variant, loadcases=loadcases)
            
                # Process in parallel with progress updates
                batch_size = max(1, total_variants // 10)  # Update progress every 10%
            
                with Pool(processes=cpu_count()) as pool:
                    for idx, result in enumerate(pool.imap(analyze_func, all_combinations), 1):
                        scores_data.append(result)
                    
                        if idx % batch_size == 0 or idx == total_variants:
                            print(f"Progress: {idx}/{total_variants} ({100*idx//total_variants}%)")

                # Create scores DataFrame
                scores_df = pd.DataFrame([
                    {
                        'Canoe Variant': result['variant'],
                        **{f'Loadcase {i+1} Score': result['scores'][i] for i in range(len(loadcases))},
                        'Success': result['success']
                    }
                    for result in scores_data
                ])

                # Calculate average and sort
                score_cols = [f'Loadcase {i+1} Score' for i in range(len(loadcases))]
                scores_df['Average Score'] = scores_df[score_cols].mean(axis=1)
                scores_df = scores_df.sort_values(by='Average Score', ascending=False)

                # Output results
                output_path = DATA_DIR / "output.csv"
                scores_df.to_csv(output_path, index=False)
            
                print(f"\nBulk analysis complete!")
                print(f"Results saved to {output_path}")
                print(f"Successful analyses: {scores_df['Success'].sum()}/{total_variants}")
                
                # Iteration restarted if user desires
                user_input_possum = input("(1) Run next iteration\n(2) Quit bulk analysis\n\n")
                if user_input_possum == '1':
                    counter += 1
                    revised_possum_calc.main()
                elif user_input_possum == '2':
                    print("Exiting bulk analysis...\n")
                    UserInterface()
                else:
                    print("Invalid input. Returning to start of bulk analysis...") 
                    bulk_canoe_UI()
            

    elif user_input == '2':
        print("Returning to main menu...")
        UserInterface()
    else:
        print("Invalid input. Try again...")
        bulk_canoe_UI()
    

def test_mode():
    print("Starting PANDA-POSSUM 2T6 test program...")
    ### PROCESS LOADCASES ###
    loadcases = process_loadcases()

    ### EXAMPLE OF USING LOADCSASE DATAFRAMES ###
    print("Printing loadcase dataframes info:")
    print(loadcases[0].paddlers_df.info())
    print(loadcases[0].weights_df.info())
    print(loadcases[0].back_weights_df.info())

    print(loadcases[0].paddlers_df.loc["Paddler1", "weight (kg)"])
    print("\nPrinting loadcase 2 Cp mean value:")
    print(loadcases[0].weights_df.loc["Cp"])

    ### CANOE CALCULATIONS ###
    our_canoe = canoe.Canoe(
        L=5.7, 
        Lp=2.0, 
        Ld=2.75, 
        Lf=1.0, 
        W=0.65, 
        t1=1.5, 
        t2=1.25, 
        d=0.4,  
        b=0.0, 
        s=0.18, 
        f=0.6, 
        n=2.0,
        density=16, 
        bowpower=4, 
        sternpower=4
    )

    ### TEST HERE ####
    try:
        flag, outputs, loadcases_array, actualbeam, hull_weight, surfacearea, cmx = our_canoe.analyze_all(loadcases)
        print(outputs)
    except Exception as e:
        print(f"LEAK during analysis: {e}")

    ##################

    return

if __name__ == "__main__":
    UserInterface()
    # test_mode()