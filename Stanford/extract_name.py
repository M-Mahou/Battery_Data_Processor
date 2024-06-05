def extract_tokens(input_string):
    """
    Extracts tokens from the given input string to form a file name and sheet name.

    :param input_string: The input string to extract tokens from.
    :return: A tuple containing the file name and sheet name.
    """
    common_part = "INR21700_M50T_T23_Aging_UDDS_SOC20_80_CC"

    tokens = input_string.split('_')

    position = 8
    key1 = ""
    # Loop to build key1 until a token starting with 'N' is found
    while not tokens[position].startswith("N"):
        key1 += "_" + tokens[position]
        position += 1

    key2 = "_" + tokens[position]
    position += 1

    key3 = "_" + tokens[position]
    position += 1

    key4 = ""
    # Check if the next token starts with 'C' to decide whether to add it to key4
    if not tokens[position].startswith("C"):
        key4 = tokens[position]
        position += 1

    # Construct the sheet name from the next two tokens
    sheet_name = tokens[position] + "_" + tokens[position + 1]

    # Split the sheet name and format it correctly
    sheet_tokens = sheet_name.split('.')
    sheet_name = sheet_tokens[0] + "_1"

    # Construct the file name using the extracted keys
    file_name = common_part + key1 + key2 + key3 + key4 + "_" + sheet_tokens[0] + "."

    return file_name, sheet_name