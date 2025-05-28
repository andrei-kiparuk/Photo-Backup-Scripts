import os
from collections import Counter

def list_extensions(directory):
    """List all unique file extensions in the specified directory and its subdirectories."""
    extensions_counter = Counter()

    # Walk through the directory and subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext:
                extensions_counter[ext.lower()] += 1

    return extensions_counter

def main():
    # Specify the directory you want to scan
    folder = input("Enter the path of the folder to scan: ").strip()

    if not os.path.exists(folder):
        print("The specified folder does not exist. Please provide a valid path.")
        return

    # Get the extensions
    extensions = list_extensions(folder)

    if not extensions:
        print("No files found in the specified folder.")
    else:
        print("\nFile extensions found and their counts:")
        for ext, count in sorted(extensions.items()):
            print(f"{ext}: {count}")

if __name__ == "__main__":
    main()
