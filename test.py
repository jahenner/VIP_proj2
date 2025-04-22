import cProfile
import pstats
import tracemalloc
import subprocess
import os


def main():
    os.chdir("./GEOSmie")
    filename = os.path.join(os.getcwd(), "generate_geos_optics.sh")
    print(filename)
    test_command = ["/usr/bin/bash", filename]
    subprocess.run(test_command, capture_output=True, text=True, check=True)


if __name__ == "__main__":
    profiler = cProfile.Profile()
    
    profiler.enable()
    tracemalloc.start()
    main()
    profiler.disable()
    tracemalloc.stop()
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats(10)
    
    print()
    print('-'*40)
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024:.2f} KiB")
    print(f"Peak memory usage: {peak / 1024:.2f} KiB")