"""
Title: CITS 1401 - Project 2
Author: Akhila Liyanage (23729213)
"""


def main(csvfile, SubjIDs):
    try:
        if len(SubjIDs) != 2:  # check exactly two IDs are provided
            raise IndexError
        all_subj_data = {}  # data will be stored in a dictionary of key, and value = list of lists
        OP1, OP2, OP3 = [], [], []

        # read and extract from file with the following headers:
        # SubjID[0], Landmark[1], OX[2], OY[3], OZ[4], MX[5], MY[6], MZ[7]
        with open(csvfile, "r") as file:
            header_idxs = get_header_idxs(file.readline())  # holds header indices to match with data

            for line in file:
                curr_line = line.strip('\n').split(",")

                # read each line and extract the data for each ID
                subj_data_line = []
                key = curr_line[header_idxs[0]]  # key = SubjID
                if key in all_subj_data:  # if data with key is present, update. Else, create a new key
                    existing_data = all_subj_data[key]
                else:
                    all_subj_data[key] = []
                    existing_data = []

                # append to an array in the correct order
                subj_data_line.append(key)  # SubjID
                subj_data_line.append((curr_line[header_idxs[1]].upper()))  # Landmark

                for i in range(2, 8):
                    # check if data is not empty and within bounds
                    if curr_line[header_idxs[i]] != '':
                        if -200 <= float(curr_line[header_idxs[i]]) <= 200:
                            subj_data_line.append(float(curr_line[header_idxs[i]]))  # X, Y, Z data
                        else:
                            subj_data_line.append(None)
                    else:
                        subj_data_line.append(None)

                if None in subj_data_line:
                    existing_data.append(None)
                else:
                    existing_data.append(subj_data_line)
                    all_subj_data[key] = existing_data

        # set None for all IDs with missing landmarks, Nones in X, Y, Z values, and nose tip difference is not zero
        for key, value in all_subj_data.items():
            if len(value) != 7 or None in value or (value[6][4] - value[6][7]) != 0:
                all_subj_data[key] = None

        try:  # if F1 was in file, do calculations
            subj1_data = all_subj_data[SubjIDs[0]]
            if subj1_data is not None:  # if all F1 data is present, calculate OP1 for F1
                OP1.append(calc_fasym(subj1_data))
                round_to_4(OP1[0])
            else:
                OP1.append(None)

            if subj1_data is not None:  # if all F1 data is present, calculate OP2 for F1
                OP2.append(calc_fdist(subj1_data))
                round_to_4(OP2[0])
            else:
                OP2.append(None)
        except KeyError:
            OP1.append(None)
            OP2.append(None)

        try:  # if F2 was in file, do calculations
            subj2_data = all_subj_data[SubjIDs[1]]
            if subj2_data is not None:  # if all F2 data is present, calculate OP1 for F2
                OP1.append(calc_fasym(subj2_data))
                round_to_4(OP1[1])
            else:
                OP1.append(None)

            if subj2_data is not None:  # if all F2 data is present, calculate OP2 for F2
                OP2.append(calc_fdist(subj2_data))
                round_to_4(OP2[1])
            else:
                OP2.append(None)
        except KeyError:
            OP1.append(None)
            OP2.append(None)

        # flag to check if both F1 and F2 are not None to calculate OP4
        OP4_flag = OP1[0] is not None and OP1[1] is not None

        # OP3:
        all_subj_asym = {}
        total = 0
        for key, value in all_subj_data.items():
            if value is not None:
                all_subj_asym[key] = calc_fasym(value)
                for key_op3, value_op3 in all_subj_asym[key].items():
                    total += all_subj_asym[key][key_op3]
                OP3.append((key, round(total, 4)))
                total = 0
        OP3.sort(key=lambda tup: tup[1])  # sort the tuples according to ascending total

        # OP4:
        if OP4_flag:
            a_x_b = (OP2[0]['EXEN'] * OP2[1]['EXEN'] + OP2[0]['ENAL'] * OP2[1]['ENAL'] +
                     OP2[0]['ALEX'] * OP2[1]['ALEX'] + OP2[0]['FTSBAL'] * OP2[1]['FTSBAL'] +
                     OP2[0]['SBALCH'] * OP2[1]['SBALCH'] + OP2[0]['CHFT'] * OP2[1]['CHFT'])
            a_sqr = (OP2[0]['EXEN'] ** 2 + OP2[0]['ENAL'] ** 2 + OP2[0]['ALEX'] ** 2 +
                     OP2[0]['FTSBAL'] ** 2 + OP2[0]['SBALCH'] ** 2 + OP2[0]['CHFT'] ** 2)
            b_sqr = (OP2[1]['EXEN'] ** 2 + OP2[1]['ENAL'] ** 2 + OP2[1]['ALEX'] ** 2 +
                     OP2[1]['FTSBAL'] ** 2 + OP2[1]['SBALCH'] ** 2 + OP2[1]['CHFT'] ** 2)
            OP4 = round(a_x_b / (a_sqr ** 0.5 * b_sqr ** 0.5), 4)
        else:
            OP4 = None

        return OP1, OP2, OP3[0:5], OP4

    except IOError:
        print("File not found")
        return None, None, None, None
    except (IndexError, TypeError):
        print("Invalid input arguments")
        return None, None, None, None


"""
Function to get the indices of the headers
input: line | type: string
output: header_idxs | type: list  
"""


def get_header_idxs(line):
    # SubjID[0], Landmark[1], OX[2], OY[3], OZ[4], MX[5], MY[6], MZ[7]
    check_headers = ["subjid", "landmark", "ox", "oy", "oz", "mx", "my", "mz"]
    header_idxs = []

    header_line = line.lower().split(",")
    header_line[7] = header_line[7].strip("\n")

    for i in range(8):
        idx = header_line.index(check_headers[i])
        header_idxs.append(idx)

    return header_idxs


"""
Function to calculate facial asymmetry
input: subj_data | type: list
output: fasym | type: dict 
"""


def calc_fasym(subj_data):
    fasym = {}

    for val in subj_data[0:6]:
        fasym[val[1]] = calc_eucld(val[2:8])
    return fasym


"""
Function to calculate 3D euclidean distance for facial landmarks
input: subj_data | type: list
output: fdist | type: dict 
"""


def calc_fdist(subj_data):
    fdist = {}
    landmarks_sort = {}

    # use landmarks as keys in case landmark data was not input in a particular order
    for val in subj_data[0:6]:
        landmarks_sort[val[1]] = val[2:8]

    # i.e. EXEN = calc_eucld([EX_X, EX_Y, EX_Z, EN_X, EN_Y, EN_Z])
    fdist['EXEN'] = calc_eucld(landmarks_sort['EX'][0:3] + landmarks_sort['EN'][0:3])
    fdist['ENAL'] = calc_eucld(landmarks_sort['EN'][0:3] + landmarks_sort['AL'][0:3])
    fdist['ALEX'] = calc_eucld(landmarks_sort['AL'][0:3] + landmarks_sort['EX'][0:3])
    fdist['FTSBAL'] = calc_eucld(landmarks_sort['FT'][0:3] + landmarks_sort['SBAL'][0:3])
    fdist['SBALCH'] = calc_eucld(landmarks_sort['SBAL'][0:3] + landmarks_sort['CH'][0:3])
    fdist['CHFT'] = calc_eucld(landmarks_sort['CH'][0:3] + landmarks_sort['FT'][0:3])

    return fdist


"""
Function to calculate 3D euclidean distance
input: vals | type: list
output: answer | type: float 
"""


def calc_eucld(vals):
    return ((vals[3] - vals[0]) ** 2 +
            (vals[4] - vals[1]) ** 2 +
            (vals[5] - vals[2]) ** 2) ** 0.5


"""
Function to round values in a dictionary to 4 decimal places
input: dictionary | type: dict
output: dictionary | type: dict 
"""


def round_to_4(dictionary):
    for key in dictionary:
        dictionary[key] = round(dictionary[key], 4)
    return dictionary


[OP1, OP2, OP3, OP4] = main('TestData10.csv', ('D8328', 'E4996'))
print(OP1)
print(OP2)
print(OP3)
print(OP4)
