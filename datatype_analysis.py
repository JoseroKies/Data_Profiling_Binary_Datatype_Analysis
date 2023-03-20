import os
import csv

all_binary_candidates = []


# iterate through all csv data:
def process_csv_files(folder_path):
    DATA_COUNT = 975729  # work_data
    # DATA_COUNT = 1488      # test_data
    c = 0
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.csv'):
                csv_path = os.path.join(root, filename)
                with open(csv_path, 'r', encoding='utf-8') as csv_file:
                    csv_data = csv.reader(csv_file)
                    analyse_csv(csv_data)  # analyse each csv file
                    c += 1
                    print(csv_path + ", " + str("{:.2f}".format(round(c / DATA_COUNT * 100, 2))) + "%")

    with open('bin_value_canditate_analysis.csv', 'w', encoding='utf-8') as f:
        analysed_binary_values = analyse_all_binary_candidates()
        f.write("binary_candidate\tcount\tdatatypes\tjaccard_similarity\n")
        for v in analysed_binary_values:
            f.write(str(v[0]) + "\t" + str(v[1]) + "\t" + str(v[2]) + "\t" + str(v[3]) + "\n")


# analyse the binary candidates
def analyse_all_binary_candidates():
    global all_binary_candidates

    counts = {}
    for s in all_binary_candidates:
        s = frozenset(s)  # convert set to frozenset to make it hashable
        if s in counts:
            counts[s] += 1
        else:
            counts[s] = 1

    result = [(tuple(s), counts[s], (check_datatype_of_string(tuple(s)[0]), check_datatype_of_string(tuple(s)[1])),
               sim_jaccard(tuple(s)[0], tuple(s)[1], False, 1)) for s in counts]

    # sort result:
    result.sort(key=lambda x: x[1], reverse=True)

    return result


# analyse attribute datatypes in a csv reader object
def analyse_csv(csv_data):
    columns = get_columns_from_csv_data(csv_data)
    for col in columns:
        # print("{",col[0],",",len(col),",",col[1],",",col[2],",",col[3],"}")
        print("Attributname: " + str(col[0]) + ", " + "Datentyp: " + str(get_datatype(col[1:])))


# get all columns (attributes) from a csv reader. first object is the attribute name
def get_columns_from_csv_data(csv_data):
    header = next(csv_data)
    columns = [[] for _ in range(len(next(csv_data)))]
    for i, attribute in enumerate(header):
        columns[i].append(attribute)
    for row in csv_data:
        for i, value in enumerate(row):
            columns[i].append(value)
    return columns


# get the datatype of a column (attribute) of a csv reader
def get_datatype(attribute):
    global all_binary_candidates

    for element in attribute:
        element = str(element)
        # check if datatype is binary ---------------------------------------------------------------------------------
        binary_set = set()
        binary_set.update(attribute)
        if len(binary_set) == 2:
            all_binary_candidates.append(binary_set)
            return "binary"
        # check if datatype is numeric --------------------------------------------------------------------------------
        return check_datatype_of_string(element)
        # -------------------------------------------------------------------------------------------------------------
        return "string"


# check if a string can be a float or an integer
def check_datatype_of_string(string):
    if "." in string:
        try:
            float(string)
            return "float"
        except ValueError:
            return "string"
    else:
        try:
            int(string)
            return "integer"
        except ValueError:
            return "string"


# get tokens from a string for jaccard
def get_ngram_tokens(text, case_sensitive, n):
    tokens = set()
    for i in range(0, len(text)):
        t = ""
        if i + n - 1 < len(text):
            for j in range(i, i + n):
                if case_sensitive:
                    t += text[j]
                else:
                    t += text[j].upper()
            tokens.add(t)
    return tokens


# get jaccard similarity
def sim_jaccard(s1, s2, case_sensitive, token_len):
    tokens1 = get_ngram_tokens(s1, case_sensitive, token_len)
    tokens2 = get_ngram_tokens(s2, case_sensitive, token_len)
    if len(tokens1.union(tokens2)) > 0:
        return len(tokens1.intersection(tokens2)) / len(tokens1.union(tokens2))
    else:
        return 1



#process_csv_files('C:/Users/kgmai/Documents/Uni/DI_Sem/work_data')
