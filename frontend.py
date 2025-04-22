import json

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


def geosmie_get_particle():
    print("=== GEOSmie JSON Configuration CLI ===")

    # 1) JSON filename
    base_name = input("1) Enter base name for JSON file (no extension, e.g., 'example1'): ").strip()
    file_name = f"{base_name}.json"

    # 2) Dry density
    rhop0 = prompt_value("2) Enter dry density (rhop0) as a single float (e.g., 1000.0):", float)

    # 3) Relative humidity list
    rh = prompt_list("3) Enter relative humidity values as comma-separated floats (e.g., 0.00,0.05,0.10):", float)

    # 4) RH-dependence
    dep_type = input("4) Enter RH-dependence type (e.g., simple, trivial): ").strip()
    gf_list = prompt_list("5) Enter gf values for rhDep.params.gf as comma-separated floats (e.g., 1.0,1.01,1.02):", float)

    # 6) Particle size distribution
    psd_type = input("6) Enter PSD type (e.g., lognorm, du): ").strip()
    print("7) Enter PSD parameters (press Enter to skip any):")
    r0 = prompt_json("  7a) r0 (list of lists), e.g. [[0.0118e-6]]:")
    rmax0 = prompt_json("  7b) rmax0 (list of lists), e.g. [[0.3e-6]]:")
    rmin0 = prompt_json("  7c) rmin0 (list of lists), e.g. [[1e-10]]:")
    sigma = prompt_json("  7d) sigma (list of lists), e.g. [[2.0]]:")
    numperdec = prompt_list("  7e) numperdec (list of ints), e.g. 100:", int)
    fracs = prompt_json("  7f) fracs (list of lists), e.g. [[1.0]]:")

    psd_params = {}
    if r0 is not None:
        psd_params["r0"] = r0
    if rmax0 is not None:
        psd_params["rmax0"] = rmax0
    if rmin0 is not None:
        psd_params["rmin0"] = rmin0
    if sigma is not None:
        psd_params["sigma"] = sigma
    if numperdec:
        psd_params["numperdec"] = numperdec
    if fracs is not None:
        psd_params["fracs"] = fracs

    # 8) Refractive index
    ri_format = input("8) Enter RI format (e.g., gads, wsv): ").strip()
    ri_paths_str = input("9) Enter RI path(s) as comma-separated list (e.g., data/soot00,data/soot01): ").strip()
    ri_paths = [p.strip() for p in ri_paths_str.split(",") if p.strip()]

    # 10) Hydrophobic flag
    hydro_str = input("10) Is the particle hydrophobic? (yes/no): ").strip().lower()
    hydrophobic = hydro_str in ("yes", "y", "true", "t", "1")

    # Build and write JSON
    data = {
        "rhop0": rhop0,
        "rh": rh,
        "rhDep": {"type": dep_type, "params": {"gf": gf_list}},
        "psd": {"type": psd_type, "params": psd_params},
        "ri": {"format": ri_format, "path": ri_paths},
        "hydrophobic": hydrophobic,
    }

    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Wrote configuration to '{file_name}'")
    return file_name


if __name__ == "__main__":
    geosmie_get_particle()
    