__author__ = 'Kiri'

import os

def main():
    #initiate dictionaries for storing results
    all_file_types = dict()
    valid_results = dict()
    invalid_results = dict()
    signature_types = dict()
    percentages_by_type = dict()
    not_well_formed_results = dict()
    #initiate lists for storing results
    file_identifiers = []
    non_matching = []
    #initiate counter
    total_num_files = 0
    total_num_valid = 0
    total_num_invalid = 0
    total_num_well_formed = 0
    total_num_not_well_formed = 0
    for output_file in os.listdir("/Users/Kiri/PycharmProjects/Dryad_format_scripts/jhout"):
        #read in and chunk
        infile = open("/Users/Kiri/PycharmProjects/Dryad_format_scripts/jhout/" + output_file, 'r')
        all_info = infile.read()
        chunked_output_file = all_info.splitlines()
        file_id = 'text'
        extension = 'text'
        n_lines = 0
        sig_line = 0
        total_num_files += 1
        for chunk in chunked_output_file:
            if "RepresentationInformation" in chunk:
                file_id = chunk
            #get file extension
            #add file extension to all_file_types dict or increment
            if "File Name" in chunk:
                formats = chunk.split(".")
                index = len(formats)
                if index > 1:
                    extension = formats[index - 1]
                    if formats[index - 1] not in all_file_types:
                        all_file_types[formats[index - 1]] = 1
                    else:
                        all_file_types[formats[index - 1]] += 1
                elif index == 1:
                    extension = "no extension"
                    if "no extension" not in all_file_types:
                        all_file_types["no extension"] = 1
                    else:
                        all_file_types["no extension"] += 1
            if "SignatureMatches" in chunk:
                sig_line = n_lines
            if n_lines == sig_line + 1 and n_lines > 1:
                if chunk not in signature_types:
                    sig_list = [chunk, extension]
                    signature_types[file_id] = sig_list
            if "Status: Well-Formed and valid" in chunk:
                total_num_valid += 1
                total_num_well_formed += 1
                if extension not in valid_results:
                    valid_results[extension] = 1
                else:
                    valid_results[extension] += 1
            if "Status: Well-Formed, but not valid" in chunk:
                total_num_invalid += 1
                total_num_well_formed += 1
                if extension not in invalid_results:
                    invalid_results[extension] = 1
                else:
                    invalid_results[extension] += 1
                    file_identifiers.append(file_id)
            if "Status: Not well-formed" in chunk:
                total_num_not_well_formed += 1
                if extension not in not_well_formed_results:
                    not_well_formed_results[extension] = 1
                else:
                    not_well_formed_results[extension] += 1
            n_lines += 1
        infile.close()
    for extension, number in all_file_types.iteritems():
        if extension in valid_results:
            num_valid = valid_results[extension]
        else:
            num_valid = 0
        if extension in invalid_results:
            num_invalid = invalid_results[extension]
        else:
            num_invalid = 0
        if extension in not_well_formed_results:
            num_not_well_formed = not_well_formed_results[extension]
        else:
            num_not_well_formed = 0
        if num_invalid + num_valid + num_not_well_formed == number:
            percentage_valid = int((float(num_valid)/number)*100)
            percentage_invalid = int((float(num_invalid)/number)*100)
            percentages_list = [percentage_valid, percentage_invalid]
            percentages_by_type[extension] = percentages_list
        else:
            non_matching.append(extension)
    for item in non_matching:
        print item
    #do math on total numbers
    total_percent_valid = int((float(total_num_valid)/total_num_files)*100)
    total_percent_invalid = int((float(total_num_invalid)/total_num_files)*100)
    total_percent_wellformed = int((float(total_num_well_formed)/total_num_files)*100)
    total_percent_not_wellformed = int((float(total_num_not_well_formed)/total_num_files)*100)
    #output results
    #generate_output(all_file_types, "all_file_types")
    #generate_output(valid_results, "valid_results")
    #generate_output(invalid_results, "invalid_results")
    #generate_output(signature_types, "signature_types")
    #generate_output(percentages_by_type, "percentages_by_type")
    #generate_output(not_well_formed_results, "not_well_formed_results")
    #write total numbers of files, and numbers of files of each type to file.
    percentages = open('total_percentages.txt', 'a')
    percentages.write("Total number of files = " + str(total_num_files) + " \n")
    percentages.write("Percent Valid = " + str(total_percent_valid) + "% \n")
    percentages.write("Percent Invalid = " + str(total_percent_invalid) + "% \n")
    percentages.write("Percent Well-Formed = " + str(total_percent_wellformed) + "% \n")
    percentages.write("Percent Not Well-Formed = " + str(total_percent_not_wellformed) + "% \n")
    percentages.close()


def generate_output(dictionary_name, out_file_name):
    outfile = open(out_file_name + '.csv', 'a')
    for key, values in dictionary_name.iteritems():
        outfile.write(key + ", " + str(values) + ", ")
        outfile.write('\n')
    outfile.close()




main()