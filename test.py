import cProfile
import pstats
import tracemalloc
import runpy
import os
import sys
import pathlib

def geos_runner():
    runner_script_dir = pathlib.Path(__file__).parent.resolve()
    geosmie_dir = runner_script_dir / "GEOSmie"
    runoptics_path = geosmie_dir / "runoptics.py"
    runbands_path = geosmie_dir / "runbands.py"

    geosmie_dir_str = str(geosmie_dir)
    if geosmie_dir_str not in sys.path:
        sys.path.insert(0, geosmie_dir_str)

    original_argv = list(sys.argv)
    os.chdir(geosmie_dir_str)

    try:
        # --- Run runoptics.py ---
        if not runoptics_path.is_file():
             print(f"Error: Script not found at {runoptics_path}")
             return

        runoptics_args = ['--name', os.path.join(os.getcwd(), 'geosparticles/bc.json')]
        sys.argv = [str(runoptics_path)] + runoptics_args
        print(f"\nRunning {runoptics_path} with argv: {' '.join(sys.argv)}")
        runpy.run_path(str(runoptics_path), run_name="__main__")

        # --- Run runbands.py ---
        if not runbands_path.is_file():
             print(f"Error: Script not found at {runbands_path}")
             return

        runbands_args = ["--filename", os.path.join(os.getcwd(), "optics_bc.nomom.nc4")]
        sys.argv = [str(runbands_path)] + runbands_args
        print(f"\nRunning {runbands_path} with argv: {' '.join(sys.argv)}")
        runpy.run_path(str(runbands_path), run_name="__main__")

    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    tracemalloc.start()

    geos_runner()

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('calls')
    stats.print_stats(20)

    print('-'*40)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Current memory usage: {current / 1024:.2f} KiB")
    print(f"Peak memory usage: {peak / 1024:.2f} KiB")
    
    
    
    
    
    