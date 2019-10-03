# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# Empty properties and second homes

# +
from gssutils import *

scraper = Scraper('https://www2.gov.scot/Topics/Statistics/Browse/Housing-Regeneration/HSfS/LTemptysecondhomes/EmptySecondhometables')
scraper
# -

tabs = {tab.name: tab for tab in scraper.distribution().as_databaker()}
tabs.keys()

tabs = scraper.distribution().as_databaker()

tab = next(t for t in tabs if t.name=='Second Homes & Empty properties')
cell = tab.filter(contains_string('2005'))
year = tab.filter(contains_string('Scotland')).shift(0,-1).fill(RIGHT)\
        .is_not_blank().is_not_whitespace()
observations = year.fill(DOWN).is_not_blank().is_not_whitespace().is_number() - year
area = cell.fill(DOWN).is_not_blank().is_not_whitespace() - cell

Dimensions = [
            HDim(year,'Year',DIRECTLY,ABOVE),
            HDim(area,'Geography',DIRECTLY,LEFT),
            HDim(cell,'Tenure',CLOSEST,ABOVE),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit', 'dwellings')
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
table = c1.topandas()

table['Tenure'] = table['Tenure'].map(
    lambda x: {
        'Second Homes and long term empty1 properties, 2005 - 2018' : 'second-homes-and-long-term-empty-properties/total',
       'Long term empty1 properties, 2005 - 2018' : 'second-homes-and-long-term-empty-properties/long-term-empty-properties',
       'Second Homes, 2005 - 2018' : 'second-homes-and-long-term-empty-properties/second-homes'
        }.get(x, x))

table['Period'] = 'year/' + table['Year'].astype(str).str[0:4]

import numpy as np
table['OBS'].replace('', np.nan, inplace=True)
table.dropna(subset=['OBS'], inplace=True)
table.rename(columns={'OBS': 'Value'}, inplace=True)
table['Value'] = table['Value'].astype(int)

table['Geography'] = table['Geography'].str.rstrip('12345678')
table['Geography'] = table['Geography'].str.strip()

scotland_gss_codes = pd.read_csv('scotland-gss.csv', index_col='Area')
table['Geography'] = table['Geography'].map(
    lambda x: scotland_gss_codes.loc[x]['Code']
)

table = table[['Period','Geography','Tenure','Measure Type','Value','Unit']]

tidy = pd.DataFrame()
tidy = pd.concat([tidy , table])

tab1 = next(t for t in tabs if t.name=='Unoccupied exemptions')
year1 = tab1.filter(contains_string('SCOTLAND')).shift(0,-1).fill(RIGHT).is_not_blank().is_not_whitespace()
observations1 = year1.fill(DOWN).is_not_blank().is_not_whitespace().is_number() - year1
area1 = tab1.filter(contains_string('SCOTLAND')).expand(DOWN).is_not_blank().is_not_whitespace()

Dimensions1 = [
            HDim(year1,'Year',DIRECTLY,ABOVE),
            HDim(area1,'Geography',DIRECTLY,LEFT),
            HDimConst('Tenure','second-homes-and-long-term-empty-properties/unoccupied-exemptions'),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit', 'dwellings')
            ]
c2 = ConversionSegment(observations1, Dimensions1, processTIMEUNIT=True)
table1 = c2.topandas()

table1['Period'] = 'year/' + table1['Year'].astype(str).str[0:4]

import numpy as np
table1['OBS'].replace('', np.nan, inplace=True)
table1.dropna(subset=['OBS'], inplace=True)
table1.rename(columns={'OBS': 'Value'}, inplace=True)
table1['Value'] = table1['Value'].astype(int)

table1['Geography'] = table1['Geography'].map(
    lambda x: {
        'SCOTLAND' : 'Scotland',
        'Glasgow' : 'Glasgow City'
        }.get(x, x))


scotland_gss_codes = pd.read_csv('scotland-gss.csv', index_col='Area')
table1['Geography'] = table1['Geography'].map(
    lambda x: scotland_gss_codes.loc[x]['Code']
)

table1 = table1[['Period','Geography','Tenure','Measure Type','Value','Unit']]

tidy = pd.concat([tidy , table1])

out = Path('out')
out.mkdir(exist_ok=True)
tidy.drop_duplicates().to_csv(out / 'observations.csv', index = False)

# +
scraper.dataset.family = 'housing'
scraper.dataset.theme = THEME['housing-planning-local-services']
with open(out / 'dataset.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
    
schema = CSVWMetadata('https://gss-cogs.github.io/ref_housing/')
schema.create(out / 'observations.csv', out / 'observations.csv-schema.json')
# -

tidy


