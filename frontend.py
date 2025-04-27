import json
import argparse
def prompt_list(prompt, cast=float):
    """
    Prompt the user for a comma-separated list of values and return a list cast to the given type.
    """
    while True:
        entries = input(f"{prompt} ").strip()
        if not entries:
            return []
        try:
            return [cast(item) for item in entries.split(",")]
        except ValueError:
            print("Invalid input. Please enter values separated by commas, e.g., 0.0,0.5,1.0")


def prompt_value(prompt, cast=float):
    """
    Prompt the user for a single value and return it cast to the given type.
    """
    while True:
        val = input(f"{prompt} ").strip()
        try:
            return cast(val)
        except ValueError:
            print(f"Invalid input. Please enter a valid {cast.__name__}, e.g., {cast.__name__}('1000.0')")


def prompt_json(prompt):
    """
    Prompt the user for a JSON structure and parse it. Returns the parsed object or None if blank.
    """
    while True:
        s = input(f"{prompt} ").strip()
        if not s:
            return None
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            print("Invalid JSON. Please enter a valid JSON structure, e.g., [[0.0118e-6]] or {\"r0\":[[0.0118e-6]]}")

def parse_args():
    parser = argparse.ArgumentParser(description="GEOSmie config client")
    parser.add_argument("-bc", action="store_true", help="Black Carbon")
    parser.add_argument("-brc", action="store_true", help="Brown Carbon")
    parser.add_argument("-du", action="store_true", help="Dust")
    parser.add_argument("-ss", action="store_true", help="Sea Salt")
    parser.add_argument("-su", action="store_true", help="Sulfate")
    parser.add_argument("-ni", action="store_true", help="Nitrate")
    parser.add_argument("-oc", action="store_true", help="Organic Carbon")
    return parser.parse_known_args()

def geosmie_get_particle():
    print("=== GEOSmie JSON Configuration CLI ===")
    args, unknown = parse_args()
    particle_type = None
    if args.bc:
        particle_type = "bc"
        print("particle type is bc")
    elif args.du:
        particle_type = "du"
        print("particle type is du")
    elif args.ss:
        particle_type = "ss"
        print("particle type is ss")
    elif args.su:
        particle_type = "su"
        print("particle type is su")
    elif args.brc:
        particle_type = "brc"
        print("particle type is brc")
    elif args.ni:
        particle_type = "ni"
        print("particle type is ni")
    elif args.oc:
        particle_type = "oc"
        print("particle type is oc")
    elif args.oc:
        particle_type = "oc"
        print("particle type is oc")
    valid_types = ["bc", "brc", "du", "ss", "su", "ni", "oc"]

    while particle_type not in valid_types:
        print("No valid particle type specified.")
        print("Please enter one of the following: " + ", ".join(valid_types))
        user_input = input("Enter particle type (e.g., 'ss'): ").strip().lower()
        if user_input in valid_types:
            particle_type = user_input
        else:
            print("Invalid input. Try again.\n")
    
    # 1) JSON filename
    base_name = input("1) Enter base name for JSON file (no extension, e.g., 'example1'): ").strip()
    file_name = f"{base_name}.json"

    # 2) Dry density
    if particle_type in ["du", "ni"]:
        rhop0 = prompt_list("2) Enter dry density (rhop0) as comma-separated floats (e.g., 2500,2510,2520):", float)
    else:
        rhop0 = prompt_value("2) Enter dry density (rhop0) as a single float (e.g., 1000.0):", float)

    # 3) Relative humidity list
    rh = prompt_list("3) Enter relative humidity values as comma-separated floats (e.g., 0.00,0.05,0.10):", float)

    # 4) RH-dependence
    #dep_type = input("4) Enter RH-dependence type (e.g., simple, trivial): ").strip()
    #gf_list = prompt_list("5) Enter gf values for rhDep.params.gf as comma-separated floats (e.g., 1.0,1.01,1.02):", float)


    print("4) Setting RH-dependence block:")
    if particle_type in ["bc", "brc", "ni", "su", "oc"]:
        dep_type = "simple"
        gf_list = prompt_list("  Enter gf values for RH-dependence (comma-separated, e.g., 1.0,1.01,...):", float)
        rhDep_block = {
            "type": dep_type,
            "params": {
                "gf": gf_list
        }
    }

    elif particle_type == "du":
        dep_type = "trivial"
        gf_list = [1.0]
        rhDep_block = {
            "type": dep_type,
            "params": {
                "gf": gf_list
            }
        }
        print("  Trivial RH-dependence set: gf = [1.0]")

    elif particle_type == "ss":
        dep_type = "ss"
        gf_list = []
        print("  Enter coefficients for Sea Salt RH formula:")
        c1 = prompt_value("    c1 (e.g., 0.7674):", float)
        c2 = prompt_value("    c2 (e.g., 3.079):", float)
        c3 = prompt_value("    c3 (e.g., 2.573e-11):", float)
        c4 = prompt_value("    c4 (e.g., -1.424):", float)
        rhDep_block = {
            "type": dep_type,
            "params": {
                "c1": c1,
                "c2": c2,
                "c3": c3,
                "c4": c4
            }
        }

    # 5) Particle size distribution
    print("5) Setting PSD (Particle Size Distribution) block:")

    if particle_type in ["bc", "brc", "ni", "oc", "su"]:
        psd_type = "lognorm"
        print("PSD type is 'lognorm'. Please enter the following as lists.")
        r0 = prompt_json("  r0 (list), e.g. [0.0118e-6]:")
        rmax0 = prompt_json("  rmax0 (list), e.g. [0.3e-6]:")
        rmin0 = prompt_json("  rmin0 (list), e.g. [1e-10]:")
        sigma = prompt_json("  sigma (list), e.g. [2.0]:")
        numperdec = prompt_list("  numperdec (list of ints), e.g. 100:", int)
        fracs = prompt_json("  fracs (list), e.g. [1.0]:")

        psd_params = {
            "r0": r0,
            "rmax0": rmax0,
            "rmin0": rmin0,
            "sigma": sigma,
            "numperdec": numperdec,
            "fracs": fracs
        }

    elif particle_type == "du":
        psd_type = "du"
        print("PSD type is 'du'. Please enter rMinMaj, rMaxMaj, and fracs as lists.")
        rMinMaj = prompt_json("  rMinMaj (list), e.g. [0.1e-6, 0.2e-6]:")
        rMaxMaj = prompt_json("  rMaxMaj (list), e.g. [1.0e-6, 2.0e-6]:")
        fracs = prompt_json("  fracs (list), e.g. [0.5, 0.5]:")

        psd_params = {
            "rMinMaj": rMinMaj,
            "rMaxMaj": rMaxMaj,
            "fracs": fracs
        }

    elif particle_type == "ss":
        psd_type = "ss"
        print("PSD type is 'ss'. Please enter rMinMaj, rMaxMaj, fracs, and numperdec as lists.")
        rMinMaj = prompt_json("  rMinMaj (list), e.g. [0.03e-6, 0.06e-6]:")
        rMaxMaj = prompt_json("  rMaxMaj (list), e.g. [0.1e-6, 0.2e-6]:")
        fracs = prompt_json("  fracs (list), e.g. [0.5, 0.5]:")
        numperdec = prompt_list("  numperdec (list of ints), e.g. 1600:", int)

        psd_params = {
            "rMinMaj": rMinMaj,
            "rMaxMaj": rMaxMaj,
            "fracs": fracs,
            "numperdec": numperdec
        }

    # 6) Refractive index
    if particle_type in ["bc", "du", "oc", "ss", "su"]:
        ri_format = "gads"
    else:
        ri_format = "wsv"
    print(f"Refractive index format set to '{ri_format}' based on particle type.")
    ri_paths_str = input("9) Enter RI path(s) as comma-separated list (e.g., data/soot00,data/soot01): ").strip()
    ri_paths = [p.strip() for p in ri_paths_str.split(",") if p.strip()]

    # 7) Hydrophobic flag
    if particle_type in ["bc", "brc", "oc"]:
        hydrophobic = True
        print("Particle is hydrophobic by default.")
    else:
        hydrophobic = False
        print("ℹParticle is NOT hydrophobic by default.")

    # Build and write JSON
    data = {
        "rhop0": rhop0,
        "rh": rh,
        "rhDep": rhDep_block,
        "psd": {"type": psd_type, "params": psd_params},
        "ri": {"format": ri_format, "path": ri_paths},
        "hydrophobic": hydrophobic,
    }
    if particle_type == "du":
        print("Enter kernel-related parameters:")
        kernel_path = input("  Path to kernel file (e.g., data/kernel/mykernel.dat): ").strip()
        shape_dist_path = input("  Path to shape_dist file (e.g., data/kernel_shape_dist/spheroid_fixed.txt): ").strip()
        data["mode"] = "kernel"
        data["kernel_params"] = {
            "path": kernel_path,
            "shape_dist": shape_dist_path
    }
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Wrote configuration to '{file_name}'")
    return file_name


if __name__ == "__main__":
    geosmie_get_particle()
    