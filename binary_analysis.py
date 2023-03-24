import csv
import matplotlib.pyplot as plt

"""
This function is reading the csv table for binary candidates at the given filepath and dumps all rows 
into a list. Attributes will be casted in their specific data type.
IMPORTANT: attributes have to have a specific data type
    attribute0: a tuple with two values in the form ('val1', 'val2')
    attribute1: integer
    attribute2: a tuple with two values in the form ('val1', 'val2')
    attribute3: float
    attribute4: bool (OPTIONAL)
    attribute5: float (OPTIONAL)  
    possible schemes:
        (binary_candidate, count, datatypes, jaccard_similarity)
        (binary_candidate, count, datatypes, jaccard_similarity, multiple_occurrence)
        (binary_candidate, count, datatypes, jaccard_similarity, multiple_occurrence, final_score)
        
@param filepath: The filepath for the binary candidates csv table
@return: A list with each row as a list of the csv table in the correct casted data type
"""


def read_csv_file(filepath):
    with open(filepath, newline='', encoding="utf-8") as csvfile:
        all_rows = []
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            casted_row = []
            if row[0] != "binary_candidate":
                casted_row.append(string_to_tuple(row[0]))
                casted_row.append(int(row[1]))
                casted_row.append(string_to_tuple(row[2]))
                casted_row.append(float(row[3]))
                try:
                    casted_row.append(bool(row[4]))
                except:
                    pass
                try:
                    casted_row.append(float(row[5]))
                except:
                    pass
                all_rows.append(casted_row)
        return all_rows


"""
This function is casting a string in the form of "('val1', 'val2')" to an actual tuple ('val1', 'val2').
@param s: The string which you want to cast.
@return: The tuple casted from the string.
"""


def string_to_tuple(s):
    try:
        elements = s.strip('()').split("\', \'")
        elements = [e.strip() for e in elements]
        elements[0] = elements[0][1:]
        elements[1] = elements[1][:len(elements[1]) - 1]
    except:
        elements = s.strip('()').split(", ")
        elements = [e.strip() for e in elements]
    return tuple(elements)


"""
This function needs a list created by read_csv_file(filepath) as input.
It checks for multiple occurrences. If one of the two elements of the first value of each list in the input list 
occurs in an other list from the input list a True will be appended to the current list, else False.
At the end the modified input list will be saved as a csv table with the scheme
Input_scheme:  (binary_candidate, count, datatypes, jaccard_similarity)
Output_scheme: (binary_candidate, count, datatypes, jaccard_similarity, multiple_occurrence)

@:param all_bin_candidates: The input list (created by read_csv_file(filepath))
"""


def analyse_bin_candidates(all_bin_candidates):
    with open('bin_value_canditate_analysis_V2.csv', 'w', encoding='utf-8') as f:
        f.write("binary_candidate\tcount\tdatatypes\tjaccard_similarity\tmultiple_occurrence\n")
        l = len(all_bin_candidates) * len(all_bin_candidates)
        count = 0
        for c in all_bin_candidates:
            res = False
            for c1 in all_bin_candidates:
                if not c == c1:
                    res = (c[0][0] in c1[0] or c[0][1] in c1[0])
                    if res:
                        break
                count = count + 1
            print(str("{:.4f}".format(round(count / l * 100, 4))) + "%")
            c.append(res)
            res_str = ""
            for v in c:
                res_str = res_str + str(v) + "\t"
            f.write(res_str + "\n")


"""
This function creates a weighted final_score for each binary_candidate, calculated by the four given values 
count, datatypes, jaccard_similarity, multiple_occurrence
Input-scheme: (binary_candidate, count, datatypes, jaccard_similarity, multiple_occurrence)
Output-scheme: (binary_candidate, count, datatypes, jaccard_similarity, multiple_occurrence, final_score)

@param bin_value_candidate_analysis_path: The path of binary candidate csv table with the scheme (binary_candidate, 
count, datatypes, jaccard_similarity, multiple_occurrence, final_score)
@param weighting: A list with four fload values [v1:count, v2:datatypes, v3:jaccard_similarity, v4:multiple_occurrence]
corresponding to the weights of the four parameters
@param considerNull: A bool value if you want to consider candidates which include "" as a value.
If True: such candidates will have a final_score of 0
@param useSpecialFilter: A bool value if you want to have some special filters or not.
@return: Returns a list corresponding to the output csv table sorted by the final score
"""


def compute_binary_probability(bin_value_candidate_analysis_path, weighting, considerNull, useSpecialFilter):
    abc = read_csv_file(bin_value_candidate_analysis_path)
    MAX_COUNT = abc[0][1]
    for v in abc:
        if not considerNull and "" in v[0]:
            v.append(0)
            continue

        # special_filter :
        if useSpecialFilter:
            if "1610" in str(v[0][0]) or "1610" in str(v[0][1]):
                v.append(0)
                continue
            if "www." in str(v[0][0]) or "www." in str(v[0][1]):
                v.append(0)
                continue
            if "http" in str(v[0][0]) or "http" in str(v[0][1]):
                v.append(0)
                continue
            if len(str(v[0][0])) > 70 or len(str(v[0][1])) > 70:
                v.append(0)
                continue
                # komplett gleicher string bsp ('Victoria', 'VICTORIA')
            if str(v[0][0]).lower() == str(v[0][1]).lower():
                v.append(0)
                continue

        probability = calculate_score(v[1],
                                      v[2][0] == v[2][1],
                                      v[3],
                                      v[4],
                                      weighting,
                                      MAX_COUNT)

        # special filter :
        if useSpecialFilter:
            for year in range(1800, 2023):
                if str(year) in str(v[0][0]) or str(year) in str(v[0][1]):
                    probability = 0
                    break

        v.append(probability)

    sorted_list = sorted(abc, key=lambda x: x[5], reverse=True)

    with open('bin_value_canditate_analysis_V4 (sorted by score) [count=10, type=1, sim=0.1, multiple=0.1].csv', 'w', encoding='utf-8') as f:
        f.write("binary_candidate\tcount\tdatatypes\tjaccard_similarity\tmultiple_occurrence\tfinal_score\n")

        for v in sorted_list:
            res_str = ""
            print(v)
            if v[5] != 0:
                for a in v:
                    res_str = res_str + str(a) + "\t"
                f.write(res_str + "\n")

    return sorted_list


"""
A helping function to weight the score properly for the 
compute_binary_probability(bin_value_candidate_analysis_path, weighting, considerNull, useSpecialFilter) function.
@param attribute1: count integer value of the binary candidates
@param attribute2: (datatype[0]==datatype[1]) bool value of the binary candidates
@param attribute3: jaccard_similarity float value of the binary candidates
@param attribute4: multiple_occurrence bool value of the binary candidates
@param weighting: A list corresponding to the weighting of the final score IMPORTANT: sum(weighting) <= 13
@return: The weighted final score (value between 0-1)
"""


def calculate_score(attribute1: int, attribute2: bool, attribute3: float, attribute4: bool, weighting: list,
                    MAX_COUNT: int) -> float:
    SCORE_DIVISOR = 12
    scaled_attribute1 = attribute1 / MAX_COUNT * weighting[0]               # Bonus for attribute 1
    scaled_attribute2 = 0.01 * weighting[1] if attribute2 else 0.0          # Bonus for attribute 2
    scaled_attribute3 = attribute3 * weighting[2]                           # Bonus for attribute 3
    scaled_attribute4 = -0.01 * weighting[3] if attribute4 else 0.0         # Malus for attribute 4
    total = scaled_attribute1 + scaled_attribute2 + scaled_attribute3 + scaled_attribute4
    score = total / SCORE_DIVISOR
    return score


"""
This function computes the final rank for each binary candidate and adds it to the csv table.
Input-scheme: (binary_candidate, count, datatypes, jaccard_similarity, multiple_occurrence, final_score)
Output-scheme: (binary_candidate, count, datatypes, jaccard_similarity, multiple_occurrence, final_score, rank)
"""


def compute_final_rank(scored_candidates):
        rows = read_csv_file(scored_candidates)
        num_rows = sum(1 for row in rows)
        c = num_rows
        with open('ranked_' + scored_candidates, 'w', newline='', encoding='utf-8') as f:
            for row in rows:
                if c == num_rows:
                    f.write("binary_candidate\tcount\tdatatypes\tjaccard_similarity\tmultiple_occurrence\tfinal_score\trank\n")
                    c = c-1
                    continue
                value = c / num_rows
                row_s = ""
                for r in row:
                    row_s = row_s + str(r) + "\t"
                row_s = row_s + str(value) + "\n"
                f.write(row_s)
                c = c - 1


"""
plot_count() is plotting the count attribute of bin_value_canditate_analysis.csv
"""


def plot_count():
    cs = read_csv_file("bin_value_canditate_analysis.csv")
    v = []
    sum = 0
    for i in reversed(range(0, len(cs))):
        v.append(cs[i][1])
        sum = sum+cs[i][1]
    print(sum)
    x = range(len(v))
    y = v
    plt.plot(x, y, linewidth=5)
    plt.show()



# compute_count_graph(read_csv_file("bin_value_canditate_analysis.csv"))
# analyse_bin_candidates(read_csv_file("bin_value_canditate_analysis.csv"))
# compute_binary_probability("bin_value_canditate_analysis_V2 (sorted by count) [added multiple occurrence].csv", [10, 1, 0.1, 0.1], False, True)
# compute_final_rank("bin_value_canditate_analysis_V4 (sorted by score) [count=10, type=1, sim=0.1, multiple=0.1].csv")
#plot_count()