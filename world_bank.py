import zipfile
import io
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import pandas as pd

# or: requests.get(url).content

resp = urlopen("https://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.KD.ZG?downloadformat=csv")
zip1 = BytesIO(resp.read())
myzip = ZipFile(zip1)


def make_df(file, csv_name):
    list1 = []
    with zipfile.ZipFile(file=zip1, mode="r") as archive:
        with archive.open(file, mode="r") as csv_sheet:
            for line in io.TextIOWrapper(csv_sheet, encoding="utf-8"):
                line = line.strip().replace('"', '')
                line_list = line.split(',')
                list1.append(line_list)
    df = pd.DataFrame(list1)
    df.to_csv(f'{csv_name}.csv', index=False, header=False)


numb = 1
with zipfile.ZipFile(zip1, mode="r") as archive:
    for info in archive.infolist():
        make_df(info.filename, info.filename)
        numb += 1

