import pandas as pd
from api_operations import retrieve_rates_via_api, retrieve_wos_metadata_via_api
from visualizations import visualize_data
from datetime import date, datetime, timedelta


def retrieve_rates_from_table():
    """Get the exchange rates from the locally cached .csv file in case the API endpoint doesn't
    return data.

    :return: dict.
    """
    rates_df = (pd.read_csv(filepath_or_buffer='currencies.csv', skiprows=2, index_col='Currency'))
    return rates_df.to_dict(orient='dict')['Rate VS USD']


def get_usd_rates():
    """Retrieve exchange rates to convert various currencies into USD.

    :return: dict.
    """
    tod = date.today()
    with open('currencies.csv', 'r') as reading:
        updated = datetime.strptime(reading.readline().split(',')[1][:-1], '%m/%d/%Y').date()
    if tod - updated < timedelta(days=1):
        return retrieve_rates_from_table()
    return retrieve_rates_via_api()


def fetch_names(names_json):
    """Retrieve the names of the principal investigator and other grant participants, if any.

    :param names_json: dict.
    :return: str, str.
    """
    pr_inv = ''
    other_nms = ''
    if names_json['count'] > 0:
        if names_json['count'] == 1 and names_json['name']['role'] == 'principal_investigator':
            pr_inv = names_json['name']['full_name']
        elif names_json['count'] == 1 and names_json['name']['role'] != 'principal_investigator':
            other_nms = names_json['name']['full_name']
        else:
            non_pis = []
            for name in names_json['name']:
                if name['role'] == 'principal_investigator':
                    pr_inv = name['full_name']
                else:
                    non_pis.append(name['full_name'])
            other_nms = ', '.join(non_pis)
    return pr_inv, other_nms


def fetch_grant_agency(item):
    """Retrieve the name(s) of the grant agencies, if any.

    :param item: dict.
    :return: str.
    """
    agencies = []
    if isinstance(item['grant_agency_names'], list):
        for funder in item['grant_agency_names']:
            if funder['pref'] == 'Y' and funder['content'] not in agencies:
                agencies.append(funder['content'])
        return ', '.join(agencies)
    return item['grant_agency_names']['content']


def fetch_grant_country(item):
    """Return country of the funding agency

    :param item: dict.
    :return: str.
    """
    if 'grant_agencies' in item.keys():
        if isinstance(item['grant_agencies']['grant_agency'], list):
            return ', '.join(list(set(f['country'] for f in item['grant_agencies']['grant_agency'])))
        return item['grant_agencies']['grant_agency']['country']
    return ''


def fetch_pi_institution(item):
    """Retrieve the name(s) of the principal investigator's institution, if any.

    :param item: dict.
    :return: str.
    """
    pi_orgs = []
    if 'principalInvestigatorInstitutions' in item['principalInvestigators']:
        if isinstance(item['principalInvestigators']['principalInvestigatorInstitutions'], list):
            for institutions in item['principalInvestigators']['principalInvestigatorInstitutions']:
                for institution in institutions['principalInvestigatorInstitution']:
                    if 'pref' in institution:
                        if institution['pref'] == 'Y' and institution['content'] not in pi_orgs:
                            pi_orgs.append(institution['content'])
        else:
            try:
                for institution in item['principalInvestigators']['principalInvestigatorInstitutions'][
                        'principalInvestigatorInstitution']:
                    if 'pref' in institution:
                        if institution['pref'] == 'Y':
                            pi_orgs.append(institution['content'])
            except TypeError:
                pass
    return ', '.join(pi_orgs)


def fetch_fin_year(item):
    """Retrieve the financial year value, if present in the grant record.

    :param item: dict.
    :return: int or str.
    """
    if 'financial_year' in item:
        return item['financial_year']
    return ''


def fetch_related_records(item):
    """Retrieve the associated Web of Science records list, if present in the grant record.

    :param item: dict.
    :return: str, int.
    """
    if 'related_records' in item:
        if isinstance(item['related_records']['record'], list):
            records_list = [r['uid'] for r in item['related_records']['record']]
            return ', '.join(records_list), len(records_list)
        return item['related_records']['record']['uid'], 1
    return '', 0


def fetch_document_title(item):
    """Retrieve the grant title.

    :param item: dict.
    :return: str.
    """
    if isinstance(item['title'], list):
        for title in item['title']:
            if title['type'] == 'item':
                return title['content']
    return item['title']['content']


def fetch_keywords(item):
    """Retrieve grant keywords.

    :param item: dict.
    :return: str.
    """
    keywords_list = []
    if 'keywords' in item:
        if isinstance(item['keywords']['keyword'], list):
            for keyword in item['keywords']['keyword']:
                if 'content' in keyword.keys():
                    keywords_list.append(str(keyword['content']))
            return ', '.join(keywords_list)
        if 'content' in item['keywords']['keyword'].keys():
            return item['keywords']['keyword']['content']
    return ''


def fetch_abstract(item):
    """Retrieve grant description.

    :param item: dict.
    :return: str.
    """
    if isinstance(item['abstracts'], list):
        return [', '.join(a['abstract_text']['p']) for a in item['abstracts']['abstract']]
    if 'abstract' in item['abstracts'].keys():
        return item['abstracts']['abstract']['abstract_text']['p']
    return ''


def convert_to_usd(amount, currency, r):
    """Converts grant amount into USD.

    :param amount: int or float.
    :param currency: str.
    :param r: dict.
    :return: str or float.
    """
    if amount == '':
        return ''
    if currency == 'USD':
        return amount
    if currency in r.keys():
        return amount / r[f'{currency}']


def fetch_data(json, rates, grants_list):
    """Take JSON retrieved by the API, append each record to a grants_list list.

    :param json: dict.
    :param rates: dict.
    :param grants_list: list.
    :return: None.
    """
    for record in json['Data']['Records']['records']['REC']:
        ut = record['UID']
        print(ut)
        pub_year = record['static_data']['summary']['pub_info']['pubyear']
        fin_year = fetch_fin_year(record['static_data']['item'])
        principal_investigator, other_names = fetch_names(record['static_data']['summary']['names'])
        doctype = record['static_data']['summary']['doctypes']['doctype']
        doctitle = fetch_document_title(record['static_data']['summary']['titles'])
        keywords = fetch_keywords(record['static_data']['fullrecord_metadata'])
        abstract = fetch_abstract(record['static_data']['fullrecord_metadata'])
        related_wos_records, related_wos_records_count = fetch_related_records(record['static_data']
                                                                               ['fullrecord_metadata'])
        grant = record['static_data']['fullrecord_metadata']['fund_ack']['grants']['grant']
        grant_agency = fetch_grant_agency(grant)
        grant_country = fetch_grant_country(record['static_data']['item'])
        grant_source = grant['grant_source']
        grant_data_item = grant['grant_data']['grantDataItem']
        grant_pi_institution = fetch_pi_institution(grant_data_item)
        grant_amount = grant_data_item['totalAwardAmount']
        grant_currency = grant_data_item['currency']
        grant_amount_in_usd = convert_to_usd(grant_amount, grant_currency, rates)

        grants_list.append({
            'UT': ut,
            'Publication Year': pub_year,
            'Financial Year': fin_year,
            'Principal Investigator': principal_investigator,
            'Other Names': other_names,
            'Document Type': doctype,
            'Document Title': doctitle,
            'Keywords': keywords,
            'Grant Description': abstract,
            'Related WoS Records': related_wos_records,
            'Related WoS Records Count': related_wos_records_count,
            'Funding Agency': grant_agency,
            'Funding Country': grant_country,
            'Grant Source': grant_source,
            'Principal Investigator Institution': grant_pi_institution,
            'Grant Amount': grant_amount,
            'Currency': grant_currency,
            'Grant Amount, USD': grant_amount_in_usd
        })


def visualize_excel(file):
    """Visualize graphs from previously saved Excel file.

    :param file:
    :return: tuple of str.
    """
    df = pd.read_excel(file)
    plots = visualize_data(df)
    return plots


def run_button_main_function(apikey, search_query):
    records_per_page = 100
    grants_list = []
    usd_rates = get_usd_rates()
    initial_json = retrieve_wos_metadata_via_api(apikey, search_query, records_per_page)
    fetch_data(initial_json, usd_rates, grants_list)
    total_results = initial_json['QueryResult']['RecordsFound']
    requests_required = ((total_results - 1) // records_per_page) + 1
    print(f'Total Web of Science API requests required: {requests_required}.')
    for i in range(1, requests_required):
        first_record = int(f'{i}01')
        subsequent_json = retrieve_wos_metadata_via_api(apikey, search_query, records_per_page, first_record)
        fetch_data(subsequent_json, usd_rates, grants_list)
        print(f'Request {i + 1} of {requests_required} complete.')

    df = pd.DataFrame(grants_list)
    safe_filename = search_query.replace('*', '').replace('"', '')
    df.to_excel(
        excel_writer=f'downloads/{safe_filename} - {date.today()}.xlsx',
        sheet_name='Grants Data',
        index=False
    )
    plots = visualize_data(df)
    return f'{safe_filename} - {date.today()}.xlsx', plots
