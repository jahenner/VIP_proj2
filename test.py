import cProfile
import pstats
import tracemalloc
import subprocess
import os


def main():
    os.chdir("./GEOSmie")
    test_command = ["python", "runoptics.py", "--name", "./geosparticles/bc.json"]
    subprocess.run(test_command, text=True, check=True)
    test_command = ["python", "runbands.py", "--filename", "./optics_bc.nc4"]
    subprocess.run(test_command, text=True, check=True)


if __name__ == "__main__":
    profiler = cProfile.Profile()
    
    profiler.enable()
    tracemalloc.start()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats(10)

    print('-'*40)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Current memory usage: {current / 1024:.2f} KiB")
    print(f"Peak memory usage: {peak / 1024:.2f} KiB")