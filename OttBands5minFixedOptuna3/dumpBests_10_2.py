import optuna
import statistics
import hashlib

study = optuna.create_study(study_name="Band5min", directions=["maximize", "maximize"],
                                storage="postgresql://optuna_user:optuna_password@localhost/optuna_db_10_2", load_if_exists=True)

def print_best_params():
    print("Number of finished trials: ", len(study.trials))

    trials = study.trials  # sorted(study.best_trials, key=lambda t: t.values)
    
    results = []
    parameter_list = []  # to eliminate redundant trials with same parameters
    candidates = []
    score_treshold = 1.5
    std_dev_treshold = 3
    
    for trial in trials:
        if any(v < 1 for v in trial.values):
            continue
    
        mean_value = round(statistics.mean((*trial.values, trial.user_attrs['sharpe3'])), 3)
        std_dev = round(statistics.stdev((*trial.values, trial.user_attrs['sharpe3'])), 5)
        
        rounded_params = trial.params  # {key : round(trial.params[key], 5) for key in trial.params}
        # join rounded_params values with '_'
        joined_params = '_'.join([str(value) for key, value in rounded_params.items()])
        print(joined_params)
        
        result_line = [trial.number, *trial.values, trial.user_attrs['sharpe3'],
                       trial.user_attrs['trades1'], trial.user_attrs['trades2'], trial.user_attrs['trades3'],
                       trial.user_attrs['fees1'], trial.user_attrs['fees2'], trial.user_attrs['fees3'],
                       trial.user_attrs['wr1'], trial.user_attrs['wr2'], trial.user_attrs['wr3'],
                       mean_value, std_dev, rounded_params]
        
        if trial.params not in parameter_list:
            results.append(result_line)
            parameter_list.append(trial.params)

            if mean_value > score_treshold and std_dev < std_dev_treshold:
                # hash = hashlib.sha1(str(rounded_params).encode("UTF-8")).hexdigest()[:10]  # Adler32 hash
                hash = ''.join([f'{value:0>3}.' for key, value in rounded_params.items()])
                candidates.append([hash, rounded_params])
    
    sorted_results = sorted(results, key=lambda x: x[2], reverse=True)
    # for r in sorted_results:
    #     print(r)
    print(len(results))
    
    import csv
    
    # field names 
    fields = ['Trial #', 'Score1', 'Score2', 'Score3',
              'Trades1', 'Trades2', 'Trades3',
              'Fees1', 'Fees2', 'Fees3',
              'Winrate1', 'Winrate2', 'Winrate3',
              'Average', 'Deviation',
              'Parameters'] 
        
    with open('Results_10_2.csv', 'w') as f:
        # using csv.writer method from CSV package
        write = csv.writer(f, delimiter='\t', lineterminator='\n')
        
        write.writerow(fields)
        write.writerows(results)
        
    with open('10_2_.py', 'w') as f:
        f.write("params = [\n")
        
        for sr in candidates:
            f.write(f"{sr},\n")

        f.write("]")
        
print_best_params()

# df = study.trials_dataframe(attrs=("number", "value", "params", "state"))

# print("Best params: ", study.best_params)
# print("Best value: ", study.best_value)
# print("Best Trial: ", study.best_trial)
# print("Trials: ", study.trials)


