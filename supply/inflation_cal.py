from random import sample
import matplotlib.pyplot as plt
import matplotlib.colors as pltc
import numpy as np
import csv
import argparse

# Initial supply
initial_supply = 750000000
# Total Supply
total_supply = 2500000000
# Base halving. For each experiment, we will divide this number by the multiplier value
base_halving = 1750000
# Base reward. For each experiment, we will multiply this number by the multiplier value
base_reward=500
all_colors = [k for k,v in pltc.cnames.items()]
# Epoch seconds considered
epoch_periods = [30, 60, 90]
# Multipliers
reward_multipliers = [0.5, 1, 1.5, 2, 2.5, 3]
final_results = []
labels = []

def calculate_vest(reward_per_second, step, target_share, witnet_share):
  # Results vec
  results = np.arange(0, 1, step)
  reward = reward_per_second

  inflation_values = []
  # Supply of the network
  net_supply = 0
  distris = step
  index = 1
  current_halving = int(base_halving/reward)
  for i in range(0, results.size):
    # We calculate the index for each step. 
    distris = step*(i+1)

    # Main condition. Calculate index until the witnet_share*total_supply*percentage/(circulating suppy) > than target_share
    while (witnet_share * distris * total_supply/(initial_supply+net_supply)) > target_share:
      # Increment the network supply
      net_supply = net_supply + reward*base_reward
      # Increment index
      index = index + 1
      # If index reaches the halving period, divide reward by 2-
      if(index % (current_halving) == 0):
        reward = reward/2

    # Store the index at which we broke the condition
    results[i] = index
  return results

def calculate_inf(reward_per_second):
  # Results vec
  reward = reward_per_second

  inflation_values = []
  supply_values = []
  # Supply of the network
  net_supply = 0
  index = 1
  inflation = 0
  current_halving = int(base_halving/reward)
  anual_supply = initial_supply

    # Main condition. Calculate index until the witnet_share*total_supply*percentage/(circulating suppy) > than target_share
  while True:
      # Increment the network supply
      net_supply = net_supply + reward*base_reward
      # Inflation calc
      inflation = inflation + reward*base_reward
      # Increment index
      index = index + 1
      # If index reaches the halving period, divide reward by 2-
      if(index % (current_halving) == 0):
        reward = reward/2

      if ( (index*90) % (3600*24*365) == 0):
        inflation_values.append(inflation/anual_supply)
        anual_supply = initial_supply + net_supply
        supply_values.append(net_supply+initial_supply)
        inflation = 0
      if(index==10512000):
        break;
  return inflation_values, supply_values


def main(args):
  with open('vesting.csv', 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)

    # set the labels for the graph
    for index, item in enumerate(reward_multipliers):
        labels.append('Reward multipliter/ halving divider '+str(item))

    # Get N different colours
    colors = sample(all_colors, len(reward_multipliers))

    # For each Multiplier (reward*multiplier, halving/multiplier), get results
    for index, rew in enumerate(reward_multipliers):
        iterated_colors = iter(colors)
        current_res= calculate_vest(rew, args.step, args.target_share, args.witnet_share)
        current_inf, current_sup = calculate_inf(rew)
        final_results.append(current_res)
        plt.subplot(3, 1, 1)
        plt.plot(np.arange(args.step, 1+args.step, args.step), current_res, c = colors[index])
        # Finally plot the graph
        plt.ylabel('Number of epochs elapsed')
        plt.xlabel('Percentage released')
        plt.subplot(3, 1, 2)
        plt.plot(np.arange(1, len(current_inf) +1, 1), current_inf,  c = colors[index])
        plt.xlabel('Year')
        plt.ylabel('Inflation rate')
        plt.subplot(3, 1, 3)
        plt.plot(np.arange(1, len(current_sup) +1, 1), current_sup,  c = colors[index])
        plt.xlabel('Year')
        plt.ylabel('Circulating supply')


    # Start writing the results in a CSV file
    for item in epoch_periods:
      filewriter.writerow(["EPOCH="+str(item)])
      filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
      csv_vector = ['Reward/halving Multiplier']
      steps = np.arange(args.step, 1 + args.step, args.step)
      for k in steps:
        csv_vector.append("Week at which "+ str(np.round(k*100,2))+"% can be released")

      filewriter.writerow(csv_vector)

      for i in range(len(reward_multipliers)):
        file_row = [str(reward_multipliers[i])]
        for res in final_results[i]:
          file_row.append(str(int(res*item/(3600*24*7))))
        filewriter.writerow(file_row)

    plt.figlegend(labels)
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate vesting tokens')
    parser.add_argument('--witnet_share', dest='witnet_share', action='store', required=True,type=float,
                    help='provide the share of the tokens that the foundation has')
    parser.add_argument('--target_share', dest='target_share', action='store', required=True, type=float,
                    help='target share we would like to have from the circulating suuply')
    parser.add_argument('--step', dest='step', action='store', required=True, type=float,
                    help='Steps after which we are releasing the tokens')

    args = parser.parse_args()
    main(args)
