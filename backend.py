import os
import pathlib
import select
import subprocess
import sys


CURR_DIR = pathlib.Path(__file__).parent.resolve()
GEOSMIE_DIR = CURR_DIR / "GEOSmie"
RUNOPTICS_PATH = GEOSMIE_DIR / "runoptics.py"
RUNBANDS_PATH = GEOSMIE_DIR / "runbands.py"


def run_command(command: list):
    os.chdir(str(GEOSMIE_DIR))
    last_stdout_line = None
    all_stdout_lines = []
    stderr_output = []
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        streams = [process.stdout, process.stderr]
        while process.poll() is None or streams:
            readable, _, _ = select.select(streams, [], [], 0.1)

            for stream in readable:
                line = stream.readline()
                if not line: # End of stream
                    streams.remove(stream)
                    continue

                if stream is process.stdout:
                    print(f"\t{line}", end='')
                    clean_line = line.strip()
                    if clean_line: last_stdout_line = clean_line
                    all_stdout_lines.append(line)
                elif stream is process.stderr:
                    print(f"SCRIPT STDERR: {line}", end='', file=sys.stderr)
                    stderr_output.append(line)
        
        while True:
            stdout_line = process.stdout.readline()
            if stdout_line:
                print(f"\t{stdout_line}", end='')
                clean_line = stdout_line.strip()
                if clean_line: last_stdout_line = clean_line
                all_stdout_lines.append(stdout_line)
            else:
                break

        while True:
            stderr_line = process.stderr.readline()
            if stderr_line:
                print(f"SCRIPT STDERR (final): {stderr_line}", end='', file=sys.stderr)
                stderr_output.append(stderr_line)
            else:
                break
        
        
        return_code = process.wait()
        print(f"\n--- Script finished with return code: {return_code} ---")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        os.chdir("..")
    return last_stdout_line, all_stdout_lines, stderr_output


def runoptics(fname: str):
    fq_fname = GEOSMIE_DIR / fname
    
    # --- Run runoptics.py ---
    if not RUNOPTICS_PATH.is_file():
        print(f"Error: Script not found at {RUNOPTICS_PATH}")
        return
    elif not fq_fname.is_file():
        print(f"Error: Particle file not found at {fq_fname}")
        return
        
    command = ["python", '-u', RUNOPTICS_PATH, "--name", fq_fname]
    print("Running optics")
    last_stdout_line, _, _ = run_command(command)
    
    return last_stdout_line.strip().split("Done, output file: ")[1]


def runbands(fname):
    fq_fname = GEOSMIE_DIR / fname
    
    # --- Run runbands.py ---
    if not RUNBANDS_PATH.is_file():
        print(f"Error: Script not found at {RUNBANDS_PATH}")
        return
    elif not fq_fname.is_file():
        print(f"Error: Particle file not found at {fq_fname}")
        return
        
    command = ["python", '-u', RUNBANDS_PATH, "--filename", fq_fname]
    print("Running bands")
    last_stdout_line, _, _ = run_command(command)


def compute_mie(fname: str):
    geosmie_dir_str = str(GEOSMIE_DIR)
    if geosmie_dir_str not in sys.path:
        sys.path.insert(0, geosmie_dir_str)

    try:
        optic_fname = runoptics(fname)
        runbands(optic_fname)
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        pass


if __name__ == "__main__":
    test_fname = "geosparticles/bc.json"
    compute_mie(test_fname)
    # test_bands_fname = "optics_bc.nomom.nc4"
    # runbands(test_bands_fname)
