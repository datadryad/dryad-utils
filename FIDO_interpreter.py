__author__ = 'Kiri'
#script to pull in and parse FIDO outputs from running over dev server.

def main():
    #initialize dictionaries to hold stats
    all_file_extensions =dict()
    file_status = dict()
    match_types = dict()
    not_ok_extensions = dict()
    ok_extensions = dict()
    percentages_ok_by_type = dict()
    percentages_by_match_type = dict()
    #initialize count variables
    total_num_files = 0
    curiosity = 0
    total_num_ok = 0
    total_num_not_ok = 0
    non_matching = []
    #read in data from file
    items_list = get_metadata()
    for item in items_list:
        total_num_files += 1
        #find the extension
        extension = 'text'
        formats = item[9].split(".")
        index = len(formats)
        if index > 1:
            extension = formats[index - 1]
            if formats[index - 1] not in all_file_extensions:
                    all_file_extensions[formats[index - 1]] = 1
            else:
                    all_file_extensions[formats[index - 1]] += 1
        elif index == 1:
            extension = "no extension"
            if "no extension" not in all_file_extensions:
                all_file_extensions["no extension"] = 1
            else:
                all_file_extensions["no extension"] += 1
        #check to see whether the file is ok, and add the extension to the appropriate dictionary
        if "OK" in item[0]:
            total_num_ok += 1
            if extension not in ok_extensions:
                ok_extensions[extension] = 1
            else:
                ok_extensions[extension] += 1
        if "OK" not in item[0]:
            total_num_not_ok += 1
            if extension not in not_ok_extensions:
                not_ok_extensions[extension] = 1
            else:
                not_ok_extensions[extension] += 1
            if "fail" not in item[8]:
                curiosity += 1
        #record item status in the appropriate dictionary
        if item[0] not in file_status:
            file_status[item[0]] = 1
        elif item[0] in file_status:
            file_status[item[0]] += 1
        #record the types of matches the program claimed to make
        if item[8] not in match_types:
            match_types[item[8]] = 1
        elif item[8] in match_types:
            match_types[item[8]] += 1
    #do stats on the gathered information
    for extension, number in all_file_extensions.iteritems():
        if extension in ok_extensions:
            num_ok = ok_extensions[extension]
        else:
            num_ok = 0
        if extension in not_ok_extensions:
            num_not_ok = not_ok_extensions[extension]
        else:
            num_not_ok = 0
        if num_not_ok + num_ok == number:
            percentage_valid = int((float(num_ok)/number)*100)
            percentage_invalid = int((float(num_not_ok)/number)*100)
            percentages_list = [percentage_valid, percentage_invalid]
            percentages_ok_by_type[extension] = percentages_list
        else:
            non_matching.append(extension)
    for item in non_matching:
        print item
    for match_type, number in match_types.iteritems():
        type_percentage = int((float(number)/total_num_files)*100)
        type_list = [match_type, type_percentage]
        percentages_by_match_type[match_type] = type_list
    #output results
    generate_output(all_file_extensions, "fido_all_extensions")
    generate_output(file_status, "fido_status")
    generate_output(match_types, "fido_match_types")
    generate_output(not_ok_extensions, "fido_not_ok")
    generate_output(ok_extensions, "fido_ok")
    generate_output(percentages_ok_by_type, "fido_ok_percentages")
    generate_output(percentages_by_match_type, "fido_match_percentages")
    total_percent_ok = int((float(total_num_ok)/total_num_files)*100)
    total_percent_not_ok = int((float(total_num_not_ok)/total_num_files)*100)
    percentages = open('fido_total_percentages.txt', 'a')
    percentages.write("Total number of files = " + str(total_num_files) + " \n")
    percentages.write("Percent OK = " + str(total_percent_ok) + "% \n")
    percentages.write("Percent Not OK = " + str(total_percent_not_ok) + "% \n")
    percentages.close()


def get_metadata():
    master_list = []
    infile = open("FidoOut20151020.csv", 'r')
    metadata = infile.read()
    individual_metadata = metadata.splitlines()
    for package in individual_metadata:
        entry_list = []
        fields = package.split(",")
        for field in fields:
            entry_list.append(field)
        master_list.append(entry_list)
    infile.close()
    return master_list

def generate_output(dictionary_name, out_file_name):
    outfile = open(out_file_name + '.csv', 'a')
    for key, values in dictionary_name.iteritems():
        outfile.write(key + ", " + str(values) + ", ")
        outfile.write('\n')
    outfile.close()



main()