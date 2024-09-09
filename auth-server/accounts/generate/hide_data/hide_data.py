import numpy as np

def embed_data(gi, secret_data, b):
    d = sum([secret_data[i] * 2**i for i in range(b)])
    msb_gi = np.floor(gi / 2**b) * 2**b
    zi1 = msb_gi + d
    zi2 = msb_gi - (2**b - d)
    q = gi - zi1
    p = gi - zi2
    if p >= q: 
        return zi1
    else:
        return zi2
    
def embed_data_array(gi_array, secret_data, b):
    result = np.zeros_like(gi_array)
    for i in range(len(gi_array)):
        result[i] = embed_data(gi_array[i], secret_data, b)
    return result

def string_to_binary_list(s):
    def char_to_binary_list(char):
        ascii_value = ord(char)
        binary_string = bin(ascii_value)[2:]
        binary_string = binary_string.zfill(8)
        return [int(bit) for bit in binary_string]
    
    binary_list_of_lists = [char_to_binary_list(char) for char in s]
    return binary_list_of_lists

def split_data(binary_list):
    new_binary_list = []
    chunk_sizes = [3, 3, 2]

    for sublist in binary_list:
        result = []
        start = 0
        for size in chunk_sizes:
            end = start + size
            result.append(sublist[start:end])
            start = end
        new_binary_list.append(result)
    return new_binary_list

def convert_ndarray_to_list(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, list):
            return [convert_ndarray_to_list(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: convert_ndarray_to_list(value) for key, value in obj.items()}
        return obj

def hide_data(minutiae, text):
    text = text + '\n'
    secret_data = string_to_binary_list(text)
    secret_data = split_data(secret_data)

    for i in range(len(secret_data)):
        if isinstance(minutiae[i]['locX'], (list, np.ndarray)):
            minutiae[i]['locX'] = embed_data_array(minutiae[i]['locX'], secret_data[i][0], 3)
        else:
            minutiae[i]['locX'] = embed_data(minutiae[i]['locX'], secret_data[i][0], 3)

        if isinstance(minutiae[i]['locY'], (list, np.ndarray)):
            minutiae[i]['locY'] = embed_data_array(minutiae[i]['locY'], secret_data[i][1], 3)
        else:
            minutiae[i]['locY'] = embed_data(minutiae[i]['locY'], secret_data[i][1], 3)

        if isinstance(minutiae[i]['Orientation'], (list, np.ndarray)):
            minutiae[i]['Orientation'] = embed_data_array(minutiae[i]['Orientation'], secret_data[i][2], 2)
        else:
            minutiae[i]['Orientation'] = embed_data(minutiae[i]['Orientation'], secret_data[i][2], 2)

    return convert_ndarray_to_list(minutiae)

def extract_data(zi, b):
    # Extract the least significant b bits
    d = int(zi % 2**b)
    # Convert d back to a list of bits and reverse the order to account for the inversion
    secret_data = [int(bit) for bit in bin(d)[2:].zfill(b)][::-1]
    return secret_data

def extract_message(minutiae):
    binary_data = []

    for feature in minutiae:
        locX_data = extract_data(feature['locX'], 3)
        locY_data = extract_data(feature['locY'], 3)
        orientation_data = extract_data(feature['Orientation'][0], 2)
        binary_data.append(locX_data + locY_data + orientation_data)

    # Convert binary data back to characters
    secret_message = ""
    for binary_char in binary_data:
        ascii_value = int("".join(map(str, binary_char)), 2)
        char = chr(ascii_value)
        if char == '\n':
            break
        secret_message += chr(ascii_value)

    return secret_message

def main():
    # Sample minutiae data
    minutiae = [
        {'locX': 123, 'locY': 456, 'Orientation': [30], 'Type': 'ending'},
        {'locX': 789, 'locY': 101, 'Orientation': [60], 'Type': 'bifurcation'},
        {'locX': 123, 'locY': 456, 'Orientation': [30], 'Type': 'ending'},
        {'locX': 789, 'locY': 101, 'Orientation': [60], 'Type': 'bifurcation'},
        {'locX': 123, 'locY': 456, 'Orientation': [30], 'Type': 'ending'},
        {'locX': 789, 'locY': 101, 'Orientation': [60], 'Type': 'bifurcation'},
        {'locX': 123, 'locY': 456, 'Orientation': [30], 'Type': 'ending'},
        {'locX': 789, 'locY': 101, 'Orientation': [60], 'Type': 'bifurcation'},
        {'locX': 123, 'locY': 456, 'Orientation': [30], 'Type': 'ending'},
        {'locX': 789, 'locY': 101, 'Orientation': [60], 'Type': 'bifurcation'},
        {'locX': 123, 'locY': 456, 'Orientation': [30], 'Type': 'ending'},
        {'locX': 789, 'locY': 101, 'Orientation': [60], 'Type': 'bifurcation'}
    ]
    
    # Secret message to hide
    secret_message = "letsgood" #01100001

    # Print original minutiae data
    print("Original minutiae data:")
    for m in minutiae:
        print(m)
    
    # Hide the secret message in the minutiae data
    hidden_minutiae = hide_data(minutiae, secret_message)
    
    # Print modified minutiae data
    print("\nMinutiae data with hidden message:")
    for m in hidden_minutiae:
        print(m)
    
    # Extract the secret message from the modified minutiae data
    extracted_message = extract_message(hidden_minutiae)
    
    # Print the extracted message
    print("\nExtracted message:")
    print(extracted_message)

if __name__ == "__main__":
    main()
