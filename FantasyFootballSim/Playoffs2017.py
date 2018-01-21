import pdb
import copy
import numpy as np
Team = {'name':'', 'wins':0, 'losses':0, 'pf':0, 'num':0}


Team1 = {'name':'Ammar', 'wins':6, 'losses':6, 'pf':1086, 'num':0}
Team2 = {'name':'Ajay', 'wins':6, 'losses':6, 'pf':1065.6, 'num':1}
Team3 = {'name':'Paul', 'wins':4, 'losses':8, 'pf':1163, 'num':2}
Team4 = {'name':'Karthik', 'wins':1, 'losses':11, 'pf':1001.5, 'num':3}
Team5 = {'name':'Darshan', 'wins':3, 'losses':9, 'pf':1017.1, 'num':4}
Team6 = {'name':'Aakaash', 'wins':10, 'losses':2, 'pf':1253.3, 'num':5}
Team7 = {'name':'Rohan', 'wins':6, 'losses':6, 'pf':1115.3, 'num':6}
Team8 = {'name':'Ankit', 'wins':5, 'losses':7, 'pf':1157.8, 'num':7}
Team9 = {'name':'Aroon', 'wins':6, 'losses':6, 'pf':1316.4, 'num':8}
Team10 = {'name':'Anish', 'wins':7, 'losses':5, 'pf':1281, 'num':9}
Team11 = {'name':'Darshita', 'wins':6, 'losses':6, 'pf':1101.1, 'num':10}
Team12 = {'name':'Michael', 'wins':9, 'losses':3, 'pf':1228.1, 'num':11}
Team13 = {'name':'Jennivan', 'wins':6, 'losses':6, 'pf':1135.9, 'num':12}
Team14 = {'name':'Arya', 'wins':9, 'losses':3, 'pf':1163.6, 'num':13}


Teams = [Team1, Team2, Team3, Team4, Team5, Team6, Team7, Team8, Team9, Team10, Team11, Team12, Team13, Team14]

Week13 = [[0,1], [2,3], [4,5], [6,7], [8,9], [10,11], [12,13]]

def rank(team):
	ranked_teams = sorted(team, key = lambda k: (k['wins'], k['pf']), reverse = True)
	return ranked_teams

def playWeek(week):
	ranked = rank()
	# for a given team,
	# if they win
	# how many points do they have to win by to be in the top 6?
	for i_t in range(len(Teams)):
		for w in week:
			t1 = Teams[w[0]];
			t2 = Teams[w[1]];
			if t1['wins'] != 6 and t2['wins'] != 6:
				continue # don't care!
			pdb.set_trace()

def printTable(team_list):
	row_format ="{:<15}" * 4
	for team in team_list:
		print(row_format.format(team['name'], team['wins'], team['losses'], team['pf']))


def possibleOutcomes(week):
	out = []
	p = []
	for i in range(1000):
		for w in week:
			p.append(np.random.choice(w))
		if p not in out:
			out.append(copy.deepcopy(p))
		p = []
	return out

def pointDiffMatters(teams):
	print_flag = True
	pf = teams[5]
	# check if any other team has the same number of wins
	for t in teams:
		if t != pf:
			if t['wins'] == pf['wins']:
				if print_flag:
					printTable(teams)
					print('******Point Differential Matters:  %s' %pf['name'])
					print_flag = False
				print('******Point Differential Matters:  %s' %t['name'])

def updateStandings(outs, week):
	for i in range(len(outs)):
		Teams_updated = copy.deepcopy(Teams)
		out = outs[i]
		for o in out:
			Teams_updated[o]['wins'] += 1
		for o in list(set(range(13))-set(out)):
			Teams_updated[o]['losses'] += 1
		Teams_ranked = rank(Teams_updated)
		pointDiffMatters(Teams_ranked)

		rank(Teams_updated)


		pdb.set_trace()

def main():
	# rank()
	outs = possibleOutcomes(Week13)
	updateStandings(outs, Week13)
	# playWeek(Week13)



if __name__ == '__main__':
	main()

