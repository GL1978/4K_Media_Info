import subprocess
import re
import matplotlib.pyplot as plt


def extract_hdr_metadata(input_file, output_file):
    try:
        # Run the ffmpeg command to extract HDR metadata
        subprocess.run(
            ['ffmpeg', '-i', input_file, '-f', 'ffmetadata', output_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f'HDR metadata extracted successfully to {output_file}')
    except subprocess.CalledProcessError as e:
        print(f'Error occurred while extracting HDR metadata: {e.stderr.decode()}')


# Function to parse HDR metadata from text file
def parse_hdr_metadata(file_path):
    hdr_data = {}
    with open(file_path, 'r') as file:
        content = file.read()

        # Extract display primaries
        primaries_pattern = re.compile(r'display_primaries_x=([0-9. ]+)\ndisplay_primaries_y=([0-9. ]+)')
        match = primaries_pattern.search(content)
        if match:
            hdr_data['display_primaries_x'] = list(map(float, match.group(1).split()))
            hdr_data['display_primaries_y'] = list(map(float, match.group(2).split()))

        # Extract white point
        white_point_x_pattern = re.compile(r'white_point_x=([0-9.]+)')
        white_point_y_pattern = re.compile(r'white_point_y=([0-9.]+)')
        hdr_data['white_point_x'] = float(white_point_x_pattern.search(content).group(1))
        hdr_data['white_point_y'] = float(white_point_y_pattern.search(content).group(1))

        # Extract luminance
        min_luminance_pattern = re.compile(r'min_luminance=([0-9.]+)')
        max_luminance_pattern = re.compile(r'max_luminance=([0-9.]+)')
        hdr_data['min_luminance'] = float(min_luminance_pattern.search(content).group(1))
        hdr_data['max_luminance'] = float(max_luminance_pattern.search(content).group(1))

        # Extract MaxFALL and MaxCLL if available
        max_fall_pattern = re.compile(r'MaxFALL=([0-9.]+)')
        max_cll_pattern = re.compile(r'MaxCLL=([0-9.]+)')
        max_fall_match = max_fall_pattern.search(content)
        max_cll_match = max_cll_pattern.search(content)

        if max_fall_match:
            hdr_data['MaxFALL'] = float(max_fall_match.group(1))
        if max_cll_match:
            hdr_data['MaxCLL'] = float(max_cll_match.group(1))

    return hdr_data


# Function to plot HDR metadata
def plot_hdr_metadata(hdr_data):
    fig, ax = plt.subplots()

    # Plot display primaries
    ax.plot(hdr_data['display_primaries_x'], hdr_data['display_primaries_y'], 'ro', label='Display Primaries')

    # Plot white point
    ax.plot(hdr_data['white_point_x'], hdr_data['white_point_y'], 'bo', label='White Point')

    # Annotate points
    for i, (x, y) in enumerate(zip(hdr_data['display_primaries_x'], hdr_data['display_primaries_y'])):
        ax.annotate(f'P{i + 1}', (x, y), textcoords="offset points", xytext=(0, 10), ha='center')

    ax.annotate('White Point', (hdr_data['white_point_x'], hdr_data['white_point_y']),
                textcoords="offset points", xytext=(0, 10), ha='center', color='blue')

    # Set plot labels and title
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_title('HDR Metadata Display Primaries and White Point')
    ax.legend()

    plt.show()


# Example usage
hdr_metadata_file = 'metadata.txt'
hdr_data = parse_hdr_metadata(hdr_metadata_file)
plot_hdr_metadata(hdr_data)