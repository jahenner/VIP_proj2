import json

def main():
    while True:
        particle_name = input("Give me x: ")
        # write to file example
        with open(f"{particle_name}.json", "w") as inFile:
            inFile.write(json.dumps(python_dict, indent=4))


if __name__ =="__main__":
    main()