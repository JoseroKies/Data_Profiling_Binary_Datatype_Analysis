import csv


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


def compute_binary_probability(bin_value_canditate_analysis_path, weighting, considerNull, useSpecialFilter):
    abc = read_csv_file(bin_value_canditate_analysis_path)
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


# Achtung! sum(weighting) <= 13
def calculate_score(attribute1: int, attribute2: bool, attribute3: float, attribute4: bool, weighting: list,
                    MAX_COUNT: int) -> float:
    SCORE_DIVISOR = 12
    scaled_attribute1 = attribute1 / MAX_COUNT * weighting[0]  # Bonus für Attribut 1
    scaled_attribute2 = 0.01 * weighting[1] if attribute2 else 0.0  # Bonus für Attribut 2
    scaled_attribute3 = attribute3 * weighting[2]  # Bonus für Attribut 3
    scaled_attribute4 = -0.01 * weighting[3] if attribute4 else 0.0  # Malus für Attribut 4
    total = scaled_attribute1 + scaled_attribute2 + scaled_attribute3 + scaled_attribute4
    score = total / SCORE_DIVISOR
    return score

def compute_final_rank(scored_candidates):

        rows = read_csv_file(scored_candidates)

        # Zählen Sie die Anzahl der Zeilen in der CSV-Datei
        num_rows = sum(1 for row in rows)


        c = num_rows
        # Öffnen Sie die CSV-Datei zum Schreiben
        with open('ranked_' + scored_candidates, 'w', newline='', encoding='utf-8') as f:
            # Schleife durch jede Zeile der CSV-Datei
            for row in rows:
                if c == num_rows:
                    f.write("binary_candidate\tcount\tdatatypes\tjaccard_similarity\tmultiple_occurrence\tfinal_score\trank\n")
                    c = c-1
                    continue
                # Berechnen Sie den Wert für jede Zeile
                value = c / num_rows


                row_s = ""
                for r in row:
                    row_s = row_s + str(r) + "\t"
                row_s = row_s + str(value) + "\n"
                f.write(row_s)
                c = c - 1

print(calculate_score(316322, True, 0, False, [10, 1, 0.1, 0.1], 316322))
print(calculate_score(6322, False, 0, True, [10, 1, 0.1, 0.01], 316322))
print(calculate_score(3000, True, 1, False, [10, 1, 0.1, 0.01], 316322))

# compute_count_graph(read_csv_file("bin_value_canditate_analysis.csv"))
#l = compute_binary_probability("bin_value_canditate_analysis_V2 (sorted by count) [added multiple occurrence].csv", [10, 1, 0.1, 0.1], False, True)
compute_final_rank("bin_value_canditate_analysis_V4 (sorted by score) [count=10, type=1, sim=0.1, multiple=0.1].csv")