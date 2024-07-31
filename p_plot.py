import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# read traffic log
logFile = 'traffic.log'
with open(logFile, 'r') as file:
    trafficData = file.readlines()

# get parameters
data = []
for line in trafficData:
    parts = line.strip().split(' - ')
    if len(parts) == 3:
        timeInterval, action, server = parts
        serverNum = int(server.split(': ')[1])
        data.append([timeInterval, serverNum])
df = pd.DataFrame(data, columns=['time', 'server'])

base_date = datetime.now().date()
df['time'] = df['time'].apply(lambda x: datetime.combine(base_date, datetime.strptime(x, '%M:%S.%f').time()))
df = df.sort_values('time')

# calculate parameters
start_time = df['time'].min()
df['elapsedTime'] = (df['time'] - start_time).dt.total_seconds()
df['totalPkts'] = df.groupby('server').cumcount() + 1
df['avgPkts'] = df['totalPkts'] / df['elapsedTime']

# plot
plt.figure(figsize=(12, 5))
for server in df['server'].unique():
    server_data = df[df['server'] == server]
    plt.plot(server_data['elapsedTime'], server_data['avgPkts'], label=f'Server {server}')

plt.xlabel('Time/seconds')
plt.ylabel('Average Packets Received')
plt.title('Traffic Statistics')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# final results
finalResult = df.groupby('server').last()['avgPkts']
print("average number of packets:")
for server, avg in finalResult.items():
    print(f"Server {server}: {avg:.2f} packets/second")
