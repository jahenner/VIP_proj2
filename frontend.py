#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import re
from typing import List, Any, Optional, Callable, Dict, Union

# --- Input Helper Functions ---

def get_validated_input(
    prompt: str,
    validation_func: Callable[[str], Any],
    error_message: str
) -> Any:
    """Generic function to get validated input."""
    while True:
        try:
            value_str = input(prompt).strip()
            return validation_func(value_str)
        except ValueError as e:
            print(f"Error: {error_message} ({e}). Please try again.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}. Please try again.")

def validate_float(value_str: str) -> float:
    """Validates if input is a float."""
    return float(value_str)

def validate_int(value_str: str, min_val: Optional[int] = None) -> int:
    """Validates if input is an integer, optionally checking minimum value."""
    val = int(value_str)
    if min_val is not None and val < min_val:
        raise ValueError(f"Value must be at least {min_val}")
    return val

def validate_boolean(value_str: str) -> bool:
    """Validates if input represents a boolean."""
    val_lower = value_str.lower()
    if val_lower in ['true', 't', 'yes', 'y', '1']:
        return True
    elif val_lower in ['false', 'f', 'no', 'n', '0']:
        return False
    else:
        raise ValueError("Enter true/yes/y/1 or false/no/n/0")

def validate_choice(value_str: str, options: List[str]) -> str:
    """Validates if input is one of the allowed options (case-insensitive)."""
    val_lower = value_str.lower()
    if val_lower in options:
        return val_lower # Return the canonical lower-case version
    raise ValueError(f"Input must be one of: {', '.join(options)}")

def validate_list_of_floats(value_str: str) -> List[float]:
    """Validates if input is a comma or space-separated list of floats."""
    # Replace commas with spaces, then split by spaces
    items = re.split(r'[,\s]+', value_str.strip())
    # Filter out empty strings that might result from multiple spaces
    float_list = [float(item) for item in items if item]
    if not float_list:
        raise ValueError("Input list cannot be empty.")
    return float_list

def validate_absolute_path(
    value_str: str,
    must_exist: bool = False,
    is_dir: bool = False
) -> str:
    """Validates if input is an absolute path, optionally checking existence."""
    # Expand ~ and environment variables
    expanded_path = os.path.expanduser(os.path.expandvars(value_str))
    abs_path = os.path.abspath(expanded_path)

    if not os.path.isabs(abs_path):
         # This check is somewhat redundant after os.path.abspath but good practice
         raise ValueError("Path must be absolute (e.g., /path/to/file or C:\\path\\to\\file).")

    if must_exist:
        if not os.path.exists(abs_path):
            raise ValueError(f"Path does not exist: {abs_path}")
        if is_dir and not os.path.isdir(abs_path):
            raise ValueError(f"Path is not a directory: {abs_path}")
        if not is_dir and not os.path.isfile(abs_path):
            raise ValueError(f"Path is not a file: {abs_path}")

    return abs_path

# --- Main Data Collection Function ---

def create_geosmie_json():
    """Collects user input and generates the GEOSmie JSON structure."""
    print("--- GEOSmie Particle Definition JSON Generator ---")
    print("Please provide the following parameters.")
    print("Security Note: Please provide fully-qualified absolute paths for all file inputs (e.g., /usr/data/ri.csv).\n")

    particle_data: Dict[str, Any] = {}

    # --- Determine Number of Major Size Bins ---
    # This affects the structure of rhop0 and psd params significantly
    num_major_bins = get_validated_input(
        "Enter the number of major size bins (e.g., 1 for soot, 5 for dust): ",
        lambda v: validate_int(v, min_val=1),
        "Must be a positive integer."
    )
    is_single_bin = (num_major_bins == 1)
    print("-" * 20)

    # --- rhop0 (Dry Particle Density) ---
    print("Enter dry particle density (rhop0).")
    if is_single_bin:
        particle_data['rhop0'] = get_validated_input(
            "Enter single dry density value (float): ",
            validate_float,
            "Invalid number."
        )
    else:
        print(f"Enter {num_major_bins} dry density values (comma or space-separated floats):")
        while True:
            rhop0_list = get_validated_input(
                "> ",
                validate_list_of_floats,
                "Invalid list of numbers."
            )
            if len(rhop0_list) == num_major_bins:
                particle_data['rhop0'] = rhop0_list
                break
            else:
                print(f"Error: Expected {num_major_bins} values, but got {len(rhop0_list)}. Try again.")
    print("-" * 20)

    # --- rh (Relative Humidity) ---
    print("Enter relative humidity (rh) values at which to calculate optical properties.")
    print("(Provide a comma or space-separated list of floats, e.g., 0.0 0.5 0.9 0.99)")
    rh_list = get_validated_input(
        "> ",
        validate_list_of_floats,
        "Invalid list of RH values."
    )
    particle_data['rh'] = rh_list
    print("-" * 20)

    # --- rhDep (Relative Humidity Dependence) ---
    print("Configure Relative Humidity Dependence (rhDep).")
    rhdep_data: Dict[str, Any] = {}
    rhdep_type = get_validated_input(
        "Enter rhDep type ('simple', 'trivial', 'ss'): ",
        lambda v: validate_choice(v, ['simple', 'trivial', 'ss']),
        "Invalid type."
    )
    rhdep_data['type'] = rhdep_type
    rhdep_params: Dict[str, Any] = {}

    if rhdep_type == 'simple':
        print(f"Enter growth factors (gf) corresponding to the {len(rh_list)} RH values.")
        print("(Provide a comma or space-separated list of floats)")
        while True:
            gf_list = get_validated_input(
                "> ",
                validate_list_of_floats,
                "Invalid list of growth factors."
            )
            if len(gf_list) == len(rh_list):
                rhdep_params['gf'] = gf_list
                break
            else:
                print(f"Error: Expected {len(rh_list)} growth factors, but got {len(gf_list)}. Try again.")
    elif rhdep_type == 'trivial':
        print("Enter the single growth factor (gf) to use across all RH values (e.g., 1.0).")
        gf_val = get_validated_input(
            "> ",
            validate_float,
            "Invalid number."
        )
        rhdep_params['gf'] = [gf_val] # Needs to be a list with one element
    elif rhdep_type == 'ss':
        print("Enter the four parameters for the 'ss' type:")
        rhdep_params['c1'] = get_validated_input("Enter c1 (float): ", validate_float, "Invalid number.")
        rhdep_params['c2'] = get_validated_input("Enter c2 (float): ", validate_float, "Invalid number.")
        rhdep_params['c3'] = get_validated_input("Enter c3 (float): ", validate_float, "Invalid number.")
        rhdep_params['c4'] = get_validated_input("Enter c4 (float): ", validate_float, "Invalid number.")

    rhdep_data['params'] = rhdep_params
    particle_data['rhDep'] = rhdep_data
    print("-" * 20)

    # --- psd (Particle Size Distribution) ---
    print("Configure Particle Size Distribution (psd).")
    psd_data: Dict[str, Any] = {}
    psd_type = get_validated_input(
        "Enter psd type ('lognorm', 'ss', 'du'): ",
        lambda v: validate_choice(v, ['lognorm', 'ss', 'du']),
        "Invalid type."
    )
    psd_data['type'] = psd_type
    psd_params: Dict[str, Any] = {}

    # Determine sub-distribution structure (relevant for lognorm, du)
    sub_dist_counts = []
    if psd_type in ['lognorm', 'du']:
        print(f"\nFor each of the {num_major_bins} major bins, specify the number of sub-distributions.")
        for i in range(num_major_bins):
            count = get_validated_input(
                f"  Number of sub-distributions in major bin {i+1}: ",
                lambda v: validate_int(v, min_val=1),
                "Must be a positive integer."
            )
            sub_dist_counts.append(count)
    else: # For 'ss', effectively 1 sub-distribution per major bin
        sub_dist_counts = [1] * num_major_bins

    # --- PSD Params based on Type ---
    if psd_type == 'lognorm':
        psd_params['r0'] = []
        psd_params['rmin0'] = []
        psd_params['rmax0'] = []
        psd_params['sigma'] = []
        psd_params['numperdec'] = []
        psd_params['fracs'] = []
        print("\nEnter 'lognorm' parameters for each major bin and sub-distribution:")
        for i in range(num_major_bins):
            print(f"\n--- Major Bin {i+1} ({sub_dist_counts[i]} sub-distribution(s)) ---")
            # Nested lists for these params
            r0_inner = []
            rmin0_inner = []
            rmax0_inner = []
            sigma_inner = []
            fracs_inner = []
            for j in range(sub_dist_counts[i]):
                print(f"  Sub-distribution {j+1}:")
                r0_val = get_validated_input(f"    Median dry radius r0 (e.g., 0.0118e-6): ", validate_float, "Invalid number.")
                rmin0_val = get_validated_input(f"    Min dry radius rmin0 (e.g., 1e-10): ", validate_float, "Invalid number.")
                rmax0_val = get_validated_input(f"    Max dry radius rmax0 (e.g., 0.3e-6): ", validate_float, "Invalid number.")
                sigma_val = get_validated_input(f"    Std dev sigma (e.g., 2.0): ", validate_float, "Invalid number.")
                frac_val = get_validated_input(f"    Number fraction fracs (e.g., 1.0): ", validate_float, "Invalid number.")
                r0_inner.append(r0_val)
                rmin0_inner.append(rmin0_val)
                rmax0_inner.append(rmax0_val)
                sigma_inner.append(sigma_val)
                fracs_inner.append(frac_val)

            # Validate fractions sum if multiple sub-dists
            if sub_dist_counts[i] > 1 and not abs(sum(fracs_inner) - 1.0) < 1e-6:
                 print(f"Warning: Fractions for major bin {i+1} sum to {sum(fracs_inner)}, not 1.0.")

            psd_params['r0'].append(r0_inner)
            psd_params['rmin0'].append(rmin0_inner)
            psd_params['rmax0'].append(rmax0_inner)
            psd_params['sigma'].append(sigma_inner)
            psd_params['fracs'].append(fracs_inner)

            # numperdec is per major bin
            numperdec_val = get_validated_input(
                f"  Number of points per decade (numperdec) for major bin {i+1} (e.g., 100): ",
                 lambda v: validate_int(v, min_val=1),
                 "Must be a positive integer."
            )
            psd_params['numperdec'].append(numperdec_val)

    elif psd_type == 'ss':
        psd_params['rMinMaj'] = []
        psd_params['rMaxMaj'] = []
        psd_params['numperdec'] = []
        psd_params['fracs'] = []
        print("\nEnter 'ss' parameters for each major bin:")
        for i in range(num_major_bins):
            print(f"\n--- Major Bin {i+1} ---")
            rmin_val = get_validated_input(f"  Min radius rMinMaj (e.g., 0.1e-6): ", validate_float, "Invalid number.")
            rmax_val = get_validated_input(f"  Max radius rMaxMaj (e.g., 1.0e-6): ", validate_float, "Invalid number.")
            numperdec_val = get_validated_input(
                f"  Number of points per decade (numperdec) (e.g., 500): ",
                lambda v: validate_int(v, min_val=1),
                "Must be a positive integer."
            )
            psd_params['rMinMaj'].append(rmin_val)
            psd_params['rMaxMaj'].append(rmax_val)
            psd_params['numperdec'].append(numperdec_val)
            psd_params['fracs'].append([1.0]) # 'ss' uses [[1.0], [1.0], ...]

    elif psd_type == 'du':
        psd_params['rMinMaj'] = []
        psd_params['rMaxMaj'] = []
        psd_params['fracs'] = []
        print("\nEnter 'du' parameters for each major bin and sub-distribution:")
        for i in range(num_major_bins):
            print(f"\n--- Major Bin {i+1} ({sub_dist_counts[i]} sub-distribution(s)) ---")
            # Nested lists for these params
            rmin_inner = []
            rmax_inner = []
            fracs_inner = []
            for j in range(sub_dist_counts[i]):
                 print(f"  Sub-distribution {j+1}:")
                 rmin_val = get_validated_input(f"    Min radius rMinMaj (e.g., 0.1e-6): ", validate_float, "Invalid number.")
                 rmax_val = get_validated_input(f"    Max radius rMaxMaj (e.g., 0.18e-6): ", validate_float, "Invalid number.")
                 frac_val = get_validated_input(f"    Number fraction fracs (e.g., 0.009): ", validate_float, "Invalid number.")
                 rmin_inner.append(rmin_val)
                 rmax_inner.append(rmax_val)
                 fracs_inner.append(frac_val)

            # Validate fractions sum if multiple sub-dists
            if sub_dist_counts[i] > 1 and not abs(sum(fracs_inner) - 1.0) < 1e-6:
                 print(f"Warning: Fractions for major bin {i+1} sum to {sum(fracs_inner)}, not 1.0.")

            psd_params['rMinMaj'].append(rmin_inner)
            psd_params['rMaxMaj'].append(rmax_inner)
            psd_params['fracs'].append(fracs_inner)
        # Note: 'numperdec' is not listed for 'du' type in the documentation provided.

    psd_data['params'] = psd_params
    particle_data['psd'] = psd_data
    print("-" * 20)

    # --- ri (Refractive Index) ---
    print("Configure Refractive Index (ri).")
    ri_data: Dict[str, Any] = {}
    ri_format = get_validated_input(
        "Enter refractive index file format ('gads', 'csv', 'wsv'): ",
        lambda v: validate_choice(v, ['gads', 'csv', 'wsv']),
        "Invalid format."
    )
    ri_data['format'] = ri_format

    print("Enter the absolute path(s) to the refractive index file(s).")
    print("(Usually one path. Multiple paths are for experimental multi-RI sub-distributions.)")
    num_ri_paths = get_validated_input(
         "How many RI file paths will you provide? ",
         lambda v: validate_int(v, min_val=1),
         "Must be a positive integer."
    )

    ri_paths = []
    for k in range(num_ri_paths):
        # Ask if the file *should* exist for validation, though GEOSmie might handle missing files later
        # Set must_exist=False allows specifying paths that might be generated or relative to GEOSmie run dir
        # Set must_exist=True for stricter checking during script execution. Let's use False for flexibility.
        path_val = get_validated_input(
            f"  Enter absolute path for RI file {k+1}: ",
            lambda v: validate_absolute_path(v, must_exist=False, is_dir=False),
            "Invalid absolute path."
        )
        ri_paths.append(path_val)

    ri_data['path'] = ri_paths # Stored as a list, even if only one path
    particle_data['ri'] = ri_data
    print("-" * 20)

    # --- Optional: hydrophobic ---
    if is_single_bin:
        print("Optional: Set hydrophobic flag (only for single-bin particles).")
        use_hydrophobic = get_validated_input(
            "Create a special hydrophobic bin (true/false)? [default: false]: ",
            validate_boolean,
            "Invalid boolean value."
        )
        if use_hydrophobic:
            particle_data['hydrophobic'] = True
        # else: # Default is false, so no need to add the key if false
        #    particle_data['hydrophobic'] = False
        print("-" * 20)
    else:
        print("Skipping hydrophobic option (only applicable for single-bin particles).")
        print("-" * 20)

    # --- Optional: mode & kernel_params ---
    print("Optional: Specify optical calculation mode (default is Mie).")
    specify_mode = get_validated_input(
        "Specify a mode other than Mie (yes/no)? [default: no]: ",
        validate_boolean,
        "Invalid boolean value."
    )

    if specify_mode:
        # Currently, only 'kernel' seems relevant based on examples/docs
        mode_type = get_validated_input(
            "Enter mode type (e.g., 'kernel'): ",
            lambda v: str(v).lower(), # Simple validation for now
            "Invalid mode string."
        )
        particle_data['mode'] = mode_type

        if mode_type == 'kernel':
            print("Enter kernel parameters (required for 'kernel' mode).")
            kernel_params: Dict[str, str] = {}
            kernel_params['path'] = get_validated_input(
                "  Enter absolute path to kernel file (e.g., .../kernel-grasp-....nc): ",
                lambda v: validate_absolute_path(v, must_exist=False, is_dir=False),
                "Invalid absolute path for kernel file."
            )
            kernel_params['shape_dist'] = get_validated_input(
                "  Enter absolute path to shape distribution file (e.g., .../spheroid_sphere_simple.txt): ",
                lambda v: validate_absolute_path(v, must_exist=False, is_dir=False),
                "Invalid absolute path for shape distribution file."
            )
            particle_data['kernel_params'] = kernel_params
        else:
            print(f"Warning: Mode '{mode_type}' selected, but specific parameters for it are not handled by this script.")
    print("-" * 20)


    # --- Output File ---
    print("Specify the output JSON filename.")
    output_filename = get_validated_input(
        "Enter absolute path for the output .json file: ",
        lambda v: validate_absolute_path(v, must_exist=False, is_dir=False), # Path itself doesn't need to exist yet
        "Invalid absolute path."
    )
    if not output_filename.lower().endswith('.json'):
        output_filename += '.json'
        print(f"Appending .json extension. Filename is now: {output_filename}")

    # Check for overwrite
    if os.path.exists(output_filename):
        overwrite = get_validated_input(
            f"File '{output_filename}' already exists. Overwrite (yes/no)? ",
            validate_boolean,
            "Invalid boolean value."
        )
        if not overwrite:
            print("Operation cancelled by user.")
            sys.exit(0)

    # --- Write JSON File ---
    try:
        with open(output_filename, 'w') as f:
            json.dump(particle_data, f, indent=2) # Use indent for readability
        print(f"\nSuccessfully created JSON file: {output_filename}")
    except IOError as e:
        print(f"\nError: Could not write to file {output_filename}. ({e})")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred during file writing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_geosmie_json()