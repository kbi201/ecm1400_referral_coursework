from covid_data_handler import parse_csv_data

def process_covid_csv_data(covid_csv_data: str) -> int :
    # last7days_cases :: index value = [6]
    new_cases_by_specimen = []
    # current_hospital_cases :: index value = [5]
    hospital_cases = []
    # total_deaths :: index value = [4]
    total_deaths_list = []
    for data_row in covid_csv_data:
        data_row = data_row.split(',')
        if data_row[4] == '':
            data_row[4] = 0
        total_deaths_list.append(data_row[4])
        if data_row[5] == '':
            data_row[5] = 0
        hospital_cases.append(data_row[5])
        if data_row[6] == '':
            data_row[6] = 0
        new_cases_by_specimen.append(data_row[6])
    else:
        # last7day_cases
        new_cases_by_specimen = [int(float(i)) for i in new_cases_by_specimen]
        last7_days = new_cases_by_specimen[2:9]
        last7days_cases = sum(last7_days)
        # current_hospital_cases
        hospital_cases = [int(float(i)) for i in hospital_cases]
        current_hospital_cases = hospital_cases[0]
        # total_deaths
        total_deaths_list = [int(float(i)) for i in total_deaths_list]
        index = 0
        try:
            for i in total_deaths_list:
                if total_deaths_list[index] == 0:
                    index += 1
            else:
                total_deaths = total_deaths_list[index]
                print("Total deaths calculated.")
        except IndexError:
            print('Index error occured, showing output as 0.')
            total_deaths = 0
    print(last7days_cases, current_hospital_cases, total_deaths)

process_covid_csv_data(parse_csv_data('nation_2021-10-28.csv'))
print(parse_csv_data('nation_2021-10-28.csv')[1])