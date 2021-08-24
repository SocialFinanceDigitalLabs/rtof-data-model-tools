import argparse

from faker import Faker
from random import randrange

from rtofdata.spec_parser import parse_specification

fake = Faker()


def _date_between(field):
    return fake.date_between(start_date=field.sample_generator['args']['start_date'],
                             end_date=field.sample_generator['args']['end_date'])


def create_person_data(spec, num_records):
    person_data = {}
    for i in range(0, num_records):
        person_data[i] = {}
        person_data[i]['ni_number'] = fake.bothify('?? ######')
        person_data[i]['temp_ni_number'] = fake.bothify('?? ######')
        person_data[i]['date_of_birth'] = _date_between(spec.field_by_id('person', 'date_of_birth'))
        person_data[i]['gender'] = fake.random.choice(spec.dimension_by_id('gender').values)
        person_data[i]['dispersal_area'] = fake.postcode()
        person_data[i]['date_started_service'] = fake.date_this_month(before_today=False, after_today=True)
    return person_data


def create_baseline_data(spec, num_records):
    baseline_data ={}
    for i in range(0, num_records):
        baseline_data[i] = {}
        baseline_data[i]['unique_id'] = fake.bothify('?? ######')
        baseline_data[i]['Nationality'] = fake.random.choice(spec.dimension_by_id('nationality').values)
        baseline_data[i]['language_level_on_entry'] = fake.random.choice(spec.dimension_by_id('language_level_on_entry').values)
        baseline_data[i]['gender_follow_up'] = fake.random.choice(spec.dimension_by_id('transgender').values)
        baseline_data[i]['living_status'] = fake.random.choice(spec.dimension_by_id('living_status').values)
        baseline_data[i]['current_family_composition'] = fake.random.choice(spec.dimension_by_id('current_family_composition').values)
        baseline_data[i]['current_dependents_uk'] = fake.random.sample(spec.dimension_by_id('current_dependents_uk').values, randrange(3))
        baseline_data[i]['date_arrived_in_uk'] = _date_between(spec.field_by_id('baseline', 'date_arrived_in_uk'))
        baseline_data[i]['date_asylum_status_granted'] = _date_between(spec.field_by_id('baseline', 'date_asylum_status_granted'))
        baseline_data[i]['highest_qualification_achieved'] = fake.random.choice(spec.dimension_by_id('highest_qualification_achieved').values)
        baseline_data[i]['employed_in_home_country'] = fake.random.choice(spec.dimension_by_id('employed_in_home_country').values)
        baseline_data[i]['occupation_type'] = fake.words(2)
        baseline_data[i]['occupation_sector'] = fake.words(2)
        baseline_data[i]['occupation_goal'] = fake.words(2)
        baseline_data[i]['economic_status'] = fake.random.choice(spec.dimension_by_id('economic_status').values)
        baseline_data[i]['housing_baseline_accommodation'] = fake.random.choice(spec.dimension_by_id('housing_baseline_accommodation').values)
    return baseline_data


def create_date_last_seen_data(spec, num_records):
    date_last_seen_data = {}
    for i in range(0, num_records):
        date_last_seen_data[i] = {}
        date_last_seen_data[i]['unqiue_id'] = fake.bothify('?? ######')
        date_last_seen_data[i]['date_last_seen'] = fake.date_between()
    return date_last_seen_data


def create_employment_entry_data(spec, num_records):
    employment_entry__data = {}
    for i in range(0, num_records):
        employment_entry__data[i] = {}
        employment_entry__data[i]['unique_id'] = fake.bothify('?? ######')
        employment_entry__data[i]['employment_entry_outcome_type'] = fake.random.choice(spec.dimension_by_id('employment_entry_outcome_type').values)
        employment_entry__data[i]['date_employment_entry'] = fake.date_between()
        employment_entry__data[i]['employment_entry_details'] = fake.random.choice(spec.dimension_by_id('employment_entry_details').values)
        employment_entry__data[i]['employment_entry_occupation'] = fake.words(2)
        employment_entry__data[i]['employment_entry_sector'] = fake.words(2)
    return employment_entry__data


def create_employment_intermediate_data(spec, num_records):
    employment_intermediate_data = {}
    for i in range(0, num_records):
        employment_intermediate_data[i] = {}
        employment_intermediate_data[i]['unique_id'] = fake.bothify('?? ######')
        employment_intermediate_data[i]['date_intermediate_employment_outcome'] = _date_between(spec.field_by_id('employment_intermediate', 'date_intermediate_employment_outcome'))
        employment_intermediate_data[i]['intermediate_employment_outcome_type'] = fake.random.sample(spec.dimension_by_id('employment_entry_details').values, 3)
    return employment_intermediate_data


def create_employment_sustain_data(spec, num_records):
    employment_sustain_data = {}
    for i in range(0, num_records):
        employment_sustain_data[i] = {}
        employment_sustain_data[i]['unique_id'] = fake.bothify('?? ######')
        employment_sustain_data[i]['employment_sustain_date'] = _date_between(spec.field_by_id('employment_sustain', 'employment_sustainment_date'))
    return employment_sustain_data


def create_housing_entry_data(spec, num_records):
    housing_entry_data = {}
    for i in range(0, num_records):
        housing_entry_data[i] = {}
        housing_entry_data[i]['unique_id'] = fake.bothify('?? ######')
        housing_entry_data[i]['housing_entry_date'] = _date_between(spec.field_by_id('housing_entry', 'housing_entry_date'))
        housing_entry_data[i]['housing_entry_accomodation'] = fake.random.choice(spec.dimension_by_id('housing_entry_accomodation').values)
    return housing_entry_data


def create_housing_sustain_data(spec, num_records):
    housing_sustain_data = {}
    for i in range(0, num_records):
        housing_sustain_data[i] = {}
        housing_sustain_data[i]['unique_id'] = fake.bothify('?? ######')
        housing_sustain_data[i]['housing_sustainment_date'] = _date_between(spec.field_by_id('housing_sustain', 'housing_sustainment_date'))
    return housing_sustain_data


def create_integration_data(spec, num_records):
    integration_data = {}
    for i in range(0, num_records):
        integration_data[i] = {}
        integration_data[i]['unique_id'] = fake.bothify('?? ######')
        integration_data[i]['integration_outcome_type'] = fake.random.choice(spec.dimension_by_id('integration_outcome_type').values)
        integration_data[i]['integration_outcome_achieved_date'] = _date_between(spec.field_by_id('integration_plan', 'integration_outcome_achieved_date'))
        integration_data[i]['integration_comms_language'] = fake.random.choice(spec.dimension_by_id('integration_comms_language').values)
        integration_data[i]['integration_digital'] = fake.random.choice(spec.dimension_by_id('integration_digital').values)
        integration_data[i]['integration_social'] = fake.random.choice(spec.dimension_by_id('integration_social').values)
    return integration_data


def create_all_data(num_records):
    """
    By removing the "top-level" code, we can run individual generators without running all the code inbetween
    """

    spec = parse_specification()

    person_fake = create_person_data(spec, num_records)
    baseline_fake = create_baseline_data(spec, num_records)
    date_last_seen_fake = create_date_last_seen_data(spec, num_records)
    employment_entry_fake = create_employment_entry_data(spec, num_records)
    employment_intermediate_fake = create_employment_intermediate_data(spec, num_records)
    employment_sustain_fake = create_employment_sustain_data(spec, num_records)
    housing_entry_fake = create_housing_entry_data(spec, num_records)
    housing_sustain_fake = create_housing_sustain_data(spec, num_records)
    integration_data_fake = create_integration_data(spec, num_records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create fake data'
    )
    parser.add_argument("num_records", type=int, nargs='?', default=10, help="The number of records to generate")
    args = parser.parse_args()
    create_all_data(args.num_records)
