import pytest
import sys
import json
from query.single_query import *
from query.create_embeds import *

def transform_to_dict(json_ans):

    data = json.loads('{' + json_ans + '}')

    transformed_dict = {}
    for header, items in data.items():
        transformed_dict[header] = {
            "period": {item["period"] for item in items},
            "value": {item["value"] for item in items},
            "sheet": {item["sheet"] for item in items},
            "cell": {item["cell"] for item in items}
        }
    return transformed_dict

def calculate_matching_percentage(expected_dict, result_dict):

    matching_count = 0
    total_count = 0

    for header, expected_values in expected_dict.items():
        if header in result_dict:
            result_values = result_dict[header]
            for key in expected_values: # key = "period", "value", "sheet", "cell
                value_count = 0
                value_total = 0

                if key in result_values:
                    set_expected = expected_values[key]
                    set_result = result_values[key]
                    common_elements = set_result.intersection(set_expected)
                    percentage_common = (len(common_elements) / min(len(set_result), len(set_expected))) * 100
                    if (percentage_common >= 60):   
                        matching_count += 1
                    else:
                        print(f"for term {header}")
                        print(f"For parametter {key} got only {percentage_common}% of matching values")
                        print(f"Expected values: {set_expected}")
                        print(f"Result values: {set_result}")
                    total_count += 1
                else:
                    print(f"Expected values for {key} not found in result")
    matching_percentage = (matching_count / total_count) * 100
    return matching_percentage



# Assume transform_to_dict and calculate_matching_percentage are defined elsewhere in your code

@pytest.mark.parametrize("test_input", [
    {"query": "Revenue",
     "expected_values": {
         "period": {'12 Months Ended Dec. 31, 2022', '12 Months Ended Dec. 31, 2023', '12 Months Ended Dec. 31, 2021'},
         "value": {5896, 8971, 7245},
         "sheet": {"NOW-US, IS FY'23"},
         "cell": {"C14", "B14", "D14"}
     }},
    {"query": "Cost of Goods Sold (COGS)",
     "expected_values": {
         "period": {"12 Months Ended Dec. 31, 2023", "12 Months Ended Dec. 31, 2022", "12 Months Ended Dec. 31, 2021"},
         "value": {1921, 1573, 1353},
         "sheet": {"NOW-US, IS FY'23"},
         "cell": {"D17", "C17", "B17"}
     }},
        {"query": "Operating Expenses",
        "expected_values": {
        "period": {"12 Months Ended Dec. 31, 2023", "12 Months Ended Dec. 31, 2022", "12 Months Ended Dec. 31, 2021"},
        "value": {6288, 4286, 5317},
        "sheet": {"NOW-US, IS FY'23"},
        "cell": {"B24", "C24", "D24"}
    }},
    {"query": "Other Income/Expenses",
        "expected_values": {
        "period": {"12 Months Ended Dec. 31, 2023", "12 Months Ended Dec. 31, 2022", "12 Months Ended Dec. 31, 2021"},
        "value": {-56, -38, -28},
        "sheet": {"NOW-US, IS FY'23"},
        "cell": {"B28", "C28", "D28"}
    }},
    {"query": "Capital Expenditures",
        "expected_values": {
        "period": {"12 Months Ended Dec. 31, 2023", "12 Months Ended Dec. 31, 2022", "12 Months Ended Dec. 31, 2021"},
        "value": {-694, -550, -392},
        "sheet": {"NOW-US, CF FY'23"},
        "cell": {"B33", "C33", "D33"}
    }},
    {"query":  "Stock-Based Compensation",
     "expected_values" : {
        "period": {"12 Months Ended Dec. 31, 2023", "12 Months Ended Dec. 31, 2022", "12 Months Ended Dec. 31, 2021"},
        "value": {1604, 1401, 1131},
        "sheet": {"NOW-US, CF FY'23"},
        "cell": {"B19", "C19", "D19"}
    }},

    {"query": "Depreciation and Amortization",
    "expected_values" : { 
        "period": {"12 Months Ended Dec. 31, 2023", "12 Months Ended Dec. 31, 2022", "12 Months Ended Dec. 31, 2021"},
        "value": {562, 472, 433},
        "sheet": {"NOW-US, CF FY'23"},
        "cell": {"B17", "C17", "D17"} 
        }},  
])

def test_query_processing(test_input):
    namespace = "sample.xlsx"
    filepath = "uploads/sample.xlsx"
    filtered_table_name = "test/filtered_table_sample"
    query = test_input["query"]
    expected_values = test_input["expected_values"]

    query_result = answer_single_query(query, namespace, filepath, filtered_table_name)
    result_dict = transform_to_dict(query_result)
    matching_percentage = calculate_matching_percentage({query: expected_values}, result_dict)
    assert matching_percentage >= 60, "At least 60% of period/value/sheet/cells should be equal"



    

