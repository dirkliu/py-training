import pandas as pd;

data = [['Google', 2000], ['Microsoft', 1975], ['Apple', 1976]];
df = pd.DataFrame(data, columns=['Company', 'Year Founded']);
print(df);